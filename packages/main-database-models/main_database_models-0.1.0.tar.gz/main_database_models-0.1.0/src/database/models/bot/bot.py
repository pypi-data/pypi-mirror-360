from tortoise import fields
from tortoise.models import Model
from uuid6 import uuid7


class Bot(Model):
    id = fields.UUIDField(primary_key=True, default=uuid7)
    session_id = fields.UUIDField(null=True, default=None)
    is_using = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
