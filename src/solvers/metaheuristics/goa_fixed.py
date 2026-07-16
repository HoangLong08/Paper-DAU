"""GOA-fixed — Grasshopper Optimization Algorithm cài ĐÚNG.

Bản sửa của baseline lỗi trong goa.py. Khác biệt DUY NHẤT: khoảng cách được
chuẩn hoá về ``[1, 4]`` trước khi đưa vào hàm lực xã hội ``s(r)`` (đúng như
Saremi et al. 2017 mô tả), nhờ đó lực xã hội không bão hoà về 0 và bầy giữ được
động lực khám phá kể cả khi k>2.

Trình bày **cả hai** phiên bản cạnh nhau (docs/preregistration.md §6/A6) là cách
tự bảo vệ trước phản biện *"các anh cài GOA sai ⇒ QIGOA là strawman"*: tính đúng
đắn của implementation được xác lập độc lập (cổng E1b), và kết luận trung tâm
KHÔNG phụ thuộc vào riêng GOA.

Tham chiếu: Saremi, Mirjalili & Lewis, *Advances in Engineering Software*
105:30–47 (2017), ``10.1016/j.advengsoft.2017.01.004``.
"""

from __future__ import annotations

from src.solvers.metaheuristics.goa import GOA


class GOAFixed(GOA):
    name = "GOA-fixed"

    #: khác biệt duy nhất so với GOA lỗi — chuẩn hoá khoảng cách về [1,4].
    NORMALIZE_DISTANCE: bool = True
