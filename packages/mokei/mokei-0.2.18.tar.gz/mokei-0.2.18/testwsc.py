import asyncio

from mokei.wsclient import MokeiWebSocketClient, MokeiWebSocketClientConfig
from mokei.logging import getLogger

logger = getLogger('TEST_WSC')
client = MokeiWebSocketClient('http://localhost:8002/ws')


@client.onconnect
async def log_connect():
    logger.info('Connected')


@client.ondisconnect
async def log_disconnect():
    logger.info('Disconnected')


# @client.onping
# async def send_pong():
#    logger.info('Pinged, sending pong...')


@client.onpong
async def long_pong():
    logger.info('Ponged!')


@client.ontext
async def print_text(text: str):
    logger.info(f'Received {text}')


async def auto_reset():
    while True:
        await asyncio.sleep(20.0)
        await client.reset()

async def main():
    await asyncio.gather(
        client.connect(),
        auto_reset()
    )


if __name__ == '__main__':
    asyncio.run(main())
