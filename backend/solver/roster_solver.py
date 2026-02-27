from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple
from dotenv import load_dotenv
import psycopg2

@dataclass(frozen=True)
class StaffRow:
    staff_id: int
    role_name: str
    primary_department_id: int
    employment_type: str


@dataclass(frozen=True)
class ShiftRow:
    shift_id: int
    department_id: int
    shift_start: datetime
    shift_end: datetime
    shift_type: str
    required_doctors: int
    required_nurses: int
    patient_ratio_score: float
    spontaneity_score: float


@dataclass(frozen=True)
class AssignmentHistoryRow:
    staff_id: int
    shift_id: int
    assignment_status: str
    assigned_timestamp: datetime

conn = psycopg2.connect(
    host = load_dotenv(SUPABASE_HOST),
    dbname = 'postgres',
    user = 'postgres.tauaqytpvsijqzsrhicg',
    password = 'sahilisthegoat',
    port = 5432,
    sslmode = 'require'
)