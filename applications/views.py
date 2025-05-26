from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Application
import json
import random
import string
import datetime


@login_required
def application_list(request):
    applications = Application.objects.filter(user=request.user).order_by(
        "-submission_date"
    )

    # Filter by status if provided
    status_filter = request.GET.get("status")
    if status_filter and status_filter != "all":
        applications = applications.filter(status=status_filter)

    context = {
        "applications": applications,
        "current_filter": status_filter or "all",
    }

    return render(request, "applications/list.html", context)


@login_required
def application_detail(request, pk):
    application = get_object_or_404(Application, pk=pk, user=request.user)

    # Parse the JSON data if available
    application_data = {}
    if application.data:
        import json

        try:
            application_data = json.loads(application.data)
        except json.JSONDecodeError:
            # Handle invalid JSON
            pass

    # Add the application data to the context
    context = {"application": application, "data": application_data}

    return render(request, "applications/detail_new_fixed.html", context)


@login_required
def create_business_registration(request):
    """View for creating a new business registration application"""
    if request.method == "POST":
        # Process the form submission
        application_type = request.POST.get("application_type")
        business_name = request.POST.get("business_name")
        business_type = request.POST.get("business_type")
        business_address = request.POST.get("business_address")
        business_category = request.POST.get("business_category")
        business_start_date = request.POST.get("business_start_date")
        contact_name = request.POST.get("contact_name")
        contact_email = request.POST.get("contact_email")
        contact_phone = request.POST.get("contact_phone")
        contact_position = request.POST.get("contact_position")

        # Generate a unique reference number
        current_year = datetime.datetime.now().year
        random_chars = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )
        reference_number = f"APP-{current_year}-{random_chars}"

        # Create a new application
        application = Application.objects.create(
            user=request.user,
            application_type=application_type,
            reference_number=reference_number,
            status="submitted",
            submission_date=timezone.now(),
        )

        # Store the application data
        application_data = {
            "business_name": business_name,
            "business_type": business_type,
            "business_address": business_address,
            "business_category": business_category,
            "business_start_date": business_start_date,
            "contact_name": contact_name,
            "contact_email": contact_email,
            "contact_phone": contact_phone,
            "contact_position": contact_position,
        }

        application.data = json.dumps(application_data)
        application.save()

        messages.success(
            request, "Business Registration application submitted successfully!"
        )
        return redirect("applications:detail", pk=application.pk)

    return render(request, "applications/business_registration.html")


@login_required
def create_tax_compliance(request):
    """View for creating a new tax compliance application"""
    # Get existing tax compliance applications
    existing_tax_applications = Application.objects.filter(
        user=request.user,
        application_type="Tax Compliance",
        status__in=["submitted", "under_review", "approved"],
    )

    # Track businesses that already have tax compliance applications
    businesses_with_tax_compliance = set()
    for tax_app in existing_tax_applications:
        try:
            tax_data = json.loads(tax_app.data)
            registered_business_id = tax_data.get("registered_business")
            if registered_business_id:
                businesses_with_tax_compliance.add(str(registered_business_id))
        except (json.JSONDecodeError, KeyError):
            continue

    if request.method == "POST":
        # Process the form submission
        application_type = request.POST.get("application_type")
        registered_business = request.POST.get("registered_business")

        # Validate: Check if this business already has a tax compliance application
        if registered_business in businesses_with_tax_compliance:
            # Find the existing application to reference in the error message
            for tax_app in existing_tax_applications:
                try:
                    tax_data = json.loads(tax_app.data)
                    if str(tax_data.get("registered_business")) == registered_business:
                        messages.error(
                            request,
                            f"This business already has a Tax Compliance application (Reference: {tax_app.reference_number}). Each business can only have one tax compliance application.",
                        )
                        break
                except (json.JSONDecodeError, KeyError):
                    continue
            return redirect("applications:create_tax_compliance")

        # Generate a unique reference number
        current_year = datetime.datetime.now().year
        random_chars = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )
        reference_number = f"APP-{current_year}-{random_chars}"

        # Get the registered business details
        try:
            business_application = Application.objects.get(pk=registered_business)
            business_data = json.loads(business_application.data)

            # Create a new application
            application = Application.objects.create(
                user=request.user,
                application_type=application_type,
                reference_number=reference_number,
                status="submitted",
                submission_date=timezone.now(),
            )

            # Store the application data
            application_data = {
                "registered_business": registered_business,
                "registered_business_reference": business_application.reference_number,
                "business_name": business_data.get("business_name", ""),
            }

            application.data = json.dumps(application_data)
            application.save()

            messages.success(
                request, "Tax Compliance application submitted successfully!"
            )
            return redirect("applications:detail", pk=application.pk)
        except Application.DoesNotExist:
            messages.error(request, "Selected business not found.")

    # Get the user's registered businesses
    registered_businesses = Application.objects.filter(
        user=request.user, application_type="Business Registration", status="approved"
    )

    # Prepare businesses with names
    businesses_with_names = []
    for business in registered_businesses:
        try:
            if business.data:
                business_data = json.loads(business.data)
                business_name = business_data.get("business_name", "Unnamed Business")
            else:
                business_name = "Unnamed Business"

            businesses_with_names.append(
                {
                    "id": business.id,
                    "name": business_name,
                    "reference_number": business.reference_number,
                }
            )
        except json.JSONDecodeError:
            businesses_with_names.append(
                {
                    "id": business.id,
                    "name": "Unnamed Business",
                    "reference_number": business.reference_number,
                }
            )

    return render(
        request,
        "applications/tax_compliance.html",
        {"registered_businesses": businesses_with_names},
    )


@login_required
def create_business_license(request):
    """View for creating a new business license application"""
    if request.method == "POST":
        # Process the form submission
        application_type = request.POST.get("application_type")
        business_with_tin = request.POST.get("business_with_tin")
        license_type = request.POST.get("license_type")

        # Generate a unique reference number
        current_year = datetime.datetime.now().year
        random_chars = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )
        reference_number = f"APP-{current_year}-{random_chars}"

        # Create a new application
        application = Application.objects.create(
            user=request.user,
            application_type=application_type,
            reference_number=reference_number,
            status="submitted",
            submission_date=timezone.now(),
        )

        # Get the business with TIN details
        try:
            tax_application = Application.objects.get(pk=business_with_tin)
            tax_data = json.loads(tax_application.data)

            # Get the original business registration
            business_application = Application.objects.get(
                pk=tax_data.get("registered_business")
            )
            business_data = json.loads(business_application.data)

            # Store the application data
            application_data = {
                "business_with_tin": business_with_tin,
                "tin_number": tax_data.get("tin_number", ""),
                "business_name": business_data.get("business_name", ""),
                "license_type": license_type,
            }

            application.data = json.dumps(application_data)
            application.save()

            messages.success(
                request, "Business License application submitted successfully!"
            )
            return redirect("applications:detail", pk=application.pk)
        except Application.DoesNotExist:
            messages.error(request, "Selected business not found.")

    # Get the user's businesses with TIN
    tax_applications = Application.objects.filter(
        user=request.user, application_type="Tax Compliance", status="approved"
    )

    businesses_with_tin = []
    for tax_app in tax_applications:
        tax_data = json.loads(tax_app.data)
        if "tin_number" in tax_data:
            businesses_with_tin.append(
                {
                    "id": tax_app.id,
                    "business_name": tax_data.get("business_name", ""),
                    "tin_number": tax_data.get("tin_number", ""),
                }
            )

    return render(
        request,
        "applications/business_license.html",
        {"businesses_with_tin": businesses_with_tin},
    )


@login_required
def application_create(request):
    # Get application type from query parameter if provided
    application_type_param = request.GET.get("type")

    # Map URL parameter to actual application type
    application_type_mapping = {
        "business_registration": "Business Registration",
        "tax_compliance": "Tax Compliance",
        "business_license": "Business License",
    }

    # Set default application type based on query parameter
    default_application_type = None
    if application_type_param in application_type_mapping:
        default_application_type = application_type_mapping[application_type_param]
        print(f"Application type from URL parameter: {default_application_type}")

    if request.method == "POST":
        # Get common form data
        application_type = request.POST.get("application_type")
        print(f"Application type from POST: {application_type}")

        # For Tax Compliance, we might have placeholder values for these fields
        business_name = request.POST.get("business_name")
        business_type = request.POST.get("business_type")
        business_address = request.POST.get("business_address")
        business_category = request.POST.get("business_category")

        # Log the values for debugging
        print(f"Business name: {business_name}")
        print(f"Business type: {business_type}")
        print(f"Business address: {business_address}")
        print(f"Business category: {business_category}")

        # Contact information
        contact_name = request.POST.get("contact_name")
        contact_email = request.POST.get("contact_email")
        contact_phone = request.POST.get("contact_phone")
        contact_position = request.POST.get("contact_position")

        # Generate a unique reference number (simple implementation)
        import random
        import string
        import datetime
        import json

        current_year = datetime.datetime.now().year
        random_chars = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )
        reference_number = f"APP-{current_year}-{random_chars}"

        # Determine if saving as draft or submitting
        action = request.POST.get("action", "")
        status = "draft" if action == "save_draft" else "submitted"

        # Get application-specific fields based on the application type
        application_data = {}

        # Common business information
        application_data["business_name"] = business_name
        application_data["business_type"] = business_type
        application_data["business_address"] = business_address
        application_data["business_category"] = business_category
        application_data["contact_name"] = contact_name
        application_data["contact_email"] = contact_email
        application_data["contact_phone"] = contact_phone
        application_data["contact_position"] = contact_position

        # Application-specific fields
        if application_type == "Business Registration":
            application_data["business_start_date"] = request.POST.get(
                "business_start_date"
            )

        elif application_type == "Tax Compliance":
            registered_business_id = request.POST.get("registered_business")
            is_business_model = (
                request.POST.get("is_business_model", "false").lower() == "true"
            )
            application_data["registered_business_id"] = registered_business_id
            application_data["is_business_model"] = is_business_model

            print(
                f"Processing Tax Compliance application with registered_business_id: {registered_business_id}, is_business_model: {is_business_model}"
            )

            # Get the business name from the registered business
            if registered_business_id:
                try:
                    if is_business_model:
                        # Get business from Business model
                        from applications.models import Business

                        registered_business = Business.objects.get(
                            id=registered_business_id,
                            user=request.user,
                            is_approved=True,
                        )

                        business_name = registered_business.name
                        business_type = registered_business.business_type
                        business_address = registered_business.address

                        application_data["business_name"] = business_name
                        application_data["business_type"] = business_type
                        application_data["business_address"] = business_address
                        application_data["registered_business_reference"] = (
                            registered_business.reference
                        )

                        # Generate a TIN number for the business
                        import random

                        tin_number = f"TIN-{datetime.datetime.now().year}-{random.randint(10000, 99999)}"
                        application_data["tin_number"] = tin_number

                        print(
                            f"Added business name: {business_name} and TIN: {tin_number} to application data (from Business model)"
                        )
                    else:
                        # Get business from Application model
                        registered_business = Application.objects.get(
                            id=registered_business_id,
                            application_type="Business Registration",
                            status="approved",
                        )
                        business_data = json.loads(registered_business.data)
                        business_name = business_data.get(
                            "business_name", "Unnamed Business"
                        )
                        application_data["business_name"] = business_name
                        application_data["registered_business_reference"] = (
                            registered_business.reference_number
                        )

                        # Generate a TIN number for the business
                        import random

                        tin_number = f"TIN-{datetime.datetime.now().year}-{random.randint(10000, 99999)}"
                        application_data["tin_number"] = tin_number

                        print(
                            f"Added business name: {business_name} and TIN: {tin_number} to application data (from Application model)"
                        )
                except Application.DoesNotExist:
                    print(
                        f"Registered business with ID {registered_business_id} not found in Application model"
                    )
                    pass
                except Business.DoesNotExist:
                    print(
                        f"Registered business with ID {registered_business_id} not found in Business model"
                    )
                    pass
                except json.JSONDecodeError:
                    print(
                        f"JSON decode error for business with ID {registered_business_id}"
                    )
                    pass
                except Exception as e:
                    print(f"Error processing registered business: {str(e)}")
                    pass

        elif application_type == "Business License":
            business_with_tin_id = request.POST.get("business_with_tin")
            is_business_model = (
                request.POST.get("is_business_model", "false").lower() == "true"
            )
            application_data["business_with_tin_id"] = business_with_tin_id
            application_data["is_business_model"] = is_business_model

            print(
                f"Processing Business License application with business_with_tin_id: {business_with_tin_id}, is_business_model: {is_business_model}"
            )

            # Get the business name and TIN
            if business_with_tin_id:
                try:
                    if is_business_model:
                        # Get business from Business model
                        from applications.models import Business

                        business = Business.objects.get(
                            id=business_with_tin_id,
                            user=request.user,
                            is_approved=True,
                            tin__isnull=False,
                        )

                        application_data["business_name"] = business.name
                        application_data["business_type"] = business.business_type
                        application_data["business_address"] = business.address
                        application_data["business_reference"] = business.reference
                        application_data["tin_number"] = business.tin

                        print(
                            f"Added business name: {business.name} and TIN: {business.tin} to application data (from Business model)"
                        )
                    else:
                        # Get business from Tax Compliance application
                        tax_application = Application.objects.get(
                            id=business_with_tin_id,
                            application_type="Tax Compliance",
                            status="approved",
                        )
                        tax_data = json.loads(tax_application.data)
                        application_data["business_name"] = tax_data.get(
                            "business_name", "Unnamed Business"
                        )
                        application_data["tin_number"] = tax_data.get("tin_number", "")
                        application_data["tax_compliance_id"] = business_with_tin_id
                        application_data["tax_compliance_reference"] = (
                            tax_application.reference_number
                        )

                        # Get the original business registration
                        registered_business_id = tax_data.get("registered_business_id")
                        if registered_business_id:
                            application_data["business_id"] = registered_business_id

                            try:
                                business_app = Application.objects.get(
                                    id=registered_business_id,
                                    application_type="Business Registration",
                                    status="approved",
                                )
                                application_data["business_reference"] = (
                                    business_app.reference_number
                                )
                            except Application.DoesNotExist:
                                pass

                        print(
                            f"Added business name: {application_data['business_name']} and TIN: {application_data['tin_number']} to application data (from Application model)"
                        )
                except Application.DoesNotExist:
                    print(
                        f"Tax compliance application with ID {business_with_tin_id} not found"
                    )
                    pass
                except Business.DoesNotExist:
                    print(
                        f"Business with ID {business_with_tin_id} not found in Business model"
                    )
                    pass
                except json.JSONDecodeError:
                    print(
                        f"JSON decode error for tax compliance with ID {business_with_tin_id}"
                    )
                    pass
                except Exception as e:
                    print(f"Error processing business with TIN: {str(e)}")
                    pass

        # Create the application
        application = Application.objects.create(
            user=request.user,
            application_type=application_type,
            reference_number=reference_number,
            status=status,
            data=json.dumps(application_data),  # Store all form data as JSON
        )

        # Handle file uploads
        if application_type == "Business Registration":
            # Check for any file with a name starting with "id_document"
            for key in request.FILES:
                if key.startswith("id_document"):
                    # In a real implementation, you would save the file to a storage system
                    # and store the file path in the application data
                    application_data[key] = "uploaded"
                    print(f"Uploaded file: {key}")

        # No file uploads needed for Tax Compliance in MVP

        elif application_type == "Business License":
            if request.FILES.get("business_plan"):
                application_data["business_plan"] = "uploaded"
                print("Uploaded business plan")

            if request.FILES.get("proof_of_address"):
                application_data["proof_of_address"] = "uploaded"
                print("Uploaded proof of address")

        # Update the application with file information
        application.data = json.dumps(application_data)
        application.save()

        # Redirect to the appropriate page
        if status == "draft":
            return redirect("applications:detail", pk=application.pk)
        else:
            return redirect("applications:list")

    # Check if this is a POST request
    if request.method == "POST":
        application_type = request.POST.get("application_type")

        # Redirect to the specific application form based on the selected type
        if application_type == "Business Registration":
            return redirect("applications:create_business_registration")
        elif application_type == "Tax Compliance":
            return redirect("applications:create_tax_compliance")
        elif application_type == "Business License":
            return redirect("applications:create_business_license")

    return render(
        request,
        "applications/create.html",
        {"default_application_type": default_application_type},
    )


@login_required
def apply_tax_compliance(request, business_id):
    """
    Create a Tax Compliance application based on an approved Business Registration
    """
    # Get the business registration application
    business_registration = get_object_or_404(
        Application,
        id=business_id,
        user=request.user,
        application_type="Business Registration",
        status="approved",
    )

    # Check if this business already has a tax compliance application
    existing_tax_applications = Application.objects.filter(
        user=request.user,
        application_type="Tax Compliance",
        status__in=["submitted", "under_review", "approved"],
    )

    for tax_app in existing_tax_applications:
        try:
            tax_data = json.loads(tax_app.data)
            if str(tax_data.get("registered_business")) == str(business_id):
                messages.error(
                    request,
                    f"This business already has a Tax Compliance application (Reference: {tax_app.reference_number}). Each business can only have one tax compliance application.",
                )
                return redirect("applications:detail", pk=business_id)
        except (json.JSONDecodeError, KeyError):
            continue

    # Parse the business registration data
    business_data = {}
    if business_registration.data:
        try:
            business_data = json.loads(business_registration.data)
        except json.JSONDecodeError:
            messages.error(request, "Error retrieving business data. Please try again.")
            return redirect("applications:detail", pk=business_id)

    # Generate a unique reference number
    current_year = datetime.datetime.now().year
    random_chars = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    reference_number = f"APP-{current_year}-{random_chars}"

    # Create application data for Tax Compliance
    application_data = {
        "business_name": business_data.get("business_name", ""),
        "business_type": business_data.get("business_type", ""),
        "business_address": business_data.get("business_address", ""),
        "business_category": business_data.get("business_category", ""),
        "contact_name": business_data.get("contact_name", ""),
        "contact_email": business_data.get("contact_email", ""),
        "contact_phone": business_data.get("contact_phone", ""),
        "contact_position": business_data.get("contact_position", ""),
        "registered_business_id": business_id,
        "registered_business_reference": business_registration.reference_number,
    }

    # Create the Tax Compliance application
    tax_application = Application.objects.create(
        user=request.user,
        application_type="Tax Compliance",
        reference_number=reference_number,
        status="submitted",  # Automatically submit the application
        data=json.dumps(application_data),
    )

    messages.success(request, "Tax Compliance application submitted successfully.")
    return redirect("applications:detail", pk=tax_application.pk)
