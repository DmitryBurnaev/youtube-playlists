import json

from aiohttp import web
from motor.core import AgnosticCollection

from app import WebApp


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
        print(items)
        return web.json_response(items)

    async def post(self):
        request_data = await self.request.content.read()
        request_data = json.loads(request_data)
        if not (url := request_data.get("url")):
            return web.json_response({"message": "invalid request"}, status=400)

        await self.collection.insert_one({"user_id": 1, "url": url})
        return web.json_response([{"id": 1, "url": url}])
