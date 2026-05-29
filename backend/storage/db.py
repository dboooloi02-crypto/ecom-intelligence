"""DuckDB storage layer."""
import os
try:
    import duckdb
except ImportError:
    duckdb = None

DB_PATH = os.path.join(os.path.dirname(__file__), "../../data/ecommerce.db")

def get_db(path: str = None):
    db_path = path or os.path.abspath(DB_PATH)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = duckdb.connect(db_path)
    conn.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER, name VARCHAR, price DOUBLE, price_min DOUBLE, price_max DOUBLE,
        sold INTEGER, rating DOUBLE, rating_count INTEGER, shop_location VARCHAR,
        stock INTEGER, liked_count INTEGER, keyword VARCHAR, source VARCHAR,
        collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY, product_id INTEGER, score DOUBLE,
        recommendation VARCHAR, reason VARCHAR, score_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    return conn

def insert_products(conn, products: list[dict], keyword: str):
    for p in products:
        conn.execute("INSERT INTO products (id,name,price,price_min,price_max,sold,rating,rating_count,shop_location,stock,liked_count,keyword,source) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            [p.get("rank",0), p.get("name",""), p.get("price",0), p.get("price_min",0), p.get("price_max",0),
             p.get("sold",0), p.get("rating",0), p.get("rating_count",0), p.get("shop_location","") or p.get("location",""),
             p.get("stock",0), p.get("liked_count",0), keyword, p.get("_source","unknown")])

def query_products(conn, keyword: str = None, limit: int = 100):
    if keyword:
        return conn.execute("SELECT * FROM products WHERE keyword = ? ORDER BY sold DESC LIMIT ?", [keyword, limit]).fetchdf()
    return conn.execute("SELECT * FROM products ORDER BY collected_at DESC LIMIT ?", [limit]).fetchdf()

def save_analysis(conn, product_id: int, score: float, rec: str, reason: str):
    conn.execute("INSERT INTO analyses (product_id, score, recommendation, reason) VALUES (?,?,?,?)", [product_id, score, rec, reason])

def get_latest_analyses(conn, limit: int = 50):
    return conn.execute("SELECT p.*, a.score, a.recommendation, a.reason, a.score_at FROM products p JOIN analyses a ON p.id = a.product_id ORDER BY a.score_at DESC LIMIT ?", [limit]).fetchdf()
