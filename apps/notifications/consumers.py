import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WEBSOCKET: connect called")

        user = self.scope.get("user")

        print(
            "WEBSOCKET USER:",
            user,
            "AUTH:",
            getattr(user, "is_authenticated", None),
            "ID:",
            getattr(user, "id", None),
        )

        if not user or not user.is_authenticated:
            print("WEBSOCKET: authentication failed")
            await self.close(code=4001)
            return

        self.user_id = user.id
        self.group_name = f"notifications_{self.user_id}"

        print("WEBSOCKET GROUP:", self.group_name)

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        print("WEBSOCKET: group_add successful")

        await self.accept()

        print("WEBSOCKET: accepted")

    async def disconnect(self, close_code):
        print("WEBSOCKET: disconnect", close_code)

        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

        print("WEBSOCKET: group_discard complete")

    async def notification_message(self, event):
        print("WEBSOCKET: notification received", event)

        await self.send(
            text_data=json.dumps(event["data"])
        )

        print("WEBSOCKET: notification sent")