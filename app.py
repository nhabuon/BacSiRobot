import streamlit as st
import time

# ... (Các thư viện khác)

# Mẹo giữ App luôn thức
if "keep_alive" not in st.session_state:
    st.session_state.keep_alive = True

# Tự động chạy lại nhẹ nhàng để báo hiệu server đang hoạt động
# (Sếp có thể ẩn cái này đi hoặc để nó chạy ngầm)
import streamlit as st
import urllib.parse
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ==============================================================================
# 1. CẤU HÌNH & KẾT NỐI GOOGLE SHEET
# ==============================================================================

st.set_page_config(page_title="Bác Sĩ Robot - MIT Technology", page_icon="🤖", layout="centered", initial_sidebar_state="collapsed")

PHONE_NUMBER = "0347653354" # 👉 Sếp nhớ thay số điện thoại thật vào đây
SHOP_ID = "68690982"

vip_links = {
    "bot_canxi": f"https://shopee.vn/product/{SHOP_ID}/42427536678",
    "home": "https://shopee.vn/alexaecho"
}

# --- HÀM KẾT NỐI GOOGLE SHEET (BẢO MẬT) ---
@st.cache_resource
def get_google_sheet():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        client = gspread.authorize(creds)
        # Mở file Google Sheet theo tên
        sheet = client.open("Data_BacSiRobot").sheet1
        return sheet
    except Exception as e:
        return None

# ==============================================================================
# 2. LOGIC GHI DỮ LIỆU (ĐÃ SỬA LỖI SYNTAX & NGÀY THÁNG)
# ==============================================================================

def log_to_sheet(model, error_query, action_type):
    """Ghi thẳng vào Google Sheet"""
    sheet = get_google_sheet()
    if sheet:
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # 👉 QUAN TRỌNG: Dùng value_input_option='USER_ENTERED' để Google tự hiểu ngày tháng
            sheet.append_row(
                [timestamp, model, error_query, action_type], 
                value_input_option='USER_ENTERED'
            )
        except:
            # Nếu lỗi mạng thì bỏ qua (Đây chính là phần 'except' bị thiếu lúc nãy)
            pass 

def get_safe_link(part_key, model_name, default_keyword):
    if part_key in vip_links: return vip_links[part_key]
    keyword = f"{default_keyword} {model_name}" if model_name else default_keyword
    return f"https://shopee.vn/search?keyword={keyword}&shop={SHOP_ID}"

# ==============================================================================
# 3. DỮ LIỆU BỆNH HỌC
# ==============================================================================
db_issues = [
    {"keys": ["nước", "bơm", "khô", "lau", "tắc", "không ra nước"], "name": "Lỗi Tắc Nước", "fix": "90% do cặn canxi. Dùng bột thông tắc 18k.", "type": "easy", "part_key": "bot_canxi", "keyword": "bột tẩy cặn robot"},
    {"keys": ["sạc", "pin", "nguồn", "tắt máy", "dock"], "name": "Lỗi Pin / Nguồn", "fix": "Pin chai hoặc chân sạc bẩn. Tự thay pin dễ dàng.", "type": "easy", "part_key": "pin", "keyword": "pin robot hút bụi"},
    {"keys": ["bánh xe", "kẹt", "lốp"], "name": "Lỗi Bánh Xe", "fix": "Mòn lốp cao su. Dán lốp mới là xong.", "type": "easy", "part_key": "banhxe", "keyword": "lốp bánh xe robot"},
    {"keys": ["lọc", "bụi", "hút yếu"], "name": "Lỗi Màng Lọc", "fix": "Màng lọc bẩn. Cần thay mới.", "type": "easy", "part_key": "hepa", "keyword": "lọc hepa"},
    {"keys": ["kêu", "ồn", "hộp số", "cạch"], "name": "Lỗi Hộp Số (Nghiêm trọng)", "fix": "Vỡ bánh răng. Cần tháo máy gửi sửa.", "type": "hard", "part_key": "zalo_repair", "keyword": ""},
    {"keys": ["lds", "laser", "lỗi 1"], "name": "Lỗi LDS (Laser)", "fix": "Hỏng mắt Laser. Cần gửi shop kiểm tra.", "type": "hard", "part_key": "zalo_repair", "keyword": ""},
    {"keys": ["quạt", "hút"], "name": "Lỗi Quạt Hút", "fix": "Chết quạt hút. Cần thợ xử lý.", "type": "hard", "part_key": "zalo_repair", "keyword": ""}
]

# ==============================================================================
# 4. GIAO DIỆN (FRONTEND)
# ==============================================================================
# CSS
st.markdown("""<style>.stApp {background-color:#f8f9fa;} .header-container {background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%); padding:20px; border-radius:0 0 20px 20px; color:white; text-align:center; margin-top:-50px;} .error-card {background-color:white; padding:15px; border-radius:10px; border-left:5px solid #0d47a1; margin-bottom:10px;box-shadow:0 2px 5px rgba(0,0,0,0.05);} .stButton button {width:100%; border-radius:8px; font-weight:bold;} #MainMenu {visibility:hidden;} footer {visibility:hidden;} header {visibility:hidden;}</style>""", unsafe_allow_html=True)
st.markdown("""<div class="header-container"><h2>🤖 BÁC SĨ ROBOT</h2><p>TRỰC THUỘC THƯƠNG MẠI VÀ CÔNG NGHỆ MIT</p></div>""", unsafe_allow_html=True)

# Giao diện chính
st.info("💡 **BƯỚC 1:** Chọn đời máy để bắt bệnh chuẩn nhất!")
model_options = ["Chưa rõ", "Deebot T5 / DX96", "Deebot T8 AIVI / Max", "Deebot T9", "Deebot X1 Omni / Turbo", "Dreame L10 / W10", "Roborock S7 / S8"]
user_model = st.selectbox("Đời máy:", model_options, label_visibility="collapsed")
model_clean = ""
if "T5" in user_model: model_clean = "t5"
elif "T8" in user_model: model_clean = "t8"
elif "T9" in user_model: model_clean = "t9"
elif "X1" in user_model: model_clean = "x1"

st.divider()
st.write("##### 🔍 BƯỚC 2: Robot bị sao? (Nhập mã lỗi hoặc hiện tượng)")

with st.form(key='search_form'):
    query = st.text_input("Nhập lỗi", placeholder="VD: không ra nước, kêu to...", label_visibility="collapsed")
    submitted = st.form_submit_button('🔍 BẮT BỆNH NGAY', type="primary", use_container_width=True)

if submitted:
    if not query:
        st.warning("⚠️ Bác chưa nhập lỗi kìa!")
    else:
        found = False
        st.write("---")
        for item in db_issues:
            if any(k in query.lower() for k in item["keys"]):
                found = True
                st.markdown(f"""<div class="error-card"><b>🚨 {item['name']}</b><br><small>Nguyên nhân: <span style="color:#2e7d32;font-weight:bold">{item['fix']}</span></small></div>""", unsafe_allow_html=True)
                
                # Nút bấm & Action Code
                if item.get('type') == "hard":
                    btn_text = "💬 CHAT ZALO GỬI SỬA"
                    link = f"https://zalo.me/{PHONE_NUMBER}"
                    btn_type = "secondary"
                    action_code = "Zalo Support"
                else:
                    btn_text = "🛒 MUA GÓI BỘT (18K)" if item['part_key'] == "bot_canxi" else f"🛒 MUA LINH KIỆN NGAY"
                    link = get_safe_link(item['part_key'], model_clean, item['keyword'])
                    btn_type = "primary"
                    action_code = "Shopee Buy"

                st.link_button(btn_text, link, type=btn_type, use_container_width=True)
                
                # --- GHI VÀO GOOGLE SHEET ---
                log_to_sheet(user_model, query, action_code)
                st.write("")

        if not found:
            st.warning("⚠️ Bệnh lạ quá. Chat với Zalo Hỗ Trợ Kỹ Thuật nhé!")
            st.link_button("🏠 VÀO GIAN HÀNG", vip_links["home"], use_container_width=True)
            log_to_sheet(user_model, query, "Not Found")

st.divider()
c1, c2 = st.columns(2)
with c1: st.link_button("💬 Zalo Hỗ Trợ Kỹ Thuật", f"https://zalo.me/{PHONE_NUMBER}", use_container_width=True)
with c2: st.link_button("☎️ Hotline", f"tel:{PHONE_NUMBER}", type="secondary", use_container_width=True)
st.write("")
st.markdown("<div style='text-align: center; color: #888; font-size: 12px;'>© 2026 Thương Mại và Công Nghệ MIT</div>", unsafe_allow_html=True)


