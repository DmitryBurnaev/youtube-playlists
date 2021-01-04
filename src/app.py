import asyncio
import logging

from aiohttp import web
import aiohttp_debugtoolbar
import uvloop

import settings
import views

logger = logging.getLogger(__name__)


class WebApp(web.Application):
    """ Extended web Application """


async def create_app() -> WebApp:
    """ Prepare application """
    middlewares = []

    if settings.DEBUG:
        middlewares.append(aiohttp_debugtoolbar.middleware)

    app = WebApp(middlewares=middlewares, logger=logger)

    if settings.DEBUG:
        aiohttp_debugtoolbar.setup(app, intercept_redirects=False)

    app.router.add_route(method="*", path="/api/playlists/", handler=views.PlaylistsAPIView)

    return app


if __name__ == "__main__":

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    web_app = loop.run_until_complete(create_app())

    try:
        web.run_app(web_app, host=settings.APP_HOST, port=settings.APP_PORT)
    except KeyboardInterrupt:
        logger.debug("Keyboard Interrupt ^C")

    logger.debug("Server has been stopped")
