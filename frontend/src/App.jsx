import { useState } from 'react'
import './App.css'

import CallsPage from './pages/CallsPage.jsx'
import ReviewQueuePage from './pages/ReviewQueuePage.jsx'
import SummaryPage from './pages/SummaryPage.jsx'

function App() {
  const [currentPage, setCurrentPage] = useState('calls')

  return (
    <div className="app">
      <header className="app-header">
        <div className="brand">
          <div className="brand-mark">
            K
          </div>

          <div>
            <h1>Kalam CX</h1>
            <p>AI-Powered After-Call Automation Platform</p>
          </div>
        </div>

        <nav className="main-nav">
          <button
            type="button"
            className={currentPage === 'calls' ? 'nav-active' : ''}
            onClick={() => setCurrentPage('calls')}
          >
            Call Intake
          </button>

          <button
            type="button"
            className={currentPage === 'review' ? 'nav-active' : ''}
            onClick={() => setCurrentPage('review')}
          >
            Review Queue
          </button>

          <button
            type="button"
            className={currentPage === 'summary' ? 'nav-active' : ''}
            onClick={() => setCurrentPage('summary')}
          >
            Operational Summary
          </button>
        </nav>
      </header>

      {currentPage === 'calls' && <CallsPage />}
      {currentPage === 'review' && <ReviewQueuePage />}
      {currentPage === 'summary' && <SummaryPage />}
    </div>
  )
}

export default App