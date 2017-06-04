'''
   @copyright: 2017 by Pauli Henrikki Rikula
   @license: MIT <http://www.opensource.org/licenses/mit-license.php>
'''

import logging
import asyncio
import sys

class AsyncApp:
    '''AsyncApp is a collection of overwritable methods which are called on
    different states of the app's life cycle.
    '''
    def __init__(self, logger):
        assert isinstance(logger, logging.Logger)
        self.logger = logger

    def on_run(self, loop, fut):
        '''
        called as the main method of the program.
        async loop given as parameter as is the program return value future.
        return value is given to on_exit.
        '''
        async def end():
            fut.set_result(True)
        loop.run_until_complete(end)

    def on_completed(self, loop):
        '''is called when the program wants to shut down as a part of it's normal behaviour.
        stops the event loop. If there is undone tasks it shall give exception
        '''
        loop.stop()

    def on_interrupt(self, loop, fut):
        '''is called when the user wants to interrupt and close the program.
        cancel tasks, clean all resources, be nice.
        '''
        if fut.cancelled():
            return
        loop.call_soon_threadsafe(fut.cancel)
        if sys.version_info.minor >= 6:
            loop.run_until_complete(loop.shutdown_asyncgens())

    def on_terminate(self, loop, fut):
        '''is called when the user wants to terminate and close the program in not so nice way.
        just stop the event loop
        '''
        loop.call_soon_threadsafe(loop.stop)

    def on_exit(self, all_ok):
        '''is called as a last function when the app is closing
        calls the sys.exit (false -> 1 True ->0)
        '''
        if all_ok:
            sys.exit(0)
        else:
            sys.exit(1)
