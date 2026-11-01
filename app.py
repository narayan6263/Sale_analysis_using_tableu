# import os
# import pandas as pd
# import streamlit as st
# from sqlalchemy import create_engine

# # MySQL connection. Password apne hisaab se badlo, ya MYSQL_URL environment variable set karo.
# DB_URL = os.getenv(
#     "MYSQL_URL",
#     "mysql+pymysql://root:password@localhost:3306/salesdb",
# )
# TABLE_NAME = "processed_sales"
# engine = create_engine(DB_URL)


# def process_data(df: pd.DataFrame) -> pd.DataFrame:
#     """Raw CSV ko clean aur transform karta hai."""
#     df = df.copy()

#     # Column names saaf karo: "Order Date" -> "order_date"
#     df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

#     required = ["order_date", "region", "category", "sales", "cost"]
#     missing = [c for c in required if c not in df.columns]
#     if missing:
#         raise ValueError(f"CSV mein ye columns nahi mile: {missing}")

#     # Duplicate rows hatao
#     df = df.drop_duplicates()

#     # Data types theek karo
#     df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
#     df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
#     df["cost"] = pd.to_numeric(df["cost"], errors="coerce")
#     df["region"] = df["region"].fillna("Unknown").str.strip()
#     df["category"] = df["category"].fillna("Unknown").str.strip()

#     # Kharab rows hatao (date, sales ya cost missing ho to)
#     df = df.dropna(subset=["order_date", "sales", "cost"])

#     # Naye columns banao
#     df["profit"] = df["sales"] - df["cost"]
#     df["order_month"] = df["order_date"].dt.to_period("M").astype(str)

#     return df


# st.set_page_config(page_title="CSV Pipeline", layout="wide")
# st.title("CSV Upload → Process → MySQL")

# uploaded = st.file_uploader("CSV file upload karo", type=["csv"])
# replace = st.checkbox("Purana table replace karo (nahi to data add hoga)", value=False)

# if uploaded is not None:
#     try:
#         raw_df = pd.read_csv(uploaded)

#         st.subheader("1. Raw data")
#         st.dataframe(raw_df.head())

#         processed_df = process_data(raw_df)

#         st.subheader("2. Processed data")
#         st.dataframe(processed_df.head())
#         st.write(f"Raw rows: {len(raw_df)} | Processed rows: {len(processed_df)}")

#         if st.button("MySQL mein save karo"):
#             mode = "replace" if replace else "append"
#             processed_df.to_sql(TABLE_NAME, engine, if_exists=mode, index=False)
#             st.success(f"{len(processed_df)} rows '{TABLE_NAME}' table mein save ho gaye.")

#     except ValueError as e:
#         st.error(str(e))
#     except Exception as e:
#         st.error(f"Kuch galat hua: {e}")
import os

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

# ---------- CONFIG ----------
DB_URL = os.getenv(
    "MYSQL_URL",
    "mysql+pymysql://root:password@localhost:3306/salesdb",
)
TABLE_NAME = "processed_sales"
REQUIRED = ["order_date", "region", "category", "sales", "cost"]

st.set_page_config(page_title="Sales Pipeline", page_icon="📊", layout="wide")

# ---------- STYLE ----------
st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; max-width: 1200px;}
    .hero {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        padding: 1.6rem 2rem; border-radius: 16px; color: white; margin-bottom: 1.5rem;
    }
    .hero h1 {margin: 0; font-size: 2rem; color: white;}
    .hero p {margin: .3rem 0 0; opacity: .9;}
    .kpi {
        background: #ffffff; border: 1px solid #e5e7eb; border-radius: 14px;
        padding: 1rem 1.2rem; box-shadow: 0 1px 3px rgba(0,0,0,.06);
    }
    .kpi .label {color: #6b7280; font-size: .8rem; text-transform: uppercase; letter-spacing: .05em;}
    .kpi .value {color: #111827; font-size: 1.6rem; font-weight: 700; margin-top: .2rem;}
    .kpi.good .value {color: #059669;}
    .kpi.bad .value {color: #dc2626;}
    .step {
        display: flex; align-items: center; gap: .6rem; padding: .5rem 0; color: #374151;
    }
    .badge {
        background: #eef2ff; color: #4f46e5; border-radius: 50%;
        width: 26px; height: 26px; display: inline-flex;
        align-items: center; justify-content: center; font-weight: 700; font-size: .8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def kpi(label: str, value: str, tone: str = "") -> str:
    return f'<div class="kpi {tone}"><div class="label">{label}</div><div class="value">{value}</div></div>'


@st.cache_resource
def get_engine():
    return create_engine(DB_URL, pool_pre_ping=True)


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """Raw CSV ko clean aur transform karta hai."""
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"CSV mein ye columns nahi mile: {missing}")

    df = df.drop_duplicates()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
    df["cost"] = pd.to_numeric(df["cost"], errors="coerce")
    df["region"] = df["region"].fillna("Unknown").astype(str).str.strip()
    df["category"] = df["category"].fillna("Unknown").astype(str).str.strip()
    df = df.dropna(subset=["order_date", "sales", "cost"])

    df["profit"] = df["sales"] - df["cost"]
    df["order_month"] = df["order_date"].dt.to_period("M").astype(str)
    return df


# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("⚙️ Settings")
    uploaded = st.file_uploader("CSV upload karo", type=["csv"])
    replace = st.toggle("Purana table replace karo", value=False,
                        help="Off = naya data purane ke neeche add hoga")
    st.divider()
    st.markdown("**Pipeline steps**")
    for i, s in enumerate(["Upload CSV", "Clean & transform", "Preview & charts", "Save to MySQL"], 1):
        st.markdown(f'<div class="step"><span class="badge">{i}</span>{s}</div>', unsafe_allow_html=True)
    st.divider()
    st.caption(f"Table: `{TABLE_NAME}`")
    st.caption("Required columns: " + ", ".join(f"`{c}`" for c in REQUIRED))

# ---------- HEADER ----------
st.markdown(
    '<div class="hero"><h1>📊 Sales Data Pipeline</h1>'
    "<p>CSV upload → clean → analyse → MySQL mein save</p></div>",
    unsafe_allow_html=True,
)

if uploaded is None:
    st.info("👈 Sidebar se CSV file upload karo. Shuru karne ke liye ek sample format:")
    st.dataframe(
        pd.DataFrame(
            {
                "Order Date": ["2024-01-05", "2024-01-09"],
                "Region": ["North", "South"],
                "Category": ["Electronics", "Furniture"],
                "Sales": [1200, 800],
                "Cost": [900, 650],
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
    st.stop()

# ---------- PROCESS ----------
try:
    raw_df = pd.read_csv(uploaded)
    processed_df = process_data(raw_df)
except ValueError as e:
    st.error(str(e))
    st.stop()
except Exception as e:
    st.error(f"File padhne mein dikkat: {e}")
    st.stop()

dupes = len(raw_df) - len(raw_df.drop_duplicates())
dropped = len(raw_df) - len(processed_df)

total_sales = processed_df["sales"].sum()
total_cost = processed_df["cost"].sum()
total_profit = processed_df["profit"].sum()
margin = (total_profit / total_sales * 100) if total_sales else 0

# ---------- KPIs ----------
c1, c2, c3, c4 = st.columns(4)
c1.markdown(kpi("Total Sales", f"{total_sales:,.0f}"), unsafe_allow_html=True)
c2.markdown(kpi("Total Cost", f"{total_cost:,.0f}"), unsafe_allow_html=True)
c3.markdown(kpi("Profit", f"{total_profit:,.0f}", "good" if total_profit >= 0 else "bad"), unsafe_allow_html=True)
c4.markdown(kpi("Margin", f"{margin:.1f}%", "good" if margin >= 0 else "bad"), unsafe_allow_html=True)

st.write("")

# ---------- TABS ----------
tab_charts, tab_proc, tab_raw, tab_report = st.tabs(
    ["📈 Charts", "✅ Processed data", "📄 Raw data", "🧹 Cleaning report"]
)

with tab_charts:
    left, right = st.columns(2)
    with left:
        st.subheader("Monthly profit")
        monthly = processed_df.groupby("order_month")["profit"].sum().sort_index()
        st.line_chart(monthly)
    with right:
        st.subheader("Sales by region")
        st.bar_chart(processed_df.groupby("region")["sales"].sum().sort_values(ascending=False))
    st.subheader("Profit by category")
    st.bar_chart(processed_df.groupby("category")["profit"].sum().sort_values(ascending=False))

with tab_proc:
    st.dataframe(processed_df.head(200), use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Processed CSV download karo",
        processed_df.to_csv(index=False).encode("utf-8"),
        file_name="processed_sales.csv",
        mime="text/csv",
    )

with tab_raw:
    st.dataframe(raw_df.head(200), use_container_width=True, hide_index=True)

with tab_report:
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Raw rows", f"{len(raw_df):,}")
    r2.metric("Duplicates hataye", f"{dupes:,}")
    r3.metric("Kharab rows hataye", f"{dropped - dupes:,}")
    r4.metric("Final rows", f"{len(processed_df):,}")
    st.caption("Kharab row = jisme date, sales ya cost missing/galat tha.")

# ---------- SAVE ----------
st.divider()
st.subheader("💾 MySQL mein save karo")
mode_text = "replace (purana table delete)" if replace else "append (data add)"
st.write(f"Mode: **{mode_text}** · Rows: **{len(processed_df):,}**")

if st.button("Save to MySQL", type="primary"):
    try:
        with st.spinner("Save ho raha hai..."):
            processed_df.to_sql(
                TABLE_NAME,
                get_engine(),
                if_exists="replace" if replace else "append",
                index=False,
                chunksize=1000,
                method="multi",
            )
        st.success(f"✅ {len(processed_df):,} rows '{TABLE_NAME}' table mein save ho gaye.")
        st.balloons()
    except Exception as e:
        st.error(f"Save nahi hua: {e}")