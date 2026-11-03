import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.template.loader import render_to_string


class LiveUpdateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join a global broadcast group
        self.group_name = "global_broadcast"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the broadcast group
        await self.channel_layer.group_add(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # HTMX sends data as a standard JSON string payload
        data = json.loads(text_data)
        user_message = data.get("message", "")

        # Broadcast the message event out to everyone in the group
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "broadcast_message",
                "message": user_message
            }
        )

    async def broadcast_message(self, event):
        # Render a snippet of pure HTML with new data
        html_response = render_to_string("ws_app/partials/notification.html", {
            "message": event["message"]
        })

        # send raw HTML back out to the browser
        await self.send(text_data=html_response)
