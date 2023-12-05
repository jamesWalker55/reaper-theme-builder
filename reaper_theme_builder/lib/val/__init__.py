from configparser import ConfigParser
from simpleeval import simple_eval

class Evaluator:
    def __init__(self, constants: ConfigParser|None=None) -> None:
        if constants is None:
            constants = ConfigParser()
        
        self._constants = constants

    def _functions(self):
        return {
            "rgb": lambda r,g,b: (b << 16) + (g << 8) + r,
            "rgba": lambda r,g,b,a: (r << 24) + (g << 16) + (b << 8) + a
            nrgb(r, g, b)
        }

    def val(self, text: str):
        return

def val(text: str):
    return simple_eval
