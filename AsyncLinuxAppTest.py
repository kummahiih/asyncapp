"""
   @copyright: 2017 by Pauli Henrikki Rikula
   @license: MIT <http://www.opensource.org/licenses/mit-license.php>
"""

import unittest
from unittest.mock import patch, Mock, call
import asyncio

import asyncapp
import logging
import sys

import traceback
import os
import signal
from _ast import Await
from logging import raiseExceptions


class AsyncLinuxAppRunner(unittest.TestCase):
    
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        
    def tearDown(self):        
        unittest.TestCase.tearDown(self)
        self.loop.close()
    
    def test_logger_constructor(self):
        logger =  Mock(spec=logging.Logger)
        handler = Mock(spec=asyncapp.AsyncApp)
        
        
        tested = asyncapp.AsyncLinuxAppRunner(logger, handler)            
        logger.info.assert_called_once_with('instance created')
   
   
 
    def test_logger_run_nothing(self):
        logger =  Mock(spec=logging.Logger)
        handler = Mock(spec=asyncapp.AsyncApp)                      
        tested = asyncapp.AsyncLinuxAppRunner(logger, handler)
        tested.run()
        logger.exception.assert_not_called()  
        logger.info.assert_has_calls([
            call('loophandler starting'),  
            call('loophandler done'),
            call('finalization starting'),     
            call('finalization done')
        ])
    
    def test_logger_run_throws(self):
        logger =  Mock(spec=logging.Logger)
        
        class RunException(Exception):
            pass
        
        testException = RunException()
        
        class TrowingHandler(asyncapp.AsyncApp):
            def __init__(self, aLogger):
                super().__init__(aLogger)
            def on_run(self, loop, fut):
                self.logger.info("on_run called")
                raise testException
            def on_exit(self,all_ok):
                assert all_ok == False
                self.logger.info("on_exit called")
                return
                
        handler = TrowingHandler(logger)
        
        tested = asyncapp.AsyncLinuxAppRunner(logger, handler,loop=self.loop)
        
        tested.run()
        logger.exception.assert_called_once_with("unhandled exception")
        
        logger.info.assert_has_calls([
            call('instance created'),
            call('loophandler starting'),  
            call('on_run called'),  
            call('finalization starting'),     
            call('finalization done'),
            call('on_exit called')
        ])
    
    class ReturningHandler(asyncapp.AsyncApp):
            def __init__(self, aLogger, return_value):
                super().__init__(aLogger)
                self.return_value = return_value
                
            def on_run(self, loop, fut):
                self.logger.info("on_run called")
                async def end():
                    self.logger.info("end called")
                    print('return_value' + str(self.return_value))
                    fut.set_result(self.return_value)
                loop.run_until_complete(end())
            def on_exit(self,all_ok):
                print('all_ok' + str(all_ok))
                assert all_ok == self.return_value                
                self.logger.info("on_exit called")                
                return
    
    def test_logger_run_returns_false(self):
        logger =  Mock(spec=logging.Logger)       
                
        handler = self.ReturningHandler(logger, False)
        
        tested = asyncapp.AsyncLinuxAppRunner(logger, handler,loop=self.loop)
        
        tested.run()

        logger.exception.assert_not_called()
        
        logger.info.assert_has_calls([
             call('instance created'),
             call('loophandler starting'),
             call('on_run called'),
             call('end called'),
             call('execution completed'),
             call('loophandler done'),
             call('finalization starting'),
             call('finalization done'),
             call('on_exit called')
        ])    
        
    def test_logger_run_returns_true(self):
        logger =  Mock(spec=logging.Logger)       
                
        handler = self.ReturningHandler(logger, True)
        
        tested = asyncapp.AsyncLinuxAppRunner(logger, handler,loop=self.loop)
        
        tested.run()
        logger.exception.assert_not_called()
        
        logger.info.assert_has_calls([
             call('instance created'),
             call('loophandler starting'),
             call('on_run called'),
             call('end called'),
             call('execution completed'),
             call('loophandler done'),
             call('finalization starting'),
             call('finalization done'),
             call('on_exit called')
        ])    

        
                  
    def test_handler_run_nothing_all_ok(self):
        logger =  Mock(spec=logging.Logger)
        handler = Mock(spec=asyncapp.AsyncApp)       
        handler.on_run.return_value = True #all ok   
        tested = asyncapp.AsyncLinuxAppRunner(logger, handler)
        tested.run()   
        handler.on_interrupt.assert_not_called()
        handler.on_terminate.assert_not_called()
        handler.on_run.assert_called_once_with(tested._loop, tested._exit_fut)
        handler.on_exit.assert_called_once_with(True) #all ok
            
                       
    def test_handler_run_nothing_all_not_ok(self):
        logger =  Mock(spec=logging.Logger)
        handler = Mock(spec=asyncapp.AsyncApp)        
        handler.on_run.return_value = False #all not ok   
        tested = asyncapp.AsyncLinuxAppRunner(logger, handler)
        tested.run()   
        handler.on_interrupt.assert_not_called()
        handler.on_terminate.assert_not_called()
        handler.on_run.assert_called_once_with(tested._loop, tested._exit_fut)
        handler.on_exit.assert_called_once_with(False) #all not ok
        
    def test_logger_terminate_called(self):
        logger =  Mock(spec=logging.Logger)
        handler = Mock(spec=asyncapp.AsyncApp)
        tested = asyncapp.AsyncLinuxAppRunner(logger, handler)
        tested.run()
        tested.terminate()
        
        handler.on_terminate.assert_called_once_with(tested._loop, tested._exit_fut)
        logger.info.assert_has_calls([
            call('terminating execution')
        ])
        logger.exception.assert_not_called()
        
    def test_logger_interrupt_called(self):
        logger =  Mock(spec=logging.Logger)
        handler = Mock(spec=asyncapp.AsyncApp)
        tested = asyncapp.AsyncLinuxAppRunner(logger, handler)
        tested.run()
        tested.interrupt()
        
        handler.on_interrupt.assert_called_once_with(tested._loop, tested._exit_fut)
        logger.info.assert_has_calls([
            call('interrupting execution')
        ])
        logger.exception.assert_not_called()
    
    
    class WaitingHandler(asyncapp.AsyncApp):
        def __init__(self, aLogger, coro):
            super().__init__(aLogger)
            self.coro = coro

        def on_run(self, loop, fut):
            print(self.coro)
            print("1")
                
            async def wait():
                while not fut.done():
                    print('looping')
                    await asyncio.sleep(1)
            
            loop.run_until_complete(
                asyncio.gather(
                    wait(),
                    self.coro()
                    )
                )
            print('done')
        
        def on_interrupt(self, loop, fut):
            self.logger.info('on_interrupt called')
            super().on_interrupt(loop,fut)
            
        def on_terminate(self, loop, fut):
            self.logger.info('on_terminate called')
            super().on_terminate(loop,fut)
            
        def on_exit(self,all_ok):   
            self.logger.info("on_exit called")                
            return

    def test_logger_on_interrupt(self):
        logger =  Mock(spec=logging.Logger)
        
        tested = None
        
        async def interrupt():
            print('interrupt')
            await asyncio.sleep(2, self.loop)
            tested.interrupt()
        
        handler = self.WaitingHandler(logger, interrupt)    
        tested = asyncapp.AsyncLinuxAppRunner(logger, handler, loop = self.loop)
        
        tested.run()

        
        logger.info.assert_has_calls([
            call('instance created'),
            call('loophandler starting'),
            call('interrupting execution'),
            call('on_interrupt called'),
            call('execution completed'),
            call('loophandler done'),
            call('finalization starting'),
            call('finalization done'),
            call('on_exit called')
        ])   
        
    def test_logger_on_terminate(self):
        logger =  Mock(spec=logging.Logger)
        
        tested = None
        
        async def terminate():
            print('terminate')
            await asyncio.sleep(2, self.loop)
            tested.terminate()
        
        handler = self.WaitingHandler(logger, terminate)    
        tested = asyncapp.AsyncLinuxAppRunner(logger, handler, loop = self.loop)
        
        tested.run()
        
        logger.info.assert_has_calls([
            call('instance created'),
            call('loophandler starting'),
            call('terminating execution'),
            call('on_terminate called'),
            call('loophandler done'),
            call('finalization starting'),
            call('finalization done'),
            call('on_exit called')
        ]) 
        
        
            
if __name__ == '__main__':
    
    unittest.main()
    
    
