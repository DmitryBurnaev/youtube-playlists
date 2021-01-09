import asyncio
import json

import motor.motor_asyncio
import motor.core as motor_core
from aiokafka import AIOKafkaConsumer
from loguru import logger
from pymongo import ReturnDocument

import settings


async def update_playlist(collection: motor_core.AgnosticCollection, playlist_id: str):
    logger.info(f"Updating playlist #{playlist_id}")

    # TODO: get info from YouTube's API
    description = f"Test description for list #{playlist_id}"
    videos = [
        {
            "id": "1",
            "url": "http://youtube.com?v=1",
            "title": "Video #1"
        }
    ]
    updated_playlist = await collection.find_one_and_update(
        {'id': playlist_id},
        {'$set': {'description': description, 'videos': videos}},
        projection={"id", "url"},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    logger.info(f"Updated playlist: {updated_playlist}")


async def consume():
    logger.info(
        f"Creating MongoDB connection: "
        f"DB {settings.MONGO_DB_NAME} | COLLECTION {settings.MONGO_COLLECTION}"
    )
    db_client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_DB_CONN)
    db = db_client[settings.MONGO_DB_NAME]
    collection = db[settings.MONGO_COLLECTION]

    logger.info("Creating consumer...")
    consumer = AIOKafkaConsumer(
        settings.KAFKA_TOPIC,
        bootstrap_servers=settings.KAFKA_CONN,
        group_id="my-group"
    )
    logger.info(f"Get cluster layout and join group `my-group`...")
    await consumer.start()
    logger.info(f"Started consuming for {settings.KAFKA_CONN} [{settings.KAFKA_TOPIC}]...")
    try:
        # Consume messages
        async for msg in consumer:
            logger.info(
                f"consumed:\n"
                f" topic: {msg.topic}\n"
                f" partition: {msg.partition}\n"
                f" offset: {msg.offset}\n"
                f" key: {msg.key}\n"
                f" value: {msg.value}\n"
                f" timestamp: {msg.timestamp}\n"
                f" headers: {msg.headers}\n"
            )
            msg = json.loads(msg.value.decode("utf-8"))
            await update_playlist(collection, playlist_id=msg["id"])

    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(consume())
