import React, { useState } from "react";
import Calendar from "react-calendar";
import type { CalendarProps } from "react-calendar";
import 'react-calendar/dist/Calendar.css';

const CalendarPage: React.FC = () => {
  // Use type Date or Date[] (range)
  const [date, setDate] = useState<Date | [Date, Date]>(new Date());

  // onChange type: LooseValue from react-calendar
  const handleChange: CalendarProps['onChange'] = (value) => {
    // value can be Date or [Date, Date]
    setDate(value as Date | [Date, Date]);
    console.log("Selected date:", value);
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Calendar</h1>
      <Calendar
        onChange={handleChange}
        value={date}
      />
      <p>
        Selected Date: {Array.isArray(date) 
          ? `${date[0].toDateString()} - ${date[1].toDateString()}` 
          : date.toDateString()}
      </p>
    </div>
  );
};

export default CalendarPage;