from tortoise import fields
from tortoise.models import Model
from ..bot import Bot
from gmeet_shared_models.state import BotState


class GmeetBotInfo(Model):
    bot: fields.ForeignKeyRelation[Bot] = fields.ForeignKeyField(
        "models.Bot",
        related_name="gmeet_info",
        on_delete=fields.CASCADE,
    )
    state = fields.CharEnumField(BotState, default=BotState.INITIALIZING)
    meeting_id = fields.CharField(max_length=64, null=True)
