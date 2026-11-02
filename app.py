import datetime
import html

import streamlit as st

from bacsi_core import ASK_MORE, MODELS, VIP_LINKS, build_kb, builtin_kb, diagnose, shop_link

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
    """Moi lan bat benh ghi DUNG 1 dong vao trang dau tien (giu cot cu: Time, Model, Error, Action)."""
    ss = get_spreadsheet()
    if not ss:
        return
    try:
        ts = datetime.datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M:%S")
        ss.sheet1.append_row([ts, model, query, action, result], value_input_option="USER_ENTERED")
    except Exception as e:
        print("[BacSiRobot] Ghi log loi:", e)


# ==============================================================================
# 3. HIEN THI
# ==============================================================================
def esc(s):
    return html.escape(str(s or ""))


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
        return "Zalo Support"
    link = shop_link(item, model_kw)
    if link:
        text = "🛒 MUA GÓI BỘT (18K)" if link == VIP_LINKS["bot_canxi"] else \
            f"🛒 XEM {item['part'].split(';')[0].upper() or 'LINH KIỆN'}"
        st.link_button(text, link, type="primary", width="stretch")
        return "Shopee Buy"
    return "Self Fix"


st.markdown("""<style>.stApp {background-color:#f8f9fa;} .header-container {background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%); padding:20px; border-radius:0 0 20px 20px; color:white; text-align:center; margin-top:-50px;} .error-card {background-color:white; padding:15px; border-radius:10px; border-left:5px solid #0d47a1; margin-bottom:10px;box-shadow:0 2px 5px rgba(0,0,0,0.05);} .error-card.hard {border-left-color:#d32f2f;} .error-card .steps {font-size:14px; line-height:1.55; margin-top:6px;} .code-card {background:#fff8e1; padding:10px 14px; border-radius:8px; margin-bottom:8px; font-size:14px;} .stButton button {width:100%; border-radius:8px; font-weight:bold;} #MainMenu {visibility:hidden;} footer {visibility:hidden;} header {visibility:hidden;}</style>""", unsafe_allow_html=True)
st.markdown("""<div class="header-container"><h2>🤖 BÁC SĨ ROBOT</h2><p>TRỰC THUỘC THƯƠNG MẠI VÀ CÔNG NGHỆ MIT</p></div>""", unsafe_allow_html=True)

kb, kb_source = get_kb()

st.info("💡 **BƯỚC 1:** Chọn đời máy. Mã lỗi mỗi hãng mang nghĩa khác nhau, chọn đúng để bắt bệnh chuẩn.")
user_model = st.selectbox("Đời máy:", list(MODELS.keys()), label_visibility="collapsed")
model_kw = MODELS[user_model][2]

st.divider()
st.write("##### 🔍 BƯỚC 2: Robot bị sao? (Nhập mã lỗi hoặc hiện tượng)")

with st.form(key="search_form"):
    query = st.text_input("Nhập lỗi", placeholder="VD: không ra nước, kêu to, lỗi 1, 112...",
                          label_visibility="collapsed")
    submitted = st.form_submit_button("🔍 BẮT BỆNH NGAY", type="primary", width="stretch")

if submitted:
    if not query.strip():
        st.warning("⚠️ Bác chưa nhập lỗi kìa!")
    else:
        res = diagnose(query, user_model, kb)
        st.write("---")

        if res["status"] == "found":
            for r in res["code_rows"]:
                st.markdown(
                    f"""<div class="code-card"><b>Mã lỗi {esc(r['code'])} ({esc(r['brand'])}):</b> """
                    f"""{esc(r['meaning'])}<br><b>Xử lý nhanh:</b> {esc(r['action'])}</div>""",
                    unsafe_allow_html=True)
            actions = [show_issue(it, i, model_kw) for i, it in enumerate(res["issues"])]
            if not res["issues"]:
                st.link_button("💬 HỎI KỸ THUẬT QUA ZALO", ZALO_LINK, width="stretch")
                actions = ["Zalo Support"]
            names = [f"Mã {r['brand']} {r['code']}" for r in res["code_rows"]] + [it["name"] for it in res["issues"]]
            log_to_sheet(user_model, query, ", ".join(names), " | ".join(actions))

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
            log_to_sheet(user_model, query, f"Mã {res['code']} chưa rõ hãng", "Need Model")

        elif res["status"] == "code_unknown":
            st.warning(f"⚠️ Mã lỗi {res['code']} chưa có trong bảng tra của đời máy này. "
                       "Bác nhắn Zalo kèm mã lỗi và đời máy, em trả lời ngay.")
            st.link_button("💬 GỬI MÃ LỖI QUA ZALO", ZALO_LINK, width="stretch")
            log_to_sheet(user_model, query, f"Mã lỗi {res['code']}", "Code Unknown")

        elif res["status"] == "need_info":
            st.warning("⚠️ " + ASK_MORE)
            st.link_button("💬 GỬI VIDEO QUA ZALO", ZALO_LINK, width="stretch")
            log_to_sheet(user_model, query, "", "Need Info")

        else:
            st.warning("⚠️ Bệnh lạ quá. Chat với Zalo Hỗ Trợ Kỹ Thuật nhé!")
            st.link_button("🏠 VÀO GIAN HÀNG", VIP_LINKS["home"], width="stretch")
            log_to_sheet(user_model, query, "", "Not Found")

st.divider()
c1, c2 = st.columns(2)
with c1:
    st.link_button("💬 Zalo Hỗ Trợ Kỹ Thuật", ZALO_LINK, width="stretch")
with c2:
    st.link_button("☎️ Hotline", f"tel:{PHONE_NUMBER}", type="secondary", width="stretch")
st.write("")
note = "" if kb_source == "sheet" else " · dữ liệu dự phòng"
st.markdown(f"<div style='text-align: center; color: #888; font-size: 12px;'>© 2026 Thương Mại và Công Nghệ MIT{note}</div>",
            unsafe_allow_html=True)
