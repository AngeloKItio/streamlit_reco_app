import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(page_title="AI-powered cold start products recommendation", layout="wide")

# Load data
df = pd.read_parquet("reco_data.parquet")          # Host-based reco data
group_a_df = pd.read_parquet("group_a_data.parquet")  # Group A category data
group_b_df = pd.read_parquet("group_b_data.parquet")  # Group B category data

# Title
st.title("AI-Powered cold start products recommendation")

# Tabs
tab1, tab2 = st.tabs(["Explore by Host product", "Ask the Recommender"])

# ------------------------------
# TAB 1: Host-based product view
# ------------------------------
with tab1:
    st.subheader("Personalized Recos from purchased products")

    hosts = sorted(df["host_display"].unique())
    selected_host = st.selectbox("Select a purchased product (host):", hosts)

    score_threshold = st.slider("Minimum strength to display reco", 0.0, 1.0, 0.5)

    host_row = df[df["host_display"] == selected_host].iloc[0]
    host_url = host_row["host_link"]
    #host_image = host_row["host_image_url"]
    #st.markdown(f"###View host product page: [{selected_host}]({host_url})")
    if pd.notnull(host_url):
        st.image(host_url, caption="purchased product (host)", width=200)

    filtered = df[
        (df["host_display"] == selected_host) &
        (df["score"] >= score_threshold)
    ].sort_values("score", ascending=False)

    st.markdown(f"#### Showing {len(filtered)} recommended products")

    for _, row in filtered.iterrows():
        with st.container():
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(row["reco_link"], width=180)
            with col2:
                st.markdown(f"**{row['reco_display']}**")
                st.markdown(f"**Final score:** {round(row['score'], 3)}")
                if row['score'] >= 0.75:
                    st.markdown("*Highly recommended*")
                elif row['score'] >= 0.5:
                    st.markdown("*Strong match*")
                else:
                    st.markdown("*Relevant option*")
            st.markdown("---")

# -------------------------------
# TAB 2: AI-guided category recos
# -------------------------------
with tab2:
    st.subheader("Ask the AI Recommender: It surfaces unpopular high potential categories")

    group_options = {
        "Categories from Group A": "These categories contain many recommended products with high ratings (≥4)",
        "Categories from Group B": "These categories contain recommended products that are similar to highly-rated, previously purchased items"
    }

    group_choice = st.radio("Choose a category strategy", list(group_options.keys()))
    st.caption(group_options[group_choice])

    if "Group A" in group_choice:
        selected_cat = st.selectbox("Select a category", group_a_df["catalog_name"].unique())
        recos = group_a_df[group_a_df["catalog_name"] == selected_cat]
        explanation = "These are the highest rated reco products in this category"
    else:
        selected_cat = st.selectbox("Select a category", group_b_df["catalog_name"].unique())
        recos = group_b_df[group_b_df["catalog_name"] == selected_cat]
        explanation = "These reco products are similar to what customers already love"

    st.markdown(f"### Recommendations for **{selected_cat}**")
    st.info(explanation)

    for _, row in recos.iterrows():
        with st.container():
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(row["reco_link"], width=180)
            with col2:
                st.markdown(f"**{row['reco']}**")
                if "Group A" in group_choice and 'reco_rating' in row:
                    st.markdown(f"Rating: {row['reco_rating']}")
                #st.markdown(f"[View Product]({row['reco_link']})")
            st.markdown("---")

