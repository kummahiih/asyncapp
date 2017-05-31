# asyncapp
Python 3 asyncio studying project. Could ease your burden when creating asyncronoys python3 apps for Linux.

Things I tried and managed to somehow achieve: 
 * lightweight to use, testable and easily overwritable ( dependency injection, inversion of control )
 * tests done and done by using unittest (and unittest.Mock rather than unittest.patch)
 * unit tests for asyncronous parts as well
 * overwritable SIGINT and SIGTERM signal handlers
 * program exit value related behaviour
 * top level exception handling
 * overritable top level logging
 * coroutine cancellation via program exit value future


See  EchoApp.py for an usage example and asyncapp.AsyncApp class for more points to overwrite. 
The tests are written into AsyncLinuxAppTest.py and passed when I ran em in Ubuntu using Python 3.5.2.
