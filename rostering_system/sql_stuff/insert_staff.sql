INSERT INTO department (department_name, location, min_staff_required_per_shift)
VALUES ('Emergency', 'Ground Floor - Trauma Wing', 5);

INSERT INTO department (department_name, location, min_staff_required_per_shift)
VALUES ('Intensive Care Unit', 'Level 2 - Critical Care', 4);

INSERT INTO department (department_name, location, min_staff_required_per_shift)
VALUES ('General Ward', 'Level 3 - Inpatient Services', 8);

COMMIT;

INSERT INTO role (role_id, role_name)
VALUES (1, 'Nurse');

INSERT INTO role (role_id, role_name)
VALUES (2, 'Doctor');

