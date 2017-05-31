from asyncapp import *
import asyncio

async def echo(fut):
    while not fut.done():
        data = input()
        await asyncio.sleep(2.9) #one km distance       
        if data == 'quit':
            fut.set_result(True)
        print(data)

class EchoApp(AsyncApp):
    def on_run(self, loop, fut):
        loop.run_until_complete(echo(fut))


if __name__ == '__main__':
    logger = get_default_logger("echoApp")
    handler = EchoApp(logger)
    
    app = AsyncLinuxAppRunner(logger, handler)
    app.run()
    
    