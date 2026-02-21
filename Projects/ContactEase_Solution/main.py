"""
Entry point of the application.
"""

from UI import UI
from time import sleep

if __name__ == "__main__":
    ui = UI()
    print("For an optimized experience set terminal size to: 80x25\nInitializing",end="")
    for i in range(5):
        sleep(1)
        print(".", end="", flush=True)
    ui.run()