import asyncio

from aiokafka import AIOKafkaConsumer

import settings


async def consume():
    print("Creating consumer...")
    consumer = AIOKafkaConsumer(
        settings.KAFKA_TOPIC,
        bootstrap_servers=settings.KAFKA_CONN,
        group_id="my-group"
    )
    print(f"Get cluster layout and join group `my-group`...")
    await consumer.start()
    print(f"Started consuming for {settings.KAFKA_CONN} [{settings.KAFKA_TOPIC}]...")
    try:
        # Consume messages
        async for msg in consumer:
            print(
                f"consumed:\n"
                f" topic: {msg.topic}\n"
                f" partition: {msg.partition}\n"
                f" offset: {msg.offset}\n"
                f" key: {msg.key}\n"
                f" value: {msg.value}\n"
                f" timestamp: {msg.timestamp}\n"
                f" headers: {msg.headers}\n"
            )
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(consume())
