# ==========================================================
# APP TÍNH TOÁN KHOẢN VAY NGÂN HÀNG
# Môn: Công nghệ tài chính
# Tác giả: Sinh viên
# Framework: Streamlit
# Đơn vị: Triệu đồng
# ==========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------------
# CẤU HÌNH TRANG
# ----------------------------------------------------------

st.set_page_config(
    page_title="Loan Calculator",
    page_icon="🏦",
    layout="wide"
)

# ----------------------------------------------------------
# CSS
# ----------------------------------------------------------

st.markdown("""
<style>
/* Phông chữ Times New Roman toàn cục */
* {
    font-family: 'Times New Roman', Times, serif !important;
}

/* Nền sáng màu */
.stApp, .main {
    background-color: #F8F9FA !important; 
}

/* Thống nhất 1 màu chữ phù hợp với nền sáng */
html, body, [class*="css"], .stMarkdown, h1, h2, h3, h4, h5, h6, p, span, label, li {
    color: #222222 !important; 
}

/* Giữ nguyên màu cho các thông báo (info, success, warning, error) */
div[data-testid="stAlert"] * {
    color: inherit !important;
}

.block-container{
    padding-top:2rem;
}

div[data-testid="metric-container"]{
    background:white;
    border-radius:15px;
    padding:18px;
    border:1px solid #e5e7eb;
    box-shadow:0 3px 8px rgba(0,0,0,.08);
}

.stButton>button{
    width:100%;
    border-radius:10px;
    height:45px;
    font-weight:bold;
    color: #222222 !important;
    border: 1px solid #cccccc;
    background-color: #ffffff;
}

footer{
    visibility:hidden;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------
# HÀM ĐỊNH DẠNG TIỀN
# ----------------------------------------------------------

def money(x):

    text=f"{x:,.2f}"

    text=text.replace(",", "X")
    text=text.replace(".", ",")
    text=text.replace("X",".")

    return text+" triệu đồng"

# ----------------------------------------------------------
# GỢI Ý LÃI SUẤT
# ----------------------------------------------------------

rate_default={
    "Mua nhà":7.5,
    "Mua xe":8.5,
    "Tiêu dùng":12.0,
    "Kinh doanh":9.0,
    "Khác":10.0
}

# ----------------------------------------------------------
# HEADER
# ----------------------------------------------------------

st.title("🏦 ỨNG DỤNG TÍNH TOÁN KHOẢN VAY")

st.write("""
Ứng dụng hỗ trợ tính toán khoản vay theo **hai phương thức trả nợ**.

- Trả gốc đều
- Trả góp đều (Annuity)

**Đơn vị:** Triệu đồng
""")

# ----------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------

st.sidebar.header("📋 Thông tin khoản vay")

purpose=st.sidebar.selectbox(
    "Mục đích vay",
    list(rate_default.keys())
)

loan=st.sidebar.number_input(
    "Số tiền vay (triệu đồng)",
    min_value=1.0,
    value=500.0,
    step=50.0
)

interest=st.sidebar.number_input(
    "Lãi suất (%/năm)",
    value=rate_default[purpose],
    step=0.1
)

years = st.sidebar.slider(
    "Thời hạn vay (năm)",
    min_value=1,
    max_value=30,
    value=10,
    step=1
)

# Quy đổi sang tháng để tính toán
month = years * 12

income=st.sidebar.number_input(
    "Thu nhập hàng tháng (triệu đồng)",
    min_value=1.0,
    value=25.0
)

method=st.sidebar.radio(
    "Phương thức",
    [
        "Trả gốc đều",
        "Trả góp đều"
    ]
)

st.sidebar.info(
    f"💡 Lãi suất tham khảo: **{rate_default[purpose]}%/năm**"
)

run=st.sidebar.button("📊 TÍNH TOÁN")

# ----------------------------------------------------------
# KIỂM TRA DỮ LIỆU
# ----------------------------------------------------------

def validate():
    if loan<=0:
        st.error("Số tiền vay không hợp lệ")
        return False
    if interest<=0:
        st.error("Lãi suất không hợp lệ")
        return False
    if income<=0:
        st.error("Thu nhập không hợp lệ")
        return False
    if interest>20:
        st.warning("⚠ Lãi suất khá cao.")
    return True

# ==========================================================
# HÀM TÍNH TRẢ GỐC ĐỀU
# ==========================================================

def equal_principal(principal, annual_rate, months):

    monthly_rate = annual_rate / 12 / 100
    principal_month = principal / months

    remain = principal
    total_interest = 0
    schedule = []

    for m in range(1, months + 1):
        interest = remain * monthly_rate
        payment = principal_month + interest

        remain -= principal_month
        remain = max(remain, 0)

        total_interest += interest

        schedule.append({
            "Tháng": m,
            "Gốc": round(principal_month, 2),
            "Lãi": round(interest, 2),
            "Thanh toán": round(payment, 2),
            "Dư nợ": round(remain, 2)
        })

    return pd.DataFrame(schedule), total_interest

# ==========================================================
# HÀM TÍNH TRẢ GÓP ĐỀU (ANNUITY)
# ==========================================================

def annuity(principal, annual_rate, months):

    r = annual_rate / 12 / 100

    payment = principal * r * (1 + r) ** months
    payment /= ((1 + r) ** months - 1)

    remain = principal
    total_interest = 0

    schedule = []

    for m in range(1, months + 1):
        interest = remain * r
        principal_pay = payment - interest

        remain -= principal_pay
        remain = max(remain, 0)

        total_interest += interest

        schedule.append({
            "Tháng": m,
            "Gốc": round(principal_pay, 2),
            "Lãi": round(interest, 2),
            "Thanh toán": round(payment, 2),
            "Dư nợ": round(remain, 2)
        })

    return pd.DataFrame(schedule), total_interest

# ==========================================================
# XỬ LÝ KHI NHẤN NÚT TÍNH TOÁN
# ==========================================================

if run:
    if validate():
        if method == "Trả gốc đều":
            schedule, total_interest = equal_principal(loan, interest, month)
        else:
            schedule, total_interest = annuity(loan, interest, month)

        total_payment = loan + total_interest # Đã sửa lỗi: total_payment = loan + total_interest
        first_payment = schedule.iloc[0]["Thanh toán"]
        last_payment = schedule.iloc[-1]["Thanh toán"]
        dti = first_payment / income * 100

        # ======================================================
        # DASHBOARD
        # ======================================================

        st.subheader("📊 KẾT QUẢ TÍNH TOÁN")

        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Tiền vay", money(loan))
        c2.metric("💸 Tổng lãi", money(total_interest))
        c3.metric("💳 Tổng thanh toán", money(total_payment))

        # ======================================================
        # SO SÁNH HAI PHƯƠNG THỨC
        # ======================================================

        principal_df, principal_interest = equal_principal(loan, interest, month)
        annuity_df, annuity_interest = annuity(loan, interest, month)

        compare = pd.DataFrame({
            "Tiêu chí": [
                "Tổng tiền lãi",
                "Tổng thanh toán",
                "Khoản trả tháng đầu"
            ],
            "Trả gốc đều": [
                money(principal_interest),
                money(loan + principal_interest),
                money(principal_df.iloc[0]["Thanh toán"])
            ],
            "Trả góp đều": [
                money(annuity_interest),
                money(loan + annuity_interest),
                money(annuity_df.iloc[0]["Thanh toán"])
            ]
        })

        st.subheader("⚖️ So sánh hai phương thức trả nợ")

        st.dataframe(
            compare,
            use_container_width=True,
            hide_index=True
        )

        # ======================================================
        # BẢNG LỊCH TRẢ NỢ
        # ======================================================

        st.subheader("📋 Lịch trả nợ theo từng tháng")

        display_schedule = schedule.copy()

        display_schedule["Gốc"] = display_schedule["Gốc"].apply(money)
        display_schedule["Lãi"] = display_schedule["Lãi"].apply(money)
        display_schedule["Thanh toán"] = display_schedule["Thanh toán"].apply(money)
        display_schedule["Dư nợ"] = display_schedule["Dư nợ"].apply(money)

        st.dataframe(
            display_schedule,
            use_container_width=True,
            hide_index=True
        )
# ======================================================
        # BIỂU ĐỒ
        # ======================================================

        st.subheader("📈 Trực quan khoản vay")

        # 🚨 DÒNG NÀY ĐỂ KHẮC PHỤC LỖI (Tạo 2 cột)
        col_chart1, col_chart2 = st.columns(2)

        # ------------------------------
        # Biểu đồ đường (Dư nợ theo năm)
        # ------------------------------
        with col_chart1:
            # 1. Lọc dữ liệu lấy dư nợ vào cuối mỗi năm (Tháng chia hết cho 12)
            yearly_schedule = schedule[schedule["Tháng"] % 12 == 0].copy()
            
            # ... (phần code vẽ biểu đồ bên trong) ...
        # ------------------------------
        # Biểu đồ đường (Dư nợ theo năm)
        # ------------------------------
        with col_chart1:
            # 1. Lọc dữ liệu lấy dư nợ vào cuối mỗi năm (Tháng chia hết cho 12)
            yearly_schedule = schedule[schedule["Tháng"] % 12 == 0].copy()
            yearly_schedule["Năm"] = yearly_schedule["Tháng"] // 12
            
            # 2. Thêm mốc Năm 0 (Dư nợ ban đầu lúc mới vay)
            year_0 = pd.DataFrame({"Năm": [0], "Dư nợ": [loan]})
            yearly_schedule = pd.concat([year_0, yearly_schedule], ignore_index=True)

            # 3. Vẽ biểu đồ đường với các điểm đánh dấu (markers)
            fig = px.line(
                yearly_schedule,
                x="Năm",
                y="Dư nợ",
                markers=True,
                title="Dư nợ giảm theo thời gian"
            )

            # 4. Cập nhật giao diện (ép phông chữ Times New Roman và chỉnh màu)
            fig.update_layout(
                height=420,
                xaxis_title="Năm",
                yaxis_title="Triệu đồng",
                font=dict(family="Times New Roman", color="#222222"),
                plot_bgcolor="white", # Nền trắng cho phần vẽ biểu đồ
                margin=dict(l=20, r=20, t=40, b=20)
            )

            # 5. Ép trục X hiển thị từng năm một (0, 1, 2, 3...) thay vì nhảy số
            fig.update_xaxes(dtick=1, showgrid=True, gridcolor='lightgrey')
            fig.update_yaxes(showgrid=True, gridcolor='lightgrey')

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # ------------------------------
        # Biểu đồ tròn
        # ------------------------------
        with col_chart2:
            pie = pd.DataFrame({
                "Khoản mục": ["Tiền gốc", "Tiền lãi"],
                "Giá trị": [loan, total_interest]
            })

            fig2 = px.pie(
                pie,
                names="Khoản mục",
                values="Giá trị",
                hole=0.45,
                title="Cơ cấu gốc và lãi"
            )

            fig2.update_traces(
                textposition="inside",
                textinfo="percent+label"
            )

            fig2.update_layout(
                height=420,
                font=dict(family="Times New Roman", color="#222222")
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

        # ======================================================
        # DTI
        # ======================================================

        st.subheader("💼 Đánh giá khả năng trả nợ")

        st.write(
            f"**DTI = {dti:.2f}%**"
        )

        st.progress(
            min(dti / 100,1.0)
        )

        if dti <= 40:
            st.success("🟢 Khả năng trả nợ tốt.")
        elif dti <= 60:
            st.warning("🟡 Cần cân nhắc thêm về khả năng trả nợ.")
        else:
            st.error("🔴 Rủi ro cao. Khoản thanh toán chiếm tỷ trọng lớn trong thu nhập.")

        # ======================================================
        # NHẬN XÉT TỰ ĐỘNG
        # ======================================================

        st.subheader("📝 Nhận xét")

        if method == "Trả góp đều":
            method_text = "trả góp đều"
        else:
            method_text = "trả gốc đều"

        comment = f"""
Khoản vay cho mục đích {purpose} 

với thời hạn **{years} năm ({month} tháng)**
lãi suất **{interest:.2f}%/năm**
theo phương thức **{method_text}**
có tổng tiền lãi là **{money(total_interest)}**.

Khoản thanh toán tháng đầu là **{money(first_payment)}**,
chiếm **{dti:.2f}%** thu nhập hàng tháng.
"""

        st.info(comment)

        # ======================================================
        # GỢI Ý TÀI CHÍNH
        # ======================================================

        st.subheader("💡 Gợi ý tài chính")

        if dti <= 40:
            st.success("""
Khả năng trả nợ đang ở mức **an toàn**.

Bạn hoàn toàn có thể duy trì khoản vay này nếu thu nhập ổn định.
""")
        elif dti <= 60:
            st.warning("""
Khoản vay ở mức **chấp nhận được**.

Bạn nên:
- Tăng thời hạn vay để giảm số tiền trả hàng tháng.
- Chuẩn bị quỹ dự phòng từ 3–6 tháng chi tiêu.
- Hạn chế phát sinh thêm các khoản vay mới.
""")
        else:
            st.error("""
Khoản vay có **rủi ro khá cao**.

Khuyến nghị:
- Giảm số tiền vay.
- Kéo dài thời hạn vay.
- Hoặc tăng thu nhập trước khi quyết định vay.
""")

        
        # ======================================================
        # THÔNG TIN KHOẢN VAY
        # ======================================================

        st.subheader("📌 Thông tin khoản vay")

        info = pd.DataFrame({
            "Thông tin": [
                "Mục đích vay",
                "Số tiền vay",
                "Lãi suất",
                "Thời hạn",
                "Thu nhập",
                "Phương thức"
            ],
            "Giá trị": [
                purpose,
                money(loan),
                f"{interest:.2f}%/năm",
                f"{years} năm ({month} tháng)",
                money(income),
                method
            ]
        })

        st.table(info)

        # ======================================================
        # FOOTER
        # ======================================================

        st.markdown("---")

        st.caption(
            """
Ứng dụng được xây dựng phục vụ học tập môn **Công nghệ tài chính**.

Các kết quả chỉ mang tính chất tham khảo trong tính toán khoản vay.
"""
        )

else:
    st.info("""
### 👋 Hướng dẫn sử dụng

1. Nhập thông tin khoản vay ở thanh bên trái.
2. Chọn phương thức trả nợ.
3. Nhấn **TÍNH TOÁN**.

Ứng dụng sẽ:
- Tính gốc và lãi.
- Hiển thị Dashboard.
- Hiển thị lịch trả nợ.
- Vẽ biểu đồ.
- Đánh giá khả năng trả nợ.
- So sánh hai phương thức trả nợ.
""")
# ==========================================================
# XỬ LÝ KHI NHẤN NÚT TÍNH TOÁN
# ==========================================================

if run:
    if validate():
        
        # Thêm dòng này để gọi hiệu ứng tuyết rơi
        st.snow()

        if method == "Trả gốc đều":
            schedule, total_interest = equal_principal(loan, interest, month)
        else:
            schedule, total_interest = annuity(loan, interest, month)
            
        # ... (các đoạn code tính toán bên dưới giữ nguyên) ...
