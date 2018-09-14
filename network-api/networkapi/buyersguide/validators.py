from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

@deconstructible
class VoteAttributeValidator:
    def __init__(self, valid_attributes=None):
        self.valid_attributes = valid_attributes

    def __call__(self, value):
        if value not in self.valid_attributes:
            raise ValidationError(f'{value} is not a permitted attribute')

    def __eq__(self, other):
        return self.valid_attributes == other.valid_attributes
