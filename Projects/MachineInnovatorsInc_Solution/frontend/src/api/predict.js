/**
 * API client for the sentiment inference backend.
 *
 * All calls go through the Vite dev-proxy to /api/v1 which forwards
 * to http://localhost:8000 in development. In production point
 * VITE_API_BASE_URL to the deployed backend.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

/**
 * @typedef {Object} PredictionResult
 * @property {string} label       - Predicted class label ("negative"|"neutral"|"positive")
 * @property {number} label_id    - Integer class index
 * @property {Object.<string, number>} scores - Per-class softmax probabilities
 */

/**
 * Call the /predict endpoint with a piece of text.
 *
 * @param {string} text - Raw text to classify
 * @returns {Promise<PredictionResult>}
 * @throws {Error} When the network request fails or the server returns an error
 */
export async function predict(text) {
    const response = await fetch(`${BASE_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
    })

    if (!response.ok) {
        const detail = await response.json().catch(() => ({}))
        throw new Error(detail?.detail ?? `Server error: ${response.status}`)
    }

    return response.json()
}

/**
 * Call the /health endpoint.
 *
 * @returns {Promise<{status: string, model: string}>}
 */
export async function health() {
    const response = await fetch(`${BASE_URL}/health`)
    if (!response.ok) throw new Error(`Health check failed: ${response.status}`)
    return response.json()
}
