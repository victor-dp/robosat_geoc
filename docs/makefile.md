## Makefile
```
This Makefile rules are designed for RoboSat.pink devs and power-users.
For plain user installation follow README.md instructions, instead.


 make install   To install, few Python dev tools and RoboSat.pink in editable mode.
                So any further RoboSat.pink Python code modification will be usable at once,
                throught either rsp tools commands or robosat_pink.* modules.

 make check     Launchs code tests, and tools doc updating.
                Do it, at least, before sending a Pull Request.

 make check_doc Launchs rsp commands embeded in documentation, to be sure still up to date.
                It takes a while.

 make pink      Python code beautifier,
                as Pink is the new Black ^^
```
