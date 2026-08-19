PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

INSERT INTO departments (department_id, department_name, location) VALUES
    (1, 'Human Resources', 'New York'),
    (2, 'Engineering', 'Austin'),
    (3, 'Finance', 'Chicago'),
    (4, 'Sales', 'San Francisco'),
    (5, 'Operations', 'Seattle');

INSERT INTO employees
    (employee_id, department_id, employee_number, first_name, last_name, email,
     job_title, hire_date, salary, employment_status)
VALUES
    (1, 1, 'EMP001', 'Ava', 'Morgan', 'ava.morgan@example.com', 'HR Manager', '2018-04-16', 112000.00, 'ACTIVE'),
    (2, 1, 'EMP002', 'Liam', 'Carter', 'liam.carter@example.com', 'Talent Partner', '2020-07-06', 82000.00, 'ACTIVE'),
    (3, 1, 'EMP003', 'Sofia', 'Bennett', 'sofia.bennett@example.com', 'HR Analyst', '2022-01-10', 72000.00, 'ACTIVE'),
    (4, 2, 'EMP004', 'Noah', 'Richardson', 'noah.richardson@example.com', 'Engineering Manager', '2017-09-18', 148000.00, 'ACTIVE'),
    (5, 2, 'EMP005', 'Mia', 'Thompson', 'mia.thompson@example.com', 'Senior Software Engineer', '2019-02-11', 132000.00, 'ACTIVE'),
    (6, 2, 'EMP006', 'Ethan', 'Cooper', 'ethan.cooper@example.com', 'Software Engineer', '2021-06-21', 105000.00, 'ACTIVE'),
    (7, 2, 'EMP007', 'Isabella', 'Ward', 'isabella.ward@example.com', 'Data Engineer', '2020-11-02', 118000.00, 'ACTIVE'),
    (8, 2, 'EMP008', 'Lucas', 'Peterson', 'lucas.peterson@example.com', 'QA Engineer', '2023-03-13', 92000.00, 'ACTIVE'),
    (9, 3, 'EMP009', 'Amelia', 'Gray', 'amelia.gray@example.com', 'Finance Manager', '2016-08-22', 128000.00, 'ACTIVE'),
    (10, 3, 'EMP010', 'James', 'Mitchell', 'james.mitchell@example.com', 'Financial Analyst', '2021-01-25', 88000.00, 'ACTIVE'),
    (11, 3, 'EMP011', 'Harper', 'Adams', 'harper.adams@example.com', 'Senior Accountant', '2019-10-07', 97000.00, 'ACTIVE'),
    (12, 3, 'EMP012', 'Benjamin', 'Brooks', 'benjamin.brooks@example.com', 'FP&A Analyst', '2022-05-16', 85000.00, 'ON_LEAVE'),
    (13, 4, 'EMP013', 'Evelyn', 'Parker', 'evelyn.parker@example.com', 'Sales Director', '2015-03-30', 155000.00, 'ACTIVE'),
    (14, 4, 'EMP014', 'Henry', 'Evans', 'henry.evans@example.com', 'Account Executive', '2020-08-17', 95000.00, 'ACTIVE'),
    (15, 4, 'EMP015', 'Camila', 'Edwards', 'camila.edwards@example.com', 'Sales Operations Analyst', '2021-09-27', 83000.00, 'ACTIVE'),
    (16, 4, 'EMP016', 'Daniel', 'Collins', 'daniel.collins@example.com', 'Customer Success Manager', '2019-06-03', 102000.00, 'ACTIVE'),
    (17, 5, 'EMP017', 'Abigail', 'Stewart', 'abigail.stewart@example.com', 'Operations Manager', '2016-11-14', 120000.00, 'ACTIVE'),
    (18, 5, 'EMP018', 'Michael', 'Sanchez', 'michael.sanchez@example.com', 'Business Process Analyst', '2022-02-28', 81000.00, 'ACTIVE'),
    (19, 5, 'EMP019', 'Ella', 'Morris', 'ella.morris@example.com', 'Procurement Specialist', '2020-04-06', 79000.00, 'ACTIVE'),
    (20, 5, 'EMP020', 'Alexander', 'Rogers', 'alexander.rogers@example.com', 'Program Coordinator', '2023-07-10', 68000.00, 'ACTIVE');

INSERT INTO projects
    (project_id, project_code, project_name, description, start_date, end_date, status, budget)
VALUES
    (1, 'PRJ001', 'Workforce Planning 2026', 'Annual workforce planning and capacity analysis.', '2026-01-05', NULL, 'ACTIVE', 250000.00),
    (2, 'PRJ002', 'HR Self-Service Portal', 'Employee and manager self-service improvements.', '2026-02-01', NULL, 'ACTIVE', 180000.00),
    (3, 'PRJ003', 'Data Platform Modernization', 'Modernize analytics pipelines and data models.', '2025-10-01', NULL, 'ACTIVE', 600000.00),
    (4, 'PRJ004', 'Financial Forecasting Upgrade', 'Improve forecasting models and reporting workflows.', '2026-01-19', NULL, 'ACTIVE', 320000.00),
    (5, 'PRJ005', 'Customer Insights Program', 'Create a cross-functional customer insights capability.', '2026-06-01', NULL, 'PLANNED', 275000.00),
    (6, 'PRJ006', 'Sales Enablement Automation', 'Automate sales planning and enablement processes.', '2026-03-02', NULL, 'ACTIVE', 210000.00),
    (7, 'PRJ007', 'Operations Excellence', 'Improve operational processes and service efficiency.', '2026-01-12', NULL, 'ACTIVE', 190000.00),
    (8, 'PRJ008', 'Cloud Migration', 'Migrate selected workloads to the cloud.', '2026-04-06', NULL, 'ON_HOLD', 450000.00),
    (9, 'PRJ009', 'Compliance Readiness', 'Prepare systems and processes for compliance review.', '2025-07-01', '2025-12-15', 'COMPLETED', 125000.00),
    (10, 'PRJ010', 'Employee Engagement Survey', 'Measure and improve employee engagement.', '2026-02-16', NULL, 'ACTIVE', 90000.00);

INSERT INTO employee_projects
    (employee_id, project_id, role_name, allocation_percent, assigned_date, released_date)
VALUES
    (1, 1, 'Executive Sponsor', 15.00, '2026-01-05', NULL),
    (2, 2, 'Business Lead', 40.00, '2026-02-01', NULL),
    (3, 10, 'Survey Analyst', 50.00, '2026-02-16', NULL),
    (4, 3, 'Technical Lead', 35.00, '2025-10-01', NULL),
    (5, 3, 'Solution Architect', 60.00, '2025-10-01', NULL),
    (6, 3, 'Backend Engineer', 75.00, '2025-10-15', NULL),
    (7, 3, 'Data Engineer', 80.00, '2025-10-01', NULL),
    (8, 3, 'QA Lead', 50.00, '2025-11-03', NULL),
    (9, 4, 'Executive Sponsor', 20.00, '2026-01-19', NULL),
    (10, 4, 'Financial Analyst', 70.00, '2026-01-19', NULL),
    (11, 4, 'Accounting Lead', 40.00, '2026-01-19', NULL),
    (12, 4, 'FP&A Analyst', 30.00, '2026-01-19', NULL),
    (13, 6, 'Executive Sponsor', 15.00, '2026-03-02', NULL),
    (14, 6, 'Sales Lead', 60.00, '2026-03-02', NULL),
    (15, 6, 'Process Analyst', 70.00, '2026-03-02', NULL),
    (16, 5, 'Customer Insights Lead', 40.00, '2026-06-01', NULL),
    (17, 7, 'Program Sponsor', 35.00, '2026-01-12', NULL),
    (18, 7, 'Process Analyst', 75.00, '2026-01-12', NULL),
    (19, 7, 'Procurement Lead', 60.00, '2026-01-12', NULL),
    (20, 7, 'Project Coordinator', 80.00, '2026-01-12', NULL);

COMMIT;
