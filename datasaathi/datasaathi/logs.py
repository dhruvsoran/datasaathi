"""Local DuckDB query log (no cloud, no vector DB)."""
from __future__ import annotations
import os
from datetime import datetime
import pandas as pd


def _path() -> str:
    return os.environ.get("DATASAATHI_DB", "datasaathi.duckdb")


def log(ans, trust_score: int | None = None) -> None:
    try:
        import duckdb
        con = duckdb.connect(_path())
        con.execute("""CREATE TABLE IF NOT EXISTS query_log(ts TIMESTAMP, question VARCHAR, intent VARCHAR, planner VARCHAR,
                       explainer VARCHAR, status VARCHAR, guard_ok BOOLEAN, trust INTEGER)""")
        con.execute("INSERT INTO query_log VALUES (?,?,?,?,?,?,?,?)",
                    [datetime.now(), ans.question, ans.plan.intent, ans.planner, ans.explainer, ans.status,
                     None if ans.guard is None else bool(ans.guard.ok), trust_score])
        con.close()
    except Exception:
        pass                                   # logging must never break an answer


def history(limit: int = 200) -> pd.DataFrame:
    try:
        import duckdb
        con = duckdb.connect(_path(), read_only=True)
        df = con.execute(f"SELECT * FROM query_log ORDER BY ts DESC LIMIT {int(limit)}").df()
        con.close()
        return df
    except Exception:
        return pd.DataFrame(columns=["ts", "question", "intent", "planner", "explainer", "status", "guard_ok", "trust"])
