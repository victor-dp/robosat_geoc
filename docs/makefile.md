## Makefile
```
This Makefile rules are designed for RoboSat.pink devs and power-users.
For plain user installation follow README.md instructions, instead.


 make install     To install, few Python dev tools and RoboSat.pink in editable mode.
                  So any further RoboSat.pink Python code modification will be usable at once,
                  throught either rsp tools commands or robosat_pink.* modules.

 make check       Launchs code tests, and tools doc updating.
                  Do it, at least, before sending a Pull Request.

 make check_tuto  Launchs rsp commands embeded in tutorials, to be sure everything still up to date.
                  Do it, at least, on each CLI modifications, and before a release.
                  NOTA: It takes a while.

 make kill        Kill all GPU processes running, from CUDA_VISIBLE_DEVICES GPUs.
                  Useful, to eradicate NVIDIA zombies processes...

 make pink        Python code beautifier,
                  as Pink is the new Black ^^
```
