from ._jijmodeling import dataset as _dataset  # type: ignore
import sys

for component in _dataset.__all__:
    setattr(sys.modules[__name__], component, getattr(_dataset, component))
