import datetime
import html

import streamlit as st

from bacsi_core import (ASK_MORE, FB_OK, FB_WRONG, LOG_COL, MODELS, VIP_LINKS, build_kb, builtin_kb,
                        diagnose, log_row_number, shop_link)

# ==============================================================================
# 1. CAU HINH
# ==============================================================================
st.set_page_config(page_title="Bác Sĩ Robot - MIT Technology", page_icon="🤖",
                   layout="centered", initial_sidebar_state="collapsed")

PHONE_NUMBER = "0347653354"
ZALO_LINK = f"https://zalo.me/{PHONE_NUMBER}"
SHEET_NAME = "Data_BacSiRobot"
VN_TZ = datetime.timezone(datetime.timedelta(hours=7))  # may chu Streamlit chay gio UTC


# ==============================================================================
# 2. GOOGLE SHEET: ghi log + doc du lieu benh hoc
# ==============================================================================
@st.cache_resource(show_spinner=False)
def _open_spreadsheet():
    # Loi thi NEM ra ngoai: Streamlit khong cache loi, lan sau tu ket noi lai.
    import gspread
    client = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
    return client.open(SHEET_NAME)


def get_spreadsheet():
    try:
        return _open_spreadsheet()
    except Exception as e:
        print("[BacSiRobot] Khong mo duoc Google Sheet:", e)
        return None


@st.cache_data(ttl=600, show_spinner=False)
def _load_records():
    """Doc 2 trang Benh_Hoc + Ma_Loi. Cache 10 phut: Sep sua sheet, toi da 10 phut app doi theo."""
    ss = _open_spreadsheet()
    benh = ss.worksheet("Benh_Hoc").get_all_records()
    maloi = ss.worksheet("Ma_Loi").get_all_records(numericise_ignore=["all"])
    return benh, maloi


def get_kb():
    try:
        benh, maloi = _load_records()
        kb = build_kb(benh, maloi)
        if kb["issues"]:
            return kb, "sheet"
    except Exception as e:
        print("[BacSiRobot] Doc du lieu benh hoc loi, dung ban du phong:", e)
    return builtin_kb(), "builtin"


def log_to_sheet(model, query, result, action):
    """Moi lan bat benh ghi DUNG 1 dong vao trang dau tien (cot A-E, xem LOG_COL).
    Tra ve so dong vua ghi de gan phan hoi cua khach vao dung dong; khong ghi duoc -> None."""
    ss = get_spreadsheet()
    if not ss:
        return None
    try:
        ts = datetime.datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M:%S")
        resp = ss.sheet1.append_row([ts, model, query, action, result], value_input_option="USER_ENTERED")
        return log_row_number(resp)
    except Exception as e:
        print("[BacSiRobot] Ghi log loi:", e)
        return None


def save_feedback(row, verdict):
    """Nut "Dung benh chua?": ghi vao cot F cua CHINH dong log lan bat benh do (khong them dong moi),
    de bao cao tuan doc duoc ca cau khach go, ket qua app tra va khach bao dung/sai."""
    if not row:
        print("[BacSiRobot] Phan hoi khong gan duoc dong log:", verdict)
        return
    ss = get_spreadsheet()
    if not ss:
        return
    try:
        ss.sheet1.update_cell(row, LOG_COL["feedback"] + 1, verdict)
    except Exception as e:
        print("[BacSiRobot] Ghi phan hoi loi:", e)


# ==============================================================================
# 3. HIEN THI
# ==============================================================================
def esc(s):
    return html.escape(str(s or ""))


def issue_action(item, model_kw):
    if item["type"] == "hard":
        return "Zalo Support"
    return "Shopee Buy" if shop_link(item, model_kw) else "Self Fix"


def show_issue(item, rank, model_kw):
    hard = item["type"] == "hard"
    label = "Khả năng cao nhất" if rank == 0 else "Cũng có thể là"
    rows = []
    if item["cause"]:
        rows.append(f"<b>Vì sao:</b> {esc(item['cause'])}")
    if item["check"]:
        rows.append(f"<b>Bác tự kiểm tra:</b> {esc(item['check'])}")
    if item["fixable"]:
        rows.append(f"<b>Tự xử lý được khi:</b> {esc(item['fixable'])}")
    if item["replace"]:
        rows.append(f"<b>Phải thay / gửi sửa khi:</b> {esc(item['replace'])}")
    st.markdown(
        f"""<div class="error-card{' hard' if hard else ''}"><small>{label}</small><br>"""
        f"""<b>🚨 {esc(item['name'])}</b><div class="steps">{'<br>'.join(rows)}</div></div>""",
        unsafe_allow_html=True)
    if hard:
        st.link_button("💬 CHAT ZALO GỬI SỬA", ZALO_LINK, width="stretch")
        return
    link = shop_link(item, model_kw)
    if link:
        text = "🛒 MUA GÓI BỘT (18K)" if link == VIP_LINKS["bot_canxi"] else \
            f"🛒 XEM {item['part'].split(';')[0].upper() or 'LINH KIỆN'}"
        st.link_button(text, link, type="primary", width="stretch")


def log_fields(res, model_kw):
    """(Ket qua, Hanh dong) ghi vao log - giu dung cac nhan cu de bao cao tuan loc duoc."""
    st_ = res["status"]
    if st_ == "found":
        names = [f"Mã {r['brand']} {r['code']}" for r in res["code_rows"]] + [it["name"] for it in res["issues"]]
        actions = [issue_action(it, model_kw) for it in res["issues"]] or ["Zalo Support"]
        return ", ".join(names), " | ".join(actions)
    if st_ == "code_multi":
        return f"Mã {res['code']} chưa rõ hãng", "Need Model"
    if st_ == "code_unknown":
        return f"Mã lỗi {res['code']}", "Code Unknown"
    if st_ == "need_info":
        return "", "Need Info"
    return "", "Not Found"


def _on_feedback(verdict):
    last = st.session_state.get("last")
    if not last or last["fb"]:
        return  # moi lan bat benh chi nhan 1 phan hoi
    last["fb"] = verdict
    save_feedback(last["row"], verdict)


def show_feedback(last):
    """Nut nho duoi ket qua. Bam xong thi thay bang loi cam on, khong bat khach giai thich."""
    if last["fb"] is None:
        with st.container(horizontal=True, vertical_alignment="center", key="fb_box"):
            st.markdown("<span class='fb-q'>Đúng bệnh chưa?</span>", unsafe_allow_html=True)
            st.button("👍 Đúng", key=f"fb_ok_{last['n']}", on_click=_on_feedback, args=(FB_OK,))
            st.button("👎 Chưa đúng", key=f"fb_no_{last['n']}", on_click=_on_feedback, args=(FB_WRONG,))
    elif last["fb"] == FB_OK:
        st.caption("✅ Cảm ơn bác đã xác nhận!")
    else:
        st.caption("🙏 Cảm ơn bác, em ghi lại để bổ sung bệnh này. Bác nhắn Zalo mô tả thêm, em hỗ trợ ngay.")
        st.link_button("💬 NHẮN ZALO KỸ THUẬT", ZALO_LINK, width="stretch")


def show_result(last):
    res, model_kw = last["res"], last["model_kw"]

    if res["status"] == "found":
        for r in res["code_rows"]:
            st.markdown(
                f"""<div class="code-card"><b>Mã lỗi {esc(r['code'])} ({esc(r['brand'])}):</b> """
                f"""{esc(r['meaning'])}<br><b>Xử lý nhanh:</b> {esc(r['action'])}</div>""",
                unsafe_allow_html=True)
        for i, it in enumerate(res["issues"]):
            show_issue(it, i, model_kw)
        if not res["issues"]:
            st.link_button("💬 HỎI KỸ THUẬT QUA ZALO", ZALO_LINK, width="stretch")
        show_feedback(last)

    elif res["status"] == "code_multi":
        st.warning(f"⚠️ Mã lỗi {res['code']} mỗi hãng một nghĩa. Bác chọn đúng đời máy ở BƯỚC 1 "
                   "rồi bấm lại. Tham khảo nhanh:")
        seen = set()
        for r in res["code_rows"]:
            key = (r["brand"], r["line"], r["meaning"])
            if key in seen:
                continue
            seen.add(key)
            st.markdown(f"""<div class="code-card"><b>{esc(r['brand'])}</b> <small>({esc(r['line'])})</small>: """
                        f"""{esc(r['meaning'])}</div>""", unsafe_allow_html=True)

    elif res["status"] == "code_unknown":
        st.warning(f"⚠️ Mã lỗi {res['code']} chưa có trong bảng tra của đời máy này. "
                   "Bác nhắn Zalo kèm mã lỗi và đời máy, em trả lời ngay.")
        st.link_button("💬 GỬI MÃ LỖI QUA ZALO", ZALO_LINK, width="stretch")

    elif res["status"] == "need_info":
        st.warning("⚠️ " + ASK_MORE)
        st.link_button("💬 GỬI VIDEO QUA ZALO", ZALO_LINK, width="stretch")

    else:
        st.warning("⚠️ Bệnh lạ quá. Chat với Zalo Hỗ Trợ Kỹ Thuật nhé!")
        st.link_button("🏠 VÀO GIAN HÀNG", VIP_LINKS["home"], width="stretch")


st.markdown("""<style>.stApp {background-color:#f8f9fa;} .header-container {background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%); padding:14px 12px; border-radius:14px; color:white; text-align:center; margin-bottom:8px;} .header-container h2 {color:white; font-size:clamp(24px, 7.5vw, 32px); margin:0; padding:0;} .header-container p {font-size:12px; margin:4px 0 0; opacity:.9;} [data-testid="stMainBlockContainer"] {padding-top:1rem; padding-bottom:2rem;} @media (max-width:640px) {[data-testid="stMainBlockContainer"] {padding-left:.75rem; padding-right:.75rem;}} [data-testid="stWidgetLabel"] p {font-size:15px; font-weight:700; color:#0d47a1;} .stTextInput input, .stSelectbox input, .stSelectbox [data-baseweb="select"] div {font-size:16px !important;} .error-card {background-color:white; padding:15px; border-radius:10px; border-left:5px solid #0d47a1; margin-bottom:10px;box-shadow:0 2px 5px rgba(0,0,0,0.05);} .error-card.hard {border-left-color:#d32f2f;} .error-card .steps {font-size:14px; line-height:1.55; margin-top:6px;} .code-card {background:#fff8e1; padding:10px 14px; border-radius:8px; margin-bottom:8px; font-size:14px;} .stButton button {width:100%; border-radius:8px; font-weight:bold;} .st-key-fb_box {margin-top:4px;} .st-key-fb_box .stButton button {width:auto; font-weight:normal; font-size:14px; min-height:38px; padding:4px 14px;} .fb-q {font-size:13px; color:#555;} #MainMenu {visibility:hidden;} footer {visibility:hidden;} header {visibility:hidden;}</style>""", unsafe_allow_html=True)
st.markdown("""<div class="header-container"><h2>🤖 BÁC SĨ ROBOT</h2><p>TRỰC THUỘC THƯƠNG MẠI VÀ CÔNG NGHỆ MIT</p></div>""", unsafe_allow_html=True)

kb, kb_source = get_kb()

user_model = st.selectbox("BƯỚC 1: Chọn đời máy", list(MODELS.keys()),
                          help="Mã lỗi mỗi hãng mang nghĩa khác nhau, chọn đúng để bắt bệnh chuẩn.")
model_kw = MODELS[user_model][2]

with st.form(key="search_form", border=False):
    query = st.text_input("BƯỚC 2: Robot bị sao?", placeholder="VD: không ra nước, kêu to, lỗi 1, 112...")
    submitted = st.form_submit_button("🔍 BẮT BỆNH NGAY", type="primary", width="stretch")

# Ket qua giu trong session_state: bam nut "Dung benh chua?" lam app chay lai,
# neu chi ve ket qua khi vua bam BAT BENH thi ket qua se bien mat.
if submitted:
    if not query.strip():
        st.session_state.pop("last", None)
        st.warning("⚠️ Bác chưa nhập lỗi kìa!")
    else:
        res = diagnose(query, user_model, kb)
        result_text, action = log_fields(res, model_kw)
        row = log_to_sheet(user_model, query, result_text, action)
        n = st.session_state.get("last", {}).get("n", 0) + 1
        st.session_state["last"] = {"res": res, "model_kw": model_kw, "row": row, "n": n, "fb": None}

if st.session_state.get("last"):
    with st.container(key="ket_qua"):
        show_result(st.session_state["last"])
    if submitted:
        # Dien thoai: ket qua nam duoi man hinh, khach bam xong khong thay gi -> cuon toi ket qua.
        # So lan tim (n) nam trong noi dung de lan tim sau doan script chay lai.
        st.html("<script>/* lan %d */ setTimeout(function () {"
                " var el = document.querySelector('.st-key-ket_qua');"
                " if (el) el.scrollIntoView({behavior: 'smooth', block: 'start'}); }, 150);</script>"
                % st.session_state["last"]["n"], unsafe_allow_javascript=True)

st.divider()
c1, c2 = st.columns(2)
with c1:
    st.link_button("💬 Zalo Hỗ Trợ Kỹ Thuật", ZALO_LINK, width="stretch")
with c2:
    st.link_button(f"☎️ Hotline {PHONE_NUMBER[:4]} {PHONE_NUMBER[4:7]} {PHONE_NUMBER[7:]}", f"tel:{PHONE_NUMBER}", type="secondary", width="stretch")
st.write("")
note = "" if kb_source == "sheet" else " · dữ liệu dự phòng"
st.markdown(f"<div style='text-align: center; color: #888; font-size: 12px;'>© 2026 Thương Mại và Công Nghệ MIT{note}</div>",
            unsafe_allow_html=True)
