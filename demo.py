"""
ecom-intelligence demo — runs with zero setup."""
import os,sys,csv; from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("""
╔══════════════════════════════════════════════╗
║         ecom-intelligence  Demo              ║
╚══════════════════════════════════════════════╝
""")

print("📦 Loading sample products...")
products = []
with open(os.path.join(os.path.dirname(__file__),"examples/shopee_sample.csv"),"r",encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        products.append({"name":row["name"],"price":float(row["price"]),"sold":int(row["sold"]),"rating":float(row["rating"]),"shop_location":row["location"]})
print(f"   ✅ {len(products)} products loaded\n")

print("🤖 Scoring (mock mode)...")
from backend.pipelines.scorer import score_products
scored = score_products(products, use_mock=True)
print(f"   ✅ Done\n")

print("📊 PRODUCT RANKING"); print("="*72)
print(f"  {'Rank':<5}{'Score':<6}{'Rec':<6}{'Price':<8}{'Sold':<8}{'Rating':<6}Name"); print(f"  {'-'*66}")
for i,p in enumerate(scored[:20],1):
    icon = {"yes":"✅","no":"❌","watch":"👀"}.get(p.get("recommendation",""),"❓")
    print(f"  {i:<5}{p['score']:<6}{icon:<6}RM{p['price']:<6.2f}{p['sold']:<8}{p['rating']:<6.1f}{(p['name'] or '')[:40]}")

print(); yes = sum(1 for p in scored if p["recommendation"]=="yes")
watch = sum(1 for p in scored if p["recommendation"]=="watch")
no = sum(1 for p in scored if p["recommendation"]=="no")
print(f"📈 Summary: {yes} ✅ | {watch} 👀 | {no} ❌\n")

print("🏆 TOP 5"); print("="*72)
for p in scored[:5]:
    print(f"  ✅ Score {p['score']}/10 — {p['name'][:50]}"); print(f"     {p['reason']}\n")

print(); print("🚀 Next:"); print("  1. Add Zhipu API key to .env for real AI")
print("  2. Install extension for live data"); print("  3. streamlit run dashboard/app.py")
