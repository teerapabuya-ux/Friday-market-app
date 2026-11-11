import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

# ---------------------------------------------------------
# 1. การตั้งค่าหน้าเว็บ (Page Configuration)
# ---------------------------------------------------------
st.set_page_config(
    page_title="ระบบแผนผังและจัดการร้านค้าตลาดนัด",
    page_icon="🏪",
    layout="wide"
)

# ---------------------------------------------------------
# 2. ข้อมูลจำลองร้านค้าและสต็อก (Mock Data)
# ---------------------------------------------------------
if "shops_data" not in st.session_state:
    st.session_state.shops_data = [
        {
            "id": "A01",
            "name": "ลูกชิ้นทอดโอชา",
            "category": "อาหาร",
            "lat": 13.7563,
            "lng": 100.5018,
            "open_time": "17:00",
            "close_time": "23:00",
            "items": [
                {"name": "ลูกชิ้นหมู", "stock": 15, "unit": "ไม้", "price": 10},
                {"name": "ลูกชิ้นเนื้อ", "stock": 5, "unit": "ไม้", "price": 12},
                {"name": "ไส้กรอกแดง", "stock": 0, "unit": "ไม้", "price": 10}
            ]
        },
        {
            "id": "B02",
            "name": "ชาเย็นชื่นใจ",
            "category": "เครื่องดื่ม",
            "lat": 13.7565,
            "lng": 100.5020,
            "open_time": "16:00",
            "close_time": "22:00",
            "items": [
                {"name": "ชาไทยเย็น", "stock": 25, "unit": "แก้ว", "price": 35},
                {"name": "ชาเขียวมัทฉะ", "stock": 8, "unit": "แก้ว", "price": 40},
                {"name": "ชามะนาว", "stock": 20, "unit": "แก้ว", "price": 30}
            ]
        },
        {
            "id": "C03",
            "name": "แฟชั่นวินเทจ 90s",
            "category": "เสื้อผ้า/แฟชั่น",
            "lat": 13.7561,
            "lng": 100.5022,
            "open_time": "18:00",
            "close_time": "24:00",
            "items": [
                {"name": "เสื้อยืดลายวินเทจ", "stock": 10, "unit": "ตัว", "price": 190},
                {"name": "กางเกงยีนส์ขาสั้น", "stock": 4, "unit": "ตัว", "price": 250}
            ]
        },
        {
            "id": "D04",
            "name": "เคสโทรศัพท์ & กิ๊ฟช็อป",
            "category": "ของใช้/กิ๊ฟช็อป",
            "lat": 13.7567,
            "lng": 100.5024,
            "open_time": "17:00",
            "close_time": "23:00",
            "items": [
                {"name": "เคส iPhone 15", "stock": 12, "unit": "ชิ้น", "price": 120},
                {"name": "พวงกุญแจไหมพรม", "stock": 3, "unit": "ชิ้น", "price": 59}
            ]
        }
    ]

# ---------------------------------------------------------
# 3. ฟังก์ชันคำนวณสถานะเปิด-ปิดร้าน
# ---------------------------------------------------------
def is_shop_open(open_time_str, close_time_str):
    now = datetime.now().time()
    open_t = datetime.strptime(open_time_str, "%H:%M").time()
    close_t = datetime.strptime(close_time_str, "%H:%M").time()
    
    if open_t <= close_t:
        return open_t <= now <= close_t
    else: # รองรับกรณีเปิดข้ามคืน (เช่น 18:00 ถึง 02:00)
        return now >= open_t or now <= close_t

# ---------------------------------------------------------
# 4. ส่วนหัวของเว็บไซต์ (Header)
# ---------------------------------------------------------
st.title("🎪 ระบบจัดการและผังร้านค้าตลาดนัด (Night Market Map)")
st.caption("ตรวจสอบตำแหน่งร้านค้า สินค้าคงเหลือ เวลาเปิด-ปิด ได้แบบเรียลไทม์")

# ---------------------------------------------------------
# 5. แถบข้างสำหรับกรองข้อมูล (Sidebar Filter)
# ---------------------------------------------------------
st.sidebar.header("🔍 กรองข้อมูลร้านค้า")

categories = ["ทั้งหมด"] + list(set(shop["category"] for shop in st.session_state.shops_data))
selected_category = st.sidebar.selectbox("เลือกประเภทสินค้า:", categories)

search_keyword = st.sidebar.text_input("ค้นหาชื่อร้าน หรือชื่อสินค้า:")

only_open = st.sidebar.checkbox("แสดงเฉพาะร้านที่เปิดอยู่ ณ ตอนนี้")

# กรองร้านค้าตามเงื่อนไข
filtered_shops = []
for shop in st.session_state.shops_data:
    # กรองประเภท
    if selected_category != "ทั้งหมด" and shop["category"] != selected_category:
        continue
    
    # กรองการเปิด-ปิด
    if only_open and not is_shop_open(shop["open_time"], shop["close_time"]):
        continue
        
    # กรองคำค้นหา
    if search_keyword:
        match_name = search_keyword.lower() in shop["name"].lower()
        match_item = any(search_keyword.lower() in item["name"].lower() for item in shop["items"])
        if not (match_name or match_item):
            continue
            
    filtered_shops.append(shop)

# ---------------------------------------------------------
# 6. แสดงผลแผนผังตลาดนัด (Map Section)
# ---------------------------------------------------------
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("🗺️ แผนผังตำแหน่งร้านค้าในตลาดนัด")
    
    # สร้างแผนที่ Folium
    m = folium.Map(location=[13.7564, 100.5021], zoom_start=19)
    
    for shop in filtered_shops:
        open_status = is_shop_open(shop["open_time"], shop["close_time"])
        status_text = "🟢 เปิดให้บริการ" if open_status else "🔴 ปิดให้บริการ"
        marker_color = "green" if open_status else "red"
        
        # ข้อความใน Popup
        popup_html = f"""
        <b>[ล็อก {shop['id']}] {shop['name']}</b><br>
        หมวดหมู่: {shop['category']}<br>
        เวลา: {shop['open_time']} - {shop['close_time']} น.<br>
        สถานะ: <b>{status_text}</b>
        """
        
        folium.Marker(
            location=[shop["lat"], shop["lng"]],
            popup=popup_html,
            tooltip=f"{shop['id']}: {shop['name']}",
            icon=folium.Icon(color=marker_color, icon="shopping-cart", prefix="fa")
        ).add_to(m)
        
    st_folium(m, width="100%", height=450)

# ---------------------------------------------------------
# 7. รายละเอียดร้านค้าและสินค้าคงเหลือ (Shop Details & Inventory)
# ---------------------------------------------------------
with col2:
    st.subheader("📋 รายละเอียดร้านค้าและสต็อกสินค้า")
    
    if not filtered_shops:
        st.warning("ไม่พบร้านค้าที่ตรงกับเงื่อนไขการค้นหา")
    else:
        shop_names = [f"[{s['id']}] {s['name']}" for s in filtered_shops]
        selected_shop_name = st.selectbox("เลือกร้านค้าเพื่อดูรายละเอียดสต็อก:", shop_names)
        
        # ดึงข้อมูลร้านที่เลือก
        selected_shop_id = selected_shop_name.split("]")[0].replace("[", "")
        target_shop = next(s for s in st.session_state.shops_data if s["id"] == selected_shop_id)
        
        # คำนวณสถานะเปิด-ปิด
        is_open = is_shop_open(target_shop["open_time"], target_shop["close_time"])
        
        # แสดงข้อมูลทั่วไปของร้าน
        st.markdown(f"### {target_shop['name']} (ล็อก {target_shop['id']})")
        st.write(f"🏷️ **ประเภท:** {target_shop['category']}")
        st.write(f"⏰ **เวลาเปิด-ปิด:** {target_shop['open_time']} - {target_shop['close_time']} น.")
        
        if is_open:
            st.success("🟢 สถานะ: ร้านเปิดอยู่")
        else:
            st.error("🔴 สถานะ: ร้านปิดอยู่")
            
        st.divider()
        st.subheader("📦 สินค้าคงเหลือ")
        
        # ตารางแสดงสต็อกสินค้า
        df_items = pd.DataFrame(target_shop["items"])
        
        def get_stock_status(stock):
            if stock == 0:
                return "❌ สินค้าหมด"
            elif stock <= 5:
                return "⚠️ ใกล้หมด"
            return "✅ มีสินค้า"
            
        df_items["สถานะสต็อก"] = df_items["stock"].apply(get_stock_status)
        df_items.columns = ["ชื่อสินค้า", "คงเหลือ", "หน่วย", "ราคา (บาท)", "สถานะ"]
        
        st.dataframe(df_items[["ชื่อสินค้า", "ราคา (บาท)", "คงเหลือ", "หน่วย", "สถานะ"]], use_container_width=True)

# ---------------------------------------------------------
# 8. ระบบหลังบ้านจำลอง: อัปเดตจำนวนสินค้า (Stock Update)
# ---------------------------------------------------------
st.divider()
with st.expander("🛠️ [สำหรับเจ้าของร้าน] อัปเดตสต็อกสินค้าคงเหลือแบบเรียลไทม์"):
    st.write("จัดการและอัปเดตจำนวนสินค้าในร้านของคุณ")
    
    all_shop_names = [f"[{s['id']}] {s['name']}" for s in st.session_state.shops_data]
    edit_shop_name = st.selectbox("เลือกร้านค้าของคุณ:", all_shop_names, key="edit_shop_select")
    
    edit_shop_id = edit_shop_name.split("]")[0].replace("[", "")
    edit_shop = next(s for s in st.session_state.shops_data if s["id"] == edit_shop_id)
    
    item_names = [item["name"] for item in edit_shop["items"]]
    selected_item_name = st.selectbox("เลือกสินค้าที่ต้องการแก้ไข:", item_names)
    
    target_item = next(item for item in edit_shop["items"] if item["name"] == selected_item_name)
    
    new_stock = st.number_input(
        f"ปรับปรุงจำนวนคงเหลือของ '{target_item['name']}' ({target_item['unit']}):",
        min_value=0,
        max_value=999,
        value=int(target_item["stock"])
    )
    
    if st.button("💾 บันทึกการอัปเดตสต็อก"):
        target_item["stock"] = new_stock
        st.success(f"อัปเดตสต็อก '{target_item['name']}' เป็น {new_stock} {target_item['unit']} เรียบร้อยแล้ว!")
        st.rerun()