# -*- coding: utf-8 -*-
"""Bo test bat benh V2. Chay: python test_bacsi.py  (phai PASS het truoc khi day len GitHub)"""
from bacsi_core import builtin_kb, build_kb, diagnose, normalize, shop_link, COL_B, COL_M
from bacsi_core import FB_WRONG, log_row_number
import datetime
import bao_cao_tuan as bct

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


def weekly_checks():
    """Nut "Dung benh chua?" + bao cao tuan. Ky vong suy ra tu chinh du lieu (L10)."""
    now = datetime.datetime(2026, 11, 9, 8, 23)
    serial = lambda d: (d - datetime.datetime(1899, 12, 30)).total_seconds() / 86400
    d1 = serial(datetime.datetime(2026, 11, 5, 10, 0))
    log = [
        ["Time", "Model", "Error", "Action", "Result", "Feedback"],         # dong tieu de -> bo
        [d1, "Chưa rõ", "nước lau sàn nhiều bọt", "Not Found", ""],         # dong cu chi co 5 cot
        [d1 + 1, "Dreame D9", "Nuoc lau san nhieu bot", "Not Found", ""],   # cung cau, khong dau -> gop
        [d1, "Chưa rõ", "đèn nháy đỏ", "Need Info", "", ""],
        [d1, "Roborock S7 / S8", 999.0, "Code Unknown", "Mã lỗi 999", ""],  # sheet luu so 999.0
        [d1, "Chưa rõ", "kêu to", "Self Fix", "Chổi chính", FB_WRONG],
        [d1, "Chưa rõ", "khong sac duoc", "Shopee Buy", "Pin", "Đúng"],     # khach bao dung -> bo
        [d1 - 9, "Chưa rõ", "robot chưa chạy", "Not Found", ""],            # qua 7 ngay -> bo
        ["2026-11-08 09:00:00", "Chưa rõ", "lớp sơn bị xước", "Not Found", ""],  # thoi gian dang chuoi
        [],
    ]
    g = bct.weekly_rows(log, now, KB)
    by = {(x["kind"], normalize(x["query"]).strip()): x for x in g}
    bot = by.get(("Not Found", "nuoc lau san nhieu bot"))
    table = bct.to_table(g, now)
    return [
        ("log: doc so dong tu append_row", log_row_number({"updates": {"updatedRange": "'Trang tính1'!A12:E12"}}) == 12),
        ("log: append_row la/None khong vo", log_row_number(None) is None and log_row_number({}) is None),
        ("tuan: serial va chuoi deu doc duoc", bct.parse_ts(d1) == datetime.datetime(2026, 11, 5, 10, 0)
         and bct.parse_ts("08/11/2026 09:00:00") == datetime.datetime(2026, 11, 8, 9, 0)),
        ("tuan: tieu de/rac bo qua", bct.parse_ts("Time") is None and bct.parse_ts(True) is None),
        ("tuan: gop cau co dau/khong dau", bot is not None and bot["count"] == 2
         and bot["models"] == ["Chưa rõ", "Dreame D9"]),
        ("tuan: du 4 loai, bo dong 'Dung' va dong cu", sorted(k for k, _ in by) ==
         sorted(["Not Found", "Not Found", "Need Info", "Code Unknown", "Khách báo sai"])),
        ("tuan: ma so 999.0 -> '999'", ("Code Unknown", "999") in by),
        ("tuan: Not Found dung dau, so lan giam dan", g[0] is bot and [x["kind"] for x in g] ==
         sorted([x["kind"] for x in g], key=list(bct.KINDS).index)),
        ("tuan: cot 'bay gio app tra' chay lai chan doan", by[("Khách báo sai", "keu to")]["now"].startswith("Đã đổi")
         and bot["now"] == "Vẫn chưa nhận ra"
         and by[("Not Found", "lop son bi xuoc")]["now"] == "Vẫn chưa nhận ra"),
        ("tuan: bao sai ma app van tra y cu -> 'Vẫn như cũ'", bct.describe(diagnose("kêu to", "Chưa rõ", KB), "Khách báo sai",
         ", ".join(i["name"] for i in diagnose("kêu to", "Chưa rõ", KB)["issues"])) == "Vẫn như cũ (chưa sửa)"),
        ("tuan: hien ban co dau", bot["query"] == "nước lau sàn nhiều bọt"),
        ("tuan: bang = tieu de + header + so nhom", len(table) == 2 + len(g) and table[1] == bct.HEADER),
        ("tuan: tuan trong van co dong bao", len(bct.to_table([], now)) == 3),
    ]


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
    ] + weekly_checks()
    for name, cond in extra:
        print("%-4s %s" % ("PASS" if cond else "FAIL", name))
        ok += bool(cond)
    total = len(CASES) + len(extra)
    print("\nTONG: %d/%d PASS" % (ok, total))
    return ok == total


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
