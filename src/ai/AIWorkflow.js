// AIWorkflow.js - orchestrates Pulse's step-by-step generation flow
import { aiClient } from './AIClient'
import { localLearning } from './LocalLearning'
import { patternAdapter } from './PatternAdapter'

const WORKFLOW_STEPS = [
  { section: 'drums', handler: (payload) => aiClient.generateDrums(payload) },
  { section: 'bassline', handler: (payload) => aiClient.generateBassline(payload) },
  { section: 'melody', handler: (payload) => aiClient.generateMelody(payload) },
  { section: 'chords', handler: (payload) => aiClient.generateChords(payload) }
]

export class AIWorkflow {
  constructor(client = aiClient, adapter = patternAdapter, learner = localLearning) {
    this.client = client
    this.adapter = adapter
    this.learner = learner
  }

  async generateBeat(input) {
    const payload = this.#buildPayload(input)
    const sections = {}

    for (const step of WORKFLOW_STEPS) {
      const response = await this.#generateSection(step.section, payload)
      if (response?.pattern) {
        sections[step.section] = response.pattern
      }
    }

    if (!sections.drums) {
      throw new Error('AI engine did not return a drum section, generation aborted.')
    }

    const sequencerPattern = this.adapter.sectionsToSequencer(sections)
    const timelineFromSections = this.adapter.sectionsToTimeline(sections, payload.style)
    const arrangement = await this.#requestArrangement(payload, sections, sequencerPattern)
    const arrangementTimeline = this.adapter.createArrangementClips(arrangement)

    if (payload.allowLearning) {
      await this.#syncMidiSnapshot(payload, sequencerPattern)
    }

    return {
      sequencerPattern,
      timeline: this.adapter.mergeTimeline(input.timeline ?? [], [...timelineFromSections, ...arrangementTimeline]),
      sections,
      arrangement,
      metadata: {
        workflow: 'pulse-local-v1',
        bpm: payload.bpm,
        style: payload.style,
        generatedAt: new Date().toISOString(),
        sectionsGenerated: Object.keys(sections)
      }
    }
  }

  async generateSingleSection(section, input) {
    return this.#generateSection(section, this.#buildPayload(input))
  }

  #buildPayload(input = {}) {
    const base = {
      bpm: input.bpm ?? 128,
      style: input.style ?? 'Hybrid',
      temperature: input.temperature ?? 0.65,
      steps: this.adapter.steps,
      timeline: input.timeline ?? [],
      metadata: input.metadata ?? {}
    }

    const userContext = input.user ?? this.learner.getUserContext()
    return {
      ...base,
      user: {
        ...userContext,
        optedIn: Boolean(userContext?.optedIn && this.learner.hasOptedIn())
      },
      allowLearning: Boolean(input.allowLearning && this.learner.hasOptedIn())
    }
  }

  async #generateSection(section, payload) {
    try {
      const methodName = `generate${section.charAt(0).toUpperCase() + section.slice(1)}`
      const generator = this.client[methodName]
      if (typeof generator !== 'function') {
        throw new Error(`Missing AI client method: ${methodName}`)
      }
      const response = await generator.call(this.client, payload)
      return response
    } catch (error) {
      console.warn(`Pulse could not generate ${section}:`, error)
      return null
    }
  }

  async #requestArrangement(payload, sections, sequencerPattern) {
    try {
      return await this.client.generateArrangement({
        ...payload,
        sections: this.adapter.summarizePattern(sequencerPattern)
      })
    } catch (error) {
      console.warn('Arrangement generation failed:', error)
      return null
    }
  }

  async #syncMidiSnapshot(payload, sequencerPattern) {
    try {
      await this.client.uploadMidiAsset({
        name: `${payload.style} pattern @${payload.bpm}bpm`,
        data: JSON.stringify(sequencerPattern),
        metadata: { workflow: 'pulse-local-v1' },
        user: payload.user
      })
    } catch (error) {
      console.warn('Unable to sync MIDI snapshot:', error)
    }
  }
}

export const aiWorkflow = new AIWorkflow()
export default AIWorkflow
