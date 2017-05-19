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








class AsyncLinuxAppRunner:
    def __init__(self, logger, asyncApp):
        assert sys.version_info.major == 3
        assert sys.version_info.minor == 5 or sys.version_info.minor == 6    
        assert isinstance(logger, logging.Logger)
        assert isinstance(asyncApp, AsyncApp)
        self._logger = logger     
        self.asyncApp =  asyncApp
        self.is_initialized = False
        self.is_terminating = False
        self._logger.info('instance created')
  

    
    def run(self):
        self._initialize()
        
        self.all_ok = True

        try:
            self._logger.info('loophandler starting')
            try:
                self.all_ok = self.all_ok and self.asyncApp.on_run(
                    self._loop, 
                    self._exit_fut)
            except RuntimeError as runtime_error:
                if self.is_terminating:
                    self._logger.exception('excetion while terminating. should be ok', exception = e)
                else:
                    raise runtime_error            
            self._logger.info('loophandler done')
        except Exception as e:
             self._logger.exception("unhandled exception", exception = e) 
             self.all_ok = False
        finally:
            self._logger.info('finalization starting')

            
            self._loop.close()
            self._logger.info('finalization done')            
   
        self.asyncApp.on_exit(self.all_ok)
        
        
    def _initialize(self):
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
        self._logger.info("execution completed")
        self.all_ok = fut.result()
        try:
            self.asyncApp.on_completed(self._loop)            
        except Exception as e:
            self._logger.exception("unhandled exception on shutdown. program shutdown anyway.", exception = e) 
            self.asyncApp.on_exit(False)   
        
    def interrupt(self):
        self._logger.info("interrupting execution")
        self.all_ok = False
        try:
            self.asyncApp.on_interrupt(self._loop, self._exit_fut)            
        except Exception as e:
            self._logger.exception("unhandled exception on interrupt. program shutdown.", exception = e) 
            self.asyncApp.on_exit(False)
            
    
            
    def terminate(self):
        self._logger.info("terminating execution")
        self.is_terminating = True
        self.all_ok = False
        try:
            self.asyncApp.on_terminate(self._loop, self._exit_fut)            
        except Exception as e:
            self._logger.exception("unhandled exception on terminate. program shutdown.", exception = e) 
            self.asyncApp.on_exit(False)

           