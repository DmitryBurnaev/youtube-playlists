import asyncio
import json
import re
from typing import Optional

from aiohttp import web
from aiokafka import AIOKafkaProducer
from motor.core import AgnosticCollection
from loguru import logger

from app import WebApp
from models import Playlist
from src import settings


class PlaylistsAPIView(web.View):

    @property
    def app(self) -> WebApp:
        return self.request.app  # noqa

    @property
    def collection(self) -> AgnosticCollection:
        return self.app.db["playlists"]

    async def get(self):
        cursor = self.collection.find({"user_id": 1}).sort("created_at")
        items = await cursor.to_list(length=100)
        items = [Playlist(**item).dict() for item in items]
        return web.json_response(items)

    async def post(self):
        request_data = await self.request.content.read()
        request_data = json.loads(request_data)
        try:
            request_data["user_id"] = 1
            playlist = Playlist(**request_data)
        except Exception as e:
            return web.json_response({"message": f"invalid request: {e}"}, status=400)

        playlist.id = self.extract_id(playlist.url)

        exists_playlist = await self.collection.find_one({"id": playlist.id})
        if not exists_playlist:
            await self.collection.insert_one(playlist.dict())

        await self.publish_message(playlist)
        return web.json_response(playlist.dict(), status=201)

    @staticmethod
    async def publish_message(playlist: Playlist):
        loop = asyncio.get_event_loop()
        producer = AIOKafkaProducer(loop=loop, bootstrap_servers=settings.KAFKA_CONN)
        message = json.dumps({"id": playlist.id}).encode("utf-8")

        # Get cluster layout and initial topic/partition leadership information
        await producer.start()
        try:
            # Produce message
            await producer.send_and_wait(
                settings.KAFKA_TOPIC,
                message,
                key=b"new-playlist-key",
                headers=[("content-type", b"application/json")]
            )
        finally:
            # Wait for all pending messages to be delivered or expire.
            await producer.stop()

    @staticmethod
    def extract_id(url: str) -> Optional[str]:
        matched_url = re.findall(r"(?:list=|/)([0-9A-Za-z_-]{34}).*", url)
        if not matched_url:
            logger.error(f"Couldn't extract video ID: Source link is not correct: {url}")
            return None

        return matched_url[0]
