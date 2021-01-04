import json

from aiohttp import web


class PlaylistsAPIView(web.View):

    async def get(self):
        return web.json_response([{"id": 1, "url": "https://test.com"}])

    async def post(self):
        request_data = await self.request.content.read()
        request_data = json.loads(request_data)
        if not (url := request_data.get("url")):
            return web.json_response({"message": "invalid request"}, status=400)

        return web.json_response([{"id": 1, "url": url}])

