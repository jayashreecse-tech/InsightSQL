from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Any, Iterable

from .models import HistoryItem, QueryResult


_SCHEMA = """
CREATE TABLE IF NOT EXISTS departments (
    department_id INTEGER PRIMARY KEY,
    department_name TEXT NOT NULL UNIQUE,
    location TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS employees (
    employee_id INTEGER PRIMARY KEY,
    department_id INTEGER NOT NULL REFERENCES departments(department_id),
    employee_number TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    job_title TEXT NOT NULL,
    hire_date TEXT NOT NULL,
    salary REAL NOT NULL CHECK (salary > 0),
    employment_status TEXT NOT NULL DEFAULT 'ACTIVE'
        CHECK (employment_status IN ('ACTIVE', 'ON_LEAVE', 'INACTIVE'))
);
CREATE TABLE IF NOT EXISTS projects (
    project_id INTEGER PRIMARY KEY,
    project_code TEXT NOT NULL UNIQUE,
    project_name TEXT NOT NULL,
    description TEXT,
    start_date TEXT NOT NULL,
    end_date TEXT,
    status TEXT NOT NULL CHECK (status IN ('PLANNED', 'ACTIVE', 'COMPLETED', 'ON_HOLD', 'CANCELLED')),
    budget REAL NOT NULL CHECK (budget >= 0)
);
CREATE TABLE IF NOT EXISTS employee_projects (
    employee_id INTEGER NOT NULL REFERENCES employees(employee_id),
    project_id INTEGER NOT NULL REFERENCES projects(project_id),
    role_name TEXT NOT NULL,
    allocation_percent REAL NOT NULL CHECK (allocation_percent > 0 AND allocation_percent <= 100),
    assigned_date TEXT NOT NULL,
    released_date TEXT,
    PRIMARY KEY (employee_id, project_id)
);
CREATE TABLE IF NOT EXISTS query_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    sql_text TEXT,
    status TEXT NOT NULL,
    error_message TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

_DEPARTMENTS = [
    (1, "Human Resources", "New York"), (2, "Engineering", "Austin"),
    (3, "Finance", "Chicago"), (4, "Sales", "San Francisco"), (5, "Operations", "Seattle"),
]
_EMPLOYEES = [
    (1, 1, "EMP001", "Ava", "Morgan", "ava.morgan@example.com", "HR Manager", "2018-04-16", 112000, "ACTIVE"),
    (2, 1, "EMP002", "Liam", "Carter", "liam.carter@example.com", "Talent Partner", "2020-07-06", 82000, "ACTIVE"),
    (3, 1, "EMP003", "Sofia", "Bennett", "sofia.bennett@example.com", "HR Analyst", "2022-01-10", 72000, "ACTIVE"),
    (4, 2, "EMP004", "Noah", "Richardson", "noah.richardson@example.com", "Engineering Manager", "2017-09-18", 148000, "ACTIVE"),
    (5, 2, "EMP005", "Mia", "Thompson", "mia.thompson@example.com", "Senior Software Engineer", "2019-02-11", 132000, "ACTIVE"),
    (6, 2, "EMP006", "Ethan", "Cooper", "ethan.cooper@example.com", "Software Engineer", "2021-06-21", 105000, "ACTIVE"),
    (7, 2, "EMP007", "Isabella", "Ward", "isabella.ward@example.com", "Data Engineer", "2020-11-02", 118000, "ACTIVE"),
    (8, 2, "EMP008", "Lucas", "Peterson", "lucas.peterson@example.com", "QA Engineer", "2023-03-13", 92000, "ACTIVE"),
    (9, 3, "EMP009", "Amelia", "Gray", "amelia.gray@example.com", "Finance Manager", "2016-08-22", 128000, "ACTIVE"),
    (10, 3, "EMP010", "James", "Mitchell", "james.mitchell@example.com", "Financial Analyst", "2021-01-25", 88000, "ACTIVE"),
    (11, 3, "EMP011", "Harper", "Adams", "harper.adams@example.com", "Senior Accountant", "2019-10-07", 97000, "ACTIVE"),
    (12, 3, "EMP012", "Benjamin", "Brooks", "benjamin.brooks@example.com", "FP&A Analyst", "2022-05-16", 85000, "ON_LEAVE"),
    (13, 4, "EMP013", "Evelyn", "Parker", "evelyn.parker@example.com", "Sales Director", "2015-03-30", 155000, "ACTIVE"),
    (14, 4, "EMP014", "Henry", "Evans", "henry.evans@example.com", "Account Executive", "2020-08-17", 95000, "ACTIVE"),
    (15, 4, "EMP015", "Camila", "Edwards", "camila.edwards@example.com", "Sales Operations Analyst", "2021-09-27", 83000, "ACTIVE"),
    (16, 4, "EMP016", "Daniel", "Collins", "daniel.collins@example.com", "Customer Success Manager", "2019-06-03", 102000, "ACTIVE"),
    (17, 5, "EMP017", "Abigail", "Stewart", "abigail.stewart@example.com", "Operations Manager", "2016-11-14", 120000, "ACTIVE"),
    (18, 5, "EMP018", "Michael", "Sanchez", "michael.sanchez@example.com", "Business Process Analyst", "2022-02-28", 81000, "ACTIVE"),
    (19, 5, "EMP019", "Ella", "Morris", "ella.morris@example.com", "Procurement Specialist", "2020-04-06", 79000, "ACTIVE"),
    (20, 5, "EMP020", "Alexander", "Rogers", "alexander.rogers@example.com", "Program Coordinator", "2023-07-10", 68000, "ACTIVE"),
]
_PROJECTS = [
    (1, "PRJ001", "Workforce Planning 2026", "Annual workforce planning.", "2026-01-05", None, "ACTIVE", 250000),
    (2, "PRJ002", "HR Self-Service Portal", "Employee self-service improvements.", "2026-02-01", None, "ACTIVE", 180000),
    (3, "PRJ003", "Data Platform Modernization", "Modernize analytics pipelines.", "2025-10-01", None, "ACTIVE", 600000),
    (4, "PRJ004", "Financial Forecasting Upgrade", "Improve forecasting workflows.", "2026-01-19", None, "ACTIVE", 320000),
    (5, "PRJ005", "Customer Insights Program", "Cross-functional customer insights.", "2026-06-01", None, "PLANNED", 275000),
    (6, "PRJ006", "Sales Enablement Automation", "Automate sales planning.", "2026-03-02", None, "ACTIVE", 210000),
    (7, "PRJ007", "Operations Excellence", "Improve operational efficiency.", "2026-01-12", None, "ACTIVE", 190000),
    (8, "PRJ008", "Cloud Migration", "Migrate selected workloads.", "2026-04-06", None, "ON_HOLD", 450000),
    (9, "PRJ009", "Compliance Readiness", "Prepare for compliance review.", "2025-07-01", "2025-12-15", "COMPLETED", 125000),
    (10, "PRJ010", "Employee Engagement Survey", "Measure employee engagement.", "2026-02-16", None, "ACTIVE", 90000),
]
_ASSIGNMENTS = [(1, 1, "Sponsor", 15), (2, 2, "Business Lead", 40), (3, 10, "Analyst", 50), (4, 3, "Technical Lead", 35), (5, 3, "Architect", 60), (6, 3, "Engineer", 75), (7, 3, "Data Engineer", 80), (8, 3, "QA Engineer", 50), (9, 4, "Sponsor", 20), (10, 4, "Analyst", 70), (11, 4, "Accountant", 40), (12, 4, "Analyst", 30), (13, 6, "Sponsor", 15), (14, 6, "Sales Lead", 60), (15, 6, "Process Analyst", 70), (16, 5, "Insights Lead", 40), (17, 7, "Sponsor", 35), (18, 7, "Process Analyst", 75), (19, 7, "Procurement Lead", 60), (20, 7, "Coordinator", 80)]


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=5)
        connection.execute("PRAGMA foreign_keys = ON")
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(_SCHEMA)
            if connection.execute("SELECT COUNT(*) FROM departments").fetchone()[0] == 0:
                connection.executemany("INSERT INTO departments VALUES (?, ?, ?)", _DEPARTMENTS)
                connection.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", _EMPLOYEES)
                connection.executemany("INSERT INTO projects VALUES (?, ?, ?, ?, ?, ?, ?, ?)", _PROJECTS)
                connection.executemany("INSERT INTO employee_projects(employee_id, project_id, role_name, allocation_percent, assigned_date) VALUES (?, ?, ?, ?, '2026-01-01')", _ASSIGNMENTS)

    def execute_select(self, sql: str, max_rows: int) -> QueryResult:
        started = time.perf_counter()
        with self.connect() as connection:
            cursor = connection.execute(sql)
            rows = cursor.fetchmany(max_rows + 1)
            columns = [description[0] for description in cursor.description or []]
        truncated = len(rows) > max_rows
        visible_rows = rows[:max_rows]
        return QueryResult(columns, [tuple(row) for row in visible_rows], len(visible_rows), truncated, (time.perf_counter() - started) * 1000)

    def add_history(self, question: str, sql: str | None, status: str, error: str | None = None) -> None:
        with self.connect() as connection:
            connection.execute("INSERT INTO query_history(question, sql_text, status, error_message) VALUES (?, ?, ?, ?)", (question, sql, status, error))

    def history(self, limit: int = 20) -> list[HistoryItem]:
        with self.connect() as connection:
            records = connection.execute("SELECT question, sql_text, status, created_at, error_message FROM query_history ORDER BY history_id DESC LIMIT ?", (limit,)).fetchall()
        return [HistoryItem(r[0], r[1] or "", r[2], datetime.fromisoformat(r[3]), r[4]) for r in records]
