import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.group_name = f"user_notifications_{self.user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))


def notify_user(user_id, message):
    channel_layer = get_channel_layer()
    group_name = f"user_notifications_{user_id}"
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send_notification",
            "message": message,
        },
    )
