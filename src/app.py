import asyncio
import logging

import motor.motor_asyncio
import motor.core as motor_core
from aiohttp import web
import aiohttp_debugtoolbar
import uvloop

import settings

logger = logging.getLogger(__name__)


class WebApp(web.Application):
    """ Extended web Application """
    db_client: motor_core.AgnosticClient
    db: motor_core.AgnosticDatabase


async def create_app() -> WebApp:
    """ Prepare application """
    middlewares = []

    if settings.DEBUG:
        middlewares.append(aiohttp_debugtoolbar.middleware)

    app = WebApp(middlewares=middlewares, logger=logger)
    app.db_client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_DB_CONN)
    app.db = app.db_client[settings.MONGO_DB_NAME]

    if settings.DEBUG:
        aiohttp_debugtoolbar.setup(app, intercept_redirects=False)

    import views
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
