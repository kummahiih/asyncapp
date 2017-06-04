'''
@copyright: 2017 by Pauli Henrikki Rikula
@license: MIT <http://www.opensource.org/licenses/mit-license.php>

Yet another Python 3 async app framework for Linux
done as Python 3 asyncio studying project.
Could ease your burden when creating
asyncronoys python 3 apps for Linux.

Inherit AsyncApp, create a logger for example with
default_logger -factory and run your application instance by using
AsyncLinuxAppRunner -instance.
'''

__version__ = '0.1.0'

__author__ = 'Pauli Henrikki Rikula'

__all__ = [
    #classes
    'get_default_logger',
    'AsyncApp',
    'AsyncLinuxAppSession',
    #for mocking
    'default_logger',
    'async_app',
    'async_linux_app_session'
    ]


from asyncapp.async_app import AsyncApp
from asyncapp.async_linux_app_session import AsyncLinuxAppSession
from asyncapp.default_logger import get_default_logger



