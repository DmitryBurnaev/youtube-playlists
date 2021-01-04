import asyncio
import logging

import aiohttp_debugtoolbar
import uvloop

from aiohttp import web

import settings

logger = logging.getLogger(__name__)
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class WebApp(web.Application):
    """ Extended web Application """


async def shutdown_app(app):
    """ Safe close server """
    app.redis_pool.close()
    await app.redis_pool.wait_closed()
    await app.objects.close()


async def create_app() -> WebApp:
    """ Prepare application """
    middlewares = []

    if settings.DEBUG:
        middlewares.append(aiohttp_debugtoolbar.middleware)

    app = WebApp(middlewares=middlewares, logger=logger, debug=settings.DEBUG)
    app.on_shutdown.append(shutdown_app)

    if settings.DEBUG:
        aiohttp_debugtoolbar.setup(app, intercept_redirects=False)

    # make routes
    from urls import urls as app_routes

    for route in app_routes:
        app.router.add_route(**route.as_dict)

    app.logger = logger
    return app


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    web_app = loop.run_until_complete(create_app())

    try:
        web.run_app(web_app, host=settings.APP_HOST, port=settings.APP_PORT)
    except KeyboardInterrupt:
        logger.debug("Keyboard Interrupt ^C")

    logger.debug("Server has been stopped")
