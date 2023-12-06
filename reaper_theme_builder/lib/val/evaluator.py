import functools

from simpleeval import simple_eval

from .constants import ConstantsConfig
from .formatter import split_double, split_single
from .funcs import FUNCTIONS, NRGB_CONST


class Evaluator:
    def __init__(self, constants: ConstantsConfig | None = None) -> None:
        if constants is None:
            constants = ConstantsConfig(None)

        self._constants = constants

    @functools.cache
    def get_constant(self, full_name: str):
        raw_value = self._constants.get_constant(full_name)
        return self.val(raw_value)

    def _functions(self):
        return {
            **FUNCTIONS,
            "c": self.get_constant,
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

    def parse_single(self, text: str):
        result = []
        for prefix, raw in split_single(text):
            result.append(prefix)
            if raw is not None:
                result.append(str(self.val(raw)))
        return "".join(result)

    def parse_double(self, text: str):
        result = []
        for prefix, raw in split_double(text):
            result.append(prefix)
            if raw is not None:
                result.append(str(self.val(raw)))
        return "".join(result)
