try:
    from . import logging

    __all__ = [
        "logging",
    ]

except ImportError:
    raise ImportError(
        "NVFlare package not found. Please install "
        "apheris-utils with the 'nvflare' extra to use this module. "
        "`pip install apheris-utils[nvflare]`"
    )
