from configparser import ConfigParser

from simpleeval import simple_eval

from .funcs import FUNCTIONS, NRGB_CONST


class Evaluator:
    def __init__(self, constants: ConfigParser | None = None) -> None:
        if constants is None:
            constants = ConfigParser()

        self._constants = constants

    def _functions(self):
        return {
            **FUNCTIONS,
        }

    def _names(self):
        return {
            "NRGB": NRGB_CONST,
        }

    def val(self, text: str):
        return simple_eval(
            text,
            functions=self._functions(),
            names=self._names(),
        )
