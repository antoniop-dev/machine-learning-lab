/**
 * Displays a sentiment prediction result with an animated label badge
 * and per-class probability bars.
 *
 * @param {{ result: import('../api/predict').PredictionResult }} props
 */
export function ResultCard({ result }) {
    const { label, scores } = result

    const LABEL_EMOJI = { positive: '😊', neutral: '😐', negative: '😞' }
    const BAR_ORDER = ['positive', 'neutral', 'negative']

    return (
        <div className="card result-card">
            <div className="result-header">
                <span className={`result-label-badge ${label}`}>
                    {LABEL_EMOJI[label] ?? '🤔'} {label}
                </span>

                <p className="result-confidence">
                    Confidence:{' '}
                    <strong>{(scores[label] * 100).toFixed(1)}%</strong>
                </p>
            </div>

            <div className="score-bars" role="list" aria-label="Score breakdown">
                {BAR_ORDER.map((cls) => {
                    const pct = (scores[cls] ?? 0) * 100
                    return (
                        <div key={cls} className="score-row" role="listitem">
                            <span className="score-label">{cls}</span>
                            <div className="score-track" aria-hidden="true">
                                <div
                                    className={`score-fill ${cls}`}
                                    style={{ width: `${pct}%` }}
                                />
                            </div>
                            <span className="score-pct">{pct.toFixed(1)}%</span>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
