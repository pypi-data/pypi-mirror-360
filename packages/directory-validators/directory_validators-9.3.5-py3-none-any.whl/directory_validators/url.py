import re

from django.core.validators import RegexValidator

from directory_validators.helper import validate_social_media_url


MESSAGE_REMOVE_URL = 'Please remove the web or email addresses'
MESSAGE_NOT_FACEBOOK = 'Please provide a link to Facebook.'
MESSAGE_NOT_TWITTER = 'Please provide a link to Twitter.'
MESSAGE_NOT_LINKEDIN = 'Please provide a link to LinkedIn.'


class ContainsUrlValidator(RegexValidator):
    # Modified django.core.validators.URLValidator.regex.pattern, without the
    # '://'' in the pattern and start/end of the string
    link_pattern = (
        '(?:[a-z0-9\\.\\-]*)(?:\\S+(?::\\S*)?@)?(?:(?:25[0-5]|2[0-4]\\d|[0-1]'
        '?\\d?\\d)(?:\\.(?:25[0-5]|2[0-4]\\d|[0-1]?\\d?\\d)){3}|\\[[0-9a-f:\\'
        '.]+\\]|([a-z¡-\uffff0-9](?:[a-z¡-\uffff0-9-]*[a-z¡-\uffff0-9])?(?:\\'
        '.(?!-)[a-z¡-\uffff0-9-]+(?<!-))*\\.(?!-)(?:[a-z¡-\uffff-]{2,}|xn--[a'
        '-z0-9]+)(?<!-)\\.?|localhost))(?::\\d{2,5})?(?:[/?#][^\\s]*)?'
    )
    regex = re.compile(link_pattern, re.IGNORECASE)


def not_contains_url_or_email(value):
    if not value:
        return
    ContainsUrlValidator(inverse_match=True, message=MESSAGE_REMOVE_URL)(value)


def is_facebook(value):
    """
    Confirms that the social media url is pointed at the correct domain.

    Args:
        value (string): The url to check.

    Raises:
        django.forms.ValidationError

    """
    allowed_list = ['facebook.com', '*.facebook.com']
    return validate_social_media_url(value, allowed_list, MESSAGE_NOT_FACEBOOK)


def is_twitter(value):
    """
    Confirms that the social media url is pointed at the correct domain.

    Args:
        value (string): The url to check.

    Raises:
        django.forms.ValidationError

    """
    allowed_list = ['twitter.com', '*.twitter.com']
    return validate_social_media_url(value, allowed_list, MESSAGE_NOT_TWITTER)


def is_linkedin(value):
    """
    Confirms that the social media url is pointed at the correct domain.

    Args:
        value (string): The url to check.

    Raises:
        django.forms.ValidationError

    """
    allowed_list = ['linkedin.com', '*.linkedin.com']
    return validate_social_media_url(value, allowed_list, MESSAGE_NOT_LINKEDIN)
