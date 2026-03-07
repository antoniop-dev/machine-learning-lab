import { useState } from 'react'
import './index.css'
import { PredictForm } from './components/PredictForm'
import { ResultCard } from './components/ResultCard'

export default function App() {
  const [result, setResult] = useState(null)

  return (
    <div className="app">
      <header className="app-header">
        <div className="logo" aria-hidden="true">✦</div>
        <h1>Sentiment Analyser</h1>
        <span className="subtitle">MachineInnovatorsInc</span>
      </header>

      <main className="app-main">
        <div className="hero">
          <h2>How does this text feel?</h2>
          <p>Paste any text below and the model will classify its sentiment.</p>
        </div>

        <PredictForm onResult={setResult} />

        {result && <ResultCard result={result} />}
      </main>

      <footer className="app-footer">
        Powered by <strong>antoniop-dev/sentiment-model-finetuned</strong>
      </footer>
    </div>
  )
}
