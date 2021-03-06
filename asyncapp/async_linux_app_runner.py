"""
   @copyright: 2017 by Pauli Henrikki Rikula
   @license: MIT <http://www.opensource.org/licenses/mit-license.php>
"""

from . import AsyncApp
import asyncio
import functools
import os
import signal
import logging
import sys
from symbol import except_clause








class AsyncLinuxAppRunner:
    def __init__(self, logger, asyncApp, loop = None):
        assert sys.version_info.major == 3
        assert sys.version_info.minor == 5 or sys.version_info.minor == 6    
        assert isinstance(logger, logging.Logger)
        assert isinstance(asyncApp, AsyncApp)
        self._logger = logger     
        self.asyncApp =  asyncApp
        self._loop = loop
        self.exception = None
        self.exception_info = None
        self.is_initialized = False
        self.is_terminating = False
        self._logger.info('instance created')
  

    
    def run(self):
        self._initialize()
        assert isinstance(self._exit_fut, asyncio.Future)
        
        self.all_ok = True

        try:
            self._logger.info('loophandler starting')
            result = None
            try:
                result = self.asyncApp.on_run(
                    self._loop, 
                    self._exit_fut)
            except asyncio.CancelledError:
                pass 
            except RuntimeError as runtime_error:
                if self.is_terminating:
                    self._logger.exception('exception while terminating. should be ok')
                else:
                    raise runtime_error            
            
            if not self._exit_fut.done():
                self.all_ok = result == True
                self._exit_fut.set_result(self.all_ok) 
            elif self._exit_fut.cancelled():
                self.all_ok = False
            elif self._exit_fut.exception() != None:
                raise self._exit_fut.exception()
            else:
                self.all_ok = self._exit_fut.result()
            
            self._logger.info('loophandler done')
            
        except Exception as e:
             self._logger.exception("unhandled exception") 
             self.exception = e
             self.exception_info = sys.exc_info()
             self.all_ok = False
        finally:
            self._logger.info('finalization starting')

            
            self._loop.close()
            self._logger.info('finalization done')            
   
        
        self.asyncApp.on_exit(self.all_ok)
        
        
    def _initialize(self):
        assert self.is_initialized == False
        if self._loop == None:
            self._loop = asyncio.new_event_loop() #cant just use get_event_loop because of unit testing
        self._exit_fut = self._loop.create_future()
        self._exit_fut.add_done_callback( self._completed )
        
        self._loop.add_signal_handler(
                signal.SIGINT,
                self.interrupt)    
                
        self._loop.add_signal_handler(
                signal.SIGTERM,
                self.terminate)
        
        asyncio.set_event_loop(self._loop)
        self.is_initialized = True
        self.is_terminating = False
        
    def _completed(self, fut):
        assert isinstance(fut, asyncio.Future)
        self._logger.info("execution completed")
        if fut.cancelled():
            self.all_ok = False
        else:
            self.all_ok = fut.result()
        try:
            self.asyncApp.on_completed(self._loop)            
        except Exception as e:
            self._logger.exception("unhandled exception on shutdown. program shutdown anyway.") 
            self.asyncApp.on_exit(False)   
        
    def interrupt(self):
        self._logger.info("interrupting execution")
        self.is_terminating = True
        self.all_ok = False
        try:
            self.asyncApp.on_interrupt(self._loop, self._exit_fut)            
        except Exception as e:
            self._logger.exception("unhandled exception on interrupt. program shutdown.") 
            self.asyncApp.on_exit(False)
            
    
            
    def terminate(self):
        self._logger.info("terminating execution")
        self.is_terminating = True
        self.all_ok = False
        try:
            self.asyncApp.on_terminate(self._loop, self._exit_fut)            
        except Exception as e:
            self._logger.exception("unhandled exception on terminate. program shutdown.") 
            self.asyncApp.on_exit(False)

           