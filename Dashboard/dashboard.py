import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style="whitegrid")

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="E-Commerce Public Dataset Dashboard",
    page_icon="🛒",
    layout="wide"
)


@st.cache_data
def load_data() -> pd.DataFrame:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "main_data.csv")
    df = pd.read_csv(file_path)
    datetime_cols = [
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
    for col in datetime_cols:
        df[col] = pd.to_datetime(df[col])
    return df


def create_monthly_trend_df(df: pd.DataFrame) -> pd.DataFrame:
    temp = df.copy()
    temp["year_month"] = temp["order_purchase_timestamp"].dt.to_period("M").astype(str)
    monthly = temp.groupby("year_month", as_index=False).agg(
        order_count=("order_id", "nunique"),
        total_revenue=("price", "sum")
    ).sort_values("year_month")
    return monthly


def create_category_perf_df(df: pd.DataFrame) -> pd.DataFrame:
    cat_df = df.groupby("product_category_name_english", as_index=False).agg(
        total_revenue=("price", "sum"),
        total_orders=("order_id", "nunique"),
        total_items=("order_item_id", "count")
    ).sort_values(by="total_revenue", ascending=False)
    return cat_df


def create_delivery_review_df(df: pd.DataFrame) -> pd.DataFrame:
    order_level = df.drop_duplicates(subset=["order_id"]).dropna(subset=["review_score"])
    summary = order_level.groupby("delivery_status", as_index=False).agg(
        order_count=("order_id", "count"),
        avg_review_score=("review_score", "mean")
    )
    return summary


def create_state_delivery_df(df: pd.DataFrame) -> pd.DataFrame:
    order_level = df.drop_duplicates(subset=["order_id"]).dropna(subset=["review_score"])
    state_df = order_level.groupby("customer_state", as_index=False).agg(
        total_orders=("order_id", "count"),
        late_orders=("delivery_status", lambda x: (x == "Late").sum()),
        avg_review_score=("review_score", "mean")
    )
    state_df["late_rate"] = (state_df["late_orders"] / state_df["total_orders"]) * 100
    return state_df


def create_rfm_df(df: pd.DataFrame) -> pd.DataFrame:
    recent_date = df["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
    rfm = df.groupby("customer_unique_id", as_index=False).agg(
        max_order_timestamp=("order_purchase_timestamp", "max"),
        frequency=("order_id", "nunique"),
        monetary=("price", "sum")
    )
    rfm["recency"] = (recent_date - rfm["max_order_timestamp"]).dt.days
    rfm.drop(columns=["max_order_timestamp"], inplace=True)

    if len(rfm) >= 4 and rfm["recency"].nunique() >= 4 and rfm["monetary"].nunique() >= 4:
        rfm["r_score"] = pd.qcut(rfm["recency"].rank(method="first"), q=4, labels=[4, 3, 2, 1]).astype(int)
        rfm["m_score"] = pd.qcut(rfm["monetary"].rank(method="first"), q=4, labels=[1, 2, 3, 4]).astype(int)
    else:
        rfm["r_score"] = 3
        rfm["m_score"] = 3

    def assign_segment(row):
        if row["frequency"] >= 2 and row["r_score"] >= 3 and row["m_score"] >= 3:
            return "Champions / Loyal"
        elif row["r_score"] >= 3 and row["m_score"] >= 3:
            return "Potential Loyalists (High Value)"
        elif row["r_score"] >= 3:
            return "Recent Customers"
        elif row["r_score"] == 2:
            return "Need Attention"
        else:
            return "At Risk / Hibernating"

    rfm["segment"] = rfm.apply(assign_segment, axis=1)
    return rfm


# --- LOAD DATA ---
all_df = load_data()

# --- SIDEBAR FILTER ---
with st.sidebar:
    st.title("🛒 E-Commerce Analytics")
    st.markdown("**Nama:** Satria Dwi Cahya Fatiawan\n**ID Dicoding:** satriadc")
    st.divider()

    min_date = all_df["order_purchase_timestamp"].min().date()
    max_date = all_df["order_purchase_timestamp"].max().date()

    default_start = max(min_date, pd.to_datetime("2017-01-01").date())
    default_end = min(max_date, pd.to_datetime("2018-08-31").date())

    date_range = st.date_input(
        label="Rentang Tanggal Pembelian",
        min_value=min_date,
        max_value=max_date,
        value=[default_start, default_end]
    )

    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = default_start, default_end

    states = sorted(all_df["customer_state"].dropna().unique().tolist())
    selected_states = st.multiselect(
        label="Filter Negara Bagian (State)",
        options=states,
        default=[]
    )

# Terapkan filter
main_df = all_df[
    (all_df["order_purchase_timestamp"].dt.date >= start_date) &
    (all_df["order_purchase_timestamp"].dt.date <= end_date)
].copy()

if selected_states:
    main_df = main_df[main_df["customer_state"].isin(selected_states)].copy()

if main_df.empty:
    st.warning("Tidak ada data transaksi pada filter yang dipilih. Silakan ubah rentang tanggal atau negara bagian.")
    st.stop()

# --- HEADER & KPI METRICS ---
st.title("📊 E-Commerce Public Dataset Dashboard")
st.caption(f"Periode Analisis: {start_date} s.d. {end_date}")

total_orders = main_df["order_id"].nunique()
total_revenue = main_df["price"].sum()
order_unique = main_df.drop_duplicates(subset=["order_id"])
avg_review = order_unique["review_score"].mean()
late_pct = (order_unique["delivery_status"] == "Late").mean() * 100

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Pesanan (Delivered)", f"{total_orders:,}")
with col2:
    st.metric("Total Pendapatan (Revenue)", f"BRL {total_revenue:,.2f}")
with col3:
    st.metric("Rata-rata Skor Ulasan", f"{avg_review:.2f} / 5.00")
with col4:
    st.metric("Tingkat Keterlambatan", f"{late_pct:.2f}%")

st.divider()

# --- BAGIAN 1: TREN BULANAN & PERFORMA KATEGORI ---
st.subheader("1. Tren Pertumbuhan Pesanan, Revenue Bulanan, & Performa Kategori Produk")

monthly_df = create_monthly_trend_df(main_df)
category_df = create_category_perf_df(main_df)

tab1, tab2 = st.tabs(["📈 Tren Bulanan", "🏆 Kategori Produk (Top & Bottom 10)"])

with tab1:
    fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(14, 8), sharex=True)
    sns.lineplot(
        data=monthly_df, x="year_month", y="total_revenue",
        marker="o", linewidth=2.5, color="#1f77b4", ax=ax[0]
    )
    ax[0].set_title("Tren Total Pendapatan (Revenue) Bulanan", fontsize=13, fontweight="bold")
    ax[0].set_ylabel("Revenue (BRL)")
    ax[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))

    sns.lineplot(
        data=monthly_df, x="year_month", y="order_count",
        marker="s", linewidth=2.5, color="#2ca02c", ax=ax[1]
    )
    ax[1].set_title("Tren Jumlah Pesanan Bulanan", fontsize=13, fontweight="bold")
    ax[1].set_ylabel("Jumlah Pesanan")
    ax[1].set_xlabel("Bulan")
    ax[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with tab2:
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(16, 6))
    top_10 = category_df.head(10)
    bot_10 = category_df.tail(10).sort_values(by="total_revenue", ascending=True)

    colors_top = ["#1f77b4" if i == 0 else "#a6c8e0" for i in range(len(top_10))]
    sns.barplot(
        data=top_10, x="total_revenue", y="product_category_name_english",
        hue="product_category_name_english", palette=colors_top, dodge=False, ax=ax[0]
    )
    if ax[0].get_legend():
        ax[0].get_legend().remove()
    ax[0].set_title("Top 10 Kategori Revenue Tertinggi", fontsize=12, fontweight="bold")
    ax[0].set_xlabel("Total Revenue (BRL)")
    ax[0].set_ylabel(None)
    ax[0].xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
    for bar in ax[0].patches:
        w = bar.get_width()
        if w > 0:
            ax[0].text(w + top_10["total_revenue"].max() * 0.015, bar.get_y() + bar.get_height() / 2,
                       f"{w:,.0f}", va="center", ha="left", fontsize=9)
    ax[0].set_xlim(0, top_10["total_revenue"].max() * 1.18)

    colors_bot = ["#d62728" if i == 0 else "#f2a6a6" for i in range(len(bot_10))]
    sns.barplot(
        data=bot_10, x="total_revenue", y="product_category_name_english",
        hue="product_category_name_english", palette=colors_bot, dodge=False, ax=ax[1]
    )
    if ax[1].get_legend():
        ax[1].get_legend().remove()
    ax[1].set_title("Bottom 10 Kategori Revenue Terendah", fontsize=12, fontweight="bold")
    ax[1].set_xlabel("Total Revenue (BRL)")
    ax[1].set_ylabel(None)
    for bar in ax[1].patches:
        w = bar.get_width()
        if w > 0:
            ax[1].text(w + bot_10["total_revenue"].max() * 0.015, bar.get_y() + bar.get_height() / 2,
                       f"{w:,.0f}", va="center", ha="left", fontsize=9)
    ax[1].set_xlim(0, bot_10["total_revenue"].max() * 1.18)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

st.divider()

# --- BAGIAN 2: HUBUNGAN KETERLAMBATAN PENGIRIMAN TERHADAP SKOR ULASAN ---
st.subheader("2. Hubungan Keterlambatan Pengiriman terhadap Skor Ulasan Pelanggan per Negara Bagian")

delivery_rev_df = create_delivery_review_df(main_df)
state_deliv_df = create_state_delivery_df(main_df)

min_orders_filter = 100 if len(state_deliv_df[state_deliv_df["total_orders"] >= 100]) > 0 else 1
state_filtered = state_deliv_df[state_deliv_df["total_orders"] >= min_orders_filter].copy()
top_states = state_filtered.sort_values(by="late_rate", ascending=False).head(10)

col_left, col_mid, col_right = st.columns(3)

with col_left:
    fig, ax = plt.subplots(figsize=(6, 5))
    order_list = [s for s in ["On Time", "Late"] if s in delivery_rev_df["delivery_status"].values]
    plot_deliv = delivery_rev_df.set_index("delivery_status").loc[order_list].reset_index()
    palette_map = {"On Time": "#2ca02c", "Late": "#d62728"}
    sns.barplot(
        data=plot_deliv, x="delivery_status", y="avg_review_score",
        hue="delivery_status", palette=palette_map, dodge=False, ax=ax, width=0.5
    )
    if ax.get_legend():
        ax.get_legend().remove()
    ax.set_title("Rata-rata Skor Ulasan:\nOn Time vs Late", fontsize=11, fontweight="bold")
    ax.set_xlabel("Status Pengiriman")
    ax.set_ylabel("Rata-rata Review Score (1-5)")
    ax.set_ylim(0, 5.2)
    for bar in ax.patches:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.1,
                    f"{h:.2f}", ha="center", va="bottom", fontsize=11, fontweight="bold")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with col_mid:
    fig, ax = plt.subplots(figsize=(6, 5))
    if len(state_filtered) >= 2 and state_filtered["late_rate"].nunique() > 1:
        corr_r = state_filtered["late_rate"].corr(state_filtered["avg_review_score"], method="pearson")
        sns.regplot(
            data=state_filtered, x="late_rate", y="avg_review_score",
            scatter_kws={"s": 60, "alpha": 0.8, "color": "#1f77b4"},
            line_kws={"color": "#d62728", "linewidth": 2},
            ax=ax
        )
        for _, row in state_filtered.iterrows():
            if row["late_rate"] > 15 or row["customer_state"] in ["SP", "RJ", "MG"]:
                ax.text(row["late_rate"] + 0.3, row["avg_review_score"], row["customer_state"], fontsize=8.5, fontweight="bold")
        ax.set_title(f"Korelasi Keterlambatan vs Skor Ulasan\nper State (Pearson r = {corr_r:.2f})", fontsize=11, fontweight="bold")
    else:
        sns.scatterplot(data=state_filtered, x="late_rate", y="avg_review_score", s=80, color="#1f77b4", ax=ax)
        ax.set_title("Keterlambatan vs Skor Ulasan per State", fontsize=11, fontweight="bold")
    ax.set_xlabel("Persentase Terlambat (%)")
    ax.set_ylabel("Rata-rata Review Score")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with col_right:
    fig, ax = plt.subplots(figsize=(6, 5))
    state_colors = ["#d62728" if i == 0 else "#f2a6a6" for i in range(len(top_states))]
    sns.barplot(
        data=top_states, x="late_rate", y="customer_state",
        hue="customer_state", palette=state_colors, dodge=False, ax=ax
    )
    if ax.get_legend():
        ax.get_legend().remove()
    ax.set_title(f"Top 10 State Keterlambatan Tertinggi\n(Min. {min_orders_filter} Pesanan)", fontsize=11, fontweight="bold")
    ax.set_xlabel("Persentase Terlambat (%)")
    ax.set_ylabel("Customer State")
    ax.set_xlim(0, top_states["late_rate"].max() * 1.18)
    for bar in ax.patches:
        w = bar.get_width()
        if w > 0:
            ax.text(w + top_states["late_rate"].max() * 0.015, bar.get_y() + bar.get_height() / 2,
                    f"{w:.2f}%", va="center", ha="left", fontsize=9.5)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

st.divider()

# --- BAGIAN 3: RFM ANALYSIS ---
st.subheader("3. Analisis Lanjutan: Segmentasi Pelanggan (RFM Analysis)")

rfm_df = create_rfm_df(main_df)

r_col, f_col, m_col = st.columns(3)
with r_col:
    st.metric("Rata-rata Recency", f"{rfm_df['recency'].mean():.1f} Hari")
with f_col:
    st.metric("Rata-rata Frequency", f"{rfm_df['frequency'].mean():.2f} Transaksi")
with m_col:
    st.metric("Rata-rata Monetary", f"BRL {rfm_df['monetary'].mean():,.2f}")

seg_summary = rfm_df.groupby("segment", as_index=False).agg(
    customer_count=("customer_unique_id", "count"),
    total_revenue=("monetary", "sum")
).sort_values(by="customer_count", ascending=False)

fig, ax = plt.subplots(figsize=(11, 4.5))
sns.barplot(
    data=seg_summary, x="customer_count", y="segment",
    hue="segment", palette="viridis", dodge=False, ax=ax
)
if ax.get_legend():
    ax.get_legend().remove()
ax.set_title("Distribusi Segmen Pelanggan Berdasarkan RFM", fontsize=12, fontweight="bold")
ax.set_xlabel("Jumlah Pelanggan Unik")
ax.set_ylabel("Segmen Pelanggan")
ax.set_xlim(0, seg_summary["customer_count"].max() * 1.18)
for bar in ax.patches:
    w = bar.get_width()
    if w > 0:
        ax.text(w + seg_summary["customer_count"].max() * 0.015, bar.get_y() + bar.get_height() / 2,
                f"{int(w):,}", va="center", ha="left", fontsize=10)
plt.tight_layout()
st.pyplot(fig)
plt.close(fig)

st.caption("Copyright © 2026 - Satria Dwi Cahya Fatiawan | Dicoding Data Analytics Project")
