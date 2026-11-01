# -*- coding: utf-8 -*-
"""
BAC SI ROBOT - LOI CHAN DOAN (khong phu thuoc Streamlit, test duoc doc lap)

Thay doi so voi ban cu (Giai doan 1):
- Chuan hoa bo dau tieng Viet: khach go "khong ra nuoc" van nhan dung.
- So khop theo NGUYEN TU / CUM TU, khong so chuoi con
  (sua loi "kho" nam trong "khong" -> moi cau co chu "khong" bi chan la Tac Nuoc).
- Cham diem, chi hien 1-2 benh khop nhat thay vi liet ke tat ca.
- Ma loi khop chinh xac ("loi 1" khong con khop "loi 10").
- Mo ta mo ho ("khong chay", "den nhay do") -> hoi them du kien, khong doan mo.
"""
import re
import unicodedata
import urllib.parse

SHOP_ID = "68690982"

VIP_LINKS = {
    "bot_canxi": "https://shopee.vn/product/%s/42427536678" % SHOP_ID,
    "home": "https://shopee.vn/alexaecho",
}

# Doi may -> tu khoa ghep vao link tim kiem
MODEL_KEYWORDS = {
    "Chưa rõ": "",
    "Deebot T5 / DX96": "t5",
    "Deebot T8 AIVI / Max": "t8",
    "Deebot T9": "t9",
    "Deebot X1 Omni / Turbo": "x1",
    "Dreame L10 / W10": "dreame l10",
    "Roborock S7 / S8": "roborock s7",
}


def normalize(text):
    """Chu thuong, bo dau, d->d, chi giu chu va so, cach nhau 1 dau cach."""
    s = (text or "").replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " " + s.strip() + " "


# ------------------------------------------------------------------------------
# DU LIEU BENH HOC
# phrases: {cum tu khong dau: diem}. So khop theo nguyen tu.
# type: easy = khach tu xu ly / mua linh kien; hard = gui Zalo sua.
# Thu tu trong danh sach = thu tu uu tien khi bang diem (benh de kiem tra truoc).
# ------------------------------------------------------------------------------
DB_ISSUES = [
    {
        "id": "tac_nuoc", "name": "Lỗi Tắc Nước",
        "fix": "Cặn canxi bít vòi bơm hoặc lỗ ra nước ở khay lau. Dùng bột thông tắc 18k.",
        "type": "easy", "part_key": "bot_canxi", "keyword": "bột tẩy cặn robot",
        "phrases": {"khong ra nuoc": 3, "ra nuoc yeu": 3, "it nuoc": 2, "tac nuoc": 3,
                    "nuoc khong xuong": 3, "khong bom": 3, "bom nuoc": 2, "lau kho": 3,
                    "gie kho": 3, "khan kho": 3, "tac voi": 2, "can canxi": 3, "canxi": 2,
                    "khong nha nuoc": 3, "khong thoat nuoc": 1},
    },
    {
        "id": "pin", "name": "Lỗi Pin / Nguồn",
        "fix": "Pin chai hoặc chân sạc bẩn, ôxy hóa. Lau chân sạc trước; vẫn sập nguồn thì thay pin.",
        "type": "easy", "part_key": "pin", "keyword": "pin robot hút bụi",
        "phrases": {"không sạc": 3, "sạc không vào": 3, "không vào sạc": 3, "không nhận sạc": 3,
                    "het pin": 3, "chai pin": 3, "pin": 2, "sạc": 1, "tu tat": 2, "tat may": 2,
                    "sap nguon": 3, "khong len nguon": 3, "mat nguon": 3, "về sạc": 1},
    },
    {
        "id": "banh_xe", "name": "Lỗi Bánh Xe / Lốp",
        "fix": "Lốp cao su mòn nên bánh trượt, máy chạy lệch. Thay cặp lốp mới.",
        "type": "easy", "part_key": "banhxe", "keyword": "lốp bánh xe robot",
        "phrases": {"banh xe": 3, "lốp": 3, "mòn lốp": 3, "chay lech": 3, "lech": 1,
                    "vong tron": 2, "quay vong": 2, "quay tron": 2, "truot": 2,
                    "ket banh": 3, "khong leo": 2},
    },
    {
        "id": "choi", "name": "Chổi Chính Quấn Tóc / Mòn",
        "fix": "Tóc quấn đầu trục chổi làm kẹt, máy kêu rít. Gỡ tóc; viền cao su rách thì thay chổi.",
        "type": "easy", "part_key": "choi", "keyword": "chổi chính robot",
        "phrases": {"chổi": 2, "chổi chính": 3, "tóc": 2, "quấn tóc": 3, "keu rit": 3, "rit": 2,
                    "chổi không quay": 3, "keu to": 2},
    },
    {
        "id": "loc", "name": "Lỗi Màng Lọc",
        "fix": "Màng lọc HEPA bẩn hoặc rách làm lực hút giảm. Đập sạch; rách thì thay mới.",
        "type": "easy", "part_key": "hepa", "keyword": "lọc hepa",
        "phrases": {"loc": 2, "hepa": 3, "hut yeu": 3, "hut bui yeu": 3, "luc hut yeu": 3,
                    "hut kem": 3, "bui bay": 2, "khong hut bui": 2},
    },
    {
        "id": "tram_rac", "name": "Trạm Không Hút Rác",
        "fix": "Nghẹt ống dẫn rác trong trạm hoặc túi bụi đầy, mủn. Thông ống, thay túi bụi.",
        "type": "easy", "part_key": "tui_bui", "keyword": "túi bụi robot",
        "phrases": {"tram khong hut rac": 4, "khong hut rac": 3, "nghet tram": 3, "tui rac": 2,
                    "tui bui": 2, "do rac": 2, "trạm": 1, "dock": 1},
    },
    {
        "id": "hoi_gie", "name": "Giẻ Lau Bị Hôi",
        "fix": "Vi khuẩn sinh sôi ở giẻ ẩm không được sấy kiệt. Giặt, phơi khô; giẻ cũ đã ám mùi thì thay.",
        "type": "easy", "part_key": "gie_lau", "keyword": "giẻ lau robot",
        "phrases": {"hôi": 3, "mùi hôi": 3, "bốc mùi": 3, "hôi giẻ": 3, "giẻ hôi": 3, "mốc": 2},
    },
    {
        "id": "hop_so", "name": "Lỗi Hộp Số (Nghiêm trọng)",
        "fix": "Vỡ bánh răng hộp số. Cần tháo máy gửi sửa.",
        "type": "hard", "part_key": "zalo_repair", "keyword": "",
        "phrases": {"hop so": 3, "lach cach": 3, "cach cach": 2, "banh rang": 3, "keu to": 2,
                    "tieng on": 2, "on qua": 2},
    },
    {
        "id": "lds", "name": "Lỗi LDS (Laser)",
        "fix": "Mắt laser kẹt hoặc đứt dây curoa, máy mất định vị. Cần gửi shop kiểm tra.",
        "type": "hard", "part_key": "zalo_repair", "keyword": "",
        "phrases": {"lds": 3, "laser": 3, "mat laser": 3, "mu duong": 3, "mat ban do": 2,
                    "khong nhan ban do": 2, "di lung tung": 2},
        "codes": {"1"},
    },
    {
        "id": "quat", "name": "Lỗi Quạt Hút",
        "fix": "Mô tơ quạt hút yếu hoặc chết. Kiểm tra màng lọc trước; lọc sạch mà vẫn không hút thì cần thợ.",
        "type": "hard", "part_key": "zalo_repair", "keyword": "",
        "phrases": {"quat": 3, "quat hut": 3, "mo to hut": 3, "khong hut": 2},
    },
]

# Mo ta chung chung -> phai hoi them (Ranh gioi "Cam doan mo")
VAGUE_PHRASES = ["khong chay", "hong", "loi", "den nhay", "den do", "nhay do",
                 "khong hoat dong", "bao loi", "dung lai", "khong bat", "khong len"]

ASK_MORE = ("Mô tả chưa đủ để bắt bệnh. Bác cho em thêm: máy báo lỗi số mấy hoặc đọc câu gì, "
            "đèn nháy màu gì, hỏng lúc nào (khi hút, khi lau, khi về sạc). "
            "Quay video lật gầm máy gửi Zalo là nhanh nhất.")

CODE_RE = re.compile(r" (?:loi|error|err|ma loi|ma|code|e) ?(\d{1,3}) ")


def extract_code(norm):
    m = CODE_RE.search(norm)
    return m.group(1) if m else None


def lower_keep_accents(text):
    """Chu thuong, GIU dau, chi giu chu va so."""
    s = unicodedata.normalize("NFC", (text or "").lower())
    return " " + re.sub(r"[\W_]+", " ", s).strip() + " "


def has_accents(text):
    return normalize(text).strip() != lower_keep_accents(text).strip()


def phrase_in(phrase, query, norm, accented):
    """Cum tu viet KHONG dau: so tren ban bo dau.
    Cum tu viet CO dau (tu de nham: hoi/hôi, toc/tốc, lop/lớp, sac/sắc...):
    khach go co dau thi phai khop dung dau; khach go khong dau thi so ban bo dau."""
    if not any(ord(c) > 127 for c in phrase):
        return (" " + phrase + " ") in norm
    if accented is not None:
        return (" " + unicodedata.normalize("NFC", phrase) + " ") in accented
    return normalize(phrase) in norm


def score_issue(issue, query, norm=None, accented=None):
    norm = norm if norm is not None else normalize(query)
    s = 0
    for phrase, w in issue["phrases"].items():
        if phrase_in(phrase, query, norm, accented):
            s += w
    return s


def diagnose(query, max_results=2, ratio=0.75):
    """
    Tra ve dict:
      status: "found" | "code_unknown" | "need_info" | "not_found"
      issues: danh sach benh (toi da max_results), da sap xep
      code:   ma loi neu co
    """
    norm = normalize(query)
    code = extract_code(norm)

    if code:
        by_code = [i for i in DB_ISSUES if code in i.get("codes", set())]
        if by_code:
            return {"status": "found", "issues": by_code[:max_results], "code": code}

    accented = lower_keep_accents(query) if has_accents(query) else None
    scored = [(score_issue(i, query, norm, accented), idx, i) for idx, i in enumerate(DB_ISSUES)]
    scored = [x for x in scored if x[0] > 0]
    if scored:
        scored.sort(key=lambda x: (-x[0], x[1]))
        top = scored[0][0]
        picked = [i for s, _, i in scored if s >= top * ratio][:max_results]
        return {"status": "found", "issues": picked, "code": code}

    if code:
        return {"status": "code_unknown", "issues": [], "code": code}
    if any((" " + p + " ") in norm for p in VAGUE_PHRASES):
        return {"status": "need_info", "issues": [], "code": None}
    return {"status": "not_found", "issues": [], "code": None}


def shop_link(part_key, model_keyword, default_keyword):
    if part_key in VIP_LINKS:
        return VIP_LINKS[part_key]
    keyword = ("%s %s" % (default_keyword, model_keyword)).strip()
    return "https://shopee.vn/search?" + urllib.parse.urlencode(
        {"keyword": keyword, "shop": SHOP_ID})
