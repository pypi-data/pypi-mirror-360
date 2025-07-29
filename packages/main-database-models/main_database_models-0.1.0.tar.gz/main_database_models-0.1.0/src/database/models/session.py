from tortoise import fields
from tortoise.models import Model
from .bot import Bot
from .user import User
from uuid6 import uuid7
from session_shared_models.state import SessionState


class Session(Model):
    id = fields.UUIDField(primary_key=True, default=uuid7)
    bot: fields.ForeignKeyRelation[Bot] = fields.ForeignKeyField(
        "models.Bot",
        related_name="session",
        on_delete=fields.CASCADE,
    )
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User",
        related_name="sessions",
        on_delete=fields.CASCADE,
    )
    state = fields.CharEnumField(SessionState, default=SessionState.CREATED)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
