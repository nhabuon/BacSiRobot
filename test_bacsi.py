# -*- coding: utf-8 -*-
"""Bo test bat benh V2. Chay: python test_bacsi.py  (phai PASS het truoc khi day len GitHub)"""
from bacsi_core import builtin_kb, build_kb, diagnose, normalize, shop_link, COL_B, COL_M

KB = builtin_kb()
U = "Chưa rõ"
CASES = [
    # (cau khach go, doi may, ket qua mong doi: id benh dau tien hoac status)
    ("không sạc được", U, "pin"),
    ("robot không chạy", U, "need_info"),
    ("kêu to", U, "choi"),
    ("khong ra nuoc", U, "tac_nuoc"),
    ("hút bụi yếu", U, "loc"),
    ("mù đường", U, "lds"),
    ("giẻ lau bị hôi", U, "hoi_gie"),
    ("trạm không hút rác", U, "tram_rac"),
    ("máy chạy lệch vòng tròn", U, "banh_xe"),
    ("đèn nháy đỏ", U, "need_info"),
    ("nước lau sàn nhiều bọt", U, "not_found"),
    ("không ra nước", U, "tac_nuoc"),
    ("bơm nước yếu", U, "tac_nuoc"),
    ("hết pin nhanh", U, "pin"),
    ("tự tắt máy", U, "pin"),
    ("lốp mòn", U, "banh_xe"),
    ("thay màng lọc hepa", U, "loc"),
    ("kêu lạch cạch", U, "hop_so"),
    ("loi laser", U, "lds"),
    ("quạt hút không chạy", U, "quat"),
    ("máy không về sạc", U, "ve_tram"),
    ("không lên nguồn", U, "pin"),
    ("chổi chính quấn tóc", U, "choi"),
    ("chạy ổn nhưng hơi ồn", U, "on_to"),
    ("robot chưa chạy", U, "not_found"),
    ("ROBOT KHÔNG RA NƯỚC!!!", U, "tac_nuoc"),
    ("chạy tốc độ chậm", U, "not_found"),
    ("lớp sơn bị xước", U, "not_found"),
    ("gie hoi qua", U, "hoi_gie"),
    ("khong sac duoc", U, "pin"),
    ("lop mon", U, "banh_xe"),
    ("quan toc o choi", U, "choi"),
    ("trạm sạc không hút rác", U, "tram_rac"),
    # --- MA LOI THEO HANG (trong tam GD2) ---
    ("lỗi 1", "Roborock S7 / S8", "lds"),
    ("Error 1", "Xiaomi Mi Robot Vacuum-Mop", "can_va"),
    ("lỗi 01", "Xiaomi Mi Robot Vacuum-Mop Essential", "banh_xe"),
    ("Error 1", U, "code_multi"),
    ("lỗi 112", "Ecovacs Deebot T8 AIVI / Max", "lds"),
    ("112", "Ecovacs Deebot T9", "lds"),
    ("báo lỗi 109", "Ecovacs Deebot T5 / DX96", "choi"),
    ("lỗi 312", "Ecovacs Deebot X1 Omni / Turbo", "tram_rac"),
    ("lỗi 10", "Roborock S5 / S6", "loc"),
    ("lỗi 10", "Xiaomi Mi Robot Vacuum-Mop", "pin"),
    ("lỗi 26", "Roborock Q7", "cam_bien_tuong"),
    ("lỗi 999", "Roborock S7 / S8", "code_unknown"),
    ("lỗi 999", U, "code_unknown"),
    ("lỗi 13 không sạc", "Roborock S7 / S8", "pin"),
    ("Clean the brush", "Dreame L10 / W10", "choi"),
    ("laser distance sensor error", "Dreame D9", "lds"),
]


def first(res):
    if res["status"] == "found":
        return res["issues"][0]["id"] if res["issues"] else "found_no_issue"
    return res["status"]


def main():
    ok = 0
    for q, model, want in CASES:
        res = diagnose(q, model, KB)
        got = first(res)
        flag = "PASS" if got == want else "FAIL"
        ok += got == want
        extra = ""
        if res["code_rows"]:
            extra = "| " + "; ".join("%s %s=%s" % (r["brand"], r["code"], r["meaning"]) for r in res["code_rows"][:4])
        print("%-4s %-28s %-24s -> %-14s %s" % (flag, q, model[:24], got, extra))

    # Doc tu Google Sheet: giong cau truc get_all_records
    sheet_benh = [{COL_B["id"]: "test_x", COL_B["name"]: "Benh thu", COL_B["phrases"]: "kêu ù ù; ù ù",
                   COL_B["type"]: "HARD", COL_B["link"]: "https://shopee.vn/x"}]
    sheet_ma = [{COL_M["brand"]: "Roborock", COL_M["line"]: "S7", COL_M["code"]: 5,
                 COL_M["meaning"]: "m", COL_M["issue"]: "test_x"}]
    kb2 = build_kb(sheet_benh, sheet_ma)
    r1 = diagnose("may keu u u", "Chưa rõ", kb2)
    r2 = diagnose("lỗi 5", "Roborock S7 / S8", kb2)
    extra = [
        ("normalize bo dau + d", normalize("Đổi Bánh XE") == " doi banh xe "),
        ("toi da 2 benh", all(len(diagnose(q, m, KB)["issues"]) <= 2 for q, m, _ in CASES)),
        ("moi ma trong bang tro toi benh co that", all(r["issue"] in KB["by_id"] or not r["issue"] for r in KB["codes"])),
        ("sheet moi: nhan cum tu Sep them", first(r1) == "test_x" and r1["issues"][0]["type"] == "hard"),
        ("sheet moi: ma so (kieu so) van tra duoc", first(r2) == "test_x"),
        ("link Sep dien duoc uu tien", shop_link(kb2["by_id"]["test_x"], "s7") == "https://shopee.vn/x"),
        ("link tim kiem ma hoa URL", "keyword=l%E1%BB%91p" in (shop_link(KB["by_id"]["banh_xe"], "t8") or "")),
        ("benh moi truong khong co nut mua", shop_link(KB["by_id"]["bi_ket"], "") is None),
        ("cau rong khong vo", diagnose("", "Chưa rõ", KB)["status"] == "not_found"),
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
