# asyncapp
Yet another Python 3 async app framework for Linux (Python 3 asyncio studying project).
Could ease your burden when creating asyncronoys python 3 apps for Linux.

Things I tried and managed to somehow achieve: 
 * lightweight to use, testable and easily overwritable 
   ( dependency injection, inversion of control, composition instead of inheritance )
 * tests done and done by using unittest (and unittest.Mock rather than unittest.patch)
 * unit tests for asyncronous parts as well
 * overwritable SIGINT and SIGTERM signal handlers
 * program exit value related behaviour
 * top level exception handling
 * overritable top level logging
 * coroutine cancellation via program exit value future

See  EchoApp.py for an usage example and asyncapp.AsyncApp class for more points to overwrite. 
The tests are written into AsyncLinuxAppTest.py and passed when I ran em in Ubuntu using Python 3.5.2.

Things to do:
 * the usage of this library is not fluent enough (you know what I mean)
 * asyncapp.AsyncLinuxAppRunner is messy. Getters, abstract base class, ... ? 
 * study how similar things are done in windows and try to write a class named asyncapp.AsyncWindowsAppRunner


