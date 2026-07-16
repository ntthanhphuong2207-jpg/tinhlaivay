# ==========================================================
# APP TÍNH TOÁN KHOẢN VAY NGÂN HÀNG
# Môn: Công nghệ tài chính
# Tác giả: ...
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO

# ----------------------------------------------------------
# CẤU HÌNH TRANG
# ----------------------------------------------------------

st.set_page_config(
    page_title="Ứng dụng tính khoản vay",
    page_icon="🏦",
    layout="wide"
)

# ----------------------------------------------------------
# CSS
# ----------------------------------------------------------

st.markdown("""
<style>

.main{
    background-color:#f8fafc;
}

.metric-container{
    padding:15px;
    border-radius:12px;
}

h1,h2,h3{
    color:#003366;
}

.stButton>button{
    width:100%;
    border-radius:10px;
    height:45px;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------
# TIÊU ĐỀ
# ----------------------------------------------------------

st.title("🏦 Ứng dụng tính toán khoản vay")

st.write("""
Ứng dụng hỗ trợ tính toán khoản vay ngân hàng theo hai phương thức trả nợ:

- Trả gốc đều
- Trả góp đều (Annuity)

Đơn vị nhập liệu: **Triệu đồng**
""")

# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.header("Nhập thông tin khoản vay")

loan_type = st.sidebar.selectbox(
    "Mục đích vay",
    [
        "Mua nhà",
        "Mua xe",
        "Tiêu dùng",
        "Kinh doanh",
        "Khác"
    ]
)

loan_amount = st.sidebar.number_input(
    "Số tiền vay (triệu đồng)",
    min_value=1.0,
    value=500.0,
    step=10.0
)

interest = st.sidebar.number_input(
    "Lãi suất (%/năm)",
    min_value=0.1,
    value=8.0,
    step=0.1
)

months = st.sidebar.number_input(
    "Thời hạn vay (tháng)",
    min_value=1,
    value=120
)

income = st.sidebar.number_input(
    "Thu nhập hàng tháng (triệu đồng)",
    min_value=1.0,
    value=25.0,
    step=1.0
)

method = st.sidebar.radio(
    "Phương thức trả nợ",
    (
        "Trả gốc đều",
        "Trả góp đều"
    )
)

calculate = st.sidebar.button("Tính toán")

# ==========================================================
# HÀM KIỂM TRA
# ==========================================================

def validate_input():

    if loan_amount <= 0:
        st.error("Số tiền vay không hợp lệ")
        return False

    if interest <= 0:
        st.error("Lãi suất không hợp lệ")
        return False

    if months <= 0:
        st.error("Thời hạn vay không hợp lệ")
        return False

    if income <= 0:
        st.error("Thu nhập không hợp lệ")
        return False

    return True

# ==========================================================
# HÀM TÍNH GỐC ĐỀU
# ==========================================================

def equal_principal(principal, annual_rate, months):

    monthly_rate = annual_rate / 12 / 100

    principal_payment = principal / months

    remain = principal

    schedule = []

    total_interest = 0

    for month in range(1, months + 1):

        interest_payment = remain * monthly_rate

        total_payment = principal_payment + interest_payment

        remain -= principal_payment

        if remain < 0:
            remain = 0

        total_interest += interest_payment

        schedule.append({

            "Tháng": month,

            "Gốc": round(principal_payment,2),

            "Lãi": round(interest_payment,2),

            "Tổng thanh toán": round(total_payment,2),

            "Dư nợ": round(remain,2)

        })

    df = pd.DataFrame(schedule)

    return df, total_interest

# ==========================================================
# HÀM TÍNH TRẢ GÓP ĐỀU (ANNUITY)
# ==========================================================

def annuity(principal, annual_rate, months):

    monthly_rate = annual_rate / 12 / 100

    payment = principal * monthly_rate * (1 + monthly_rate) ** months

    payment /= ((1 + monthly_rate) ** months - 1)

    remain = principal

    total_interest = 0

    schedule = []

    for month in range(1, months + 1):

        interest_payment = remain * monthly_rate

        principal_payment = payment - interest_payment

        remain -= principal_payment

        if remain < 0:
            remain = 0

        total_interest += interest_payment

        schedule.append({

            "Tháng": month,

            "Gốc": round(principal_payment,2),

            "Lãi": round(interest_payment,2),

            "Tổng thanh toán": round(payment,2),

            "Dư nợ": round(remain,2)

        })

    df = pd.DataFrame(schedule)

    return df, total_interest

# ==========================================================
# CHỌN PHƯƠNG THỨC TÍNH
# ==========================================================

if calculate:

    if validate_input():

        if method == "Trả gốc đều":

            schedule, total_interest = equal_principal(
                loan_amount,
                interest,
                months
            )

        else:

            schedule, total_interest = annuity(
                loan_amount,
                interest,
                months
            )

        total_payment = loan_amount + total_interest
              # ==========================================================
        # DASHBOARD TỔNG QUAN
        # ==========================================================

        st.divider()
        st.subheader("📊 Kết quả tính toán")

        first_payment = schedule.iloc[0]["Tổng thanh toán"]
        last_payment = schedule.iloc[-1]["Tổng thanh toán"]

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                "💰 Tiền vay",
                f"{loan_amount:,.2f} triệu"
            )

        with col2:
            st.metric(
                "💸 Tổng lãi",
                f"{total_interest:,.2f} triệu"
            )

        with col3:
            st.metric(
                "💵 Tổng phải trả",
                f"{total_payment:,.2f} triệu"
            )

        with col4:
            st.metric(
                "📅 Tháng đầu",
                f"{first_payment:,.2f} triệu"
            )

        with col5:
            st.metric(
                "🏁 Tháng cuối",
                f"{last_payment:,.2f} triệu"
            )

        st.divider()

        # ==========================================================
        # THÔNG TIN KHOẢN VAY
        # ==========================================================

        info1, info2 = st.columns(2)

        with info1:

            st.info(f"""
**Mục đích vay:** {loan_type}

**Phương thức trả nợ:** {method}

**Lãi suất:** {interest:.2f}%/năm
""")

        with info2:

            monthly_rate = interest / 12

            st.success(f"""
**Số tiền vay:** {loan_amount:,.2f} triệu đồng

**Thời hạn:** {months} tháng

**Lãi suất tháng:** {monthly_rate:.3f}%
""")

        st.divider()

        # ==========================================================
        # BẢNG LỊCH TRẢ NỢ
        # ==========================================================

        st.subheader("📑 Lịch trả nợ")

        schedule_display = schedule.copy()

        schedule_display["Gốc"] = schedule_display["Gốc"].map(
            lambda x: f"{x:,.2f}"
        )

        schedule_display["Lãi"] = schedule_display["Lãi"].map(
            lambda x: f"{x:,.2f}"
        )

        schedule_display["Tổng thanh toán"] = schedule_display[
            "Tổng thanh toán"
        ].map(lambda x: f"{x:,.2f}")

        schedule_display["Dư nợ"] = schedule_display[
            "Dư nợ"
        ].map(lambda x: f"{x:,.2f}")

        st.dataframe(
            schedule_display,
            use_container_width=True,
            hide_index=True,
            height=500
        )

        st.divider()

        # ==========================================================
        # BIỂU ĐỒ DƯ NỢ
        # ==========================================================

        st.subheader("📉 Biểu đồ dư nợ giảm dần")

        fig = px.line(
            schedule,
            x="Tháng",
            y="Dư nợ",
            markers=True,
            title="Dư nợ còn lại theo từng tháng"
        )

        fig.update_layout(
            xaxis_title="Tháng",
            yaxis_title="Triệu đồng",
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.divider()

        # ==========================================================
        # ĐÁNH GIÁ KHẢ NĂNG TRẢ NỢ
        # ==========================================================

        st.subheader("📝 Đánh giá khả năng trả nợ")

        payment_ratio = first_payment / income * 100

        colA, colB = st.columns(2)

        with colA:

            st.metric(
                "Thu nhập hàng tháng",
                f"{income:,.2f} triệu"
            )

        with colB:

            st.metric(
                "DTI",
                f"{payment_ratio:.2f}%"
            )

        if payment_ratio <= 40:

            st.success(f"""
### 🟢 An toàn

Khoản thanh toán tháng đầu chiếm **{payment_ratio:.2f}%**
thu nhập.

Khả năng trả nợ được đánh giá **tốt**.
""")

        elif payment_ratio <= 60:

            st.warning(f"""
### 🟡 Cần cân nhắc

Khoản thanh toán tháng đầu chiếm **{payment_ratio:.2f}%**
thu nhập.

Bạn nên cân nhắc giảm số tiền vay hoặc kéo dài thời hạn.
""")

        else:

            st.error(f"""
### 🔴 Rủi ro cao

Khoản thanh toán tháng đầu chiếm **{payment_ratio:.2f}%**
thu nhập.

Nguy cơ áp lực tài chính lớn.
""")
                  # ==========================================================
        # XUẤT EXCEL
        # ==========================================================

        st.divider()
        st.subheader("📥 Xuất lịch trả nợ")

        def convert_excel(df):

            output = BytesIO()

            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(
                    writer,
                    index=False,
                    sheet_name="Lich tra no"
                )

            output.seek(0)

            return output

        excel_file = convert_excel(schedule)

        st.download_button(
            label="📥 Tải lịch trả nợ (.xlsx)",
            data=excel_file,
            file_name="Lich_tra_no.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # ==========================================================
        # THỐNG KÊ NHANH
        # ==========================================================

        st.divider()
        st.subheader("📈 Thống kê nhanh")

        avg_payment = schedule["Tổng thanh toán"].mean()
        max_interest = schedule["Lãi"].max()
        min_interest = schedule["Lãi"].min()

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Thanh toán TB",
                f"{avg_payment:,.2f} triệu"
            )

        with c2:
            st.metric(
                "Lãi cao nhất",
                f"{max_interest:,.2f} triệu"
            )

        with c3:
            st.metric(
                "Lãi thấp nhất",
                f"{min_interest:,.2f} triệu"
            )

        # ==========================================================
        # KẾT LUẬN
        # ==========================================================

        st.divider()

        st.subheader("📌 Kết luận")

        if method == "Trả gốc đều":

            st.info("""
**Đặc điểm phương thức trả gốc đều**

• Tiền gốc trả cố định mỗi tháng.

• Tiền lãi giảm dần theo dư nợ.

• Khoản thanh toán giảm dần theo thời gian.

• Tổng tiền lãi thường thấp hơn so với trả góp đều.
""")

        else:

            st.info("""
**Đặc điểm phương thức trả góp đều (Annuity)**

• Tổng tiền thanh toán mỗi tháng gần như bằng nhau.

• Các tháng đầu trả nhiều lãi hơn.

• Các tháng cuối trả nhiều gốc hơn.

• Phù hợp với người muốn ổn định dòng tiền hàng tháng.
""")

        # ==========================================================
        # FOOTER
        # ==========================================================

        st.divider()

        st.caption(
            """
Ứng dụng được xây dựng phục vụ học tập môn **Công nghệ tài chính**.

Chức năng:

✔ Tính khoản vay

✔ Hai phương thức trả nợ

✔ Lịch trả nợ

✔ Biểu đồ trực quan

✔ Đánh giá khả năng trả nợ

Đơn vị tính: **Triệu đồng**
"""
        )

else:

    st.info("👈 Vui lòng nhập thông tin khoản vay ở thanh bên trái và nhấn **Tính toán**.")
