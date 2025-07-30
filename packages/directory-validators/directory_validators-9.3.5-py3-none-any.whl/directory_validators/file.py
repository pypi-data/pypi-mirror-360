from django.conf import settings
from django.core.validators import ValidationError


ALLOWED_IMAGE_FORMATS = ('PNG', 'JPG', 'JPEG')
MESSAGE_FILE_TOO_BIG = 'File is too big.'
MESSAGE_FILE_TOO_BIG = 'File is too big.'
MESSAGE_INVALID_IMAGE_FORMAT = 'Invalid image format, allowed formats: {}'.format(', '.join(ALLOWED_IMAGE_FORMATS))


def logo_filesize(value):
    """
    Confirms that the logo is not too large in terms of filesize.
    @param {File} value
    @returns {None}
    @raises AssertionError

    """

    if value.size > settings.VALIDATOR_MAX_LOGO_SIZE_BYTES:
        raise ValidationError(MESSAGE_FILE_TOO_BIG)


def image_format(value):
    """
    Confirms that the uploaded image is of supported format.

    Args:
        value (File): The file with an `image` property containing the image

    Raises:
        django.forms.ValidationError

    """

    if value.image.format.upper() not in ALLOWED_IMAGE_FORMATS:
        raise ValidationError(MESSAGE_INVALID_IMAGE_FORMAT)


def case_study_image_filesize(value):
    """
    Confirms that the case study image is not too large in terms of file size.

    Args:
        value (File): The case study image.

    Raises:
        django.forms.ValidationError

    """

    if value.size > settings.VALIDATOR_MAX_CASE_STUDY_IMAGE_SIZE_BYTES:
        raise ValidationError(MESSAGE_FILE_TOO_BIG)
