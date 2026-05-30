"""
Cache Manager — AI 请求缓存层
"""
import os
import json
import hashlib
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

BASE      = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE_DIR = os.path.join(BASE, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

DEFAULT_TTL = 3600
MAX_SIZE    = 500
_LRU_INDEX  = os.path.join(CACHE_DIR, "_lru_index.json")

class CacheManager:
    def _hash(self, keyword: str) -> str:
        return hashlib.md5(keyword.encode("utf-8")).hexdigest()
    def _path(self, keyword: str) -> str:
        return os.path.join(CACHE_DIR, self._hash(keyword) + ".json")
    def _load_index(self) -> dict:
        if not os.path.exists(_LRU_INDEX):
            return {}
        try:
            with open(_LRU_INDEX, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            logger.warning("LRU索引损坏，已重建")
            return {}
    def _save_index(self, index: dict):
        with open(_LRU_INDEX, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
    def _touch(self, keyword: str, index: dict, created_at: float = None):
        h = self._hash(keyword)
        now = time.time()
        if h not in index:
            index[h] = {"keyword": keyword, "created_at": created_at or now, "last_access": now}
        else:
            index[h]["last_access"] = now
        return index
    def get(self, keyword: str, ttl: int = DEFAULT_TTL) -> Optional[dict]:
        path = self._path(keyword)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if time.time() - data.get("_cached_at", 0) > ttl:
                self.delete(keyword)
                return None
            index = self._load_index()
            index = self._touch(keyword, index)
            self._save_index(index)
            return data.get("result")
        except Exception as e:
            logger.warning("cache get 异常 keyword=%s: %s", keyword, e)
            return None
    def set(self, keyword: str, result: dict):
        path = self._path(keyword)
        now  = time.time()
        data = {"_cached_at": now, "_keyword": keyword, "result": result}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        index = self._load_index()
        index = self._touch(keyword, index, created_at=now)
        self._save_index(index)
        self.prune()
    def delete(self, keyword: str):
        path = self._path(keyword)
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass
        index = self._load_index()
        index.pop(self._hash(keyword), None)
        self._save_index(index)
    def exists(self, keyword: str, ttl: int = DEFAULT_TTL) -> bool:
        path = self._path(keyword)
        if not os.path.exists(path):
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return time.time() - data.get("_cached_at", 0) <= ttl
        except Exception:
            return False
    def clear(self, older_than_hours: int = 24) -> int:
        cutoff = time.time() - older_than_hours * 3600
        index  = self._load_index()
        count  = 0
        for fname in os.listdir(CACHE_DIR):
            if not fname.endswith(".json") or fname == "_lru_index.json":
                continue
            path = os.path.join(CACHE_DIR, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("_cached_at", 0) < cutoff:
                    os.remove(path)
                    h = fname.replace(".json", "")
                    index.pop(h, None)
                    count += 1
            except Exception:
                try:
                    os.remove(path)
                except OSError:
                    pass
                count += 1
        self._save_index(index)
        return count
    def prune(self) -> int:
        index = self._load_index()
        if len(index) <= MAX_SIZE:
            return 0
        sorted_entries = sorted(index.items(), key=lambda x: x[1].get("last_access", 0))
        to_evict = sorted_entries[:len(index) - MAX_SIZE]
        for h, meta in to_evict:
            path = os.path.join(CACHE_DIR, h + ".json")
            try:
                os.remove(path)
            except OSError:
                pass
            del index[h]
        self._save_index(index)
        return len(to_evict)
    def stats(self) -> dict:
        files = [f for f in os.listdir(CACHE_DIR) if f.endswith(".json") and f != "_lru_index.json"]
        total_size = sum(os.path.getsize(os.path.join(CACHE_DIR, f)) for f in files)
        index = self._load_index()
        now   = time.time()
        accesses = [v.get("last_access", 0) for v in index.values()]
        oldest   = min(accesses) if accesses else None
        newest   = max(accesses) if accesses else None
        return {"count": len(files), "max_size": MAX_SIZE, "size_kb": round(total_size / 1024, 1), "dir": CACHE_DIR, "lru_entries": len(index), "oldest_access_hours_ago": round((now - oldest) / 3600, 1) if oldest else None, "newest_access_hours_ago": round((now - newest) / 3600, 1) if newest else None}
