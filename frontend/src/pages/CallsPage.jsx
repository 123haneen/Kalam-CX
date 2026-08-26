import { useEffect, useState } from 'react'

function CallsPage() {
  const [calls, setCalls] = useState([])
  const [selectedCall, setSelectedCall] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [processing, setProcessing] = useState(false)

  useEffect(() => {
    fetch('http://127.0.0.1:8000/calls')
      .then((response) => {
        if (!response.ok) {
          throw new Error('Could not load calls')
        }

        return response.json()
      })
      .then((data) => {
        setCalls(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  const selectCall = (callId) => {
    setError('')
    setResult(null)

    fetch(`http://127.0.0.1:8000/calls/${callId}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error('Could not load call')
        }

        return response.json()
      })
      .then((data) => {
        setSelectedCall(data)
      })
      .catch((err) => {
        setError(err.message)
      })
  }

  const processCall = () => {
    setProcessing(true)
    setError('')
    setResult(null)

    fetch(`http://127.0.0.1:8000/process/${selectedCall.call_id}`, {
      method: 'POST',
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error('Could not process call')
        }

        return response.json()
      })
      .then((data) => {
        setResult(data)
        setProcessing(false)
      })
      .catch((err) => {
        setError(err.message)
        setProcessing(false)
      })
  }

  const goBackToCalls = () => {
    setSelectedCall(null)
    setResult(null)
    setError('')
  }

  const decisionClass = (decision) => {
    if (decision === 'AUTO_SAVE') return 'badge-success'
    if (decision === 'ESCALATE') return 'badge-danger'
    if (decision === 'ROUTE_TO_REVIEW') return 'badge-warning'
    if (decision === 'NON_INTERACTION') return 'badge-neutral'

    return 'badge-neutral'
  }

  const priorityClass = (priority) => {
    if (priority === 'Urgent') return 'badge-danger'
    if (priority === 'High') return 'badge-warning'
    if (priority === 'Medium') return 'badge-info'

    return 'badge-neutral'
  }

  if (loading) {
    return (
      <main>
        <div className="empty-state">
          <p>Loading calls...</p>
        </div>
      </main>
    )
  }

  return (
    <main>
      {!selectedCall ? (
        <>
          <div className="page-heading">
            <div>
              <h2>Call Intake</h2>
              <p>
                Select an incoming customer call transcript and send it through
                the guarded documentation engine.
              </p>
            </div>

            <span>{calls.length} calls</span>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="calls-list">
            {calls.map((call) => (
              <div
                className="call-card"
                key={call.call_id}
              >
                <div className="call-primary">
                  <div className="call-id">
                    {call.call_id}
                  </div>

                  <div>
                    <h3>
                      Customer {call.customer_id || 'Unknown'}
                    </h3>
                    <p>
                      Incoming customer-support interaction
                    </p>
                  </div>
                </div>

                <div className="call-meta">
                  <span>
                    {call.channel || 'Unknown channel'}
                  </span>

                  <span>
                    {call.date || 'No date provided'}
                  </span>
                </div>

                <button
                  type="button"
                  onClick={() => selectCall(call.call_id)}
                >
                  Select Call
                </button>
              </div>
            ))}
          </div>
        </>
      ) : (
        <>
          <div className="detail-toolbar">
            <button
              type="button"
              className="secondary-button"
              onClick={goBackToCalls}
            >
              ← Back to Calls
            </button>
          </div>

          <div className="intake-details">
            <div className="record-heading">
              <div>
                <span className="eyebrow">
                  Selected Call
                </span>

                <h2>{selectedCall.call_id}</h2>

                <p>
                  Review the transcript before processing it through Kalam CX.
                </p>
              </div>
            </div>

            <div className="metadata-grid">
              <div className="metadata-item">
                <span>Customer ID</span>
                <strong>
                  {selectedCall.customer_id || 'Not available'}
                </strong>
              </div>

              <div className="metadata-item">
                <span>Channel</span>
                <strong>
                  {selectedCall.channel || 'Not available'}
                </strong>
              </div>

              <div className="metadata-item">
                <span>Date</span>
                <strong>
                  {selectedCall.date || 'Not available'}
                </strong>
              </div>
            </div>

            <div className="section-heading">
              <div>
                <h3>Call Transcript</h3>
                <p>
                  Original transcribed interaction received by the intake.
                </p>
              </div>
            </div>

            <div className="transcript">
              <pre style={{ whiteSpace: 'pre-wrap' }}>
                {selectedCall.transcript}
              </pre>
            </div>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            <div className="process-actions">
              <button
                type="button"
                onClick={processCall}
                disabled={processing}
              >
                {processing
                  ? 'Processing Call...'
                  : 'Process Call'}
              </button>
            </div>

            {result && (
              <div className="process-result">
                <div className="result-header">
                  <div>
                    <span className="eyebrow">
                      Guarded Engine Output
                    </span>

                    <h2>Processed Record</h2>

                    <p>
                      Structured documentation and operational decision generated
                      from the transcript and handbook rules.
                    </p>
                  </div>

                  <div className="badge-row">
                    <span
                      className={`status-badge ${decisionClass(
                        result.decision
                      )}`}
                    >
                      {result.decision}
                    </span>

                    <span className="status-badge badge-neutral">
                      {result.status}
                    </span>
                  </div>
                </div>

                <section className="result-section">
                  <div className="section-heading">
                    <div>
                      <h3>Documentation</h3>
                      <p>
                        Concise structured fields produced from the call.
                      </p>
                    </div>
                  </div>

                  <div className="documentation-grid">
                    <div className="field-card field-card-wide">
                      <span>Summary</span>
                      <p>{result.summary}</p>
                    </div>

                    <div className="field-card">
                      <span>Issue</span>
                      <p>{result.issue}</p>
                    </div>

                    <div className="field-card">
                      <span>Root Cause</span>
                      <p>{result.root_cause}</p>
                    </div>

                    <div className="field-card">
                      <span>Resolution</span>
                      <p>{result.resolution}</p>
                    </div>

                    <div className="field-card">
                      <span>Next Action</span>
                      <p>{result.next_action}</p>
                    </div>
                  </div>
                </section>

                <section className="result-section">
                  <div className="section-heading">
                    <div>
                      <h3>Classification</h3>
                      <p>
                        Taxonomy and operational fields used by the guarded engine.
                      </p>
                    </div>
                  </div>

                  <div className="classification-grid">
                    <div className="metadata-item">
                      <span>Category</span>
                      <strong>{result.category}</strong>
                    </div>

                    <div className="metadata-item">
                      <span>Subcategory</span>
                      <strong>{result.subcategory}</strong>
                    </div>

                    <div className="metadata-item">
                      <span>Disposition</span>
                      <strong>{result.disposition}</strong>
                    </div>

                    <div className="metadata-item">
                      <span>Sentiment</span>
                      <strong>{result.sentiment}</strong>
                    </div>

                    <div className="metadata-item">
                      <span>Priority</span>
                      <strong>
                        <span
                          className={`status-badge ${priorityClass(
                            result.priority
                          )}`}
                        >
                          {result.priority}
                        </span>
                      </strong>
                    </div>

                    <div className="metadata-item">
                      <span>Escalation</span>
                      <strong>
                        <span
                          className={`status-badge ${
                            result.escalation_flag
                              ? 'badge-danger'
                              : 'badge-success'
                          }`}
                        >
                          {result.escalation_flag ? 'Yes' : 'No'}
                        </span>
                      </strong>
                    </div>
                  </div>
                </section>

                <section className="result-section">
                  <div className="section-heading">
                    <div>
                      <h3>Decision</h3>
                      <p>
                        Final code-controlled recommendation for this record.
                      </p>
                    </div>
                  </div>

                  <div className="decision-box">
                    <div>
                      <span>Decision</span>
                      <strong>{result.decision}</strong>
                    </div>

                    <p>{result.decision_reason}</p>
                  </div>

                  {result.escalation_reason && (
                    <div className="alert-box alert-danger">
                      <strong>Escalation Reason</strong>
                      <p>{result.escalation_reason}</p>
                    </div>
                  )}
                </section>

                <section className="result-section">
                  <div className="section-heading">
                    <div>
                      <h3>Follow-up Actions</h3>
                      <p>
                        Actions that remain pending after the call.
                      </p>
                    </div>
                  </div>

                  {result.follow_up_actions?.length > 0 ? (
                    <ul className="clean-list">
                      {result.follow_up_actions.map(
                        (action, index) => (
                          <li key={index}>
                            {action}
                          </li>
                        )
                      )}
                    </ul>
                  ) : (
                    <div className="empty-inline">
                      No follow-up actions required.
                    </div>
                  )}
                </section>

                <section className="result-section">
                  <div className="section-heading">
                    <div>
                      <h3>Keywords & Tags</h3>
                      <p>
                        Supporting labels generated for the record.
                      </p>
                    </div>
                  </div>

                  <div className="tag-group">
                    {result.keywords?.map((keyword) => (
                      <span
                        className="tag"
                        key={`keyword-${keyword}`}
                      >
                        {keyword}
                      </span>
                    ))}

                    {result.tags?.map((tag) => (
                      <span
                        className="tag tag-accent"
                        key={`tag-${tag}`}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </section>

                <section className="result-section">
                  <div className="section-heading">
                    <div>
                      <h3>Handbook Rules</h3>
                      <p>
                        Rule references used to support the classification and
                        decision.
                      </p>
                    </div>
                  </div>

                  <div className="tag-group">
                    {result.rule_references?.length > 0 ? (
                      result.rule_references.map((rule) => (
                        <span
                          className="rule-chip"
                          key={rule}
                        >
                          Clause {rule}
                        </span>
                      ))
                    ) : (
                      <span>No rule references available.</span>
                    )}
                  </div>
                </section>

                <section className="result-section grounding-section">
                  <div className="section-heading">
                    <div>
                      <h3>Grounding Evidence</h3>
                      <p>
                        Original transcript evidence supporting the structured
                        documentation fields.
                      </p>
                    </div>
                  </div>

                  <div className="grounding-grid">
                    {result.grounding &&
                      Object.entries(result.grounding).map(
                        ([field, evidence]) => (
                          <div
                            className="grounding-card"
                            key={field}
                          >
                            <span>
                              {field.replaceAll('_', ' ')}
                            </span>

                            <p>{evidence}</p>
                          </div>
                        )
                      )}
                  </div>
                </section>
              </div>
            )}
          </div>
        </>
      )}
    </main>
  )
}

export default CallsPage