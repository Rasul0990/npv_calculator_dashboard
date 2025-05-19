import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

# 🎯 Title
st.title("💸 NPV Calculator Dashboard")

# 📂 Upload section with fallback default data
uploaded_file = st.file_uploader("Upload your Excel file (.xlsx)", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name=0, engine='openpyxl', header=0)
    st.info("✅ File uploaded successfully.")
else:
    st.info("📎 Using default example data from 2025–2035.")
    df = pd.DataFrame({
        "Year": list(range(2025, 2036)),
        "Startup": [-20, -30, -20, -40, -10, 0, 25, 80, 200, 400, 1000],
        "Cash Flow": [300, 305, 290, 310, 300, 303, 320, 299, 315, 320, 315]
    })

# 🧹 Clean and validate
df = df[pd.to_numeric(df["Startup"], errors='coerce').notnull()]
all_years = sorted(df["Year"].unique())
startup = df["Startup"].tolist()
cashflow = df["Cash Flow"].tolist()

# 🎛️ Sidebar controls
st.sidebar.header("🔧 Controls")
interest = st.sidebar.slider("Interest Rate (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1)
start_year = st.sidebar.selectbox("Start Year", all_years, index=0)
end_year = st.sidebar.selectbox("End Year", all_years, index=len(all_years)-1)

if start_year > end_year:
    st.error("⚠️ Start year must be before or equal to end year.")
else:
    # Filter data by year range
    filtered = [(y, s, c) for y, s, c in zip(all_years, startup, cashflow) if start_year <= y <= end_year]

    if not filtered:
        st.warning("⚠️ No data in selected range.")
    else:
        years, s_vals, c_vals = zip(*filtered)

        # 🔢 Discounting function
        def discount(values, rate):
            return [round(v / (1 + rate) ** i, 2) for i, v in enumerate(values)]

        r = interest / 100
        startup_d = discount(s_vals, r)
        cashflow_d = discount(c_vals, r)
        npv_values = [round(c - s, 2) for s, c in zip(startup_d, cashflow_d)]
        total_npv = round(sum(npv_values), 2)

        # 📈 Plotting
        fig, ax = plt.subplots(figsize=(10, 5))
        x = np.arange(len(years))
        width = 0.35
        ax.bar(x - width/2, startup_d, width=width, label='Startup', color='steelblue')
        ax.bar(x + width/2, cashflow_d, width=width, label='Cash Flow', color='orange', alpha=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(years)
        ax.set_title(f"Discounted Flows at {interest:.2f}%")
        ax.set_xlabel("Year")
        ax.set_ylabel("Value")
        ax.legend()
        st.pyplot(fig)

        # 📋 Table
        table_df = pd.DataFrame({
            'Year': years,
            'Startup': s_vals,
            'Cash Flow': c_vals,
            f'Startup_disc ({interest:.2f}%)': startup_d,
            f'CashFlow_disc ({interest:.2f}%)': cashflow_d,
            'NPV (Cash - Startup)': npv_values
        })

        st.subheader("📋 Discounted Values Table")
        st.dataframe(table_df)

        # 💰 NPV Result
        st.success(f"💰 Total NPV: **{total_npv}**")

        # 📥 Excel download
        @st.cache_data
        def to_excel(df):
            from io import BytesIO
            out = BytesIO()
            with pd.ExcelWriter(out, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            return out.getvalue()

        excel_data = to_excel(table_df)
        st.download_button(
            label="📥 Download as Excel",
            data=excel_data,
            file_name="discounted_npv.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
