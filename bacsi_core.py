# -*- coding: utf-8 -*-
"""
BAC SI ROBOT - LOI CHAN DOAN V2 (Giai doan 2)

- Du lieu benh hoc doc tu 2 trang Google Sheet: Benh_Hoc va Ma_Loi.
  Sep sua sheet la app doi theo, khong can sua code. Neu khong doc duoc sheet,
  app dung ban du phong dong goi san (kb_data.py).
- Ma loi tra THEO HANG va DONG MAY: "loi 1" la thap laser tren Roborock,
  la can va tren Mi Robot Vacuum-Mop, la banh trai tren ban Essential.
- Chua ro hang ma khach go ma loi -> liet ke nghia cua ma do o tung hang
  va moi khach chon doi may.
- Giu tu Giai doan 1: bo dau, so khop nguyen tu, tu de nham (hoi/hôi...),
  cham diem, toi da 2 benh, mo ta mo ho thi hoi them.
"""
import re
import unicodedata
import urllib.parse

SHOP_ID = "68690982"
VIP_LINKS = {
    "bot_canxi": "https://shopee.vn/product/%s/42427536678" % SHOP_ID,
    "home": "https://shopee.vn/alexaecho",
}

# Doi may tren giao dien -> (hang, goi y dong may trong cot "Dong may ap dung", tu khoa Shopee)
MODELS = {
    "Chưa rõ": (None, None, ""),
    "Ecovacs Deebot T5 / DX96": ("Ecovacs", None, "t5"),
    "Ecovacs Deebot T8 AIVI / Max": ("Ecovacs", None, "t8"),
    "Ecovacs Deebot T9": ("Ecovacs", None, "t9"),
    "Ecovacs Deebot T80 / T80S Omni": ("Ecovacs", None, "t80"),
    "Ecovacs Deebot X1 Omni / Turbo": ("Ecovacs", None, "x1"),
    "Ecovacs đời khác": ("Ecovacs", None, "ecovacs"),
    "Roborock S5 / S6": ("Roborock", "S5", "roborock s5"),
    "Roborock S7 / S8": ("Roborock", "S7", "roborock s7"),
    "Roborock Q7": ("Roborock", "Q7", "roborock q7"),
    "Roborock đời khác": ("Roborock", None, "roborock"),
    "Xiaomi Mi Robot Vacuum đời đầu (Roborock sản xuất)": ("Roborock", "S5", "xiaomi robot vacuum"),
    "Xiaomi Mi Robot Vacuum-Mop": ("Xiaomi", "bản thường", "xiaomi vacuum mop"),
    "Xiaomi Mi Robot Vacuum-Mop Essential": ("Xiaomi", "Essential", "xiaomi essential"),
    "Dreame L10 / W10": ("Dreame", None, "dreame l10"),
    "Dreame D9": ("Dreame", None, "dreame d9"),
    "Dreame đời khác": ("Dreame", None, "dreame"),
}

# Ten cot trong Google Sheet (phai trung voi file Data_BacSiRobot)
COL_B = {"id": "ID", "name": "Tên bệnh", "phrases": "Cách khách hay nói (ngăn bằng ;)",
         "cause": "Điểm nghẽn vật lý", "check": "Bước khách tự kiểm", "fixable": "Sửa được khi",
         "replace": "Phải thay / gửi sửa khi", "type": "Loại (easy/hard)",
         "part": "Phụ kiện MIVAC gợi ý", "keyword": "Từ khóa tìm Shopee",
         "link": "Link Shopee riêng (Sếp điền)"}
COL_M = {"brand": "Hãng", "line": "Dòng máy áp dụng", "code": "Mã", "msg": "Thông điệp gốc (tiếng Anh)",
         "meaning": "Ý nghĩa", "action": "Cách xử lý", "issue": "ID bệnh (khớp Benh_Hoc)"}

# Trang log (trang dau tien cua sheet): moi lan bat benh = 1 dong.
# A Thoi gian | B Doi may | C Cau khach go | D Hanh dong | E Ket qua | F Khach bao (nut "Dung benh chua?")
LOG_COL = {"time": 0, "model": 1, "query": 2, "action": 3, "result": 4, "feedback": 5}
FB_OK, FB_WRONG = "Đúng", "Chưa đúng"


def log_row_number(append_response):
    """So dong vua ghi, doc tu ket qua append_row cua gspread
    ({'updates': {'updatedRange': "'Trang 1'!A12:E12"}}) -> 12. Khong doc duoc -> None."""
    try:
        rng = append_response["updates"]["updatedRange"]
    except (KeyError, TypeError):
        return None
    m = re.search(r"![A-Z]+(\d+)", str(rng))
    return int(m.group(1)) if m else None


# ------------------------------------------------------------------------------
# CHUAN HOA CHU
# ------------------------------------------------------------------------------
def normalize(text):
    """Chu thuong, bo dau, đ->d, chi giu chu va so."""
    s = (text or "").replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return " " + re.sub(r"[^a-z0-9]+", " ", s).strip() + " "


def lower_keep_accents(text):
    s = unicodedata.normalize("NFC", (text or "").lower())
    return " " + re.sub(r"[\W_]+", " ", s).strip() + " "


def has_accents(text):
    return normalize(text).strip() != lower_keep_accents(text).strip()


# ------------------------------------------------------------------------------
# NAP DU LIEU
# ------------------------------------------------------------------------------
def _clean_code(c):
    c = str(c or "").strip()
    if c in ("", "—", "-"):
        return ""
    return c.lstrip("0") or "0"


def build_kb(benh_records, maloi_records):
    """benh_records / maloi_records: list dict (nhu gspread get_all_records)."""
    issues = []
    for r in benh_records:
        iid = str(r.get(COL_B["id"], "")).strip()
        if not iid:
            continue
        phrases = {}
        for p in str(r.get(COL_B["phrases"], "")).split(";"):
            p = p.strip().lower()
            if p:
                # cum cang dai cang cu the: 1 tu = 2 diem, 2 tu = 3, tu 3 tu = 4
                phrases[p] = min(len(p.split()), 3) + 1
        issues.append({
            "id": iid, "name": str(r.get(COL_B["name"], iid)).strip(),
            "cause": str(r.get(COL_B["cause"], "")).strip(),
            "check": str(r.get(COL_B["check"], "")).strip(),
            "fixable": str(r.get(COL_B["fixable"], "")).strip(),
            "replace": str(r.get(COL_B["replace"], "")).strip(),
            "type": "hard" if str(r.get(COL_B["type"], "")).strip().lower() == "hard" else "easy",
            "part": str(r.get(COL_B["part"], "")).strip(),
            "keyword": str(r.get(COL_B["keyword"], "")).strip(),
            "link": str(r.get(COL_B["link"], "")).strip(),
            "phrases": phrases,
        })
    by_id = {i["id"]: i for i in issues}
    codes, named = [], []
    for r in maloi_records:
        row = {k: str(r.get(v, "")).strip() for k, v in COL_M.items()}
        row["code_n"] = _clean_code(row["code"])
        if row["issue"] and row["issue"] in by_id and row["msg"] and not row["code_n"]:
            # thong bao bang ten (Dreame): khach go nguyen cau tieng Anh cung nhan ra
            by_id[row["issue"]]["phrases"].setdefault(row["msg"].lower(), 4)
        if row["code_n"]:
            codes.append(row)
        else:
            named.append(row)
    return {"issues": issues, "by_id": by_id, "codes": codes, "named": named}


def builtin_kb():
    from kb_data import BENH, MA_LOI
    keys = ["id", "nhom", "name", "phrases", "cause", "check", "fixable", "replace", "type",
            "part", "keyword", "_ma", "_src", "_tc"]
    benh = []
    for b in BENH:
        d = dict(zip(keys, b))
        benh.append({COL_B["id"]: d["id"], COL_B["name"]: d["name"], COL_B["phrases"]: d["phrases"],
                     COL_B["cause"]: d["cause"], COL_B["check"]: d["check"],
                     COL_B["fixable"]: d["fixable"], COL_B["replace"]: d["replace"],
                     COL_B["type"]: d["type"], COL_B["part"]: d["part"],
                     COL_B["keyword"]: d["keyword"], COL_B["link"]: ""})
    maloi = [{COL_M["brand"]: m[0], COL_M["line"]: m[1], COL_M["code"]: m[2], COL_M["msg"]: m[3],
              COL_M["meaning"]: m[4], COL_M["action"]: m[5], COL_M["issue"]: m[6]} for m in MA_LOI]
    return build_kb(benh, maloi)


# ------------------------------------------------------------------------------
# CHAN DOAN
# ------------------------------------------------------------------------------
VAGUE_PHRASES = ["khong chay", "hong", "loi", "den nhay", "den do", "nhay do", "khong hoat dong",
                 "bao loi", "dung lai", "khong bat", "khong len"]

ASK_MORE = ("Mô tả chưa đủ để bắt bệnh. Bác cho em thêm: máy báo lỗi số mấy hoặc đọc câu gì, "
            "đèn nháy màu gì, hỏng lúc nào (khi hút, khi lau, khi về sạc). "
            "Quay video lật gầm máy gửi Zalo là nhanh nhất.")

CODE_RE = re.compile(r" (?:loi|error|err|ma loi|ma|code|e) ?(\d{1,4}) ")


def extract_code(norm):
    m = CODE_RE.search(norm)
    if m:
        return _clean_code(m.group(1))
    if re.fullmatch(r" \d{1,4} ", norm):
        return _clean_code(norm.strip())
    return None


def phrase_in(phrase, norm, accented):
    """Cum tu khong dau: so ban bo dau. Cum tu co dau, 1 tu (de nham: hôi/hơi, tóc/tốc):
    khach go co dau thi phai dung dau. Cum tu co dau nhieu tu: chap nhan ca hai."""
    if not any(ord(c) > 127 for c in phrase):
        return (" " + phrase + " ") in norm
    if accented is not None and (" " + unicodedata.normalize("NFC", phrase) + " ") in accented:
        return True
    if accented is not None and len(phrase.split()) < 2:
        return False
    return normalize(phrase) in norm


def lookup_code(kb, code, brand, line_hint):
    rows = [r for r in kb["codes"] if r["code_n"] == code and r["brand"] == brand]
    if line_hint:
        hinted = [r for r in rows if line_hint.lower() in r["line"].lower()]
        if hinted:
            return hinted
    return rows


def diagnose(query, model="Chưa rõ", kb=None, max_results=2, ratio=0.75):
    """
    status:
      found        -> issues (toi da 2), code_rows (neu khop ma loi)
      code_multi   -> chua ro hang; code_rows = nghia cua ma o cac hang
      code_unknown -> ma khong co trong bang cua hang nay
      need_info    -> mo ta mo ho, hoi them
      not_found
    """
    kb = kb or builtin_kb()
    brand, line_hint, _ = MODELS.get(model, (None, None, ""))
    norm = normalize(query)
    code = extract_code(norm)
    res = {"status": "not_found", "issues": [], "code": code, "code_rows": [], "brand": brand}

    if code:
        if brand:
            rows = lookup_code(kb, code, brand, line_hint)
            if rows:
                res["code_rows"] = rows[:1]
                iid = rows[0]["issue"]
                if iid in kb["by_id"]:
                    res["issues"] = [kb["by_id"][iid]]
                res["status"] = "found"
                return res
        else:
            rows = [r for r in kb["codes"] if r["code_n"] == code]
            if rows:
                res["status"], res["code_rows"] = "code_multi", rows
                return res

    accented = lower_keep_accents(query) if has_accents(query) else None
    scored = []
    for idx, it in enumerate(kb["issues"]):
        s = sum(w for p, w in it["phrases"].items() if phrase_in(p, norm, accented))
        if s:
            scored.append((s, idx, it))
    if scored:
        scored.sort(key=lambda x: (-x[0], x[1]))
        top = scored[0][0]
        res["status"] = "found"
        res["issues"] = [it for s, _, it in scored if s >= top * ratio][:max_results]
        return res

    if code:
        res["status"] = "code_unknown"
        return res
    if any((" " + p + " ") in norm for p in VAGUE_PHRASES):
        res["status"] = "need_info"
    return res


def shop_link(issue, model_keyword):
    """Uu tien link Sep dien trong sheet; khong co thi tim theo tu khoa + doi may."""
    if issue.get("link"):
        return issue["link"]
    if issue.get("keyword") == "bột tẩy cặn robot":
        return VIP_LINKS["bot_canxi"]
    if not issue.get("keyword"):
        return None
    keyword = ("%s %s" % (issue["keyword"], model_keyword)).strip()
    return "https://shopee.vn/search?" + urllib.parse.urlencode({"keyword": keyword, "shop": SHOP_ID})
