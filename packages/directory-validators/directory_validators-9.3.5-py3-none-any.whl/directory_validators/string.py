from django.core.validators import ValidationError
from django.utils.html import strip_tags


MESSAGE_KEYWORD_LIMIT = 'Please choose no more than 10 keywords.'
MESSAGE_KEYWORD_SPECIAL_CHARS = 'You can only enter letters, numbers and commas.'
MESSAGE_REMOVE_HTML = 'Please remove the HTML.'


def tokenize_words(keywords):
    return keywords.replace(', ', ',').replace(' ,', ',').strip(' ,').split(',')


def word_limit(allowed_word_limit):

    def inner(words):
        """
        Confirms that the number of keywords selected is less than the allowed max.

        Args:
            keywords (str)

        Raises:
            django.forms.ValidationError

        """
        if len(tokenize_words(words)) > allowed_word_limit:
            raise ValidationError(MESSAGE_KEYWORD_LIMIT)
    return inner


def no_special_characters(keywords):
    """
    Confirms that the keywords don't contain special characters

    Args:
        keywords (str)

    Raises:
        django.forms.ValidationError
    """
    invalid_chars = '!\"#$%&\'()*+-./:;<=>?@[\\]^_{|}~\t\n'
    if any(char in invalid_chars for char in keywords):
        raise ValidationError(MESSAGE_KEYWORD_SPECIAL_CHARS)


def no_html(value):
    if value != strip_tags(value):
        raise ValidationError(MESSAGE_REMOVE_HTML)
