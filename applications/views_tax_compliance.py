from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Application
import json
import random
import string
import datetime


@login_required
def tax_compliance_form(request):
    """
    Simplified Tax Compliance application form
    """
    # Get user's approved business registrations
    from applications.models import Business

    # First, get businesses from the Business model
    user_businesses = Business.objects.filter(
        user=request.user, is_approved=True
    ).order_by("-registration_date")

    # If no businesses found in the Business model, fall back to applications
    if not user_businesses.exists():
        # Get approved business registration applications
        approved_businesses = Application.objects.filter(
            user=request.user,
            application_type="Business Registration",
            status="approved",
        ).order_by("-submission_date")

        # Check if user has any approved business registrations
        if not approved_businesses.exists():
            messages.warning(
                request,
                "You need to have an approved business registration before applying for Tax Compliance.",
            )
            return redirect("applications:create")

    # Get businesses that already have tax compliance applications or TIN
    businesses_with_tax_compliance = []

    # First check businesses with TIN in the Business model
    businesses_with_tin = Business.objects.filter(
        user=request.user, tin__isnull=False
    ).values_list("reference", flat=True)

    # Then check applications for businesses that have tax compliance applications
    tax_applications = Application.objects.filter(
        user=request.user,
        application_type="Tax Compliance",
        status__in=["submitted", "under_review", "approved"],
    )

    for tax_app in tax_applications:
        try:
            tax_data = json.loads(tax_app.data)
            registered_business_id = tax_data.get("registered_business_id")
            if registered_business_id:
                # Get the business registration application
                try:
                    business_app = Application.objects.get(id=registered_business_id)
                    businesses_with_tax_compliance.append(business_app.id)
                except Application.DoesNotExist:
                    continue
        except (json.JSONDecodeError, KeyError):
            continue

    # Get available businesses (those without tax compliance)
    available_businesses = []

    # First try to get businesses from the Business model
    if user_businesses.exists():
        for business in user_businesses:
            # Skip businesses that already have a TIN
            if business.tin:
                continue

            # Check if this business already has a tax compliance application
            has_tax_compliance = False
            for tax_app in tax_applications:
                try:
                    tax_data = json.loads(tax_app.data)
                    if (
                        tax_data.get("registered_business_reference")
                        == business.reference
                    ):
                        has_tax_compliance = True
                        break
                except (json.JSONDecodeError, KeyError):
                    continue

            if not has_tax_compliance:
                # Add business to available businesses
                available_businesses.append(
                    {
                        "id": business.id,
                        "name": business.name,
                        "reference": business.reference,
                        "type": business.business_type,
                        "is_business_model": True,
                    }
                )

    # If no businesses found in the Business model, fall back to applications
    if not available_businesses:
        approved_businesses = (
            Application.objects.filter(
                user=request.user,
                application_type="Business Registration",
                status="approved",
            )
            .exclude(id__in=businesses_with_tax_compliance)
            .order_by("-submission_date")
        )

        for business in approved_businesses:
            try:
                # Extract business data
                business_data = {}
                try:
                    business_data = json.loads(business.data)
                except json.JSONDecodeError:
                    print(f"Error parsing JSON for business {business.id}")

                # Try multiple approaches to get the business name
                business_name = None

                # First try: direct business_name field
                if "business_name" in business_data and business_data["business_name"]:
                    business_name = business_data["business_name"]
                    print(
                        f"Found business name in business_name field: {business_name}"
                    )

                # Second try: look for any field containing 'name'
                if not business_name:
                    for key, value in business_data.items():
                        if isinstance(value, str) and "name" in key.lower() and value:
                            business_name = value
                            print(
                                f"Found business name in {key} field: {business_name}"
                            )
                            break

                # Third try: use contact name as fallback
                if (
                    not business_name
                    and "contact_name" in business_data
                    and business_data["contact_name"]
                ):
                    business_name = f"{business_data['contact_name']}'s Business"
                    print(f"Using contact name as fallback: {business_name}")

                # Last resort: use reference number
                if not business_name:
                    business_name = f"Business {business.reference_number}"
                    print(f"Using reference number as fallback: {business_name}")

                print(
                    f"Final business name for {business.reference_number}: {business_name}"
                )

                # Print the entire business data for debugging
                print(f"Complete business data: {business_data}")

                available_businesses.append(
                    {
                        "id": business.id,
                        "name": business_name,
                        "reference": business.reference_number,
                        "type": business_data.get("business_type", ""),
                        "is_business_model": False,
                    }
                )
            except (json.JSONDecodeError, KeyError):
                continue

    # Process form submission
    if request.method == "POST":
        # Get the selected registered business
        registered_business_id = request.POST.get("registered_business")
        is_business_model = (
            request.POST.get("is_business_model", "false").lower() == "true"
        )

        if not registered_business_id:
            messages.error(request, "Please select a registered business.")
            return render(
                request,
                "applications/tax_compliance_form.html",
                {
                    "available_businesses": available_businesses,
                },
            )

        # Check if this business already has a tax compliance application
        existing_tax_application = None

        # If using Business model
        if is_business_model:
            try:
                business = Business.objects.get(
                    id=registered_business_id, user=request.user
                )

                # Check if business already has a TIN
                if business.tin:
                    messages.error(
                        request,
                        f"This business already has a Tax Identification Number (TIN): {business.tin}",
                    )
                    return render(
                        request,
                        "applications/tax_compliance_form.html",
                        {
                            "available_businesses": available_businesses,
                        },
                    )

                # Check for existing tax compliance applications for this business
                for tax_app in tax_applications:
                    try:
                        tax_data = json.loads(tax_app.data)
                        if (
                            tax_data.get("registered_business_reference")
                            == business.reference
                        ):
                            existing_tax_application = tax_app
                            break
                    except (json.JSONDecodeError, KeyError):
                        continue

                if existing_tax_application:
                    messages.error(
                        request,
                        f"This business already has a Tax Compliance application (Ref: {existing_tax_application.reference_number}).",
                    )
                    return render(
                        request,
                        "applications/tax_compliance_form.html",
                        {
                            "available_businesses": available_businesses,
                        },
                    )

                # Generate a reference number based on the business reference
                business_ref = business.reference
                business_ref_parts = business_ref.split("-")
                if len(business_ref_parts) >= 3:
                    # Use the same year and sequence from business registration
                    year_part = business_ref_parts[1]
                    sequence_part = business_ref_parts[2]
                    reference_number = f"TAX-{year_part}-{sequence_part}"
                else:
                    # Fallback to random generation if business ref format is unexpected
                    current_year = datetime.datetime.now().year
                    random_chars = "".join(
                        random.choices(string.ascii_uppercase + string.digits, k=6)
                    )
                    reference_number = f"TAX-{current_year}-{random_chars}"

                # Prepare application data
                application_data = {
                    "registered_business_id": registered_business_id,
                    "registered_business_reference": business.reference,
                    "business_name": business.name,
                    "business_type": business.business_type,
                    "business_address": business.address,
                    "is_business_model": True,
                }

                # Create the tax compliance application
                Application.objects.create(
                    user=request.user,
                    application_type="Tax Compliance",
                    reference_number=reference_number,
                    status="submitted",  # Direct submission
                    data=json.dumps(application_data),
                )

                messages.success(
                    request,
                    "Your Tax Compliance application has been submitted successfully.",
                )
                return redirect("applications:list")

            except Business.DoesNotExist:
                messages.error(request, "Selected business not found or not approved.")
                return render(
                    request,
                    "applications/tax_compliance_form.html",
                    {
                        "available_businesses": available_businesses,
                    },
                )

        # If using Application model
        else:
            # Check for existing tax compliance applications for this business
            for tax_app in tax_applications:
                try:
                    tax_data = json.loads(tax_app.data)
                    if str(tax_data.get("registered_business_id")) == str(
                        registered_business_id
                    ):
                        existing_tax_application = tax_app
                        break
                except (json.JSONDecodeError, KeyError):
                    continue

            if existing_tax_application:
                messages.error(
                    request,
                    f"This business already has a Tax Compliance application (Ref: {existing_tax_application.reference_number}).",
                )
                return render(
                    request,
                    "applications/tax_compliance_form.html",
                    {
                        "available_businesses": available_businesses,
                    },
                )

            # Get the registered business details
            try:
                registered_business = Application.objects.get(
                    id=registered_business_id,
                    user=request.user,
                    application_type="Business Registration",
                    status="approved",
                )

                # Parse the business data
                business_data = {}
                if registered_business.data:
                    try:
                        business_data = json.loads(registered_business.data)
                    except json.JSONDecodeError:
                        pass

                # Generate a reference number based on the business registration
                business_ref = registered_business.reference_number
                business_ref_parts = business_ref.split("-")
                if len(business_ref_parts) >= 3:
                    # Use the same year and sequence from business registration
                    year_part = business_ref_parts[1]
                    sequence_part = business_ref_parts[2]
                    reference_number = f"TAX-{year_part}-{sequence_part}"
                else:
                    # Fallback to random generation if business ref format is unexpected
                    current_year = datetime.datetime.now().year
                    random_chars = "".join(
                        random.choices(string.ascii_uppercase + string.digits, k=6)
                    )
                    reference_number = f"TAX-{current_year}-{random_chars}"

                # Extract business name with fallbacks
                business_name = business_data.get("business_name", "")

                # If business_name is empty, try to find it in other fields
                if not business_name:
                    for key, value in business_data.items():
                        if "name" in key.lower() and value:
                            business_name = value
                            print(f"Found business name '{value}' in field '{key}'")
                            break

                # If still no business name, try to extract from other fields
                if not business_name and "contact_name" in business_data:
                    business_name = f"{business_data['contact_name']}'s Business"
                    print(f"Using contact name as fallback: {business_name}")

                # If still no name, use a placeholder with the reference number
                if not business_name:
                    business_name = f"Business {registered_business.reference_number}"
                    print(f"Using reference number as fallback: {business_name}")

                print(f"Final business name for tax compliance: {business_name}")

                # Prepare application data
                application_data = {
                    "registered_business_id": registered_business_id,
                    "registered_business_reference": registered_business.reference_number,
                    "business_name": business_name,
                    "business_type": business_data.get("business_type", ""),
                    "business_address": business_data.get("business_address", ""),
                    "is_business_model": False,
                }

                # Create the tax compliance application
                Application.objects.create(
                    user=request.user,
                    application_type="Tax Compliance",
                    reference_number=reference_number,
                    status="submitted",  # Direct submission
                    data=json.dumps(application_data),
                )

                messages.success(
                    request,
                    "Your Tax Compliance application has been submitted successfully.",
                )
                return redirect("applications:list")

            except Application.DoesNotExist:
                messages.error(request, "Selected business not found or not approved.")

    # Render the form
    return render(
        request,
        "applications/tax_compliance_form.html",
        {
            "available_businesses": available_businesses,
        },
    )
