from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from applications.models import Business
from .serializers import BusinessSerializer


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_approved_businesses(request):
    """
    Get the user's approved business registrations for tax compliance application
    """
    try:
        print(
            f"User: {request.user.username}, authenticated: {request.user.is_authenticated}"
        )

        # Get the user's approved businesses
        approved_businesses = Business.objects.filter(
            user=request.user,
            is_approved=True,
        )

        print(f"Found {approved_businesses.count()} approved businesses")

        # Serialize the businesses
        serializer = BusinessSerializer(approved_businesses, many=True)

        print(f"Returning {len(serializer.data)} businesses")
        return Response(serializer.data)
    except Exception as e:
        # Log the error and return an empty list with an error status
        print(f"Error in get_approved_businesses: {str(e)}")
        return Response(
            {"error": "Failed to retrieve approved businesses"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_businesses_with_tin(request):
    """
    Get the user's businesses with TIN for business license application
    """
    try:
        print(
            f"User: {request.user.username}, authenticated: {request.user.is_authenticated}"
        )

        # Get the user's businesses with TIN
        businesses_with_tin = Business.objects.filter(
            user=request.user, is_approved=True, tin__isnull=False
        ).exclude(tin="")

        print(f"Found {businesses_with_tin.count()} businesses with TIN")

        # Serialize the businesses
        serializer = BusinessSerializer(businesses_with_tin, many=True)

        print(f"Returning {len(serializer.data)} businesses with TIN")
        return Response(serializer.data)
    except Exception as e:
        # Log the error and return an empty list with an error status
        print(f"Error in get_businesses_with_tin: {str(e)}")
        return Response(
            {"error": "Failed to retrieve businesses with TIN"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
