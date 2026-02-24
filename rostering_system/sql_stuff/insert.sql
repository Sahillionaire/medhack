------------------------------------------------
-- REALISTIC 7-DAY ROTATING ROSTER
-- Week starting 17 Feb 2026
------------------------------------------------

------------------------------------------------
-- CREATE DEPARTMENTS (3 departments)
------------------------------------------------

insert into department (
    department_name,
    location,
    min_staff_required_per_shift
) values ( 'Emergency',
           'Ground Floor - Trauma Wing',
           5 );

insert into department (
    department_name,
    location,
    min_staff_required_per_shift
) values ( 'Intensive Care Unit',
           'Level 2 - Critical Care',
           4 );

insert into department (
    department_name,
    location,
    min_staff_required_per_shift
) values ( 'General Ward',
           'Level 3 - Inpatient Services',
           8 );


------------------------------------------------
-- CREATE SHIFTS (7 days)
------------------------------------------------
begin
    for i in 0..6 loop
    -- DAY SHIFT
        insert into shift (
            department_id,
            shift_start,
            shift_end,
            shift_type,
            required_staff_count
        ) values ( 1,
                   to_timestamp('2026-02-17 08:00',
                                'YYYY-MM-DD HH24:MI') + i,
                   to_timestamp('2026-02-17 16:00',
                                'YYYY-MM-DD HH24:MI') + i,
                   'MORNING',
                   19 );

    -- NIGHT SHIFT
        insert into shift (
            department_id,
            shift_start,
            shift_end,
            shift_type,
            required_staff_count
        ) values ( 1,
                   to_timestamp('2026-02-17 20:00',
                                'YYYY-MM-DD HH24:MI') + i,
                   to_timestamp('2026-02-18 06:00',
                                'YYYY-MM-DD HH24:MI') + i,
                   'NIGHT',
                   13 );
    end loop;
end;
/

------------------------------------------------
-- 2 ASSIGN DOCTORS (ROTATING)
------------------------------------------------
-- Doctors Day (6 per day)
insert into assignment (
    staff_id,
    shift_id
)
    select d.staff_id,
           s.shift_id
      from (
        select staff_id,
               row_number()
               over(
                    order by staff_id
               ) rn
          from staff
         where role_id = 2
    ) d
      join (
        select shift_id,
               row_number()
               over(
                    order by shift_start
               ) day_num
          from shift
         where shift_type = 'MORNING'
    ) s
    on mod(
        d.rn + s.day_num,
        10
    ) < 6;

-- Doctors Night (3 per day)
insert into assignment (
    staff_id,
    shift_id
)
    select d.staff_id,
           s.shift_id
      from (
        select staff_id,
               row_number()
               over(
                    order by staff_id
               ) rn
          from staff
         where role_id = 2
    ) d
      join (
        select shift_id,
               row_number()
               over(
                    order by shift_start
               ) day_num
          from shift
         where shift_type = 'NIGHT'
    ) s
    on mod(
        d.rn + s.day_num,
        10
    ) < 3;

------------------------------------------------
-- ASSIGN NURSES (ROTATING)
------------------------------------------------
-- Nurses Day (13 per day)
insert into assignment (
    staff_id,
    shift_id
)
    select n.staff_id,
           s.shift_id
      from (
        select staff_id,
               row_number()
               over(
                    order by staff_id
               ) rn
          from staff
         where role_id = 1
    ) n
      join (
        select shift_id,
               row_number()
               over(
                    order by shift_start
               ) day_num
          from shift
         where shift_type = 'MORNING'
    ) s
    on mod(
        n.rn + s.day_num,
        26
    ) < 13;

-- Nurses Night (10 per day)
insert into assignment (
    staff_id,
    shift_id
)
    select n.staff_id,
           s.shift_id
      from (
        select staff_id,
               row_number()
               over(
                    order by staff_id
               ) rn
          from staff
         where role_id = 1
    ) n
      join (
        select shift_id,
               row_number()
               over(
                    order by shift_start
               ) day_num
          from shift
         where shift_type = 'NIGHT'
    ) s
    on mod(
        n.rn + s.day_num,
        26
    ) < 10;

--  commit; 