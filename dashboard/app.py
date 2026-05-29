"""
ecom-intelligence Dashboard — Streamlit app."""
import os, sys, csv; from pathlib import Path
import streamlit as st; import pandas as pd
sys.path.insert(0, str(Path(__file__).parent.parent))
from backend.pipelines.scorer import score_products

st.set_page_config(page_title="ecom-intelligence", page_icon="📊", layout="wide")
st.title("📊 ecom-intelligence")
st.caption("AI-powered cross-border e-commerce intelligence pipeline")

st.sidebar.header("Data Source")
data_option = st.sidebar.radio("Choose data source:", ["Sample data (no setup)", "CSV upload", "DuckDB (from extension)"])
use_mock = st.sidebar.checkbox("Mock AI scoring (no API key)", value=True)

products = []
if data_option == "Sample data (no setup)":
    with open(os.path.join(os.path.dirname(__file__), "../examples/shopee_sample.csv"), "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            products.append({"name": row["name"], "price": float(row["price"]), "sold": int(row["sold"]), "rating": float(row["rating"]), "shop_location": row["location"]})
    st.sidebar.success(f"📦 {len(products)} sample products loaded")
elif data_option == "CSV upload":
    uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded); products = df.to_dict(orient="records")
        st.sidebar.success(f"📦 {len(products)} products loaded")
    else: st.info("Upload a CSV file, or switch to sample data.")
else:
    from backend.storage.db import get_db, query_products
    try:
        df = query_products(get_db()); products = df.to_dict(orient="records")
        st.sidebar.success(f"📦 {len(products)} products from DuckDB")
    except Exception as e: st.sidebar.error(f"DB error: {e}")

if not products: st.warning("No data loaded."); st.stop()

with st.spinner("🤖 Scoring..."):
    scored = score_products(products, use_mock=use_mock)
df = pd.DataFrame(scored)

yes = sum(1 for p in scored if p.get("recommendation")=="yes")
watch = sum(1 for p in scored if p.get("recommendation")=="watch")
no = sum(1 for p in scored if p.get("recommendation")=="no")
avg = round(sum(p.get("score",0) for p in scored)/len(scored),1) if scored else 0
c1,c2,c3,c4 = st.columns(4)
c1.metric("✅ Recommended", yes); c2.metric("👀 Watch", watch); c3.metric("❌ Skip", no); c4.metric("⭐ Avg Score", avg)

st.subheader("Product Ranking")
display = [c for c in ["score","recommendation","name","price","sold","rating","reason","shop_location"] if c in df.columns]
if not df.empty:
    d = df[display].copy(); d.columns = ["Score","Rec","Name","Price","Sold","Rating","Reason","Location"]
    def color(v): return {"yes":"bg:#d4edda","no":"bg:#f8d7da","watch":"bg:#fff3cd"}.get(v,"")
    st.dataframe(d.style.applymap(color, subset=["Rec"]), use_container_width=True, height=500)

st.subheader("Charts")
c1,c2 = st.columns(2)
if "score" in df.columns:
    bins = pd.cut(df["score"], bins=[0,3,5,7,10], labels=["1-3","4-5","6-7","8-10"])
    c1.bar_chart(bins.value_counts().sort_index())
if "recommendation" in df.columns:
    c2.bar_chart(df["recommendation"].value_counts())

if all(c in df.columns for c in ["price","sold","score"]):
    c = df[["price","sold","score","name"]].copy(); c["size"] = c["score"]*10
    st.subheader("Price vs Sales")
    st.scatter_chart(c, x="price", y="sold", size="size", color="score")

st.divider(); st.caption("ecom-intelligence — open-source e-commerce intelligence pipeline")
