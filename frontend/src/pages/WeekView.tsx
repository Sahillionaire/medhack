import { Calendar, momentLocalizer, Views } from "react-big-calendar";
import moment from "moment";
import "react-big-calendar/lib/css/react-big-calendar.css";
import { useState, useEffect } from "react";
import api from "../services/api";

const localizer = momentLocalizer(moment);

type Shift = {
  shift_id: number;
  department_id: number;
  shift_start: string;
  shift_end: string;
  shift_type: string; // DAY or NIGHT
};

export default function WeekView() {
  const [date, setDate] = useState(new Date());
  const [shifts, setShifts] = useState<Shift[]>([]);
  
  useEffect(() => {
  api.get("/shifts")
    .then(res => {
      console.log("SHIFTS FROM API:", res.data);
      setShifts(res.data);
    })
    .catch(err => console.error("API ERROR:", err));
}, []);

  // Transform shifts into react-big-calendar events
  const events = shifts.map(shift => ({
    id: shift.shift_id,
    title: `${shift.shift_type} - Dept ${shift.department_id}`,
    start: moment(shift.shift_start).toDate(),
    end: moment(shift.shift_end).toDate(),
    allDay: false,
    resource: shift
  }));
  
  return (
    <div className="page-background">
        <div className="calendar-card">
            <Calendar
            localizer={localizer}
            events={events}
            defaultView={Views.WEEK}
            views={{ week : true }}
            date={date}
            onNavigate={setDate}
            step={30}
            timeslots={2}
            style={{ height: "100%", color: "black" }}
            eventPropGetter={(event) => {
            // Color by shift type
            const backgroundColor = event.resource.shift_type === "DAY" ? "#3b82f6" : "#f97316";
            return { style: { backgroundColor, color: "black", borderRadius: "6px", padding: "2px" } };
          }}
            />
        </div>
    </div>
  );
}