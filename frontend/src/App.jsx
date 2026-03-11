import { useState } from 'react'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Rooms from './pages/Rooms'
import Students from './pages/Students'
import Allocations from './pages/Allocations'
import Billing from './pages/Billing'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard': return <Dashboard />
      case 'rooms': return <Rooms />
      case 'students': return <Students />
      case 'allocations': return <Allocations />
      case 'billing': return <Billing />
      default: return <Dashboard />
    }
  }

  return (
    <div className="app-container">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="main-content">
        {renderContent()}
      </main>
    </div>
  )
}

export default App
