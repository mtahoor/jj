from django import template
import json

register = template.Library()


@register.filter
def load_json(value):
    """
    Converts a JSON string into a Python object
    """
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return {}


@register.filter
def get_business_name(application):
    """
    Extracts the business name from an application
    """
    try:
        if not application.data:
            return "Unknown Business"

        data = json.loads(application.data)

        # For Tax Compliance applications, return the business name
        if application.application_type == "Tax Compliance":
            business_name = data.get("business_name", "")
            if business_name:
                return business_name

        # For Business Registration applications, return the business name
        if application.application_type == "Business Registration":
            business_name = data.get("business_name", "")
            if business_name:
                return business_name

            # Try to find business name in other fields
            for key, value in data.items():
                if isinstance(value, str) and "name" in key.lower() and value:
                    return value

        # Return a default if no name found
        return f"Business {application.reference_number}"

    except (ValueError, TypeError, json.JSONDecodeError):
        return f"Business {application.reference_number}"
