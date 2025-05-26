from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import messages
from applications.models import Application
import json


@login_required
def index(request):
    """
    User dashboard view showing user's applications and available services
    """
    # Get user's applications
    applications = Application.objects.filter(user=request.user).order_by(
        "-submission_date"
    )

    # Count applications by status
    applications_count = applications.count()
    pending_count = applications.filter(
        status__in=["draft", "submitted", "under_review"]
    ).count()
    approved_count = applications.filter(status="approved").count()
    rejected_count = applications.filter(status="rejected").count()

    # Get recent applications (last 5)
    recent_applications = applications[:5]

    # Get user's businesses from the Business model
    from applications.models import Business

    businesses = Business.objects.filter(user=request.user, is_approved=True).order_by(
        "-registration_date"
    )

    # If no businesses found in the Business model, fall back to applications
    if not businesses.exists():
        # Get approved business registrations from applications
        business_registrations = Application.objects.filter(
            user=request.user,
            application_type="Business Registration",
            status="approved",
        )

        # Create temporary business objects for display
        temp_businesses = []
        for business in business_registrations:
            try:
                data = json.loads(business.data)
                business_name = data.get("business_name", "Unnamed Business")

                # Check if this business already has a tax compliance application
                has_tax_compliance = False
                tin_number = None

                for tax_app in Application.objects.filter(
                    user=request.user,
                    application_type="Tax Compliance",
                    status="approved",
                ):
                    try:
                        tax_data = json.loads(tax_app.data)
                        if str(tax_data.get("registered_business_id")) == str(
                            business.id
                        ):
                            has_tax_compliance = True
                            tin_number = tax_data.get("tin_number")
                            break
                    except (json.JSONDecodeError, KeyError):
                        continue

                # Check if this business already has a license
                has_license = False
                if has_tax_compliance:
                    for license_app in Application.objects.filter(
                        user=request.user,
                        application_type="Business License",
                        status="approved",
                    ):
                        try:
                            license_data = json.loads(license_app.data)
                            if str(license_data.get("business_id")) == str(business.id):
                                has_license = True
                                break
                        except (json.JSONDecodeError, KeyError):
                            continue

                # Add business to the list
                temp_businesses.append(
                    {
                        "name": business_name,
                        "reference": business.reference_number,
                        "tin": tin_number,
                        "has_license": has_license,
                        "id": business.id,
                    }
                )
            except json.JSONDecodeError:
                # Skip businesses with invalid data
                pass
            except Exception as e:
                # Log the error and continue
                print(f"Error processing business {business.id}: {str(e)}")
                pass

        businesses = temp_businesses

    context = {
        "applications_count": applications_count,
        "pending_count": pending_count,
        "approved_count": approved_count,
        "rejected_count": rejected_count,
        "recent_applications": recent_applications,
        "businesses": businesses,
    }

    return render(request, "dashboard/index.html", context)


@staff_member_required
def admin_dashboard(request):
    """
    Admin dashboard view showing all applications and system statistics
    """
    # Redirect non-staff users to regular dashboard
    if not request.user.is_staff:
        return redirect("dashboard:home")

    # Get all applications
    all_applications = Application.objects.all().order_by("-submission_date")

    # Count total applications
    total_applications = all_applications.count()

    # Count pending applications
    pending_applications = all_applications.filter(
        status__in=["submitted", "under_review"]
    ).count()

    # Count applications approved today
    today = timezone.now().date()
    approved_today = all_applications.filter(
        status="approved", last_updated__date=today
    ).count()

    # Count total users
    total_users = User.objects.count()

    # Get recent applications (last 10)
    recent_applications = all_applications[:10]

    context = {
        "total_applications": total_applications,
        "pending_applications": pending_applications,
        "approved_today": approved_today,
        "total_users": total_users,
        "recent_applications": recent_applications,
    }

    return render(request, "dashboard/admin.html", context)


@staff_member_required
def review_applications(request):
    """
    Admin view for reviewing and managing all applications
    """
    # Redirect non-staff users to regular dashboard
    if not request.user.is_staff:
        return redirect("dashboard:home")

    # Get all applications
    all_applications = Application.objects.all().order_by("-submission_date")

    # Filter by status if provided
    status_filter = request.GET.get("status")
    if status_filter and status_filter != "all":
        all_applications = all_applications.filter(status=status_filter)

    context = {
        "applications": all_applications,
        "current_filter": status_filter or "all",
        "status_choices": Application.STATUS_CHOICES,
    }

    return render(request, "dashboard/review_applications.html", context)


@staff_member_required
def admin_application_detail(request, pk):
    """
    Admin view for viewing and managing a specific application
    """
    # Redirect non-staff users to regular dashboard
    if not request.user.is_staff:
        return redirect("dashboard:home")

    # Get the application
    application = get_object_or_404(Application, pk=pk)

    # Parse the JSON data if available
    application_data = {}
    if application.data:
        try:
            application_data = json.loads(application.data)
        except json.JSONDecodeError:
            # Handle invalid JSON
            pass

    # Handle form submission for status update
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "approve":
            application.status = "approved"

            # Handle Business Registration approval
            if application.application_type == "Business Registration":
                from applications.models import Business
                import datetime

                # Extract business data from application
                business_name = application_data.get("business_name", "")
                business_type = application_data.get("business_type", "")
                business_address = application_data.get("business_address", "")
                business_category = application_data.get("business_category", "")
                business_start_date_str = application_data.get(
                    "business_start_date", ""
                )

                # Parse the business start date
                try:
                    business_start_date = datetime.datetime.strptime(
                        business_start_date_str, "%Y-%m-%d"
                    ).date()
                except (ValueError, TypeError):
                    business_start_date = timezone.now().date()

                # Check if a business with this name already exists
                if Business.objects.filter(name__iexact=business_name).exists():
                    # Update application status to rejected
                    application.status = "rejected"
                    application_data["rejection_reason"] = (
                        "A business with this name already exists."
                    )
                    application.data = json.dumps(application_data)
                    application.save()

                    messages.error(
                        request,
                        f"Application {application.reference_number} has been rejected. A business with this name already exists.",
                    )
                    return redirect("dashboard:review_applications")

                # Create a new Business record
                Business.objects.create(
                    user=application.user,
                    name=business_name,
                    business_type=business_type,
                    address=business_address,
                    category=business_category,
                    reference=application.reference_number,
                    registration_date=business_start_date,
                    is_approved=True,
                )

                # Update application data to indicate business is registered
                application_data["is_registered"] = True
                application.data = json.dumps(application_data)

            # Generate TIN for Tax Compliance applications
            elif application.application_type == "Tax Compliance":
                from applications.models import Business

                # Generate a unique TIN (Tax Identification Number)
                import random
                import string

                # Format: TIN-YYYY-XXXXXX (Year + 6 alphanumeric characters)
                current_year = timezone.now().year
                random_chars = "".join(
                    random.choices(string.ascii_uppercase + string.digits, k=6)
                )
                tin_number = f"TIN-{current_year}-{random_chars}"

                # Store the TIN in the application data
                if application_data:
                    application_data["tin_number"] = tin_number
                    application_data["tin_issue_date"] = timezone.now().strftime(
                        "%Y-%m-%d"
                    )
                    application.data = json.dumps(application_data)

                # Update the Business record with the TIN
                registered_business_id = application_data.get("registered_business_id")
                if registered_business_id:
                    try:
                        # First try to get the business by the application ID
                        business_app = Application.objects.get(
                            id=registered_business_id,
                            application_type="Business Registration",
                            status="approved",
                        )

                        # Then try to get the Business record by reference
                        business = Business.objects.get(
                            reference=business_app.reference_number
                        )
                        business.tin = tin_number
                        business.save()
                    except (Application.DoesNotExist, Business.DoesNotExist):
                        # If we can't find the business, log an error but continue
                        print(
                            f"Could not find business for tax compliance application {application.reference_number}"
                        )

            # Handle Business License approval
            elif application.application_type == "Business License":
                from applications.models import Business

                # Update the Business record to indicate it has a license
                tax_compliance_id = application_data.get("tax_compliance_id")
                if tax_compliance_id:
                    try:
                        # Get the tax compliance application
                        tax_app = Application.objects.get(
                            id=tax_compliance_id,
                            application_type="Tax Compliance",
                            status="approved",
                        )

                        # Get the tax compliance data
                        tax_data = json.loads(tax_app.data)
                        registered_business_id = tax_data.get("registered_business_id")

                        if registered_business_id:
                            # Get the business registration application
                            business_app = Application.objects.get(
                                id=registered_business_id,
                                application_type="Business Registration",
                                status="approved",
                            )

                            # Update the Business record
                            business = Business.objects.get(
                                reference=business_app.reference_number
                            )
                            business.has_license = True
                            business.save()
                    except (
                        Application.DoesNotExist,
                        Business.DoesNotExist,
                        json.JSONDecodeError,
                    ):
                        # If we can't find the business, log an error but continue
                        print(
                            f"Could not find business for license application {application.reference_number}"
                        )

            application.save()
            messages.success(
                request,
                f"Application {application.reference_number} has been approved.",
            )
            return redirect("dashboard:review_applications")

        elif action == "reject":
            application.status = "rejected"
            rejection_reason = request.POST.get("rejection_reason", "")

            # Store rejection reason in the data field
            if application_data:
                application_data["rejection_reason"] = rejection_reason
                application.data = json.dumps(application_data)

            application.save()
            messages.success(
                request,
                f"Application {application.reference_number} has been rejected.",
            )
            return redirect("dashboard:review_applications")

        elif action == "under_review":
            application.status = "under_review"
            application.save()
            messages.success(
                request,
                f"Application {application.reference_number} has been marked as under review.",
            )
            return redirect("dashboard:review_applications")

    context = {
        "application": application,
        "data": application_data,
    }

    return render(request, "dashboard/application_detail_simple.html", context)
