import React, { useState } from "react";
import Calendar from "react-calendar";
import 'react-calendar/dist/Calendar.css';

const CalendarPage: React.FC = () => {
  const [date, setDate] = useState<Date>(new Date());

  return (
    <div className="calendar-card">
      <div className="calendar-container">
        <h2 style={{ marginBottom: "20px" }}>Calendar</h2>
      <Calendar
        onChange={(value) => setDate(value as Date)}
        value={date}
      />
      <p className="selected-date">
        Selected: {date.toDateString()}
      </p>
      </div>
    </div>
  );
};

export default CalendarPage;