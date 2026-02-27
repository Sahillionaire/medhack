from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple
import psycopg2

conn = psycopg2.connect(
    host = 'aws-1-ap-northeast-1.pooler.supabase.com',
    dbname = 'postgres',
    user = 'postgres.tauaqytpvsijqzsrhicg',
    password = 'sahilisthegoat',
    port = 5432,
    sslmode = 'require'
)

cur = conn.cursor()
cur.execute(
    "SELECT * FROM SHIFT;"
)

rows = cur.fetchall()

print(rows)

conn.close()