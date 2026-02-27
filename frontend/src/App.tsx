// import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'
import './App.css'
import Navbar from "./components/Navbar";
import CalendarPage from "./pages/CalendarPage";

function App() {
  //const [count, setCount] = useState(0)

  return (
    <div>
      <Navbar />
      <h2>Welcome to the app!</h2>
      <CalendarPage />;
    </div>
  )
}

export default App
