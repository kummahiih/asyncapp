"""
   @copyright: 2017 by Pauli Henrikki Rikula
   @license: MIT <http://www.opensource.org/licenses/mit-license.php>
"""

import unittest
from unittest.mock import patch, Mock, call

import asyncapp
import logging
import sys

class AsyncLinuxAppRunner(unittest.TestCase):
    
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
        

        
    
  
            
if __name__ == '__main__':
    
    unittest.main()
    
    