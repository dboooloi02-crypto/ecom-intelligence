#!/usr/bin/env python3
"""
测试套件
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.shared.models.product import Product
from app.engines.unified_scorer import UnifiedScorer
from app.pipelines.csv_pipeline import CSVPipeline

print("=== 选品决策助手 自检 ===\n")
errors = 0

# 1. Product 模型
try:
    p = Product(title="测试", price=599, sold=123)
    assert p.title == "测试"
    print("[OK] Product 模型")
except Exception as e:
    print(f"[FAIL] Product 模型: {e}")
    errors += 1

# 2. Rule Scorer
try:
    from app.engines.rule_engine.scorer import RuleScorer
    p = Product(title="测试", price=599, sold=200)
    p = RuleScorer.score(p)
    assert p.scores["demand"] > 0
    print(f"[OK] RuleScorer: demand={p.scores['demand']:.1f}")
except Exception as e:
    print(f"[FAIL] RuleScorer: {e}")
    errors += 1

# 3. UnifiedScorer (CSV模式)
try:
    p = Product(title="测试", price=599, sold=200, scores={"demand":8,"price_band":6,"rating_score":9,"competition":5,"profit":5})
    p = UnifiedScorer.calculate(p)
    assert p.final_score > 0
    print(f"[OK] UnifiedScorer: score={p.final_score:.1f} rec={p.recommendation}")
except Exception as e:
    print(f"[FAIL] UnifiedScorer: {e}")
    errors += 1

# 4. CSV Pipeline
try:
    csv = CSVPipeline()
    rows = [{"title":"测试A","price":"599","sold":"123","rating":"4.5"}]
    ps = csv.run(rows)
    assert len(ps) == 1
    print(f"[OK] CSVPipeline: {ps[0].title} score={ps[0].final_score:.1f}")
except Exception as e:
    print(f"[FAIL] CSVPipeline: {e}")
    errors += 1

print(f"\n结果: {4-errors} passed / {errors} failed / 4 total")
sys.exit(1 if errors else 0)
