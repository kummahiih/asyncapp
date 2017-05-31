"""
   @copyright: 2017 by Pauli Henrikki Rikula
   @license: MIT <http://www.opensource.org/licenses/mit-license.php>
"""

import logging
import asyncio
import sys

class AsyncApp:
    def __init__(self, logger):
        assert isinstance(logger, logging.Logger)
        self.logger = logger
        
    def on_run(self, loop, fut):
        """
        called as the main method of the program.
        async loop given as parameter as is the cancellation future. return value is given to on_exit
        othervice  sys.exit(0) is called
        """
        async def end():
            fut.set_result(True)
        loop.run_until_complete(end)    
        
    def on_completed(self,loop):
        """
        should be called when the program wants to shut down as a part of it's normal behaviour. 
        stops the event loop. If there is undone tasks it shall give exception
        """
        loop.stop()
    
    def on_interrupt(self, loop, fut):
        """
        called when the user wants to interrupt and close the program. 
        cancel tasks, clean all resources, be nice.
        """
        if fut.cancelled(): #fut already cancelled
            return
        loop.call_soon_threadsafe(fut.cancel)
        if sys.version_info.minor >= 6:
            loop.run_until_complete(loop.shutdown_asyncgens())
        
    def on_terminate(self, loop, fut):
        """
        called when the user wants to terminate and close the program in not so nice way. 
        just stop the event loop
        """
        
        loop.call_soon_threadsafe(loop.stop)
        
    def on_exit(self, all_ok):
        """
        app should shut down by calling this. 
        calls the sys.exit (false -> 1 True ->0)
        """
        if all_ok:
            sys.exit(0)
        else:
            sys.exit(1)