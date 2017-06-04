'''EchoApp: asyncapp usage example

The input is echoed to the user with 2.9 second delay
until the user writes 'quit', input stream is stopped,
user interrupts (ctrl+c) or
terminates (kill) the program.
'''

import asyncio
from asyncapp import AsyncApp, get_default_logger, AsyncLinuxAppSession



class EchoApp(AsyncApp):
    '''
    The input is echoed to the user with 2.9 second delay
    until the user writes 'quit' or the input stream stops.
    '''
    def on_run(self, loop: asyncio.AbstractEventLoop, fut: asyncio.Future):
        async def echo(fut: asyncio.Future):
            while not fut.done():
                try:
                    data = input()
                    if data == 'quit':
                        fut.set_result(True)
                    else:
                        await asyncio.sleep(2.9)    # one km distance
                    print(data)
                except EOFError:
                    fut.set_result(True)

        loop.run_until_complete(echo(fut))


if __name__ == '__main__':
    execution_logger = get_default_logger("echoApp")
    app = EchoApp(execution_logger)

    session = AsyncLinuxAppSession(execution_logger, app)
    session.run()
