// AudioEngine.js - Complete Web Audio API implementation for Beat Addicts
class AudioEngine {
  constructor() {
    this.audioContext = null;
    this.masterGain = null;
    this.samples = {};
    this.pianoSamples = {};
    this.isInitialized = false;
    this.isPlaying = false;
    this.currentStep = 0;
    this.bpm = 120;
    this.stepInterval = null;
    this.tracks = {};
    this.effects = {};
    this.activePianoNotes = new Map();
    
    // Piano note frequencies (C4 = 261.63 Hz)
    this.noteFrequencies = {
      'C3': 130.81, 'C#3': 138.59, 'D3': 146.83, 'D#3': 155.56, 'E3': 164.81, 'F3': 174.61,
      'F#3': 185.00, 'G3': 196.00, 'G#3': 207.65, 'A3': 220.00, 'A#3': 233.08, 'B3': 246.94,
      'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13, 'E4': 329.63, 'F4': 349.23,
      'F#4': 369.99, 'G4': 392.00, 'G#4': 415.30, 'A4': 440.00, 'A#4': 466.16, 'B4': 493.88,
      'C5': 523.25, 'C#5': 554.37, 'D5': 587.33, 'D#5': 622.25, 'E5': 659.25, 'F5': 698.46,
      'F#5': 739.99, 'G5': 783.99, 'G#5': 830.61, 'A5': 880.00, 'A#5': 932.33, 'B5': 987.77
    };
    
    this.initPromise = null;
  }

  async init() {
    if (this.initPromise) {
      return this.initPromise;
    }

    this.initPromise = this._initAudio();
    return this.initPromise;
  }

  async _initAudio() {
    try {
      // Create audio context
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      
      console.log('Audio context created, state:', this.audioContext.state);
      
      // Resume context if suspended (required for user interaction)
      if (this.audioContext.state === 'suspended') {
        console.log('Resuming suspended audio context...');
        await this.audioContext.resume();
        console.log('Audio context resumed, new state:', this.audioContext.state);
      }
      
      // Wait a bit for context to be ready
      if (this.audioContext.state !== 'running') {
        console.log('Waiting for audio context to start...');
        await new Promise(resolve => {
          const checkState = () => {
            if (this.audioContext.state === 'running') {
              resolve();
            } else {
              setTimeout(checkState, 10);
            }
          };
          checkState();
        });
      }
      
      console.log('Audio context is running');
      
      // Create master gain node
      this.masterGain = this.audioContext.createGain();
      this.masterGain.connect(this.audioContext.destination);
      this.masterGain.gain.value = 0.7;

      // Generate drum samples
      await this.generateDrumSamples();
      
      // Generate piano samples
      await this.generatePianoSamples();
      
      // Initialize track effects
      this.initializeEffects();
      
      this.isInitialized = true;
      console.log('Audio Engine initialized successfully');
      console.log('Available drum samples:', Object.keys(this.samples));
      console.log('Available piano notes:', Object.keys(this.pianoSamples));
      
      // Test audio immediately
      setTimeout(() => {
        console.log('Testing audio with kick sample...');
        this.playSample('kick', 0.5);
      }, 100);
      
      return true;
    } catch (error) {
      console.error('Failed to initialize audio engine:', error);
      return false;
    }
  }

  async generateDrumSamples() {
    const sampleRate = this.audioContext.sampleRate;
    
    // Generate kick drum - deep, punchy
    this.samples.kick = this.generateKickSample(sampleRate);
    
    // Generate snare drum - crisp, snappy
    this.samples.snare = this.generateSnareSample(sampleRate);
    
    // Generate hi-hat - bright, short
    this.samples.hihat = this.generateHiHatSample(sampleRate);
    
    // Generate open hi-hat - sustained, bright
    this.samples.openhat = this.generateOpenHatSample(sampleRate);
    
    // Generate crash cymbal - explosive, sustained
    this.samples.crash = this.generateCrashSample(sampleRate);
    
    // Generate ride cymbal - bell-like, sustained
    this.samples.ride = this.generateRideSample(sampleRate);
    
    // Generate clap - percussive, mid-range
    this.samples.perc1 = this.generateClapSample(sampleRate);
    
    // Generate shaker - high-frequency, rhythmic
    this.samples.perc2 = this.generateShakerSample(sampleRate);
  }

  async generatePianoSamples() {
    const sampleRate = this.audioContext.sampleRate;
    
    // Generate piano samples for each note
    Object.keys(this.noteFrequencies).forEach(note => {
      this.pianoSamples[note] = this.generatePianoSample(this.noteFrequencies[note], sampleRate);
    });
  }

  generateKickSample(sampleRate) {
    const length = Math.floor(sampleRate * 0.6); // 0.6 seconds
    const buffer = this.audioContext.createBuffer(1, length, sampleRate);
    const data = buffer.getChannelData(0);
    
    for (let i = 0; i < length; i++) {
      const t = i / sampleRate;
      const envelope = Math.exp(-t * 25);
      const frequency = 60 * Math.exp(-t * 40);
      const sine = Math.sin(2 * Math.PI * frequency * t);
      const click = Math.random() * 0.15 * Math.exp(-t * 80);
      const subBass = Math.sin(2 * Math.PI * 30 * t) * 0.3;
      data[i] = (sine * 0.7 + click + subBass) * envelope;
    }
    
    return buffer;
  }

  generateSnareSample(sampleRate) {
    const length = Math.floor(sampleRate * 0.25); // 0.25 seconds
    const buffer = this.audioContext.createBuffer(1, length, sampleRate);
    const data = buffer.getChannelData(0);
    
    for (let i = 0; i < length; i++) {
      const t = i / sampleRate;
      const envelope = Math.exp(-t * 35);
      const tone1 = Math.sin(2 * Math.PI * 200 * t) * 0.4;
      const tone2 = Math.sin(2 * Math.PI * 400 * t) * 0.2;
      const noise = (Math.random() * 2 - 1) * 0.6;
      const filtered = this.bandpassFilter(noise, 1000, 5000, i / length);
      data[i] = (tone1 + tone2 + filtered) * envelope;
    }
    
    return buffer;
  }

  generateHiHatSample(sampleRate) {
    const length = Math.floor(sampleRate * 0.08); // 0.08 seconds
    const buffer = this.audioContext.createBuffer(1, length, sampleRate);
    const data = buffer.getChannelData(0);
    
    for (let i = 0; i < length; i++) {
      const t = i / sampleRate;
      const envelope = Math.exp(-t * 100);
      const noise = (Math.random() * 2 - 1);
      const highpass = this.highpassFilter(noise, 8000, i / length);
      data[i] = highpass * envelope * 0.4;
    }
    
    return buffer;
  }

  generateOpenHatSample(sampleRate) {
    const length = Math.floor(sampleRate * 0.4); // 0.4 seconds
    const buffer = this.audioContext.createBuffer(1, length, sampleRate);
    const data = buffer.getChannelData(0);
    
    for (let i = 0; i < length; i++) {
      const t = i / sampleRate;
      const envelope = Math.exp(-t * 12);
      const noise = (Math.random() * 2 - 1);
      const highpass = this.highpassFilter(noise, 6000, i / length);
      const shimmer = Math.sin(2 * Math.PI * 12000 * t) * 0.1;
      data[i] = (highpass + shimmer) * envelope * 0.35;
    }
    
    return buffer;
  }

  generateCrashSample(sampleRate) {
    const length = Math.floor(sampleRate * 1.5); // 1.5 seconds
    const buffer = this.audioContext.createBuffer(1, length, sampleRate);
    const data = buffer.getChannelData(0);
    
    for (let i = 0; i < length; i++) {
      const t = i / sampleRate;
      const envelope = Math.exp(-t * 2.5);
      const noise = (Math.random() * 2 - 1);
      const shimmer1 = Math.sin(2 * Math.PI * 4000 * t) * 0.2;
      const shimmer2 = Math.sin(2 * Math.PI * 8000 * t) * 0.15;
      data[i] = (noise * 0.7 + shimmer1 + shimmer2) * envelope * 0.5;
    }
    
    return buffer;
  }

  generateRideSample(sampleRate) {
    const length = Math.floor(sampleRate * 1.0); // 1.0 seconds
    const buffer = this.audioContext.createBuffer(1, length, sampleRate);
    const data = buffer.getChannelData(0);
    
    for (let i = 0; i < length; i++) {
      const t = i / sampleRate;
      const envelope = Math.exp(-t * 4);
      const bell = Math.sin(2 * Math.PI * 2000 * t) * 0.4;
      const overtone = Math.sin(2 * Math.PI * 3000 * t) * 0.2;
      const noise = (Math.random() * 2 - 1) * 0.15;
      data[i] = (bell + overtone + noise) * envelope * 0.45;
    }
    
    return buffer;
  }

  generateClapSample(sampleRate) {
    const length = Math.floor(sampleRate * 0.18); // 0.18 seconds
    const buffer = this.audioContext.createBuffer(1, length, sampleRate);
    const data = buffer.getChannelData(0);
    
    for (let i = 0; i < length; i++) {
      const t = i / sampleRate;
      const envelope = Math.exp(-t * 45);
      const noise = (Math.random() * 2 - 1);
      const bandpass = this.bandpassFilter(noise, 800, 4000, i / length);
      // Add multiple clap hits
      const multiHit = Math.sin(t * 200) > 0.7 ? 1.5 : 1.0;
      data[i] = bandpass * envelope * multiHit * 0.6;
    }
    
    return buffer;
  }

  generateShakerSample(sampleRate) {
    const length = Math.floor(sampleRate * 0.12); // 0.12 seconds
    const buffer = this.audioContext.createBuffer(1, length, sampleRate);
    const data = buffer.getChannelData(0);
    
    for (let i = 0; i < length; i++) {
      const t = i / sampleRate;
      const envelope = Math.exp(-t * 70);
      const noise = (Math.random() * 2 - 1);
      const highpass = this.highpassFilter(noise, 12000, i / length);
      data[i] = highpass * envelope * 0.25;
    }
    
    return buffer;
  }

  generatePianoSample(frequency, sampleRate) {
    const length = Math.floor(sampleRate * 2.0); // 2 seconds
    const buffer = this.audioContext.createBuffer(1, length, sampleRate);
    const data = buffer.getChannelData(0);
    
    for (let i = 0; i < length; i++) {
      const t = i / sampleRate;
      const envelope = Math.exp(-t * 1.5); // Piano decay
      
      // Fundamental frequency
      const fundamental = Math.sin(2 * Math.PI * frequency * t);
      
      // Harmonics for realistic piano sound
      const harmonic2 = Math.sin(2 * Math.PI * frequency * 2 * t) * 0.5;
      const harmonic3 = Math.sin(2 * Math.PI * frequency * 3 * t) * 0.25;
      const harmonic4 = Math.sin(2 * Math.PI * frequency * 4 * t) * 0.125;
      
      // Attack transient
      const attack = t < 0.01 ? Math.sin(t * 1000) * 0.1 : 0;
      
      data[i] = (fundamental + harmonic2 + harmonic3 + harmonic4 + attack) * envelope * 0.3;
    }
    
    return buffer;
  }

  // Simple filter implementations
  highpassFilter(input, cutoff, progress) {
    const normalized = cutoff / 22050; // Normalize to Nyquist
    return input * (1 - Math.exp(-normalized * 10));
  }

  bandpassFilter(input, lowCutoff, highCutoff, progress) {
    const low = lowCutoff / 22050;
    const high = highCutoff / 22050;
    const bandWidth = high - low;
    return input * Math.sin(progress * Math.PI) * bandWidth;
  }

  initializeEffects() {
    // Initialize reverb
    this.effects.reverb = this.createReverb();
    
    // Initialize delay
    this.effects.delay = this.createDelay();
    
    // Initialize filter
    this.effects.filter = this.createFilter();
  }

  createReverb() {
    const convolver = this.audioContext.createConvolver();
    const length = this.audioContext.sampleRate * 2; // 2 seconds
    const impulse = this.audioContext.createBuffer(2, length, this.audioContext.sampleRate);
    
    for (let channel = 0; channel < 2; channel++) {
      const channelData = impulse.getChannelData(channel);
      for (let i = 0; i < length; i++) {
        const decay = Math.pow(1 - i / length, 2);
        channelData[i] = (Math.random() * 2 - 1) * decay * 0.5;
      }
    }
    
    convolver.buffer = impulse;
    return convolver;
  }

  createDelay() {
    const delay = this.audioContext.createDelay(1.0);
    delay.delayTime.value = 0.25; // 250ms delay
    return delay;
  }

  createFilter() {
    const filter = this.audioContext.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = 2000;
    filter.Q.value = 1;
    return filter;
  }

  async playSample(sampleName, volume = 1.0, time = null) {
    if (!this.isInitialized) {
      console.log('Audio engine not initialized, initializing now...');
      await this.init();
    }

    if (!this.samples[sampleName]) {
      console.warn(`Sample ${sampleName} not found`);
      return;
    }

    if (this.audioContext.state === 'suspended') {
      console.log('Audio context suspended, resuming...');
      await this.audioContext.resume();
    }

    try {
      const source = this.audioContext.createBufferSource();
      const gainNode = this.audioContext.createGain();
      
      source.buffer = this.samples[sampleName];
      gainNode.gain.value = volume;
      
      source.connect(gainNode);
      gainNode.connect(this.masterGain);
      
      const playTime = time || this.audioContext.currentTime;
      source.start(playTime);
      
      console.log(`Playing sample: ${sampleName} at volume: ${volume}`);
      
      return source;
    } catch (error) {
      console.error(`Error playing sample ${sampleName}:`, error);
      return null;
    }
  }

  async playPianoNote(note, volume = 0.7, duration = null) {
    if (!this.isInitialized) {
      await this.init();
    }

    if (!this.pianoSamples[note]) {
      console.warn(`Piano note ${note} not found`);
      return;
    }

    const source = this.audioContext.createBufferSource();
    const gainNode = this.audioContext.createGain();
    
    source.buffer = this.pianoSamples[note];
    gainNode.gain.value = volume;
    
    source.connect(gainNode);
    gainNode.connect(this.masterGain);
    
    const startTime = this.audioContext.currentTime;
    source.start(startTime);
    
    // Store active note for potential stopping
    this.activePianoNotes.set(note, { source, gainNode, startTime });
    
    // Auto-stop after duration if specified
    if (duration) {
      setTimeout(() => {
        this.stopPianoNote(note);
      }, duration * 1000);
    }
    
    return source;
  }

  stopPianoNote(note) {
    if (this.activePianoNotes.has(note)) {
      const { source, gainNode } = this.activePianoNotes.get(note);
      
      // Fade out to prevent clicks
      gainNode.gain.exponentialRampToValueAtTime(0.001, this.audioContext.currentTime + 0.1);
      
      setTimeout(() => {
        try {
          source.stop();
        } catch (e) {
          // Note might already be stopped
        }
        this.activePianoNotes.delete(note);
      }, 100);
    }
  }

  start(patterns, bpm = 120) {
    if (!this.isInitialized) {
      console.warn('Audio engine not initialized');
      return;
    }

    this.bpm = bpm;
    this.isPlaying = true;
    this.currentStep = 0;
    
    const stepTime = (60 / bpm) / 4; // 16th notes
    
    const playStep = () => {
      if (!this.isPlaying) return;
      
      // Play samples for current step
      Object.keys(patterns).forEach(track => {
        if (patterns[track][this.currentStep]) {
          this.playSample(track, 0.8);
        }
      });
      
      this.currentStep = (this.currentStep + 1) % 32;
      
      this.stepInterval = setTimeout(playStep, stepTime * 1000);
    };
    
    playStep();
  }

  stop() {
    this.isPlaying = false;
    this.currentStep = 0;
    if (this.stepInterval) {
      clearTimeout(this.stepInterval);
      this.stepInterval = null;
    }
    
    // Stop all active piano notes
    this.activePianoNotes.forEach((_, note) => {
      this.stopPianoNote(note);
    });
  }

  setMasterVolume(volume) {
    if (this.masterGain) {
      this.masterGain.gain.value = Math.max(0, Math.min(1, volume));
    }
  }

  // Load custom audio sample from file
  async loadCustomSample(file, sampleName) {
    if (!this.isInitialized) {
      await this.init();
    }

    try {
      console.log(`Loading custom sample: ${sampleName} from file: ${file.name}`);
      
      // Read file as array buffer
      const arrayBuffer = await file.arrayBuffer();
      
      // Decode audio data
      const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
      
      // Store the custom sample
      this.samples[sampleName] = audioBuffer;
      
      console.log(`Custom sample loaded successfully: ${sampleName}`);
      console.log(`Duration: ${audioBuffer.duration.toFixed(2)}s, Channels: ${audioBuffer.numberOfChannels}, Sample Rate: ${audioBuffer.sampleRate}Hz`);
      
      return true;
    } catch (error) {
      console.error(`Failed to load custom sample ${sampleName}:`, error);
      return false;
    }
  }

  // Get list of all available samples (generated + custom)
  getAvailableSamples() {
    return Object.keys(this.samples);
  }

  // Remove a custom sample
  removeCustomSample(sampleName) {
    if (this.samples[sampleName]) {
      delete this.samples[sampleName];
      console.log(`Removed custom sample: ${sampleName}`);
      return true;
    }
    return false;
  }

  // Check if a sample is custom (not generated)
  isCustomSample(sampleName) {
    const generatedSamples = ['kick', 'snare', 'hihat', 'openhat', 'crash', 'ride', 'perc1', 'perc2'];
    return !generatedSamples.includes(sampleName) && this.samples[sampleName];
  }

  getCurrentStep() {
    return this.currentStep;
  }

  // Export pattern as audio file
  async exportAudio(patterns, bpm = 120, bars = 4) {
    if (!this.isInitialized) {
      await this.init();
    }

    const stepTime = (60 / bpm) / 4;
    const totalTime = stepTime * 32 * bars;
    const sampleRate = this.audioContext.sampleRate;
    const length = Math.floor(totalTime * sampleRate);
    
    const offlineContext = new OfflineAudioContext(2, length, sampleRate);
    const masterGain = offlineContext.createGain();
    masterGain.connect(offlineContext.destination);
    masterGain.gain.value = 0.7;

    // Schedule all samples
    for (let bar = 0; bar < bars; bar++) {
      for (let step = 0; step < 32; step++) {
        const time = (bar * 32 + step) * stepTime;
        
        Object.keys(patterns).forEach(track => {
          if (patterns[track][step] && this.samples[track]) {
            const source = offlineContext.createBufferSource();
            source.buffer = this.samples[track];
            source.connect(masterGain);
            source.start(time);
          }
        });
      }
    }

    const renderedBuffer = await offlineContext.startRendering();
    return this.bufferToWav(renderedBuffer);
  }

  bufferToWav(buffer) {
    const length = buffer.length;
    const numberOfChannels = buffer.numberOfChannels;
    const sampleRate = buffer.sampleRate;
    const arrayBuffer = new ArrayBuffer(44 + length * numberOfChannels * 2);
    const view = new DataView(arrayBuffer);
    
    // WAV header
    const writeString = (offset, string) => {
      for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
      }
    };
    
    writeString(0, 'RIFF');
    view.setUint32(4, 36 + length * numberOfChannels * 2, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, numberOfChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * numberOfChannels * 2, true);
    view.setUint16(32, numberOfChannels * 2, true);
    view.setUint16(34, 16, true);
    writeString(36, 'data');
    view.setUint32(40, length * numberOfChannels * 2, true);
    
    // Convert float samples to 16-bit PCM
    let offset = 44;
    for (let i = 0; i < length; i++) {
      for (let channel = 0; channel < numberOfChannels; channel++) {
        const sample = Math.max(-1, Math.min(1, buffer.getChannelData(channel)[i]));
        view.setInt16(offset, sample * 0x7FFF, true);
        offset += 2;
      }
    }
    
    return new Blob([arrayBuffer], { type: 'audio/wav' });
  }

  // Test audio functionality
  async testAudio() {
    console.log('Testing audio engine...');
    
    // Test drum samples
    console.log('Testing drum samples...');
    await this.playSample('kick');
    await new Promise(resolve => setTimeout(resolve, 300));
    await this.playSample('snare');
    await new Promise(resolve => setTimeout(resolve, 300));
    await this.playSample('hihat');
    
    // Test piano
    console.log('Testing piano...');
    await new Promise(resolve => setTimeout(resolve, 500));
    await this.playPianoNote('C4');
    await new Promise(resolve => setTimeout(resolve, 300));
    await this.playPianoNote('E4');
    await new Promise(resolve => setTimeout(resolve, 300));
    await this.playPianoNote('G4');
    
    console.log('Audio test complete!');
  }
}

export default AudioEngine;

