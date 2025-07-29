"""Sampler utilities re-exported from NetKet with custom rules."""

from netket import sampler as _nksampler
from .rules import GaussianRule

__all__ = ["GaussianRule", "rules"]
__all__ += [name for name in dir(_nksampler) if not name.startswith("_")]

# Re-export everything from netket.sampler, without overwriting custom objects
locals().update(
    {
        name: getattr(_nksampler, name)
        for name in __all__
        if name not in {"GaussianRule", "rules"} and hasattr(_nksampler, name)
    }
)
