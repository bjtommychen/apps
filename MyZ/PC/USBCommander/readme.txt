Tommy:
use WINDDK/2600 build OK.
but use latest WDK (WINDDK 7600), ALWAYS FAILED. DON'T KNOW REASON !!!

find the reason.
check ./sources, add below line to fix this.

#Tommy add this for latest winddk 7600.
USE_MSVCRT=1
