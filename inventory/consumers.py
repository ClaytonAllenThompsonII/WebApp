
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class InventoryConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        await self.close()

    async def receive(self, text_data):
        data_json = json.loads(text_data)
        message = data_json['message']
        # Process message
        await self.send(text_data=json.dumps({
            'response': 'Message received'
        }))
