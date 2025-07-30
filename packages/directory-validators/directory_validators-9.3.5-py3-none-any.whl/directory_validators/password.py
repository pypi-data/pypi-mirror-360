import re
from django.core.exceptions import ValidationError

ALPHABETIC_VALIDATION_MESSAGE = 'This password contains letters only.'
ALPHABETIC_HELP_TEXT = 'Your password cannot contain letters only.'
PASSWORD_WORD_VALIDATION_MESSAGE = 'This password contains the word \'password\''
PASSWORD_WORD_HELP_TEXT = 'Your password cannot contain the word \'password\''


class AlphabeticPasswordValidator:

    def validate(self, password, user=None):
        if password.isalpha():
            raise ValidationError(ALPHABETIC_VALIDATION_MESSAGE, code='password_entirely_alphabetic')

    def get_help_text(self):
        return ALPHABETIC_HELP_TEXT


class PasswordWordPasswordValidator:

    def validate(self, password, user=None):
        if re.search('password', password, re.IGNORECASE):
            raise ValidationError(PASSWORD_WORD_VALIDATION_MESSAGE, code='password_used_in_password')

    def get_help_text(self):
        return PASSWORD_WORD_HELP_TEXT
