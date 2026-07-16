"""MODULE D — decode (vector ngưỡng → mask) + oracle (trần Dice).

Xem :mod:`src.decode.decoding` cho toàn bộ hợp đồng interface và ghi chú A1/A2
(docs/preregistration.md §6). Re-export các API công khai để dùng ngắn gọn:
    from src.decode import decode, oracle_levelset, mask_hash
"""

from src.decode.decoding import (
    LABELMAP_DECODERS,
    RULES,
    decode,
    decode_labelmap,
    label_map,
    mask_hash,
    oracle_interval,
    oracle_levelset,
    oracle_single,
)

__all__ = [
    "RULES",
    "LABELMAP_DECODERS",
    "decode",
    "decode_labelmap",
    "label_map",
    "oracle_single",
    "oracle_interval",
    "oracle_levelset",
    "mask_hash",
]
