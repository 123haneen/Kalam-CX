import { useEffect, useState } from 'react'

function SummaryPage() {
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetch('http://127.0.0.1:8000/summary')
      .then((response) => {
        if (!response.ok) {
          throw new Error('Could not load operational summary')
        }

        return response.json()
      })
      .then((data) => {
        setSummary(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <main>
        <div className="empty-state">
          <p>Loading operational summary...</p>
        </div>
      </main>
    )
  }

  if (error) {
    return (
      <main>
        <div className="error-message">
          {error}
        </div>
      </main>
    )
  }

  const categoryEntries = Object.entries(summary.categories || {})
  const sentimentEntries = Object.entries(summary.sentiments || {})

  const maxCategoryCount = Math.max(
    1,
    ...categoryEntries.map(([, count]) => Number(count) || 0)
  )

  const maxSentimentCount = Math.max(
    1,
    ...sentimentEntries.map(([, count]) => Number(count) || 0)
  )

  return (
    <main>
      <div className="page-heading">
        <div>
          <h2>Operational Summary</h2>
          <p>
            Current state of processed customer-support calls.
          </p>
        </div>

        <span>{summary.total_calls} processed</span>
      </div>

      <div className="summary-counts">
        <div className="summary-card">
          <span className="summary-label">Total Calls</span>
          <p>{summary.total_calls ?? 0}</p>
          <small>All processed interactions</small>
        </div>

        <div className="summary-card summary-card-success">
          <span className="summary-label">Auto Saved</span>
          <p>{summary.auto_saved ?? 0}</p>
          <small>Routine calls saved automatically</small>
        </div>

        <div className="summary-card summary-card-warning">
          <span className="summary-label">Human Review</span>
          <p>{summary.human_review ?? 0}</p>
          <small>Calls waiting for reviewer action</small>
        </div>

        <div className="summary-card summary-card-danger">
          <span className="summary-label">Escalated</span>
          <p>{summary.escalated ?? 0}</p>
          <small>Calls requiring escalation</small>
        </div>

        <div className="summary-card summary-card-neutral">
          <span className="summary-label">Non-Interactions</span>
          <p>{summary.non_interactions ?? 0}</p>
          <small>Wrong number, silent, or dropped calls</small>
        </div>
      </div>

      <div className="summary-breakdowns">
        <section className="summary-panel">
          <div className="section-heading">
            <div>
              <h3>Calls by Category</h3>
              <p>
                Distribution of processed calls across the support taxonomy.
              </p>
            </div>
          </div>

          {categoryEntries.length === 0 ? (
            <div className="empty-inline">
              No category data available.
            </div>
          ) : (
            <div className="breakdown-list">
              {categoryEntries.map(([category, count]) => {
                const numericCount = Number(count) || 0
                const percentage =
                  (numericCount / maxCategoryCount) * 100

                return (
                  <div
                    className="breakdown-item"
                    key={category}
                  >
                    <div className="breakdown-row">
                      <span>{category}</span>
                      <strong>{numericCount}</strong>
                    </div>

                    <div className="breakdown-track">
                      <div
                        className="breakdown-fill"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </section>

        <section className="summary-panel">
          <div className="section-heading">
            <div>
              <h3>Calls by Sentiment</h3>
              <p>
                Customer sentiment detected across processed calls.
              </p>
            </div>
          </div>

          {sentimentEntries.length === 0 ? (
            <div className="empty-inline">
              No sentiment data available.
            </div>
          ) : (
            <div className="breakdown-list">
              {sentimentEntries.map(([sentiment, count]) => {
                const numericCount = Number(count) || 0
                const percentage =
                  (numericCount / maxSentimentCount) * 100

                return (
                  <div
                    className="breakdown-item"
                    key={sentiment}
                  >
                    <div className="breakdown-row">
                      <span>{sentiment}</span>
                      <strong>{numericCount}</strong>
                    </div>

                    <div className="breakdown-track">
                      <div
                        className="breakdown-fill"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </section>
      </div>

      <section className="summary-note">
        <div>
          <span className="eyebrow">
            Operational View
          </span>

          <h3>What this panel shows</h3>

          <p>
            Kalam CX intentionally provides a lightweight counts panel rather
            than a full analytics dashboard. It shows how processed calls are
            distributed across automatic saving, human review, escalation,
            non-interactions, categories, and sentiments.
          </p>
        </div>
      </section>
    </main>
  )
}

export default SummaryPage