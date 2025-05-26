from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Application
import json
import random
import string
import datetime


@login_required
def business_license_form(request):
    """
    Simplified Business License application form
    """
    # Get user's businesses with tax compliance (TIN)
    from applications.models import Business

    # First, try to get businesses from the Business model that have a TIN
    businesses_with_tin = Business.objects.filter(
        user=request.user, tin__isnull=False, is_approved=True
    ).order_by("-registration_date")

    # Check if any of these businesses already have a license
    businesses_without_license = []

    for business in businesses_with_tin:
        # Skip businesses that already have a license
        if business.has_license:
            continue

        # Check if this business already has a pending license application
        has_pending_license = False

        for license_app in Application.objects.filter(
            user=request.user,
            application_type="Business License",
            status__in=["submitted", "under_review"],
        ):
            try:
                license_data = json.loads(license_app.data)
                if license_data.get("business_reference") == business.reference:
                    has_pending_license = True
                    break
            except (json.JSONDecodeError, KeyError):
                continue

        if not has_pending_license:
            # Add to the list of available businesses
            businesses_without_license.append(
                {
                    "id": business.id,
                    "name": business.name,
                    "type": business.business_type,
                    "reference": business.reference,
                    "tin": business.tin,
                    "is_business_model": True,
                }
            )

    # If no businesses found in the Business model, fall back to applications
    if not businesses_without_license:
        # Get approved tax compliance applications
        approved_tax_apps = Application.objects.filter(
            user=request.user, application_type="Tax Compliance", status="approved"
        ).order_by("-submission_date")

        # For each approved tax compliance, get the business details
        for tax_app in approved_tax_apps:
            try:
                tax_data = json.loads(tax_app.data)
                business_id = tax_data.get("registered_business_id")
                tin_number = tax_data.get("tin_number")

                if business_id and tin_number:
                    # Check if this business already has a business license application
                    existing_license = False

                    for license_app in Application.objects.filter(
                        user=request.user,
                        application_type="Business License",
                        status__in=["submitted", "under_review", "approved"],
                    ):
                        try:
                            license_data = json.loads(license_app.data)
                            if str(license_data.get("tax_compliance_id")) == str(
                                tax_app.id
                            ):
                                existing_license = True
                                break
                        except (json.JSONDecodeError, KeyError):
                            continue

                    if not existing_license:
                        # Get the business registration details
                        try:
                            business = Application.objects.get(id=business_id)
                            business_data = {}

                            if business.data:
                                try:
                                    business_data = json.loads(business.data)
                                except json.JSONDecodeError:
                                    pass

                            # Add to the list of available businesses
                            businesses_without_license.append(
                                {
                                    "id": tax_app.id,  # Use tax compliance app ID
                                    "name": business_data.get("business_name", ""),
                                    "type": business_data.get("business_type", ""),
                                    "reference": business.reference_number,
                                    "tin": tin_number,
                                    "is_business_model": False,
                                    "tax_app_id": tax_app.id,
                                    "business_id": business_id,
                                }
                            )
                        except Application.DoesNotExist:
                            continue
            except (json.JSONDecodeError, KeyError):
                continue

    # Check if user has any businesses with tax compliance
    if not businesses_without_license:
        messages.warning(
            request,
            "You need to have an approved Tax Compliance application before applying for a Business License.",
        )
        return redirect("applications:tax_compliance_form")

    # Process form submission
    if request.method == "POST":
        # Get the selected business and license type
        business_id = request.POST.get("business_id")
        is_business_model = (
            request.POST.get("is_business_model", "false").lower() == "true"
        )
        license_type = request.POST.get("license_type")

        if not business_id:
            messages.error(request, "Please select a business with Tax Compliance.")
            return render(
                request,
                "applications/business_license_form.html",
                {"businesses_without_license": businesses_without_license},
            )

        if not license_type:
            messages.error(request, "Please select a license type.")
            return render(
                request,
                "applications/business_license_form.html",
                {"businesses_without_license": businesses_without_license},
            )

        # If using Business model
        if is_business_model:
            try:
                # Get the business from the Business model
                business = Business.objects.get(
                    id=business_id,
                    user=request.user,
                    tin__isnull=False,
                    is_approved=True,
                )

                # Check if business already has a license
                if business.has_license:
                    messages.error(request, "This business already has a license.")
                    return render(
                        request,
                        "applications/business_license_form.html",
                        {"businesses_without_license": businesses_without_license},
                    )

                # Check if this business already has a pending license application
                for license_app in Application.objects.filter(
                    user=request.user,
                    application_type="Business License",
                    status__in=["submitted", "under_review"],
                ):
                    try:
                        license_data = json.loads(license_app.data)
                        if license_data.get("business_reference") == business.reference:
                            messages.error(
                                request,
                                f"This business already has a pending license application (Ref: {license_app.reference_number}).",
                            )
                            return render(
                                request,
                                "applications/business_license_form.html",
                                {
                                    "businesses_without_license": businesses_without_license
                                },
                            )
                    except (json.JSONDecodeError, KeyError):
                        continue

                # Generate a reference number based on the business reference
                business_ref = business.reference
                business_ref_parts = business_ref.split("-")
                if len(business_ref_parts) >= 3:
                    # Use the same year and sequence from business registration
                    year_part = business_ref_parts[1]
                    sequence_part = business_ref_parts[2]
                    reference_number = f"LIC-{year_part}-{sequence_part}"
                else:
                    # Fallback to random generation
                    current_year = datetime.datetime.now().year
                    random_chars = "".join(
                        random.choices(string.ascii_uppercase + string.digits, k=6)
                    )
                    reference_number = f"LIC-{current_year}-{random_chars}"

                # Determine license duration based on license type
                license_durations = {
                    "Retail": "2 Years",
                    "Wholesale": "3 Years",
                    "Manufacturing": "5 Years",
                    "Service": "2 Years",
                    "Tourism": "3 Years",
                }
                license_duration = license_durations.get(license_type, "1 Year")

                # Prepare application data
                application_data = {
                    "business_id": business.id,
                    "business_reference": business.reference,
                    "business_name": business.name,
                    "business_type": business.business_type,
                    "business_address": business.address,
                    "tin_number": business.tin,
                    "license_type": license_type,
                    "license_duration": license_duration,
                    "is_business_model": True,
                }

                # Create the business license application
                Application.objects.create(
                    user=request.user,
                    application_type="Business License",
                    reference_number=reference_number,
                    status="submitted",  # Direct submission
                    data=json.dumps(application_data),
                )

                messages.success(
                    request,
                    "Your Business License application has been submitted successfully.",
                )
                return redirect("applications:list")

            except Business.DoesNotExist:
                messages.error(
                    request, "Selected business not found or does not have a TIN."
                )
                return render(
                    request,
                    "applications/business_license_form.html",
                    {"businesses_without_license": businesses_without_license},
                )

        # If using Application model
        else:
            try:
                # Get the tax compliance application
                tax_app = Application.objects.get(
                    id=business_id,  # This is actually the tax_app_id
                    user=request.user,
                    application_type="Tax Compliance",
                    status="approved",
                )

                # Parse the tax compliance data
                tax_data = {}
                if tax_app.data:
                    try:
                        tax_data = json.loads(tax_app.data)
                    except json.JSONDecodeError:
                        pass

                # Get the business registration details
                registered_business_id = tax_data.get("registered_business_id")
                business = None
                business_data = {}

                if registered_business_id:
                    try:
                        business = Application.objects.get(id=registered_business_id)
                        if business.data:
                            try:
                                business_data = json.loads(business.data)
                            except json.JSONDecodeError:
                                pass
                    except Application.DoesNotExist:
                        pass

                # Generate a reference number based on the business registration
                if business:
                    business_ref = business.reference_number
                    business_ref_parts = business_ref.split("-")
                    if len(business_ref_parts) >= 3:
                        # Use the same year and sequence from business registration
                        year_part = business_ref_parts[1]
                        sequence_part = business_ref_parts[2]
                        reference_number = f"LIC-{year_part}-{sequence_part}"
                    else:
                        # Fallback to random generation
                        current_year = datetime.datetime.now().year
                        random_chars = "".join(
                            random.choices(string.ascii_uppercase + string.digits, k=6)
                        )
                        reference_number = f"LIC-{current_year}-{random_chars}"
                else:
                    # Fallback to random generation
                    current_year = datetime.datetime.now().year
                    random_chars = "".join(
                        random.choices(string.ascii_uppercase + string.digits, k=6)
                    )
                    reference_number = f"LIC-{current_year}-{random_chars}"

                # Determine license duration based on license type
                license_durations = {
                    "Retail": "2 Years",
                    "Wholesale": "3 Years",
                    "Manufacturing": "5 Years",
                    "Service": "2 Years",
                    "Tourism": "3 Years",
                }
                license_duration = license_durations.get(license_type, "1 Year")

                # Prepare application data
                application_data = {
                    "tax_compliance_id": tax_app.id,
                    "tax_compliance_reference": tax_app.reference_number,
                    "business_id": (
                        registered_business_id if registered_business_id else ""
                    ),
                    "business_reference": business.reference_number if business else "",
                    "business_name": business_data.get("business_name", ""),
                    "business_type": business_data.get("business_type", ""),
                    "business_address": business_data.get("business_address", ""),
                    "tin_number": tax_data.get("tin_number", ""),
                    "license_type": license_type,
                    "license_duration": license_duration,
                    "is_business_model": False,
                }

                # Create the business license application
                Application.objects.create(
                    user=request.user,
                    application_type="Business License",
                    reference_number=reference_number,
                    status="submitted",  # Direct submission
                    data=json.dumps(application_data),
                )

                messages.success(
                    request,
                    "Your Business License application has been submitted successfully.",
                )
                return redirect("applications:list")

            except Application.DoesNotExist:
                messages.error(
                    request,
                    "Selected Tax Compliance application not found or not approved.",
                )

    # Render the form
    return render(
        request,
        "applications/business_license_form.html",
        {"businesses_without_license": businesses_without_license},
    )
