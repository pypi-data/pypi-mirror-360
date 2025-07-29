from tortoise import fields
from tortoise.models import Model
from uuid6 import uuid7
from bot_shared_models import BotType


class Bot(Model):
    id = fields.UUIDField(primary_key=True, default=uuid7)
    using = fields.BooleanField(default=False)
    booked = fields.BooleanField(default=False)
    type = fields.CharEnumField(BotType)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
