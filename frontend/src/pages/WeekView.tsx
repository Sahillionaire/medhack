import { Calendar, momentLocalizer } from "react-big-calendar";
import moment from "moment";
import "react-big-calendar/lib/css/react-big-calendar.css";

const localizer = momentLocalizer(moment);

const events = [
  {
    title: "Meeting",
    start: new Date(2026, 1, 27, 10, 0),
    end: new Date(2026, 1, 27, 11, 0),
  },
  {
    title: "Workout",
    start: new Date(2026, 1, 27, 15, 0),
    end: new Date(2026, 1, 27, 16, 0),
  },
];

export default function WeekView() {
  return (
    <div className="page-background">
        <div className="calendar-card">
            <Calendar
        localizer={localizer}
        events={events}
        defaultView="week"
        views={["week"]}
        step={30}
        timeslots={2}
      />
        </div>
    </div>
  );
}