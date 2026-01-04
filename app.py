import streamlit as st
import urllib.parse

# ==============================================================================
# 1. CẤU HÌNH CỦA SẾP (SỬA THÔNG TIN TẠI ĐÂY)
# ==============================================================================

# 👉 SỐ ĐIỆN THOẠI CỦA SẾP (Quan trọng: Sửa số này để khách Chat Zalo/Gọi điện)
PHONE_NUMBER = "0987654321"  # <--- Sếp thay số thật vào đây nhé!

# Shop ID Shopee (Đã chuẩn)
SHOP_ID = "68690982"

# Kho Link sản phẩm chiến lược
vip_links = {
    # Link gói bột tẩy cặn 18k
    "bot_canxi": f"https://shopee.vn/product/{SHOP_ID}/42427536678",
    # Link trang chủ dự phòng
    "home": "https://shopee.vn/alexaecho"
}

# ==============================================================================
# 2. HỆ THỐNG XỬ LÝ LINK & GIAO DIỆN
# ==============================================================================

st.set_page_config(
    page_title="Bác Sĩ Robot - MIT Technology", # Đã sửa tiêu đề tab
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hàm tạo link Shopee an toàn (cho lỗi dễ)
def get_safe_link(part_key, model_name, default_keyword):
    if part_key in vip_links:
        return vip_links[part_key]

    keyword = default_keyword
    if model_name:
        keyword = f"{default_keyword} {model_name}"
    
    base_url = "https://shopee.vn/search"
    params = {'keyword': keyword, 'shop': SHOP_ID}
    return f"{base_url}?{urllib.parse.urlencode(params)}"

# ==============================================================================
# 3. CƠ SỞ DỮ LIỆU BỆNH HỌC (PHÂN LOẠI DỄ / KHÓ)
# ==============================================================================
db_issues = [
    # --- NHÓM DỄ (BÁN LINH KIỆN TỰ THAY) ---
    {
        "keys": ["nước", "bơm", "khô", "lau", "két nước", "tắc", "không ra nước"],
        "name": "Lỗi Tắc Hệ Thống Nước (Lau khô)",
        "fix": "90% là do cặn canxi làm tắc vòi. Đừng vội thay bơm, hãy dùng Bột thông tắc chuyên dụng trước.",
        "type": "easy", # Dễ -> Bán hàng
        "part_key": "bot_canxi", 
        "keyword": "bột tẩy cặn canxi robot" 
    },
    {
        "keys": ["sạc", "pin", "nguồn", "tắt máy", "dock", "error 10020"],
        "name": "Lỗi Pin / Nguồn Điện",
        "fix": "Pin chai (chạy dưới 40p) hoặc chân sạc bẩn. Bạn có thể tự thay pin dễ dàng tại nhà.",
        "type": "easy",
        "part_key": "pin", 
        "keyword": "pin robot hút bụi"
    },
    {
        "keys": ["bánh xe", "kẹt", "lốp", "trượt", "error 102"],
        "name": "Lỗi Bánh Xe (Mòn lốp)",
        "fix": "Bánh xe bị mòn lớp cao su gây trượt. Chỉ cần mua vỏ lốp mới về dán đè lên là chạy ngon.",
        "type": "easy",
        "part_key": "banhxe", 
        "keyword": "lốp bánh xe robot"
    },
    {
        "keys": ["lọc", "bụi", "hút yếu", "hepa"],
        "name": "Lỗi Lực Hút Yếu / Màng Lọc",
        "fix": "Màng lọc HEPA quá bẩn hoặc ướt làm tắc khí. Cần thay màng lọc mới.",
        "type": "easy",
        "part_key": "hepa", 
        "keyword": "lọc hepa"
    },

    # --- NHÓM KHÓ (CẦN GỬI SỬA CHỮA) ---
    {
        "keys": ["kêu", "ồn", "cạch cạch", "hú", "hộp số", "rè"],
        "name": "Lỗi Động Cơ / Hộp Số (Nghiêm trọng)",
        "fix": "Tiếng kêu lớn do vỡ bánh răng bên trong hộp số. ⚠️ Lỗi này cần tháo tung máy, KHÔNG NÊN tự sửa.",
        "type": "hard", # Khó -> Gửi Zalo
        "part_key": "zalo_repair", 
        "keyword": "" 
    },
    {
        "keys": ["lds", "laser", "quay tròn", "lỗi 1", "error 1", "đầu u"],
        "name": "Lỗi Cụm LDS (Mắt Laser)",
        "fix": "Mắt Laser bị kẹt hoặc chết motor. Việc cân chỉnh Laser rất khó, hãy gửi shop kiểm tra để tránh hỏng mạch.",
        "type": "hard", 
        "part_key": "zalo_repair", 
        "keyword": ""
    },
    {
        "keys": ["hút yếu", "không hút", "quạt", "fan"],
        "name": "Lỗi Quạt Hút (Fan Motor)",
        "fix": "Quạt hút bị chết hoặc kẹt rác bên trong mainboard. Cần thợ chuyên nghiệp xử lý.",
        "type": "hard",
        "part_key": "zalo_repair",
        "keyword": ""
    }
]

# ==============================================================================
# 4. GIAO DIỆN NGƯỜI DÙNG
# ==============================================================================

# CSS
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .header-container {
        background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%); /* Đổi sang màu Xanh công nghệ MIT cho uy tín */
        padding: 20px; border-radius: 0 0 20px 20px; color: white; text-align: center; margin-top: -50px;
    }
    .header-container h2 { font-size: 22px; font-weight: 800; }
    .header-container p { font-size: 14px; opacity: 0.9; margin-top: -10px; }
    .error-card {
        background-color: white; padding: 15px; border-radius: 10px;
        border-left: 5px solid #0d47a1; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .solution-text { color: #2e7d32; font-weight: bold; }
    /* Style cho nút bấm */
    .stButton button { width: 100%; border-radius: 8px; font-weight: bold; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Header (ĐÃ ĐỔI TÊN THEO YÊU CẦU)
st.markdown("""
<div class="header-container">
    <h2>🤖 BÁC SĨ ROBOT</h2>
    <p>TRỰC THUỘC THƯƠNG MẠI VÀ CÔNG NGHỆ MIT</p>
</div>
""", unsafe_allow_html=True)

# BƯỚC 1: Chọn Model
st.info("💡 **BƯỚC 1:** Chọn đời máy để bắt bệnh chuẩn nhất!")
model_options = ["Chưa rõ", "Deebot T5 / DX96", "Deebot T8 AIVI / Max", "Deebot T9", "Deebot X1 Omni / Turbo", "Dreame L10 / W10", "Roborock S7 / S8"]
user_model_select = st.selectbox("Đời máy:", model_options, label_visibility="collapsed")
# Xử lý model
user_model_clean = ""
if "T5" in user_model_select: user_model_clean = "t5"
elif "T8" in user_model_select: user_model_clean = "t8"
elif "T9" in user_model_select: user_model_clean = "t9"
elif "X1" in user_model_select: user_model_clean = "x1"

st.divider()

# BƯỚC 2: Nhập bệnh
st.write("##### 🔍 BƯỚC 2: Robot bị sao? (Nhập mã lỗi hoặc hiện tượng)")
with st.form(key='search_form'):
    query_input = st.text_input(label="Nhập lỗi", placeholder="VD: không ra nước, kêu to, lỗi 1...", label_visibility="collapsed")
    submit_button = st.form_submit_button(label='🔍 BẮT BỆNH NGAY', type="primary", use_container_width=True)

if submit_button:
    if not query_input:
        st.warning("⚠️ Bác chưa nhập mô tả lỗi kìa!")
    else:
        found = False
        st.write("---")
        for item in db_issues:
            if any(k in query_input.lower() for k in item["keys"]):
                found = True
                
                # HIỂN THỊ KẾT QUẢ
                st.markdown(f"""
                <div class="error-card">
                    <b>🚨 {item['name']}</b><br>
                    <p>Nguyên nhân: <span class="solution-text">{item['fix']}</span></p>
                </div>
                """, unsafe_allow_html=True)
                
                # XỬ LÝ NÚT BẤM (PHÂN LUỒNG)
                if item.get('type') == "hard":
                    # CA KHÓ -> Dẫn về Zalo Sếp
                    btn_text = "💬 CHAT ZALO ĐỂ GỬI MÁY SỬA"
                    safe_link = f"https://zalo.me/{PHONE_NUMBER}"
                    btn_type = "secondary" # Nút màu xám/trắng
                
                else:
                    # CA DỄ -> Dẫn sang Shopee bán hàng
                    if item['part_key'] == "bot_canxi":
                        btn_text = "🛒 MUA GÓI BỘT THÔNG TẮC (18K)"
                    else:
                        btn_text = "🛒 MUA LINH KIỆN VỀ TỰ THAY"
                        if user_model_clean:
                            btn_text += f" (CHO {user_model_clean.upper()})"
                    
                    safe_link = get_safe_link(item['part_key'], user_model_clean, item['keyword'])
                    btn_type = "primary" # Nút màu đỏ
                
                st.link_button(btn_text, safe_link, type=btn_type, use_container_width=True)
                st.write("") 

        if not found:
            st.warning("⚠️ Bệnh lạ quá. Hãy Chat với Sếp để kiểm tra kỹ hơn!")
            st.link_button("🏠 VÀO GIAN HÀNG XEM PHỤ KIỆN", vip_links["home"], use_container_width=True)

# FOOTER LIÊN HỆ
st.divider()
st.markdown("#### 📞 Liên hệ trực tiếp")
c1, c2 = st.columns(2)
with c1: 
    st.link_button("💬 Zalo Sếp", f"https://zalo.me/{PHONE_NUMBER}", use_container_width=True) 
with c2: 
    st.link_button("☎️ Hotline", f"tel:{PHONE_NUMBER}", type="secondary", use_container_width=True)

st.write("")
st.markdown("<div style='text-align: center; color: #888; font-size: 12px;'>© 2026 Thương Mại và Công Nghệ MIT</div>", unsafe_allow_html=True)
