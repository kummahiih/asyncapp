# asyncapp
Yet another Python 3 async app framework for Linux (Python 3 asyncio studying project).
Could ease your burden when creating asyncronoys python 3 apps for Linux.

See  EchoApp.py for an usage example and asyncapp.AsyncApp class for more points to overwrite. 
The tests are written into AsyncLinuxAppTest.py and passed when I ran em in Ubuntu using Python 3.5.2.

Things I tried and managed to somehow achieve: 
 * done as a library
 * lightweight to use, testable and easily overwritable: dependency injection, inversion of control and composition instead of inheritance
 * tests done and done by using unittest
 * tests done by using unittest.Mock rather than unittest.patch
 * unit tests done for the asyncronous parts as well
 * overwritable SIGINT and SIGTERM signal handlers
 * program exit value related behaviour
 * top level exception handling
 * overritable top level logging
 * coroutine cancellation via program exit value future


Things to do:
 * type checks
 * the usage of this library is not fluent enough. You know what I mean.
 * asyncapp.AsyncLinuxAppSession is messy. Getters, abstract base class, ... ? 
 * study how similar things are done in windows and try to write a class named asyncapp.AsyncWindowsAppSession


I know that you are lazy so here is the content of the EchoApp.py:
```python
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
```
