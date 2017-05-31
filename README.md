# asyncapp
Yet another Python 3 async app framework for Linux (Python 3 asyncio studying project).
Could ease your burden when creating asyncronoys python 3 apps for Linux.

Things I tried and managed to somehow achieve: 
 * lightweight to use, testable and easily overwritable: dependency injection, inversion of control and composition instead of inheritance
 * tests done and done by using unittest
 * tests done by using unittest.Mock rather than unittest.patch
 * unit tests done for the asyncronous parts as well
 * overwritable SIGINT and SIGTERM signal handlers
 * program exit value related behaviour
 * top level exception handling
 * overritable top level logging
 * coroutine cancellation via program exit value future

See  EchoApp.py for an usage example and asyncapp.AsyncApp class for more points to overwrite. 
The tests are written into AsyncLinuxAppTest.py and passed when I ran em in Ubuntu using Python 3.5.2.

Things to do:
 * the usage of this library is not fluent enough. You know what I mean.
 * asyncapp.AsyncLinuxAppRunner is messy. Getters, abstract base class, ... ? 
 * study how similar things are done in windows and try to write a class named asyncapp.AsyncWindowsAppRunner


I know that you are lazy so here is the content of the EchoApp.py:
```python
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
```
