from tortoise import fields
from tortoise.models import Model
from .user import User


class TelegramUser(Model):
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User",
        related_name="telegram_user",
        on_delete=fields.CASCADE,
    )
    telegram_id = fields.BigIntField(unique=True)
    username = fields.CharField(max_length=64, null=True, unique=True)
    name = fields.CharField(max_length=128, null=True)
