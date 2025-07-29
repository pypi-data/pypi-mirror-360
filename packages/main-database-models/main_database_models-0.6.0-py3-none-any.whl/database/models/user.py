from tortoise import fields
from tortoise.models import Model
from uuid6 import uuid7


class User(Model):
    id = fields.UUIDField(primary_key=True, default=uuid7)
    name = fields.CharField(max_length=255, null=True)
    email = fields.CharField(max_length=255, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)
