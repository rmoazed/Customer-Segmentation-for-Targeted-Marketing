import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Page config
st.set_page_config(
    page_title="Customer Segmentation Dashboard",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("rfm_with_segments.csv")

rfm = load_data()

# Color palette
PRIMARY_GREEN = "#4CAF50"
PRIMARY_BLUE = "#2196F3"
ACCENT_GOLD = "#FFC107"
ACCENT_RED = "#F44336"
BG_DARK = "#0E1117"
PANEL_DARK = "#262730"
TEXT_LIGHT = "white"

segment_colors = {
    "High-Value Loyal Customers": PRIMARY_GREEN,
    "At-Risk Valuable Customers": ACCENT_GOLD,
    "Recent Low-Value Customers": PRIMARY_BLUE,
    "Inactive Customers": ACCENT_RED
}

# Helper styling function for dark-theme matplotlib
def style_dark_ax(fig, ax):
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    ax.title.set_color(TEXT_LIGHT)
    ax.xaxis.label.set_color(TEXT_LIGHT)
    ax.yaxis.label.set_color(TEXT_LIGHT)
    ax.tick_params(colors=TEXT_LIGHT)
    for spine in ax.spines.values():
        spine.set_color(TEXT_LIGHT)

# Segment descriptions
segment_descriptions = {
    "High-Value Loyal Customers": {
        "summary": "These customers purchase recently, frequently, and spend the most.",
        "strategy": "Focus on retention, loyalty rewards, VIP perks, and personalized recommendations."
    },
    "At-Risk Valuable Customers": {
        "summary": "These customers used to spend meaningfully, but have not purchased as recently.",
        "strategy": "Use targeted re-engagement campaigns, win-back discounts, and personalized outreach."
    },
    "Recent Low-Value Customers": {
        "summary": "These customers purchased recently but have not yet developed strong buying habits.",
        "strategy": "Use onboarding flows, product recommendations, and second-purchase incentives."
    },
    "Inactive Customers": {
        "summary": "These customers have not purchased recently, buy infrequently, and contribute relatively little revenue.",
        "strategy": "Use low-cost reactivation campaigns or deprioritize if acquisition cost is too high."
    }
}

# Title
st.title("Customer Segmentation Dashboard")
st.write(
    "This dashboard summarizes customer segments built from Recency, Frequency, and Monetary (RFM) features."
)

# Tabs
tab1, tab2, tab3 = st.tabs(["Overview", "Segment Explorer", "Revenue Simulator"])

# TAB 1: OVERVIEW
with tab1:
    st.header("Overview")

    # Top metrics
    total_customers = rfm["CustomerID"].nunique()
    total_revenue = rfm["Monetary"].sum()
    avg_revenue = rfm["Monetary"].mean()
    avg_frequency = rfm["Frequency"].mean()
    avg_recency = rfm["Recency"].mean()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Customers", f"{total_customers:,}")
    col2.metric("Total Revenue", f"${total_revenue:,.2f}")
    col3.metric("Avg Revenue / Customer", f"${avg_revenue:,.2f}")
    col4.metric("Avg Frequency", f"{avg_frequency:.2f}")
    col5.metric("Avg Recency", f"{avg_recency:.1f} days")

    st.divider()

    # Segment counts and revenue charts
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("Customer Count by Segment")
        segment_counts = rfm["Segment"].value_counts().sort_values(ascending=False)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(segment_counts.index, segment_counts.values, color=PRIMARY_GREEN)
        ax.set_ylabel("Customers")
        ax.set_xlabel("Segment")
        ax.set_title("Customer Count")
        plt.xticks(rotation=20, ha="right")

        style_dark_ax(fig, ax)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)

    with right_col:
        st.subheader("Revenue by Segment")
        revenue_by_segment = rfm.groupby("Segment")["Monetary"].sum().sort_values(ascending=False)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(revenue_by_segment.index, revenue_by_segment.values, color=PRIMARY_BLUE)
        ax.set_ylabel("Revenue ($)")
        ax.set_xlabel("Segment")
        ax.set_title("Revenue Contribution")
        ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
        plt.xticks(rotation=20, ha="right")

        style_dark_ax(fig, ax)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)

    st.divider()

    # Revenue share pie chart
    st.subheader("Revenue Share by Segment")

    revenue_by_segment = rfm.groupby("Segment")["Monetary"].sum().sort_values(ascending=False)
    pie_colors = [segment_colors[s] for s in revenue_by_segment.index]

    fig, ax = plt.subplots(figsize=(6, 6))

    wedges, texts, autotexts = ax.pie(
        revenue_by_segment.values,
        autopct="%1.1f%%",
        startangle=90,
        colors=pie_colors,
        textprops={"color": TEXT_LIGHT, "fontsize": 10}
    )

    # Make percentage text a bit smaller + bold
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_weight("bold")

    # Add legend instead of labels on chart
    legend = ax.legend(
        wedges,
        revenue_by_segment.index,
        title="Segments",
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        facecolor=PANEL_DARK,
        edgecolor=TEXT_LIGHT,
        labelcolor=TEXT_LIGHT
    )

    legend.get_title().set_color("white")

    ax.set_title("Revenue Distribution", color=TEXT_LIGHT)

    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    fig.tight_layout()

    st.pyplot(fig, use_container_width=True)

    st.divider()

    # Strategy overview cards
    st.subheader("Recommended Strategies by Segment")

    for segment, info in segment_descriptions.items():
        st.markdown(f"### {segment}")
        st.write(f"**Profile:** {info['summary']}")
        st.write(f"**Strategy:** {info['strategy']}")
        st.markdown("---")

# TAB 2: SEGMENT EXPLORER
with tab2:
    st.header("Segment Explorer")

    selected_segment = st.selectbox(
        "Select a customer segment",
        ["All Segments"] + sorted(rfm["Segment"].unique().tolist())
    )

    if selected_segment == "All Segments":
        df_filtered = rfm.copy()
    else:
        df_filtered = rfm[rfm["Segment"] == selected_segment].copy()

    # Segment insight
    if selected_segment != "All Segments":
        st.subheader(f"Segment Insight: {selected_segment}")
        st.write(f"**Profile:** {segment_descriptions[selected_segment]['summary']}")
        st.write(f"**Suggested Strategy:** {segment_descriptions[selected_segment]['strategy']}")
        st.divider()

    # PCA plot
    st.subheader("PCA Projection of Customer Segments")
    st.write("This plot shows a 2D projection of the customer feature space for visualization.")

    fig, ax = plt.subplots(figsize=(8, 6))

    if selected_segment == "All Segments":
        for segment in sorted(rfm["Segment"].unique()):
            subset = rfm[rfm["Segment"] == segment]
            ax.scatter(
                subset["PC1"],
                subset["PC2"],
                label=segment,
                alpha=0.65,
                color=segment_colors[segment]
            )
    else:
        subset = df_filtered
        ax.scatter(
            subset["PC1"],
            subset["PC2"],
            label=selected_segment,
            alpha=0.65,
            color=segment_colors[selected_segment]
        )

    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_title("Customer Segments (PCA Projection)")
    legend = ax.legend(facecolor=PANEL_DARK, edgecolor=TEXT_LIGHT)
    for text in legend.get_texts():
        text.set_color(TEXT_LIGHT)

    style_dark_ax(fig, ax)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)

    st.divider()

    # Segment summary table
    st.subheader("Segment-Level Summary Table")

    segment_summary = (
        rfm.groupby("Segment")
        .agg(
            Customers=("CustomerID", "count"),
            Avg_Recency=("Recency", "mean"),
            Avg_Frequency=("Frequency", "mean"),
            Avg_Monetary=("Monetary", "mean"),
            Total_Revenue=("Monetary", "sum"),
        )
        .sort_values("Total_Revenue", ascending=False)
    )

    segment_summary["Revenue_Share_%"] = (
        segment_summary["Total_Revenue"] / segment_summary["Total_Revenue"].sum() * 100
    )

    st.dataframe(segment_summary.style.format({
        "Customers": "{:,}",
        "Avg_Recency": "{:.1f}",
        "Avg_Frequency": "{:.2f}",
        "Avg_Monetary": "${:,.2f}",
        "Total_Revenue": "${:,.2f}",
        "Revenue_Share_%": "{:.2f}%"
    }))

    st.divider()

    # Download button
    st.subheader("Download Segment Data")

    csv = rfm.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Customer Segmentation Data",
        data=csv,
        file_name="customer_segments.csv",
        mime="text/csv"
    )

# TAB 3: REVENUE SIMULATOR
with tab3:
    st.header("Revenue Impact Simulator")
    st.write("Estimate the effect of improving performance for a selected segment.")

    sim_segment = st.selectbox(
        "Choose a segment for uplift simulation",
        sorted(rfm["Segment"].unique()),
        key="sim_segment"
    )

    uplift_pct = st.slider(
        "Assumed revenue uplift (%)",
        min_value=1,
        max_value=30,
        value=10,
        step=1
    )

    segment_revenue = rfm.loc[rfm["Segment"] == sim_segment, "Monetary"].sum()
    incremental_revenue = segment_revenue * (uplift_pct / 100)

    colA, colB = st.columns(2)
    colA.metric("Current Segment Revenue", f"${segment_revenue:,.2f}")
    colB.metric("Estimated Incremental Revenue", f"${incremental_revenue:,.2f}")

    st.write(
        f"If revenue from **{sim_segment}** improved by **{uplift_pct}%**, "
        f"the estimated additional revenue would be **${incremental_revenue:,.2f}**."
    )