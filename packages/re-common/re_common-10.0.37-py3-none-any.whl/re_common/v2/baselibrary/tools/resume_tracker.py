import logging
from pathlib import Path
import sqlite3
from typing import Iterable, List, Literal, Union

logger = logging.getLogger(__name__)


class ResumeTracker:
    def __init__(
        self,
        db_path: Union[str, Path] = "processed.db",
        timeout: float = 10.0,
        isolation_level: Union[Literal["DEFERRED", "EXCLUSIVE", "IMMEDIATE"], None] = "DEFERRED",
    ):
        self.db_path = Path(db_path)
        self.timeout = timeout
        self.isolation_level = isolation_level
        self.init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """创建数据库连接"""
        return sqlite3.connect(self.db_path, timeout=self.timeout, isolation_level=self.isolation_level)

    def init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS processed_items (
                        item_key TEXT PRIMARY KEY
                    )
                    """)
            conn.commit()

    def is_processed(self, item_key: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM processed_items WHERE item_key = ?",
                (item_key,),
            )
            return cursor.fetchone() is not None

    def mark_processed(self, item_key: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO processed_items (item_key) VALUES (?)",
                (item_key,),
            )
            conn.commit()

    def mark_many_processed(self, item_keys: Iterable[str]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT OR IGNORE INTO processed_items (item_key) VALUES (?)",
                [(key,) for key in item_keys],
            )
            conn.commit()

    def get_processed_count(self) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM processed_items")
            return cursor.fetchone()[0]

    def get_processed_items(self) -> List[str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT item_key FROM processed_items")
            return [row[0] for row in cursor.fetchall()]

    def clear_processed_items(self):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM processed_items")
            logger.info("Cleared all processed items")


if __name__ == "__main__":
    tracker = ResumeTracker()
    # 测试标记功能
    tracker.mark_processed("test_key")
    print(f"Is 'test_key' processed? {tracker.is_processed('test_key')}")

    # 批量处理示例
    test_keys = [f"key_{i}" for i in range(1, 10000)]
    tracker.mark_many_processed(test_keys)

    # 显示处理计数
    print(f"Total processed items: {tracker.get_processed_count()}")

    # 清理测试数据
    tracker.clear_processed_items()
