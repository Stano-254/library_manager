import uuid

from django.contrib.auth.models import User
from django.db import models

from base.backend.utils.utilities import create_token, token_expiry


# Create your models here.
def salutations():
    """
    return collection of salutation tittles
    :return: salutation choices
    """
    return [('Prof.', 'Professor'), ('Dr.', 'Doctor'), ('Mr.', 'Mr'), ('Mrs.', 'Mrs'), ('Miss', 'Miss'), ('Ms', 'Ms')]


def gender():
    """
    return a collection of gender
    :return:  tuple choice
    """
    return [('M', 'Male'), ('F', 'Female')]


class BaseModel(models.Model):
    """
    template for others classes to reuse
    """
    id = models.UUIDField(max_length=100, default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    date_modified = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta(object):
        abstract = True


class GenericBaseModel(BaseModel):
    """
    template class for other classes with description and name
    """
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=255, blank=True, null=True)

    class Meta(object):
        abstract = True


class State(GenericBaseModel):
    """
    defines states within the system i.e. State Active, Archived, Deleted
    """

    def __str__(self):
        return f"{self.name}"

    class Meta(object):
        ordering = ('name',)

    @classmethod
    def default_state(cls):
        """
        set default state for any model
        :return:
        """
        try:
            state = cls.objects.get(name="Active")
        except Exception as e:
            state = None
        return state


class TransactionType(GenericBaseModel):
    """
    store types of transaction in the database e.g. add member
    """
    simple_name = models.CharField(max_length=50)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.simple_name}"

    class Meta(GenericBaseModel.Meta):
        unique_together = ('name',)


class Transaction(BaseModel):
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.CASCADE)
    request = models.TextField(null=True, blank=True)
    response = models.TextField(null=True, blank=True)
    message = models.CharField(max_length=200, null=True, blank=True)
    user = models.CharField(max_length=200, null=True, blank=True)
    source_ip = models.CharField(max_length=100, null=True, blank=True)
    response_code = models.CharField(max_length=20, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.transaction_type} {self.state}"


class UserIdentity(BaseModel):
    token = models.CharField(default=create_token, max_length=200)
    expires_at = models.DateTimeField(default=token_expiry)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source_ip = models.GenericIPAddressField(max_length=50, null=True, blank=True)
    state = models.ForeignKey(State, default=State.default_state, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} {self.source_ip}'

    class Meta(object):
        ordering = ('-date_created',)
        verbose_name_plural = 'User Identities'

    def extend(self):
        """
        Extends the access token for the model.
        @return: The model instance after saving.
        @rtype: Identity
        """
        # noinspection PyBroadException
        try:
            self.expires_at = token_expiry()
            self.save()
        except Exception:
            pass
        return self
