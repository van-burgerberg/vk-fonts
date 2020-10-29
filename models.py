from tortoise.models import Model
from tortoise.fields import JSONField, BooleanField, ForeignKeyField


class Font(Model):
    dictionary = JSONField()


class UserState(Model):
    font = ForeignKeyField("models.Font", null=True, default=None)
    force_lowercase = BooleanField(bool=True, default=True)
    enabled = BooleanField(bool=True, default=True)
