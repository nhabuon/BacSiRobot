import streamlit as st
import urllib.parse

# ==============================================================================
# 1. CẤU HÌNH HỆ THỐNG
# ==============================================================================

# Cấu hình trang web (Giao diện Mobile)
st.set_page_config(
    page_title="Bác Sĩ Robot - AlexaEcho",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# SHOP ID CỦA SẾP (Đã điền chuẩn từ ảnh Sếp gửi)
SHOP_ID = "68690982"

# KHO LINK SẢN PHẨM CHIẾN LƯỢC
vip_links = {
    # LINK BỘT TẨY CẶN (Sản phẩm 18k Sếp muốn đẩy mạnh)
    "bot_canxi": f"https://shopee.vn/product/{SHOP_ID}/42427536678",
    
    # Link dự phòng về trang chủ
    "home": "https://shopee.vn/alexaecho"
}

# ==============================================================================
# 2. HÀM XỬ LÝ LINK THÔNG MINH
# ==============================================================================
def get_safe_link(part_key, model_name, default_keyword):
    # 1. Kiểm tra xem có Link VIP (Sản phẩm chiến lược) không?
    if part_key in vip_links:
        return vip_links[part_key]

    # 2. Nếu không có Link VIP -> Dùng Tìm kiếm trong Shop (Qua Shop ID)
    keyword = default_keyword
    if model_name:
        keyword = f"{default_keyword} {model_name}"
    
    base_url = "https://shopee.vn/search"
    params = {'keyword': keyword, 'shop': SHOP_ID}
    return f"{base_url}?{urllib.parse.urlencode(params)}"

# ==============================================================================
# 3. CƠ SỞ DỮ LIỆU BỆNH HỌC (ĐÃ CẬP NHẬT GIẢI PHÁP BỘT TẨY CẶN)
# ==============================================================================
db_issues = [
    {
        "keys": ["nước", "bơm", "khô", "lau", "két nước", "tắc", "không ra nước"],
        "name": "Lỗi Tắc Hệ Thống Nước (Lau khô)",
        "fix": "90% là do cặn canxi làm tắc vòi bơm. Đừng vội thay bơm, hãy dùng Bột thông tắc chuyên dụng trước.",
        "part_key": "bot_canxi", # Kích hoạt link gói bột 18k
        "keyword": "bột tẩy cặn canxi robot" 
    },
    {
        "keys": ["lds", "laser", "quay tròn", "lỗi 1", "error 1", "đầu u"],
        "name": "Lỗi Cụm LDS (Mắt Laser) - Mã lỗi số 1",
        "fix": "Mắt Laser không quay hoặc bị vật cản che khuất. Cần thay Motor quay hoặc Cụm Laser.",
        "part_key": "lds", 
        "keyword": "motor lds"
    },
    {
        "keys": ["kêu", "ồn", "cạch cạch", "hú", "hộp số"],
        "name": "Lỗi Động Cơ / Hộp Số",
        "fix": "Tiếng kêu lớn do vỡ bánh răng hộp số chổi chính hoặc quạt hút bị kẹt rác.",
        "part_key": "hopso", 
        "keyword": "hộp số chổi chính"
    },
    {
        "keys": ["sạc", "pin", "nguồn", "tắt máy", "dock", "error 10020"],
        "name": "Lỗi Pin / Nguồn Điện",
        "fix": "Pin chai (chạy dưới 40p), hoặc chân tiếp xúc sạc bị oxy hóa (đen) cần đánh bóng.",
        "part_key": "pin", 
        "keyword": "pin robot hút bụi"
    },
    {
        "keys": ["bánh xe", "kẹt", "lốp", "trượt", "error 102"],
        "name": "Lỗi Bánh Xe Di Chuyển - Mã lỗi 102",
        "fix": "Bánh xe bị mòn lốp cao su gây trượt, hoặc bị tóc quấn chặt trục bánh.",
        "part_key": "banhxe", 
        "keyword": "lốp bánh xe robot"
    },
    {
        "keys": ["lọc", "bụi", "hút yếu", "hepa"],
        "name": "Lỗi Lực Hút Yếu / Màng Lọc",
        "fix": "Màng lọc HEPA quá bẩn hoặc ướt làm tắc khí. Cần thay màng lọc mới.",
        "part_key": "hepa", 
        "keyword": "lọc hepa"
    }
]

# ==============================================================================
# 4. GIAO DIỆN NGƯỜI DÙNG (MOBILE FRIENDLY)
# ==============================================================================

# CSS làm đẹp giao diện
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .header-container {
        background: linear-gradient(135deg, #ee4d2d 0%, #ff7337 100%);
        padding: 20px; border-radius: 0 0 20px 20px; color: white; text-align: center; margin-top: -50px;
    }
    .error-card {
        background-color: white; padding: 15px; border-radius: 10px;
        border-left: 5px solid #ee4d2d; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .solution-text { color: #2e7d32; font-weight: bold; }
    /* Nút bấm Submit */
    .stButton button { width: 100%; font-weight: bold; border-radius: 8px; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header-container">
    <h2>🤖 BÁC SĨ ROBOT</h2>
    <small>Chẩn đoán lỗi & Cấp linh kiện Chính hãng</small>
</div>
""", unsafe_allow_html=True)

# --- BƯỚC 1: Chọn Model ---
st.info("💡 **BƯỚC 1:** Chọn đời máy để lấy linh kiện chuẩn nhất!")
model_options = ["Chưa rõ", "Deebot T5 / DX96", "Deebot T8 AIVI / Max", "Deebot T9", "Deebot X1 Omni / Turbo", "Dreame L10 / W10", "Roborock S7 / S8"]
user_model_select = st.selectbox("Đời máy:", model_options, label_visibility="collapsed")

# Xử lý tên model
user_model_clean = ""
if "T5" in user_model_select: user_model_clean = "t5"
elif "T8" in user_model_select: user_model_clean = "t8"
elif "T9" in user_model_select: user_model_clean = "t9"
elif "X1" in user_model_select: user_model_clean = "x1"
elif "Dreame" in user_model_select: user_model_clean = "dreame"
elif "Roborock" in user_model_select: user_model_clean = "roborock"

st.divider()

# --- BƯỚC 2: Nhập bệnh (CÓ NÚT BẤM) ---
st.write("##### 🔍 BƯỚC 2: Robot bị sao? (Nhập mã lỗi hoặc hiện tượng)")

# Tạo Form để có nút bấm Submit
with st.form(key='search_form'):
    query_input = st.text_input(
        label="Nhập lỗi", 
        placeholder="VD: không ra nước, lỗi 1, kêu to...", 
        label_visibility="collapsed"
    )
    # Nút bấm hành động
    submit_button = st.form_submit_button(label='🔍 BẮT BỆNH NGAY', type="primary", use_container_width=True)

# Logic xử lý khi bấm nút
if submit_button:
    if not query_input:
        st.warning("⚠️ Bác chưa nhập mô tả lỗi kìa!")
    else:
        found = False
        st.write("---")
        for item in db_issues:
            if any(k in query_input.lower() for k in item["keys"]):
                found = True
                
                # Lấy link an toàn
                safe_link = get_safe_link(item['part_key'], user_model_clean, item['keyword'])
                
                st.markdown(f"""
                <div class="error-card">
                    <b>🚨 {item['name']}</b><br>
                    <p>Nguyên nhân: <span class="solution-text">{item['fix']}</span></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Nút mua hàng
                if item['part_key'] == "bot_canxi":
                    btn_text = "🛒 MUA GÓI BỘT THÔNG TẮC (18K)"
                else:
                    btn_text = "🛒 MUA LINH KIỆN KHẮC PHỤC NGAY"
                    if user_model_clean:
                        btn_text += f" (CHO {user_model_clean.upper()})"
                
                st.link_button(btn_text, safe_link, type="primary", use_container_width=True)
                st.write("") 

        if not found:
            st.warning("⚠️ Chưa rõ bệnh. Hãy Chat với Sếp để được bắt mạch!")
            st.link_button("🏠 VÀO GIAN HÀNG TỰ TÌM", vip_links["home"], use_container_width=True)

# --- FOOTER (LIÊN HỆ) ---
st.divider()
st.markdown("#### 📞 Hỗ trợ khẩn cấp")
c1, c2 = st.columns(2)

# SẾP LƯU Ý: THAY SỐ ĐIỆN THOẠI THẬT VÀO 2 DÒNG DƯỚI ĐÂY NHÉ
with c1: 
    st.link_button("💬 Zalo Sếp", "https://zalo.me/0347653354", use_container_width=True) 
with c2: 
    st.link_button("☎️ Hotline", "tel:0347653354", type="secondary", use_container_width=True)

st.write("")
st.markdown("<div style='text-align: center; color: #888; font-size: 12px;'>© 2026 Bệnh Viện Robot - AlexaEcho Official Store</div>", unsafe_allow_html=True)
