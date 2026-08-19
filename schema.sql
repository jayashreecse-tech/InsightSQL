PRAGMA foreign_keys = ON;

CREATE TABLE departments (
    department_id INTEGER PRIMARY KEY,
    department_name TEXT NOT NULL UNIQUE,
    location TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY,
    department_id INTEGER NOT NULL,
    employee_number TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    job_title TEXT NOT NULL,
    hire_date TEXT NOT NULL,
    salary NUMERIC NOT NULL CHECK (salary > 0),
    employment_status TEXT NOT NULL DEFAULT 'ACTIVE'
        CHECK (employment_status IN ('ACTIVE', 'ON_LEAVE', 'INACTIVE')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_employees_department FOREIGN KEY (department_id)
        REFERENCES departments (department_id) ON DELETE RESTRICT
);

CREATE TABLE projects (
    project_id INTEGER PRIMARY KEY,
    project_code TEXT NOT NULL UNIQUE,
    project_name TEXT NOT NULL,
    description TEXT,
    start_date TEXT NOT NULL,
    end_date TEXT,
    status TEXT NOT NULL DEFAULT 'PLANNED'
        CHECK (status IN ('PLANNED', 'ACTIVE', 'COMPLETED', 'ON_HOLD', 'CANCELLED')),
    budget NUMERIC NOT NULL CHECK (budget >= 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_project_dates CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE TABLE employee_projects (
    employee_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    role_name TEXT NOT NULL,
    allocation_percent NUMERIC NOT NULL
        CHECK (allocation_percent > 0 AND allocation_percent <= 100),
    assigned_date TEXT NOT NULL,
    released_date TEXT,
    PRIMARY KEY (employee_id, project_id),
    CONSTRAINT fk_employee_projects_employee FOREIGN KEY (employee_id)
        REFERENCES employees (employee_id) ON DELETE RESTRICT,
    CONSTRAINT fk_employee_projects_project FOREIGN KEY (project_id)
        REFERENCES projects (project_id) ON DELETE RESTRICT,
    CONSTRAINT chk_assignment_dates CHECK (released_date IS NULL OR released_date >= assigned_date)
);

CREATE INDEX idx_employees_department_id ON employees (department_id);
CREATE INDEX idx_employee_projects_project_id ON employee_projects (project_id);
