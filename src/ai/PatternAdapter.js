// PatternAdapter.js - converts backend patterns into Beat Addicts sequencer data
const DEFAULT_TRACKS = ['Kick', 'Snare', 'Hi-Hat', 'Open Hat', 'Crash', 'Ride', 'Clap', 'Perc']
const DEFAULT_STEPS = 16
const TIMELINE_COLORS = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']

export class PatternAdapter {
  constructor(config = {}) {
    this.trackNames = config.trackNames ?? DEFAULT_TRACKS
    this.steps = config.steps ?? DEFAULT_STEPS
  }

  emptyPattern() {
    return this.trackNames.reduce((acc, name) => {
      acc[name] = new Array(this.steps).fill(false)
      return acc
    }, {})
  }

  sectionsToSequencer(sections = {}) {
    const sequencer = this.emptyPattern()
    Object.values(sections).forEach(section => this.#applySection(sequencer, section))
    return sequencer
  }

  sectionsToTimeline(sections = {}, style = 'AI') {
    const entries = Object.entries(sections)
    return entries.map(([sectionKey, section], index) => {
      const color = TIMELINE_COLORS[index % TIMELINE_COLORS.length]
      return {
        id: `ai-${sectionKey}`,
        name: `${style} ${sectionKey.charAt(0).toUpperCase() + sectionKey.slice(1)}`,
        clips: this.#buildClips(section, color, sectionKey)
      }
    })
  }

  mergeTimeline(currentTimeline = [], aiTimeline = []) {
    const filtered = currentTimeline.filter(track => {
      const identifier = typeof track.id === 'string' ? track.id : ''
      return !identifier.startsWith('ai-')
    })
    return [...filtered, ...aiTimeline]
  }

  createArrangementClips(arrangement = null) {
    if (!arrangement?.sections) return []
    return arrangement.sections.map((chunk, index) => ({
      id: `ai-arrangement-${index}`,
      name: chunk.label ?? `Section ${index + 1}`,
      clips: [
        {
          start: chunk.start ?? 0,
          length: chunk.length ?? 4,
          color: TIMELINE_COLORS[index % TIMELINE_COLORS.length],
          name: chunk.intent ?? 'AI Arrangement'
        }
      ]
    }))
  }

  summarizePattern(pattern = this.emptyPattern()) {
    return Object.entries(pattern).map(([track, steps]) => ({
      track,
      active: steps.reduce((acc, active, idx) => (active ? acc.concat(idx) : acc), [])
    }))
  }

  #applySection(target, section) {
    if (!section?.tracks) return target
    section.tracks.forEach(track => {
      const trackName = this.#normalizeTrackName(track.name ?? track.id)
      if (!trackName || !target[trackName]) return
      const hits = Array.isArray(track.hits) ? track.hits : []
      hits.forEach(step => {
        const index = Math.max(0, Math.min(this.steps - 1, step))
        target[trackName][index] = true
      })
    })
    return target
  }

  #buildClips(section, color, fallbackName) {
    if (!section?.clips?.length && !section?.tracks?.length) {
      return [
        {
          start: 0,
          length: section?.length ?? 4,
          color,
          name: `${fallbackName} motif`
        }
      ]
    }

    if (section.clips?.length) {
      return section.clips.map(clip => ({
        start: clip.start ?? 0,
        length: clip.length ?? 4,
        color: clip.color ?? color,
        name: clip.name ?? `${fallbackName} clip`
      }))
    }

    return section.tracks.map((track, index) => ({
      start: (track.offset ?? index * 4) % this.steps,
      length: track.length ?? 4,
      color: color,
      name: track.name ?? `${fallbackName} track`
    }))
  }

  #normalizeTrackName(name) {
    if (!name) return null
    const normalized = name.toLowerCase()
    return this.trackNames.find(track => track.toLowerCase() === normalized) ?? null
  }
}

export const patternAdapter = new PatternAdapter()
