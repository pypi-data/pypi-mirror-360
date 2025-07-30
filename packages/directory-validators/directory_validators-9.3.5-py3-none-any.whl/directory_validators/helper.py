from urllib import parse
from django.core.validators import ValidationError


def validate_social_media_url(value, allowed_list, error_message):
    """
    Helper function to validate social media URLs.

    Args:
        value (string): The URL to check.
        allowed_list (list): List of allowed domains and subdomains.
        error_message (string): Error message to raise if validation fails.

    Raises:
        django.core.exceptions.ValidationError
    """
    parsed = parse.urlparse(value.lower())
    netloc_subdomain = parsed.netloc.split('.')
    if len(netloc_subdomain) >= 2 and '.'.join(netloc_subdomain[-2:]) in allowed_list:
        return True
    else:
        raise ValidationError(error_message)
