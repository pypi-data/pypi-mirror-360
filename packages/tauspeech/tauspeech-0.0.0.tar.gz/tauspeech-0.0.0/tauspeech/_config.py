from pathlib import Path
import sys

def get_tauspeech_path():
    return Path([x for x in sys.path if x.endswith("tauspeech")][0])