import { useState } from 'react'
import { predict } from '../api/predict'

/**
 * Text input form that calls the /predict endpoint on submit.
 *
 * @param {{ onResult: (result: object) => void }} props
 */
export function PredictForm({ onResult }) {
    const [text, setText] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const canSubmit = text.trim().length > 0 && !loading

    async function handleSubmit(e) {
        e.preventDefault()
        if (!canSubmit) return
        setError(null)
        setLoading(true)
        try {
            const result = await predict(text.trim())
            onResult(result)
        } catch (err) {
            setError(err.message ?? 'Unexpected error.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="card">
            <form className="predict-form" onSubmit={handleSubmit}>
                <label htmlFor="sentiment-input">Text to analyse</label>

                <textarea
                    id="sentiment-input"
                    placeholder="Type or paste any text here — a tweet, review, headline…"
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    disabled={loading}
                    aria-label="Text to classify"
                />

                <div className="form-footer">
                    <span className="char-count">{text.length} chars</span>

                    <button
                        type="submit"
                        className="btn btn-primary"
                        disabled={!canSubmit}
                        aria-busy={loading}
                    >
                        {loading ? (
                            <>
                                <span className="spinner" />
                                Analysing…
                            </>
                        ) : (
                            <>
                                <span>✦</span>
                                Analyse
                            </>
                        )}
                    </button>
                </div>

                {error && (
                    <div className="error-banner" role="alert">
                        <span>⚠</span> {error}
                    </div>
                )}
            </form>
        </div>
    )
}
