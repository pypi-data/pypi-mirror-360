"""
File in charge of containing the esoteric types used by tkinter so that they can be referenced in the code.
"""

import sys
from typing import Union, Literal

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    TypeAlias = type


TK_ANCHOR_TYPE: TypeAlias = Union[
    str,
    Literal[
        "nw", "n", "ne", "w", "center",
        "e", "sw", "s", "se"
    ]
]

TK_RELIEF_TYPE: TypeAlias = Union[
    str,
    Literal[
        "flat", "raised", "sunken", "groove", "ridge"
    ]
]

TK_SIDE_TYPE: TypeAlias = Union[
    str,
    Literal["left", "right", "top", "bottom"]
]


TK_SCROLL_ORIENTATION_TYPE: TypeAlias = Union[
    str,
    Literal["horizontal", "vertical"]
]
