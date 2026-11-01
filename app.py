import datetime

import streamlit as st

from bacsi_core import ASK_MORE, MODEL_KEYWORDS, VIP_LINKS, diagnose, shop_link

# ==============================================================================
# 1. CAU HINH
# ==============================================================================
st.set_page_config(page_title="Bác Sĩ Robot - MIT Technology", page_icon="🤖",
                   layout="centered", initial_sidebar_state="collapsed")

PHONE_NUMBER = "0347653354"
ZALO_LINK = f"https://zalo.me/{PHONE_NUMBER}"
VN_TZ = datetime.timezone(datetime.timedelta(hours=7))  # may chu Streamlit chay gio UTC


# ==============================================================================
# 2. GOOGLE SHEET (ghi log)
# ==============================================================================
@st.cache_resource(show_spinner=False)
def _open_sheet():
    # Neu loi thi NEM loi ra ngoai: Streamlit KHONG cache ket qua loi,
    # lan sau se thu ket noi lai (ban cu cache luon None -> mat log am tham).
    import gspread
    client = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
    return client.open("Data_BacSiRobot").sheet1


def get_sheet():
    try:
        return _open_sheet()
    except Exception as e:
        print("[BacSiRobot] Khong mo duoc Google Sheet:", e)
        return None


def log_to_sheet(model, query, result_names, action):
    """Moi lan bat benh ghi DUNG 1 dong."""
    sheet = get_sheet()
    if not sheet:
        return
    try:
        ts = datetime.datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([ts, model, query, action, result_names], value_input_option="USER_ENTERED")
    except Exception as e:
        print("[BacSiRobot] Ghi log loi:", e)


# ==============================================================================
# 3. GIAO DIEN
# ==============================================================================
st.markdown("""<style>.stApp {background-color:#f8f9fa;} .header-container {background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%); padding:20px; border-radius:0 0 20px 20px; color:white; text-align:center; margin-top:-50px;} .error-card {background-color:white; padding:15px; border-radius:10px; border-left:5px solid #0d47a1; margin-bottom:10px;box-shadow:0 2px 5px rgba(0,0,0,0.05);} .error-card.hard {border-left-color:#d32f2f;} .stButton button {width:100%; border-radius:8px; font-weight:bold;} #MainMenu {visibility:hidden;} footer {visibility:hidden;} header {visibility:hidden;}</style>""", unsafe_allow_html=True)
st.markdown("""<div class="header-container"><h2>🤖 BÁC SĨ ROBOT</h2><p>TRỰC THUỘC THƯƠNG MẠI VÀ CÔNG NGHỆ MIT</p></div>""", unsafe_allow_html=True)

st.info("💡 **BƯỚC 1:** Chọn đời máy để bắt bệnh chuẩn nhất!")
user_model = st.selectbox("Đời máy:", list(MODEL_KEYWORDS.keys()), label_visibility="collapsed")
model_kw = MODEL_KEYWORDS.get(user_model, "")

st.divider()
st.write("##### 🔍 BƯỚC 2: Robot bị sao? (Nhập mã lỗi hoặc hiện tượng)")

with st.form(key="search_form"):
    query = st.text_input("Nhập lỗi", placeholder="VD: không ra nước, kêu to, lỗi 1...",
                          label_visibility="collapsed")
    submitted = st.form_submit_button("🔍 BẮT BỆNH NGAY", type="primary", use_container_width=True)

if submitted:
    if not query.strip():
        st.warning("⚠️ Bác chưa nhập lỗi kìa!")
    else:
        res = diagnose(query)
        st.write("---")

        if res["status"] == "found":
            actions = []
            for i, item in enumerate(res["issues"]):
                hard = item["type"] == "hard"
                label = "Khả năng cao nhất" if i == 0 else "Cũng có thể là"
                st.markdown(
                    f"""<div class="error-card{' hard' if hard else ''}"><small>{label}</small><br>"""
                    f"""<b>🚨 {item['name']}</b><br><small>Nguyên nhân: """
                    f"""<span style="color:#2e7d32;font-weight:bold">{item['fix']}</span></small></div>""",
                    unsafe_allow_html=True)
                if hard:
                    st.link_button("💬 CHAT ZALO GỬI SỬA", ZALO_LINK, use_container_width=True)
                    actions.append("Zalo Support")
                else:
                    text = "🛒 MUA GÓI BỘT (18K)" if item["part_key"] == "bot_canxi" else "🛒 MUA LINH KIỆN NGAY"
                    st.link_button(text, shop_link(item["part_key"], model_kw, item["keyword"]),
                                   type="primary", use_container_width=True)
                    actions.append("Shopee Buy")
                st.write("")
            log_to_sheet(user_model, query, ", ".join(x["name"] for x in res["issues"]),
                         " | ".join(actions))

        elif res["status"] == "code_unknown":
            st.warning(f"⚠️ Mã lỗi {res['code']} cần kỹ thuật tra theo đúng hãng máy. "
                       "Bác nhắn Zalo kèm mã lỗi và đời máy, em trả lời ngay.")
            st.link_button("💬 GỬI MÃ LỖI QUA ZALO", ZALO_LINK, use_container_width=True)
            log_to_sheet(user_model, query, f"Mã lỗi {res['code']}", "Code Unknown")

        elif res["status"] == "need_info":
            st.warning("⚠️ " + ASK_MORE)
            st.link_button("💬 GỬI VIDEO QUA ZALO", ZALO_LINK, use_container_width=True)
            log_to_sheet(user_model, query, "", "Need Info")

        else:
            st.warning("⚠️ Bệnh lạ quá. Chat với Zalo Hỗ Trợ Kỹ Thuật nhé!")
            st.link_button("🏠 VÀO GIAN HÀNG", VIP_LINKS["home"], use_container_width=True)
            log_to_sheet(user_model, query, "", "Not Found")

st.divider()
c1, c2 = st.columns(2)
with c1:
    st.link_button("💬 Zalo Hỗ Trợ Kỹ Thuật", ZALO_LINK, use_container_width=True)
with c2:
    st.link_button("☎️ Hotline", f"tel:{PHONE_NUMBER}", type="secondary", use_container_width=True)
st.write("")
st.markdown("<div style='text-align: center; color: #888; font-size: 12px;'>© 2026 Thương Mại và Công Nghệ MIT</div>",
            unsafe_allow_html=True)
