"""
   @copyright: 2017 by Pauli Henrikki Rikula
   @license: MIT <http://www.opensource.org/licenses/mit-license.php>
"""


import asyncio
import signal
import logging
import sys
from collections import namedtuple

from . import AsyncApp

AppSessionInfo = namedtuple(
    'AppSessionInfo',
    ['exception', 'exception_info', 'is_initialized', 'is_terminating', 'is_cancelled', 'all_ok']
    )


class AsyncLinuxAppSession:
    """Handle the top execution of an AsyncApp instance

    AsyncLinuxAppSession's responsibility is
    to handle top level logging, top level exception handling and
    hook the interrupt and terminate signals
    """
    def __init__(self, logger, asyncApp, loop=None):
        assert sys.version_info.major == 3
        assert sys.version_info.minor == 5 or sys.version_info.minor == 6
        assert isinstance(logger, logging.Logger)
        assert isinstance(asyncApp, AsyncApp)
        self._logger = logger
        self._async_app = asyncApp
        self._loop = loop
        self._exit_fut = None
        self.info = AppSessionInfo(
            exception=None,
            exception_info=None,
            is_initialized=False,
            is_terminating=False,
            is_cancelled=False,
            all_ok=True)
        self._logger.info('instance created')

    def run(self):
        '''triggers the app's execution
        '''
        self._initialize()
        assert isinstance(self._exit_fut, asyncio.Future)

        try:
            self._logger.info('loophandler starting')
            result = None
            try:
                result = self._async_app.on_run(
                    self._loop,
                    self._exit_fut)
            except asyncio.CancelledError:
                pass
            except RuntimeError as runtime_error:
                if self.info.is_terminating:
                    self._logger.exception('exception while terminating. should be ok')
                else:
                    raise runtime_error

            if not self._exit_fut.done():
                self._update(all_ok=result is True)
                self._exit_fut.set_result(self.info.all_ok)
            elif self._exit_fut.cancelled():
                self._update(all_ok=False, is_cancelled=True)
            elif self._exit_fut.exception() is None:
                self._update(all_ok=self._exit_fut.result())
            else:
                raise self._exit_fut.exception()

            self._logger.info('loophandler done')

        except Exception as exception:
            self._logger.exception("unhandled exception")
            self._update(exception=exception, exception_info=sys.exc_info(), all_ok=False)
        finally:
            self._logger.info('finalization starting')
            self._loop.close()
            self._logger.info('finalization done')
        self._async_app.on_exit(self.info.all_ok)

    def interrupt(self):
        '''Interrupt the app's execution in controlled fashion
        '''
        self._logger.info("interrupting execution")
        self._update(is_terminating=True, all_ok=False)
        try:
            self._async_app.on_interrupt(self._loop, self._exit_fut)
        except Exception as exception:
            self._logger.exception("unhandled exception on interrupt. program shutdown.")
            self._update(exception=exception, exception_info=sys.exc_info(), all_ok=False)
            self._async_app.on_exit(False)

    def terminate(self):
        '''Terminates the app's execution in not so controlled fashion
        '''
        self._logger.info("terminating execution")
        self._update(is_terminating=True, all_ok=False)
        try:
            self._async_app.on_terminate(self._loop, self._exit_fut)
        except Exception as exception:
            self._logger.exception("unhandled exception on terminate. program shutdown.")
            self._update(exception=exception, exception_info=sys.exc_info(), all_ok=False)
            self._async_app.on_exit(False)

    def _update(self, **properties):
        old_values = self.info._asdict()
        old_values.update(properties)
        info = AppSessionInfo(**old_values)
        self._logger.debug(str(info._asdict()))
        self.info = info

    def _initialize(self):
        if self._loop is None:
            # Can't just use get_event_loop because of unit testing
            self._loop = asyncio.new_event_loop()
        self._exit_fut = self._loop.create_future()
        self._exit_fut.add_done_callback(self._completed)

        self._loop.add_signal_handler(
            signal.SIGINT,
            self.interrupt)

        self._loop.add_signal_handler(
            signal.SIGTERM,
            self.terminate)

        asyncio.set_event_loop(self._loop)

        self._update(is_initialized=True, is_terminating=False)

    def _completed(self, fut):
        assert isinstance(fut, asyncio.Future)
        self._logger.info("execution completed")
        if fut.cancelled():
            self._update(all_ok=False, is_cancelled=True)
        else:
            self._update(all_ok=fut.result())
        try:
            self._async_app.on_completed(self._loop)
        except Exception as exception:
            self._logger.exception("unhandled exception on shutdown. program shutdown.")
            self._update(exception=exception, exception_info=sys.exc_info(), all_ok=False)
            self._async_app.on_exit(False)


