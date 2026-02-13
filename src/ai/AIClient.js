// AIClient.js - Pulse's bridge to the local AI engine backend
const DEFAULT_BASE_URL = (() => {
  try {
    return import.meta.env?.VITE_AI_API_BASE_URL ?? 'http://localhost:8000'
  } catch (error) {
    console.warn('Falling back to default AI base URL:', error)
    return 'http://localhost:8000'
  }
})()

class AIClient {
  constructor(baseUrl = DEFAULT_BASE_URL) {
    this.baseUrl = this.#normalizeBaseUrl(baseUrl)
    this.defaultHeaders = { 'Content-Type': 'application/json' }
    this.requestTimeout = 20000
  }

  setBaseUrl(url) {
    this.baseUrl = this.#normalizeBaseUrl(url)
  }

  #normalizeBaseUrl(url) {
    if (!url) return 'http://localhost:8000'
    return url.endsWith('/') ? url.slice(0, -1) : url
  }

  #normalizePath(path) {
    if (!path) return ''
    return path.startsWith('/') ? path : `/${path}`
  }

  async #post(path, payload, options = {}) {
    if (typeof navigator !== 'undefined' && !navigator.onLine) {
      throw new Error('Offline mode: AI engine is unavailable without backend connectivity.')
    }

    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), options.timeout ?? this.requestTimeout)

    try {
      const response = await fetch(`${this.baseUrl}${this.#normalizePath(path)}`, {
        method: 'POST',
        headers: { ...this.defaultHeaders, ...(options.headers ?? {}) },
        body: JSON.stringify(payload ?? {}),
        signal: controller.signal
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`AI engine returned ${response.status}: ${errorText}`)
      }

      return await response.json()
    } finally {
      clearTimeout(timeout)
    }
  }

  async #generate(section, payload) {
    return this.#post(`/generate/${section}`, payload)
  }

  generateDrums(payload) {
    return this.#generate('drums', payload)
  }

  generateBassline(payload) {
    return this.#generate('bassline', payload)
  }

  generateMelody(payload) {
    return this.#generate('melody', payload)
  }

  generateChords(payload) {
    return this.#generate('chords', payload)
  }

  generateArrangement(payload) {
    return this.#generate('arrangement', payload)
  }

  submitPatternFeedback(payload) {
    return this.#post('/feedback/pattern', payload)
  }

  syncPreferenceProfile(payload) {
    return this.#post('/learning/preferences', payload)
  }

  submitTrainingBatchMetadata(payload) {
    return this.#post('/training/batch', payload)
  }

  uploadMidiAsset(payload) {
    return this.#post('/feedback/midi', payload)
  }
}

export const aiClient = new AIClient()
export default AIClient
