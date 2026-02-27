-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.department (
  department_id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  department_name character varying NOT NULL UNIQUE,
  CONSTRAINT department_pkey PRIMARY KEY (department_id)
);
CREATE TABLE public.incident_exposure (
  incident_id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  staff_id integer NOT NULL,
  shift_id integer,
  severity_level character varying,
  emotional_weight_score numeric,
  recorded_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT incident_exposure_pkey PRIMARY KEY (incident_id),
  CONSTRAINT incident_staff_fk FOREIGN KEY (staff_id) REFERENCES public.staff(staff_id),
  CONSTRAINT incident_shift_fk FOREIGN KEY (shift_id) REFERENCES public.shift(shift_id)
);
CREATE TABLE public.leave_request (
  leave_id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  staff_id integer NOT NULL,
  leave_type character varying,
  start_date date NOT NULL,
  end_date date NOT NULL,
  approval_status character varying DEFAULT 'PENDING'::character varying,
  date_submitted timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT leave_request_pkey PRIMARY KEY (leave_id),
  CONSTRAINT leave_staff_fk FOREIGN KEY (staff_id) REFERENCES public.staff(staff_id)
);
CREATE TABLE public.role (
  role_id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  role_name character varying NOT NULL UNIQUE,
  description character varying,
  base_hourly_rate numeric,
  CONSTRAINT role_pkey PRIMARY KEY (role_id)
);
CREATE TABLE public.shift (
  shift_id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  department_id integer NOT NULL,
  shift_start timestamp without time zone NOT NULL,
  shift_end timestamp without time zone NOT NULL,
  shift_type character varying CHECK (shift_type::text = ANY (ARRAY['DAY'::character varying, 'NIGHT'::character varying]::text[])),
  required_doctors integer,
  required_nurses integer,
  patient_ratio_score numeric,
  spontaneity_score numeric,
  CONSTRAINT shift_pkey PRIMARY KEY (shift_id),
  CONSTRAINT shift_department_fk FOREIGN KEY (department_id) REFERENCES public.department(department_id)
);
CREATE TABLE public.shift_assignment (
  assignment_id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  staff_id integer NOT NULL,
  shift_id integer NOT NULL,
  assignment_status character varying DEFAULT 'ASSIGNED'::character varying,
  assigned_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT shift_assignment_pkey PRIMARY KEY (assignment_id),
  CONSTRAINT assignment_staff_fk FOREIGN KEY (staff_id) REFERENCES public.staff(staff_id),
  CONSTRAINT assignment_shift_fk FOREIGN KEY (shift_id) REFERENCES public.shift(shift_id)
);
CREATE TABLE public.staff (
  staff_id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  first_name character varying NOT NULL,
  last_name character varying NOT NULL,
  email character varying UNIQUE,
  phone character varying,
  hire_date date NOT NULL,
  employment_type character varying,
  status character varying DEFAULT 'ACTIVE'::character varying,
  role_id integer NOT NULL,
  primary_department_id integer NOT NULL,
  CONSTRAINT staff_pkey PRIMARY KEY (staff_id),
  CONSTRAINT staff_role_fk FOREIGN KEY (role_id) REFERENCES public.role(role_id),
  CONSTRAINT staff_department_fk FOREIGN KEY (primary_department_id) REFERENCES public.department(department_id)
);
CREATE TABLE public.staff_qual (
  department_id integer NOT NULL,
  staff_id integer NOT NULL,
  qualified_date date,
  certification_level character varying,
  CONSTRAINT staff_qual_pkey PRIMARY KEY (department_id, staff_id),
  CONSTRAINT staff_qual_department_fk FOREIGN KEY (department_id) REFERENCES public.department(department_id),
  CONSTRAINT staff_qual_staff_fk FOREIGN KEY (staff_id) REFERENCES public.staff(staff_id)
);
CREATE TABLE public.wellness_score (
  wellness_id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  staff_id integer NOT NULL,
  date_recorded date NOT NULL,
  fatigue_score integer CHECK (fatigue_score >= 1 AND fatigue_score <= 10),
  stress_score integer CHECK (stress_score >= 1 AND stress_score <= 10),
  sleep_hours numeric,
  burnout_risk numeric DEFAULT '0'::numeric CHECK (burnout_risk >= 0::numeric AND burnout_risk <= 10::numeric),
  CONSTRAINT wellness_score_pkey PRIMARY KEY (wellness_id),
  CONSTRAINT wellness_staff_fk FOREIGN KEY (staff_id) REFERENCES public.staff(staff_id)
);
CREATE TABLE public.workload_record (
  workload_id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  staff_id integer NOT NULL,
  week_start_date date NOT NULL,
  total_hours numeric,
  night_shifts integer,
  consecutive_days integer,
  overtime_hours numeric,
  CONSTRAINT workload_record_pkey PRIMARY KEY (workload_id),
  CONSTRAINT workload_staff_fk FOREIGN KEY (staff_id) REFERENCES public.staff(staff_id)
);