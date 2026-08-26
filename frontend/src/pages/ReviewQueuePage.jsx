import { useEffect, useState } from 'react'

function ReviewQueuePage() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedItem, setSelectedItem] = useState(null)

  const [reviewMessage, setReviewMessage] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const [editMode, setEditMode] = useState(false)
  const [editData, setEditData] = useState({})

  const [overrideMode, setOverrideMode] = useState(false)
  const [overrideDecision, setOverrideDecision] = useState('AUTO_SAVE')
  const [reviewerNote, setReviewerNote] = useState('')

  useEffect(() => {
    fetch('http://127.0.0.1:8000/review-queue')
      .then((response) => {
        if (!response.ok) {
          throw new Error('Could not load review queue')
        }

        return response.json()
      })
      .then((data) => {
        setItems(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  const approveCall = () => {
    setSubmitting(true)
    setReviewMessage('')
    setError('')

    fetch(`http://127.0.0.1:8000/review/${selectedItem.call_id}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        approved: true,
        edits: {},
        override_decision: 'AUTO_SAVE',
        reviewer_note: 'Approved by human reviewer',
      }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error('Could not approve record')
        }

        return response.json()
      })
      .then(() => {
        setReviewMessage('Record approved successfully.')

        setItems((currentItems) =>
          currentItems.filter(
            (item) => item.call_id !== selectedItem.call_id
          )
        )

        setSubmitting(false)
      })
      .catch((err) => {
        setError(err.message)
        setSubmitting(false)
      })
  }

  const startEditing = () => {
    setEditData({
      summary: selectedItem.summary || '',
      issue: selectedItem.issue || '',
      root_cause: selectedItem.root_cause || '',
      resolution: selectedItem.resolution || '',
      next_action: selectedItem.next_action || '',
      category: selectedItem.category || '',
      subcategory: selectedItem.subcategory || '',
      priority: selectedItem.priority || '',
      sentiment: selectedItem.sentiment || '',
      disposition: selectedItem.disposition || '',
    })

    setReviewMessage('')
    setOverrideMode(false)
    setEditMode(true)
  }

  const handleEditChange = (event) => {
    const { name, value } = event.target

    setEditData((currentData) => ({
      ...currentData,
      [name]: value,
    }))
  }

  const saveEdits = () => {
    setSubmitting(true)
    setReviewMessage('')
    setError('')

    fetch(`http://127.0.0.1:8000/review/${selectedItem.call_id}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        approved: true,
        edits: editData,
        override_decision: null,
        reviewer_note: 'Record edited and approved by human reviewer',
      }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error('Could not save edited record')
        }

        return response.json()
      })
      .then(() => {
        setReviewMessage('Edits saved and record approved successfully.')
        setEditMode(false)

        setItems((currentItems) =>
          currentItems.filter(
            (item) => item.call_id !== selectedItem.call_id
          )
        )

        setSubmitting(false)
      })
      .catch((err) => {
        setError(err.message)
        setSubmitting(false)
      })
  }

  const submitOverride = () => {
    if (!reviewerNote.trim()) {
      setReviewMessage('Please enter a reason for the override.')
      return
    }

    setSubmitting(true)
    setReviewMessage('')
    setError('')

    fetch(`http://127.0.0.1:8000/review/${selectedItem.call_id}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        approved: true,
        edits: {},
        override_decision: overrideDecision,
        reviewer_note: reviewerNote,
      }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error('Could not override decision')
        }

        return response.json()
      })
      .then(() => {
        setReviewMessage(
          `Decision overridden to ${overrideDecision} successfully.`
        )

        setItems((currentItems) =>
          currentItems.filter(
            (item) => item.call_id !== selectedItem.call_id
          )
        )

        setOverrideMode(false)
        setReviewerNote('')
        setSubmitting(false)
      })
      .catch((err) => {
        setError(err.message)
        setSubmitting(false)
      })
  }

  const backToQueue = () => {
    setSelectedItem(null)
    setReviewMessage('')
    setEditMode(false)
    setOverrideMode(false)
    setReviewerNote('')
    setError('')
  }

  const priorityClass = (priority) => {
    if (priority === 'Urgent') return 'badge-danger'
    if (priority === 'High') return 'badge-warning'
    if (priority === 'Medium') return 'badge-info'

    return 'badge-neutral'
  }

  const decisionClass = (decision) => {
    if (decision === 'ESCALATE') return 'badge-danger'
    if (
      decision === 'ROUTE_TO_REVIEW' ||
      decision === 'HUMAN_REVIEW'
    ) {
      return 'badge-warning'
    }
    if (decision === 'AUTO_SAVE') return 'badge-success'

    return 'badge-neutral'
  }

  if (loading) {
    return (
      <main>
        <div className="empty-state">
          <p>Loading review queue...</p>
        </div>
      </main>
    )
  }

  if (selectedItem) {
    return (
      <main>
        <div className="detail-toolbar">
          <button
            type="button"
            className="secondary-button"
            onClick={backToQueue}
          >
            ← Back to Review Queue
          </button>
        </div>

        <div className="review-detail-container">
          <div className="result-header">
            <div>
              <span className="eyebrow">
                Human Review
              </span>

              <h2>Review Record</h2>

              <p>
                Inspect the drafted record and approve, edit, or override
                the engine recommendation.
              </p>
            </div>

            <div className="badge-row">
              <span
                className={`status-badge ${decisionClass(
                  selectedItem.decision
                )}`}
              >
                {selectedItem.decision}
              </span>

              <span
                className={`status-badge ${priorityClass(
                  selectedItem.priority
                )}`}
              >
                {selectedItem.priority}
              </span>
            </div>
          </div>

          <div className="metadata-grid review-metadata">
            <div className="metadata-item">
              <span>Call</span>
              <strong>{selectedItem.call_id}</strong>
            </div>

            <div className="metadata-item">
              <span>Customer</span>
              <strong>
                {selectedItem.customer_id || 'Not available'}
              </strong>
            </div>

            <div className="metadata-item">
              <span>Current Decision</span>
              <strong>{selectedItem.decision}</strong>
            </div>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {reviewMessage && (
            <div className="review-message">
              {reviewMessage}
            </div>
          )}

          {!editMode ? (
            <>
              <section className="result-section">
                <div className="section-heading">
                  <div>
                    <h3>Drafted Documentation</h3>
                    <p>
                      Review the structured fields before approving the
                      record.
                    </p>
                  </div>
                </div>

                <div className="documentation-grid">
                  <div className="field-card field-card-wide">
                    <span>Summary</span>
                    <p>{selectedItem.summary}</p>
                  </div>

                  <div className="field-card">
                    <span>Issue</span>
                    <p>{selectedItem.issue}</p>
                  </div>

                  <div className="field-card">
                    <span>Root Cause</span>
                    <p>{selectedItem.root_cause}</p>
                  </div>

                  <div className="field-card">
                    <span>Resolution</span>
                    <p>{selectedItem.resolution}</p>
                  </div>

                  <div className="field-card">
                    <span>Next Action</span>
                    <p>{selectedItem.next_action}</p>
                  </div>
                </div>
              </section>

              <section className="result-section">
                <div className="section-heading">
                  <div>
                    <h3>Classification</h3>
                    <p>
                      Classification proposed by the guarded engine.
                    </p>
                  </div>
                </div>

                <div className="classification-grid">
                  <div className="metadata-item">
                    <span>Category</span>
                    <strong>{selectedItem.category}</strong>
                  </div>

                  <div className="metadata-item">
                    <span>Subcategory</span>
                    <strong>{selectedItem.subcategory}</strong>
                  </div>

                  <div className="metadata-item">
                    <span>Priority</span>
                    <strong>{selectedItem.priority}</strong>
                  </div>

                  <div className="metadata-item">
                    <span>Sentiment</span>
                    <strong>{selectedItem.sentiment}</strong>
                  </div>

                  <div className="metadata-item">
                    <span>Disposition</span>
                    <strong>{selectedItem.disposition}</strong>
                  </div>

                  <div className="metadata-item">
                    <span>Decision</span>
                    <strong>{selectedItem.decision}</strong>
                  </div>
                </div>
              </section>

              <section className="result-section">
                <div className="section-heading">
                  <div>
                    <h3>Engine Recommendation</h3>
                    <p>
                      Why Kalam CX routed this record for human review.
                    </p>
                  </div>
                </div>

                <div className="decision-box">
                  <div>
                    <span>Recommendation</span>
                    <strong>{selectedItem.decision}</strong>
                  </div>

                  <p>
                    {selectedItem.decision_reason}
                  </p>
                </div>
              </section>

              {selectedItem.grounding && (
                <section className="result-section">
                  <div className="section-heading">
                    <div>
                      <h3>Grounding Evidence</h3>
                      <p>
                        Transcript evidence supporting the drafted
                        documentation.
                      </p>
                    </div>
                  </div>

                  <div className="grounding-grid">
                    {Object.entries(selectedItem.grounding).map(
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
              )}

              {selectedItem.rule_references?.length > 0 && (
                <section className="result-section">
                  <div className="section-heading">
                    <div>
                      <h3>Handbook Rules</h3>
                      <p>
                        Handbook clauses referenced by the engine.
                      </p>
                    </div>
                  </div>

                  <div className="tag-group">
                    {selectedItem.rule_references.map((rule) => (
                      <span
                        className="rule-chip"
                        key={rule}
                      >
                        Clause {rule}
                      </span>
                    ))}
                  </div>
                </section>
              )}

              <section className="review-actions-section">
                <div>
                  <h3>Human Decision</h3>
                  <p>
                    Choose how this drafted record should be handled.
                  </p>
                </div>

                <div className="review-actions">
                  <button
                    type="button"
                    className="approve-button"
                    onClick={approveCall}
                    disabled={submitting}
                  >
                    {submitting ? 'Approving...' : 'Approve Record'}
                  </button>

                  <button
                    type="button"
                    className="edit-button"
                    onClick={startEditing}
                    disabled={submitting}
                  >
                    Edit Record
                  </button>

                  <button
                    type="button"
                    className="override-button"
                    onClick={() => {
                      setOverrideMode(true)
                      setEditMode(false)
                      setReviewMessage('')
                    }}
                    disabled={submitting}
                  >
                    Override Decision
                  </button>
                </div>
              </section>

              {overrideMode && (
                <div className="override-form">
                  <div className="section-heading">
                    <div>
                      <h3>Override Decision</h3>
                      <p>
                        Select a new decision and document the reason for
                        overriding the engine.
                      </p>
                    </div>
                  </div>

                  <label>
                    New Decision

                    <select
                      value={overrideDecision}
                      onChange={(event) =>
                        setOverrideDecision(event.target.value)
                      }
                    >
                      <option value="AUTO_SAVE">
                        AUTO_SAVE
                      </option>

                      <option value="ESCALATE">
                        ESCALATE
                      </option>

                      <option value="NON_INTERACTION">
                        NON_INTERACTION
                      </option>
                    </select>
                  </label>

                  <label>
                    Reviewer Note

                    <textarea
                      value={reviewerNote}
                      onChange={(event) =>
                        setReviewerNote(event.target.value)
                      }
                      placeholder="Explain why you are overriding the engine decision..."
                    />
                  </label>

                  <div className="form-actions">
                    <button
                      type="button"
                      onClick={submitOverride}
                      disabled={submitting}
                    >
                      {submitting
                        ? 'Submitting...'
                        : 'Confirm Override'}
                    </button>

                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => {
                        setOverrideMode(false)
                        setReviewerNote('')
                        setReviewMessage('')
                      }}
                      disabled={submitting}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="edit-form">
              <div className="section-heading">
                <div>
                  <h3>Edit Drafted Record</h3>
                  <p>
                    Correct supported documentation fields before
                    approving the record.
                  </p>
                </div>
              </div>

              <label>
                Summary
                <textarea
                  name="summary"
                  value={editData.summary}
                  onChange={handleEditChange}
                />
              </label>

              <label>
                Issue
                <textarea
                  name="issue"
                  value={editData.issue}
                  onChange={handleEditChange}
                />
              </label>

              <label>
                Root Cause
                <textarea
                  name="root_cause"
                  value={editData.root_cause}
                  onChange={handleEditChange}
                />
              </label>

              <label>
                Resolution
                <textarea
                  name="resolution"
                  value={editData.resolution}
                  onChange={handleEditChange}
                />
              </label>

              <label>
                Next Action
                <textarea
                  name="next_action"
                  value={editData.next_action}
                  onChange={handleEditChange}
                />
              </label>

              <div className="edit-fields-grid">
                <label>
                  Category
                  <input
                    type="text"
                    name="category"
                    value={editData.category}
                    onChange={handleEditChange}
                  />
                </label>

                <label>
                  Subcategory
                  <input
                    type="text"
                    name="subcategory"
                    value={editData.subcategory}
                    onChange={handleEditChange}
                  />
                </label>

                <label>
                  Priority
                  <input
                    type="text"
                    name="priority"
                    value={editData.priority}
                    onChange={handleEditChange}
                  />
                </label>

                <label>
                  Sentiment
                  <input
                    type="text"
                    name="sentiment"
                    value={editData.sentiment}
                    onChange={handleEditChange}
                  />
                </label>

                <label>
                  Disposition
                  <input
                    type="text"
                    name="disposition"
                    value={editData.disposition}
                    onChange={handleEditChange}
                  />
                </label>
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  className="approve-button"
                  onClick={saveEdits}
                  disabled={submitting}
                >
                  {submitting
                    ? 'Saving...'
                    : 'Save Edits & Approve'}
                </button>

                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => {
                    setEditMode(false)
                    setReviewMessage('')
                  }}
                  disabled={submitting}
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
    )
  }

  return (
    <main>
      <div className="page-heading">
        <div>
          <h2>Review Queue</h2>
          <p>
            Calls that require human review before they can be saved.
          </p>
        </div>

        <span>{items.length} pending</span>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {items.length === 0 ? (
        <div className="queue-empty">
          <div className="queue-empty-icon">✓</div>

          <h3>Review queue is clear</h3>

          <p>
            No calls currently require human review.
          </p>
        </div>
      ) : (
        <div className="review-list">
          {items.map((item) => (
            <div
              className="review-card"
              key={item.call_id}
            >
              <div className="review-card-header">
                <div>
                  <span className="eyebrow">
                    Human Review Required
                  </span>

                  <h3>{item.call_id}</h3>

                  <p>
                    Customer {item.customer_id || 'Unknown'}
                  </p>
                </div>

                <div className="badge-row">
                  <span
                    className={`status-badge ${decisionClass(
                      item.decision
                    )}`}
                  >
                    {item.decision}
                  </span>

                  <span
                    className={`status-badge ${priorityClass(
                      item.priority
                    )}`}
                  >
                    {item.priority}
                  </span>
                </div>
              </div>

              <div className="review-summary">
                <span>Summary</span>
                <p>{item.summary}</p>
              </div>

              <div className="review-card-meta">
                <div>
                  <span>Category</span>
                  <strong>{item.category}</strong>
                </div>

                <div>
                  <span>Priority</span>
                  <strong>{item.priority}</strong>
                </div>
              </div>

              <div className="review-recommendation">
                <span>Why human review?</span>
                <p>{item.decision_reason}</p>
              </div>

              <button
                type="button"
                onClick={() => {
                  setSelectedItem(item)
                  setReviewMessage('')
                  setEditMode(false)
                  setOverrideMode(false)
                  setReviewerNote('')
                }}
              >
                Review Call
              </button>
            </div>
          ))}
        </div>
      )}
    </main>
  )
}

export default ReviewQueuePage