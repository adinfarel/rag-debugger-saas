from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from pathlib import Path

def get_checkpointer():
    path       = Path("db/graph_state.db")
    if not path.parent.exists():
        print(f"[FALLBACK] Directory database not found. Fallback created: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        
    conn    = sqlite3.connect("./db/graph_state.db", check_same_thread=False)
    return SqliteSaver(conn)