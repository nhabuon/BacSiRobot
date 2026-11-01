# -*- coding: utf-8 -*-
"""Bo test bat benh. Chay: python test_bacsi.py  (phai PASS het truoc khi day len GitHub)"""
from bacsi_core import diagnose, normalize, shop_link

# (cau khach go, ket qua mong doi)
# ket qua: id benh dung DAU TIEN, hoac "need_info" / "code_unknown" / "not_found"
CASES = [
    # --- 13 cau da lam app cu tra sai ---
    ("không sạc được", "pin"),
    ("robot không chạy", "need_info"),
    ("kêu to", "choi"),
    ("khong ra nuoc", "tac_nuoc"),
    ("hút bụi yếu", "loc"),
    ("báo lỗi 10", "code_unknown"),
    ("Error 1", "lds"),
    ("mù đường", "lds"),
    ("giẻ lau bị hôi", "hoi_gie"),
    ("trạm không hút rác", "tram_rac"),
    ("máy chạy lệch vòng tròn", "banh_xe"),
    ("đèn nháy đỏ", "need_info"),
    ("nước lau sàn nhiều bọt", "not_found"),
    # --- cau ban cu da dung, phai giu dung ---
    ("không ra nước", "tac_nuoc"),
    ("bơm nước yếu", "tac_nuoc"),
    ("hết pin nhanh", "pin"),
    ("tự tắt máy", "pin"),
    ("lốp mòn", "banh_xe"),
    ("thay màng lọc hepa", "loc"),
    ("kêu lạch cạch", "hop_so"),
    ("lỗi 1", "lds"),
    ("loi laser", "lds"),
    ("quạt hút không chạy", "quat"),
    # --- bay chuoi con ---
    ("máy không về sạc", "pin"),
    ("không lên nguồn", "pin"),
    ("chổi chính quấn tóc", "choi"),
    ("chạy ổn nhưng hơi ồn", "not_found"),
    ("robot chưa chạy", "not_found"),
    ("ERROR 12", "code_unknown"),
    ("lỗi 11 không sạc", "pin"),
    ("ROBOT KHÔNG RA NƯỚC!!!", "tac_nuoc"),
    # --- tu de nham khi bo dau ---
    ("chạy tốc độ chậm", "not_found"),
    ("lớp sơn bị xước", "not_found"),
    ("gie hoi qua", "hoi_gie"),
    ("khong sac duoc", "pin"),
    ("lop mon", "banh_xe"),
    ("quan toc o choi", "choi"),
    ("trạm sạc không hút rác", "tram_rac"),
]


def first(res):
    if res["status"] == "found":
        return res["issues"][0]["id"]
    return res["status"]


def main():
    ok = 0
    for q, want in CASES:
        res = diagnose(q)
        got = first(res)
        names = [i["id"] for i in res["issues"]]
        flag = "PASS" if got == want else "FAIL"
        ok += got == want
        print("%-4s %-30s -> %-12s %s" % (flag, q, got, names if len(names) > 1 else ""))
    # kiem tra phu
    extra = [
        ("normalize bo dau + d", normalize("Đổi Bánh XE") == " doi banh xe "),
        ("toi da 2 benh", all(len(diagnose(q)["issues"]) <= 2 for q, _ in CASES)),
        ("link ma hoa URL", " " not in shop_link("pin", "t8", "pin robot hút bụi")
         and "keyword=pin+robot" in shop_link("pin", "t8", "pin robot hút bụi")),
        ("link VIP giu nguyen", shop_link("bot_canxi", "", "x").endswith("42427536678")),
        ("cau rong khong vo", diagnose("")["status"] == "not_found"),
    ]
    for name, cond in extra:
        print("%-4s %s" % ("PASS" if cond else "FAIL", name))
        ok += bool(cond)
    total = len(CASES) + len(extra)
    print("\nTONG: %d/%d PASS" % (ok, total))
    return ok == total


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
