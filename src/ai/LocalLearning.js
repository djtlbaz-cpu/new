// LocalLearning.js - lightweight preference learning with Phase 0 legal checks
import { aiClient } from './AIClient'

const STORAGE_KEY = 'beat-addicts-local-learning'
const PHASE0_OPT_IN_KEY = 'phase0-legal-opt-in'
const PHASE0_LIMIT_KEY = 'phase0-generation-limit'
const DEFAULT_GENERATION_LIMIT = 64

class LocalLearning {
  constructor(storageKey = STORAGE_KEY) {
    this.storageKey = storageKey
    this.state = {
      optedIn: false,
      generationCount: 0,
      maxGenerations: DEFAULT_GENERATION_LIMIT,
      preferences: {},
      lastSyncedAt: null,
      user: this.#bootstrapUser()
    }

    this.#loadFromStorage()
    this.#syncWithPhaseZero()
  }

  #bootstrapUser() {
    const randomId = typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : `user-${Date.now()}`
    const safeStorage = this.#getStorage()
    const storedId = safeStorage?.getItem('phase0-user-id')
    if (!storedId && safeStorage) {
      safeStorage.setItem('phase0-user-id', randomId)
    }

    return {
      id: storedId ?? randomId,
      email: 'beta@beataddicts.local',
      licenseTier: 'Phase0',
      region: 'local'
    }
  }

  #getStorage() {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        return window.localStorage
      }
    } catch (error) {
      console.warn('Local learning storage unavailable:', error)
    }
    return null
  }

  #loadFromStorage() {
    const storage = this.#getStorage()
    if (!storage) return
    try {
      const raw = storage.getItem(this.storageKey)
      if (raw) {
        this.state = { ...this.state, ...JSON.parse(raw) }
      }
    } catch (error) {
      console.warn('Failed to parse local learning state:', error)
    }
  }

  #saveToStorage() {
    const storage = this.#getStorage()
    if (!storage) return
    try {
      storage.setItem(this.storageKey, JSON.stringify(this.state))
    } catch (error) {
      console.warn('Failed to persist local learning state:', error)
    }
  }

  #syncWithPhaseZero() {
    const storage = this.#getStorage()
    if (!storage) return
    const optInValue = storage.getItem(PHASE0_OPT_IN_KEY)
    if (optInValue !== null) {
      this.state.optedIn = optInValue === 'true'
    }
    const limitValue = parseInt(storage.getItem(PHASE0_LIMIT_KEY) ?? '', 10)
    if (!Number.isNaN(limitValue)) {
      this.state.maxGenerations = limitValue
    }
    this.#saveToStorage()
  }

  hasOptedIn() {
    return Boolean(this.state.optedIn)
  }

  setOptIn(value) {
    const storage = this.#getStorage()
    this.state.optedIn = Boolean(value)
    if (storage) {
      storage.setItem(PHASE0_OPT_IN_KEY, String(this.state.optedIn))
    }
    this.#saveToStorage()
  }

  canGenerate() {
    return this.state.generationCount < this.state.maxGenerations
  }

  recordGeneration(metadata = {}) {
    this.state.generationCount += 1
    this.state.lastSyncedAt = Date.now()
    this.#saveToStorage()
    if (this.state.optedIn) {
      this.#pushTrainingMetadata(metadata)
    }
  }

  recordPreference({ style, accepted = true, metadata = {} }) {
    if (!style) return
    const entry = this.state.preferences[style] ?? { accepted: 0, rejected: 0 }
    if (accepted) {
      entry.accepted += 1
    } else {
      entry.rejected += 1
    }
    this.state.preferences[style] = entry
    this.#saveToStorage()

    if (metadata?.patternId || metadata?.pattern_id) {
      this.#pushPatternFeedback({
        style,
        accepted,
        metadata,
        patternId: metadata.patternId ?? metadata.pattern_id
      })
    }

    if (this.state.optedIn) {
      aiClient.syncPreferenceProfile({
        style,
        accepted,
        metadata,
        user: this.getUserContext(),
        preferences: this.state.preferences
      }).catch((error) => console.warn('Preference sync failed:', error))
    }
  }

  getUserContext() {
    return {
      ...this.state.user,
      optedIn: this.state.optedIn,
      generationLimit: this.state.maxGenerations,
      generationCount: this.state.generationCount
    }
  }

  getGenerationLimit() {
    return this.state.maxGenerations
  }

  #pushTrainingMetadata(metadata = {}) {
    aiClient.submitTrainingBatchMetadata({
      timestamp: new Date().toISOString(),
      user: this.getUserContext(),
      metadata
    }).catch((error) => console.warn('Training metadata sync failed:', error))
  }

  #pushPatternFeedback(payload) {
    aiClient.submitPatternFeedback({
      patternId: payload.patternId,
      accepted: payload.accepted,
      style: payload.style,
      metadata: payload.metadata,
      user: this.getUserContext()
    }).catch((error) => console.warn('Pattern feedback sync failed:', error))
  }
}

export const localLearning = new LocalLearning()
export default LocalLearning
