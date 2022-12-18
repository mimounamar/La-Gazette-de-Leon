import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from gazette_backend.models import Article


class DocConsumer(WebsocketConsumer):
    def connect(self):
        self.document_room_name = self.scope['url_route']['kwargs']['room_name']
        async_to_sync(self.channel_layer.group_add)(
            self.document_room_name,
            self.channel_name)
        self.accept()

        self.article = Article.objects.get(id=self.document_room_name)
        self.content = self.article.get_content()
        self.title = self.article.get_title()
        self.status = self.article.get_status()
        print("Init",self.content)

        self.send(text_data=json.dumps({
            'type': 'connected',
            'content': self.content,
            'title': self.title,
            'status': self.status
        }))

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        token = self.scope['url_route']['kwargs']['token']
        async_to_sync(self.channel_layer.group_send)(
            self.document_room_name,
            {
                'type': text_data_json['type'],
                'content': text_data_json['changes'],
                'title': text_data_json['title'],
                'trigger': token
            }
        )

    def update(self, event):
        changes = event['content']
        title = event['title']
        trigger = event['trigger']
        self.send(text_data=json.dumps({
            'type': 'updated',
            'content': changes,
            'title': title,
            'trigger': trigger
        }))

    def save(self, event):
        data = json.dumps(event['content'])
        title = event['title']
        Article.objects.filter(id=self.document_room_name).update(content=data, title=title)
