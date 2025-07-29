import sys
from junklang.interpreter import run_junk

def main():
    if len(sys.argv) != 2:
        print("Usage: junklang <filename>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        run_junk(f.read())
