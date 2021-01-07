import json

from aiohttp import web
from motor.core import AgnosticCollection

from app import WebApp
from models import Playlist


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

        await self.collection.insert_one(playlist.dict())
        return web.json_response(playlist.dict(), status=201)
