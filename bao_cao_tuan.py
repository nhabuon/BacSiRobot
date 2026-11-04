# -*- coding: utf-8 -*-
"""
BAO CAO TUAN - loc cac cau app CHUA bat duoc benh de Sep bo sung benh hoc.

Doc trang log (trang dau tien cua sheet Data_BacSiRobot), lay 7 ngay gan nhat, giu cac dong:
  - Not Found     : app khong nhan ra benh       -> them cum tu / them benh moi (Benh_Hoc)
  - Need Info     : mo ta qua mo ho, app hoi them -> cau nao thuc ra du ro thi them cum tu
  - Code Unknown  : ma loi chua co trong bang     -> them ma vao Ma_Loi
  - Khach bao sai : khach bam "Chua dung" o nut "Dung benh chua?" -> xem lai cum tu gay nham
Gop cac cau giong nhau (bo dau, chu thuong), dem so lan, roi GHI DE trang "Can_Bo_Sung".
Cot "Bay gio app tra" chay lai cau do tren du lieu benh hoc hien tai: Sep da bo sung thi thay ngay.

Chay tay:   GCP_SERVICE_ACCOUNT='<noi dung file json>' python bao_cao_tuan.py
Chi in, khong ghi sheet:  python bao_cao_tuan.py --khong-ghi
GitHub Actions chay 8h23 sang thu Hai (gio VN): .github/workflows/bao_cao_tuan.yml
"""
import datetime
import json
import os
import sys

from bacsi_core import FB_WRONG, LOG_COL, build_kb, builtin_kb, diagnose, has_accents, normalize

SHEET_NAME = "Data_BacSiRobot"
REPORT_TAB = "Can_Bo_Sung"
VN_TZ = datetime.timezone(datetime.timedelta(hours=7))
DAYS = 7

# Thu tu hien trong bao cao + viec Sep can lam
KINDS = {
    "Not Found": "Thêm cụm từ vào 'Cách khách hay nói' của bệnh đúng, hoặc thêm bệnh mới (Benh_Hoc)",
    "Need Info": "Câu đã đủ rõ thì thêm cụm từ; mơ hồ thật thì bỏ qua",
    "Code Unknown": "Thêm mã vào trang Ma_Loi (đúng hãng, đúng dòng máy)",
    "Khách báo sai": "App nhận nhầm: xem lại cụm từ nào kéo về bệnh sai",
}
HEADER = ["Loại", "Câu khách gõ", "Số lần", "Đời máy", "Lần cuối", "App trả lúc đó", "Bây giờ app trả", "Việc cần làm"]


def parse_ts(v):
    """Thoi gian trong log -> datetime (gio VN, khong mui gio). Nhan so serial cua Google Sheet
    (doc bang UNFORMATTED_VALUE) hoac chuoi nhieu kieu. Dong tieu de / rac -> None."""
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        if 20000 < v < 80000:  # ~1954..2119
            return datetime.datetime(1899, 12, 30) + datetime.timedelta(days=float(v))
        return None
    s = str(v or "").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M",
                "%m/%d/%Y %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None


def _cell(row, col):
    i = LOG_COL[col]
    v = row[i] if i < len(row) else ""
    if isinstance(v, float) and v.is_integer():
        v = int(v)  # khach go "112" -> sheet luu so 112.0
    return str(v if v is not None else "").strip()


def kind_of(row):
    if _cell(row, "feedback") == FB_WRONG:
        return "Khách báo sai"
    action = _cell(row, "action")
    return action if action in KINDS else None


def describe(res, kind="", result_then=""):
    if res["status"] == "found":
        names = ", ".join([f"Mã {r['brand']} {r['code']}" for r in res["code_rows"]] +
                          [it["name"] for it in res["issues"]])
        if kind == "Khách báo sai":
            return "Vẫn như cũ (chưa sửa)" if names == result_then else "Đã đổi: " + names
        return "✓ Đã nhận: " + names
    return {"code_multi": "Mã nhiều hãng (cần chọn đời máy)", "code_unknown": "Vẫn chưa có mã",
            "need_info": "Vẫn hỏi thêm", "not_found": "Vẫn chưa nhận ra"}.get(res["status"], res["status"])


def weekly_rows(log_rows, now, kb, days=DAYS):
    """log_rows: list cac dong (list) cua trang log. now: datetime gio VN, khong mui gio.
    Tra ve list dict da gop, sap theo loai roi so lan giam dan."""
    since = now - datetime.timedelta(days=days)
    groups = {}
    for row in log_rows:
        ts = parse_ts(row[LOG_COL["time"]] if row else None)
        if ts is None or not (since <= ts <= now):
            continue
        kind = kind_of(row)
        query = _cell(row, "query")
        if not kind or not query:
            continue
        key = (kind, normalize(query).strip())
        g = groups.setdefault(key, {"kind": kind, "query": query, "count": 0, "models": [],
                                    "last": ts, "result": "", "model_last": ""})
        g["count"] += 1
        model = _cell(row, "model")
        if model and model not in g["models"]:
            g["models"].append(model)
        if ts >= g["last"]:
            g["last"], g["model_last"], g["result"] = ts, model, _cell(row, "result")
            # hien ban co dau cho de doc; chi lay ban moi hon khi khong lam mat dau
            if has_accents(query) or not has_accents(g["query"]):
                g["query"] = query
    out = list(groups.values())
    for g in out:
        g["now"] = describe(diagnose(g["query"], g["model_last"] or "Chưa rõ", kb), g["kind"], g["result"])
    order = list(KINDS)
    out.sort(key=lambda g: (order.index(g["kind"]), -g["count"], g["query"].lower()))
    return out


def to_table(groups, now, days=DAYS):
    since = now - datetime.timedelta(days=days)
    title = (f"Tuần {since:%d/%m} – {now:%d/%m/%Y} · {len(groups)} câu cần xem · "
             f"cập nhật {now:%d/%m %H:%M} (bảng tự ghi đè mỗi thứ Hai, đừng ghi chú vào đây)")
    rows = [[title] + [""] * (len(HEADER) - 1), HEADER]
    for g in groups:
        rows.append([g["kind"], g["query"], g["count"], ", ".join(g["models"]), f"{g['last']:%d/%m %H:%M}",
                     g["result"], g["now"], KINDS[g["kind"]]])
    if not groups:
        rows.append(["", "Tuần này không có câu nào app chưa bắt được 🎉"] + [""] * (len(HEADER) - 2))
    return rows


def to_markdown(groups, now, days=DAYS):
    since = now - datetime.timedelta(days=days)
    lines = [f"## Bác Sĩ Robot – câu cần bổ sung ({since:%d/%m} – {now:%d/%m/%Y})", ""]
    counts = {k: sum(1 for g in groups if g["kind"] == k) for k in KINDS}
    lines.append(" · ".join(f"**{k}**: {v}" for k, v in counts.items()))
    lines += ["", "| Loại | Câu khách gõ | Số lần | Đời máy | Bây giờ app trả |", "|---|---|---|---|---|"]
    for g in groups:
        q = g["query"].replace("|", "\\|")
        lines.append(f"| {g['kind']} | {q} | {g['count']} | {', '.join(g['models'])} | {g['now']} |")
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------------------
# GOOGLE SHEET
# ------------------------------------------------------------------------------
def open_sheet():
    import gspread
    raw = os.environ.get("GCP_SERVICE_ACCOUNT", "").strip()
    if not raw:
        sys.exit("LOI: thieu bien moi truong GCP_SERVICE_ACCOUNT (noi dung file JSON service account).")
    client = gspread.service_account_from_dict(json.loads(raw))
    return client.open(SHEET_NAME)


def load_kb(ss):
    try:
        benh = ss.worksheet("Benh_Hoc").get_all_records()
        maloi = ss.worksheet("Ma_Loi").get_all_records(numericise_ignore=["all"])
        kb = build_kb(benh, maloi)
        if kb["issues"]:
            return kb
    except Exception as e:
        print("Doc Benh_Hoc/Ma_Loi loi, dung ban du phong:", e)
    return builtin_kb()


def write_report(ss, table):
    import gspread
    try:
        ws = ss.worksheet(REPORT_TAB)
    except gspread.exceptions.WorksheetNotFound:
        ws = ss.add_worksheet(title=REPORT_TAB, rows=max(len(table) + 20, 100), cols=len(HEADER))
    ws.clear()
    ws.update(values=table, range_name="A1")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ss = open_sheet()
    log = ss.sheet1.get_all_values(value_render_option="UNFORMATTED_VALUE",
                                   date_time_render_option="SERIAL_NUMBER")
    now = datetime.datetime.now(VN_TZ).replace(tzinfo=None)
    groups = weekly_rows(log, now, load_kb(ss))
    md = to_markdown(groups, now)
    print(md)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(md)
    if "--khong-ghi" not in argv:
        write_report(ss, to_table(groups, now))
        print(f"Da ghi {len(groups)} dong vao trang {REPORT_TAB}.")
    return groups


if __name__ == "__main__":
    main()
