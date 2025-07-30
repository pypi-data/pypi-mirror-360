import spectra
import sys

browser = "c"
src = "r"
for argv in sys.argv:
    if argv == "-c" or argv == "--chrome":
        browser = "c"
    elif argv == "-f" or argv == "--firefox":
        browser = "f"
    elif argv == "-e" or argv == "--edge":
        browser = "e"
    elif argv == "-s" or argv == "--safari":
        browser = "s"
    elif argv == "-l" or argv == "--local":
        src = "l"
    elif argv == "-r" or argv == "--remote":
        src = "r"

spectra.Start(mode="g", src=src, browser=browser)
