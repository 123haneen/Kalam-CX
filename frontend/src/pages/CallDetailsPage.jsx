import { useEffect, useState } from 'react'

function CallDetailsPage({ callId, onBack }) {
  const [call, setCall] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/calls/${callId}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error('Could not load call details')
        }

        return response.json()
      })
      .then((data) => {
        setCall(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [callId])

  if (loading) {
    return <p>Loading call details...</p>
  }

  if (error) {
    return <p>Error: {error}</p>
  }

  return (
    <main>
      <button type="button" onClick={onBack}>
        ← Back to Calls
      </button>

      <h2>Call Details</h2>

      <div>
        <h3>{call.call_id}</h3>

        <p>
          <strong>Customer ID:</strong> {call.customer_id}
        </p>

        <p>
          <strong>Channel:</strong> {call.channel}
        </p>

        <p>
          <strong>Date:</strong> {call.date}
        </p>
      </div>

      <div>
        <h3>Full Transcript</h3>

        <pre style={{ whiteSpace: 'pre-wrap' }}>
          {call.transcript}
        </pre>
      </div>
    </main>
  )
}

export default CallDetailsPage