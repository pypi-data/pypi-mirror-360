import asyncio

from mokei import Mokei
from mokei.logging import getLogger
from mokei import MokeiWebSocket

logger = getLogger('WS_TEST')
app = Mokei()
ws = app.websocketroute('/ws')


@ws.onconnect
async def log_connect():
    logger.info('Connected')


@ws.ondisconnect
async def log_disconnect():
    logger.info('Disconnected')


@ws.onping
async def send_pong(socket: MokeiWebSocket):
    logger.info('Pinged')


@ws.onpong
async def log_pong():
    logger.info('Received Pong')


@app.background_task
async def ping():
    while True:
        await asyncio.sleep(5.0)
        logger.info('Pinging...')
        await ws.send_ping()


@app.background_task
async def text():
    while True:
        await asyncio.sleep(5.0)
        await ws.send_text('boom')


if __name__ == '__main__':
    app.run(port=8002)
