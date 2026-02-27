// import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'
import Navbar from "./components/Navbar";
import CalendarPage from "./pages/CalendarPage";

function App() {
  return (
    <div className="app-container">
      <Navbar />
      <main className="main-content">
        <CalendarPage />
      </main>
    </div>
  );
}

export default App;
