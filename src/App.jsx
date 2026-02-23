import { useCallback, useEffect, useRef, useState } from "react";
import AudioEngine from "./audio/AudioEngine";
import { aiWorkflow } from "./ai/AIWorkflow";
import { aiClient } from "./ai/AIClient";
import { localLearning } from "./ai/LocalLearning";
import "./App.css";

const API_BASE_URL = "/api";
const PULSE = "Pulse";

/* ── Track palette (FL Studio / Ableton style colors) ── */
const TRACK_COLORS = [
  "#e84855", // Kick – red
  "#f4a261", // Snare – amber
  "#e9c46a", // Hi-Hat – gold
  "#2a9d8f", // Open Hat – teal
  "#264653", // Crash – dark teal
  "#457b9d", // Ride – steel blue
  "#7b2cbf", // Clap – purple
  "#c77dff", // Perc – lavender
];

function App() {
  /* ── State ── */
  const [isPlaying, setIsPlaying] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [bpm, setBpm] = useState(128);
  const [masterVolume, setMasterVolume] = useState(75);
  const [currentTime, setCurrentTime] = useState("00:00:000");
  const [projectName, setProjectName] = useState("Untitled Project");
  const [activeView, setActiveView] = useState("sequencer");
  const [cpuUsage, setCpuUsage] = useState(23);
  const [ramUsage, setRamUsage] = useState(45);
  const [snapValue] = useState("1/16");

  const TRACKS = ["Kick", "Snare", "Hi-Hat", "Open Hat", "Crash", "Ride", "Clap", "Perc"];

  const [pattern, setPattern] = useState(() => {
    const p = {};
    TRACKS.forEach((t) => { p[t] = new Array(16).fill(false); });
    return p;
  });

  const [mixerChannels, setMixerChannels] = useState(() =>
    TRACKS.map((name, i) => ({
      id: i, name, volume: 75, pan: 0, mute: false, solo: false, color: TRACK_COLORS[i],
    })),
  );

  const [instruments] = useState([
    { id: 1, name: "Vintage Keys", type: "Synth", params: { cutoff: 75, reso: 25, atk: 30, dec: 60, sus: 70, rel: 40 } },
    { id: 2, name: "Analog Bass", type: "Synth", params: { cutoff: 60, reso: 40, atk: 10, dec: 50, sus: 80, rel: 30 } },
    { id: 3, name: "Studio Reverb", type: "FX", params: { room: 50, damp: 30, wet: 25, pre: 20, diff: 70, mod: 15 } },
    { id: 4, name: "Tape Delay", type: "FX", params: { time: 65, fdbk: 35, wet: 20, hi: 80, lo: 10, mod: 5 } },
  ]);

  const [aiMessages, setAiMessages] = useState([
    { type: "ai", text: "Engine online. Ready for AI-powered composition." },
  ]);
  const [aiLoading, setAiLoading] = useState(false);
  const [lyricsTheme, setLyricsTheme] = useState("");
  const [lyricsGenre, setLyricsGenre] = useState("");
  const [lyricsOutput, setLyricsOutput] = useState("");
  const [lyricsLoading, setLyricsLoading] = useState(false);

  const [timelineData, setTimelineData] = useState([
    { id: 1, name: "Drums", clips: [{ start: 0, length: 4, color: "#e84855", name: "Pattern A" }, { start: 8, length: 4, color: "#e84855", name: "Pattern B" }] },
    { id: 2, name: "Bass", clips: [{ start: 4, length: 8, color: "#2a9d8f", name: "Bass Line" }] },
    { id: 3, name: "Lead", clips: [{ start: 2, length: 6, color: "#457b9d", name: "Melody" }, { start: 10, length: 4, color: "#457b9d", name: "Solo" }] },
    { id: 4, name: "Pads", clips: [{ start: 0, length: 16, color: "#7b2cbf", name: "Ambient" }] },
  ]);

  /* ── Audio engine ── */
  const audioEngineRef = useRef(null);
  const [audioReady, setAudioReady] = useState(false);

  const initAudio = useCallback(async () => {
    if (audioEngineRef.current?.isInitialized) { setAudioReady(true); return true; }
    if (!audioEngineRef.current) audioEngineRef.current = new AudioEngine();
    const ok = await audioEngineRef.current.init();
    setAudioReady(ok);
    return ok;
  }, []);

  /* ── Playback loop ── */
  useEffect(() => {
    let interval;
    if (isPlaying) {
      const stepMs = (60 / bpm / 4) * 1000;
      interval = setInterval(() => {
        setCurrentStep((prev) => {
          const next = (prev + 1) % 16;
          const engine = audioEngineRef.current;
          if (engine?.isInitialized) {
            const vols = {};
            mixerChannels.forEach((ch) => { vols[ch.name] = ch.mute ? 0 : ch.volume; });
            engine.playStep(pattern, next, vols);
          }
          return next;
        });
        setCurrentTime((prev) => {
          const [m, rest] = prev.split(":");
          const [s, ms] = rest.split(":");
          let totalMs = Number(m)*60000 + Number(s)*1000 + Number(ms || 0) + Math.round((60/bpm/4)*1000);
          const nm = Math.floor(totalMs/60000); totalMs -= nm*60000;
          const ns = Math.floor(totalMs/1000); totalMs -= ns*1000;
          return `${String(nm).padStart(2,"0")}:${String(ns).padStart(2,"0")}:${String(totalMs).padStart(3,"0")}`;
        });
      }, stepMs);
    }
    return () => clearInterval(interval);
  }, [isPlaying, bpm, pattern, mixerChannels]);

  useEffect(() => {
    const iv = setInterval(() => {
      setCpuUsage((p) => Math.max(8, Math.min(85, p + (Math.random() - 0.5) * 6)));
      setRamUsage((p) => Math.max(20, Math.min(75, p + (Math.random() - 0.5) * 4)));
    }, 2500);
    return () => clearInterval(iv);
  }, []);

  useEffect(() => {
    if (audioEngineRef.current?.isInitialized) audioEngineRef.current.setMasterVolume(masterVolume / 100);
  }, [masterVolume]);

  /* ── Handlers ── */
  const toggleStep = (track, step) => {
    setPattern((p) => ({ ...p, [track]: p[track].map((v, i) => (i === step ? !v : v)) }));
  };
  const updateMixer = (id, key, val) => {
    setMixerChannels((chs) => chs.map((c) => (c.id === id ? { ...c, [key]: val } : c)));
  };

  const handlePlay = async () => {
    if (!isPlaying) await initAudio();
    setIsPlaying(!isPlaying);
    if (isPlaying) setCurrentStep(0);
  };
  const handleStop = () => { setIsPlaying(false); setCurrentStep(0); setCurrentTime("00:00:000"); };

  /* ── AI generate ── */
  const generateAIBeat = async (style) => {
    if (!localLearning.canGenerate()) {
      setAiMessages((p) => [...p, { type: "ai", text: "Generation limit reached. Upgrade your plan for more." }]);
      return;
    }
    setAiLoading(true);
    setAiMessages((p) => [...p, { type: "user", text: `Generate ${style} pattern` }]);
    try {
      const result = await aiWorkflow.generateBeat({ style, bpm, user: localLearning.getUserContext(), timeline: timelineData, allowLearning: true });
      if (result?.sequencerPattern) setPattern(result.sequencerPattern);
      if (result?.timeline) setTimelineData(result.timeline);
      localLearning.recordGeneration({ style, metadata: result?.metadata });
      localLearning.recordPreference({ style, accepted: true, metadata: result?.metadata });
      const sections = result?.metadata?.sectionsGenerated?.length ? result.metadata.sectionsGenerated.join(", ") : "pattern";
      setAiMessages((p) => [...p, { type: "ai", text: `${PULSE} deployed ${sections} — ${style} groove loaded.` }]);
    } catch {
      setAiMessages((p) => [...p, { type: "ai", text: `${PULSE} couldn't reach the engine. Pattern unchanged.` }]);
    } finally {
      setAiLoading(false);
    }
  };

  const handleGenerateLyrics = async () => {
    if (!lyricsTheme.trim()) return;
    setLyricsLoading(true);
    setLyricsOutput("");
    try {
      const result = await aiClient.generateLyrics({
        theme: lyricsTheme,
        genre: lyricsGenre || undefined,
        user: localLearning.getUserContext(),
      });
      if (result?.lyrics) setLyricsOutput(result.lyrics);
    } catch {
      setLyricsOutput("Could not reach the lyrics engine. Please try again.");
    } finally {
      setLyricsLoading(false);
    }
  };

  const exportProject = async (format) => {
    const data = { name: projectName, bpm, pattern, mixerChannels, instruments, timeline: timelineData, timestamp: new Date().toISOString() };
    try {
      const r = await fetch(`${API_BASE_URL}/export/${format}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) });
      if (r.ok) { const b = await r.blob(); const u = URL.createObjectURL(b); const a = document.createElement("a"); a.href = u; a.download = `${projectName}.${format}`; a.click(); URL.revokeObjectURL(u); return; }
    } catch { /* fallback below */ }
    const b = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const u = URL.createObjectURL(b); const a = document.createElement("a"); a.href = u; a.download = `${projectName}.${format}`; a.click(); URL.revokeObjectURL(u);
  };

  /* ═══════════════════════════════════════════════════ */
  /*                     R E N D E R                     */
  /* ═══════════════════════════════════════════════════ */
  return (
    <div className="daw-shell">

      {/* ── Menu Bar ── */}
      <div className="daw-menubar">
        <span className="daw-menubar-brand">BEAT ADDICTS</span>
        {["File", "Edit", "View", "Options", "Tools", "Help"].map((m) => (
          <span key={m} className="daw-menubar-item">{m}</span>
        ))}
        <span style={{ flex: 1 }} />
        <span className="daw-menubar-item" style={{ color: "var(--daw-accent)", fontWeight: 700 }}>
          {projectName}
        </span>
      </div>

      {/* ── Toolbar / Transport ── */}
      <div className="daw-toolbar">
        {/* Transport buttons */}
        <div className="transport-group">
          <button className="t-btn" onClick={handleStop} title="Stop">⏹</button>
          <button className={`t-btn ${isPlaying ? "play-on" : ""}`} onClick={handlePlay} title={isPlaying ? "Pause" : "Play"}>
            {isPlaying ? "⏸" : "▶"}
          </button>
          <button className={`t-btn ${isRecording ? "rec-on" : ""}`} onClick={() => setIsRecording(!isRecording)} title="Record">⏺</button>
        </div>

        {/* Time display */}
        <div className="transport-group">
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
            <div className="led led-time">{currentTime}</div>
            <div className="led-label">Time</div>
          </div>
        </div>

        {/* BPM */}
        <div className="transport-group">
          <button className="t-btn" onClick={() => setBpm(Math.max(40, bpm - 1))}>−</button>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
            <div className="led led-bpm">{bpm}</div>
            <div className="led-label">BPM</div>
          </div>
          <button className="t-btn" onClick={() => setBpm(Math.min(300, bpm + 1))}>+</button>
        </div>

        {/* Master volume */}
        <div className="transport-group">
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 2 }}>
            <span className="led-label">Master</span>
            <input
              type="range" min={0} max={100} value={masterVolume}
              onChange={(e) => setMasterVolume(Number(e.target.value))}
              style={{ width: 80, accentColor: "var(--daw-accent)" }}
            />
          </div>
          <span style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 11, color: "var(--daw-text-dim)", width: 30, textAlign: "right" }}>
            {masterVolume}
          </span>
        </div>

        <div style={{ flex: 1 }} />

        {/* Step indicator */}
        <div className="transport-group" style={{ gap: 3 }}>
          {Array.from({ length: 16 }, (_, i) => (
            <div
              key={i}
              style={{
                width: 6, height: 6, borderRadius: 1,
                background: i === currentStep && isPlaying ? "var(--daw-green)" : i % 4 === 0 ? "var(--daw-surface-4)" : "var(--daw-surface-3)",
                transition: "background .05s",
              }}
            />
          ))}
        </div>

        {/* Audio ready indicator */}
        <div className="transport-group">
          <span style={{ width: 6, height: 6, borderRadius: "50%", background: audioReady ? "var(--daw-green)" : "var(--daw-red)" }} />
          <span style={{ fontSize: 9, color: "var(--daw-text-muted)", marginLeft: 3 }}>
            {audioReady ? "AUDIO" : "NO AUDIO"}
          </span>
        </div>
      </div>

      {/* ── Workspace ── */}
      <div className="daw-workspace">

        {/* ── Left sidebar ── */}
        <div className="daw-sidebar">
          {/* System Monitor */}
          <div className="sidebar-section">
            <div className="sidebar-heading">System</div>
            <div className="monitor-row">
              <span className="monitor-label">CPU</span>
              <div className="monitor-bar">
                <div className="monitor-bar-fill cpu" style={{ width: `${cpuUsage}%` }} />
              </div>
              <span className="monitor-val">{cpuUsage.toFixed(0)}%</span>
            </div>
            <div className="monitor-row">
              <span className="monitor-label">RAM</span>
              <div className="monitor-bar">
                <div className="monitor-bar-fill ram" style={{ width: `${ramUsage}%` }} />
              </div>
              <span className="monitor-val">{ramUsage.toFixed(0)}%</span>
            </div>
            <div style={{ marginTop: 6, display: "flex", flexDirection: "column", gap: 2 }}>
              <span className="monitor-stat">Latency  2.3ms</span>
              <span className="monitor-stat">Sample   48kHz</span>
              <span className="monitor-stat">Buffer   256</span>
            </div>
          </div>

          {/* Channel overview */}
          <div className="sidebar-section">
            <div className="sidebar-heading">Channels</div>
            {mixerChannels.map((ch) => (
              <div key={ch.id} className="ch-mini">
                <div className="ch-mini-dot" style={{ background: ch.color }} />
                <span className="ch-mini-name">{ch.name}</span>
                <div className="ch-mini-bar">
                  <div className="ch-mini-fill" style={{ width: `${ch.mute ? 0 : ch.volume}%`, background: ch.color }} />
                </div>
              </div>
            ))}
          </div>

          {/* Snap / Grid */}
          <div className="sidebar-section">
            <div className="sidebar-heading">Grid</div>
            <div style={{ display: "flex", gap: 6, fontSize: 10 }}>
              <span style={{ color: "var(--daw-text-dim)" }}>Snap</span>
              <span style={{ color: "var(--daw-accent)", fontWeight: 700, fontFamily: "'JetBrains Mono'" }}>{snapValue}</span>
            </div>
          </div>
        </div>

        {/* ── Center area ── */}
        <div className="daw-center">

          {/* Tab bar */}
          <div className="daw-tabbar">
            {[
              { key: "sequencer", label: "Channel Rack" },
              { key: "timeline", label: "Arrangement" },
              { key: "piano", label: "Piano Roll" },
              { key: "mixer", label: "Mixer" },
            ].map((tab) => (
              <button
                key={tab.key}
                className={`daw-tab ${activeView === tab.key ? "active" : ""}`}
                onClick={() => setActiveView(tab.key)}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* View content */}
          <div className="daw-view">

            {/* ── SEQUENCER ── */}
            {activeView === "sequencer" && (
              <div>
                <div className="seq-header">
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span className="seq-title">Channel Rack</span>
                    <span className="seq-badge">Pattern 1</span>
                    <span className="seq-badge">16 Steps</span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                    {["Boom Bap", "Trap", "House", "Techno"].map((s) => (
                      <button key={s} className="ai-seq-btn" disabled={aiLoading} onClick={() => generateAIBeat(s)}>
                        ✦ {s}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="seq-grid">
                  {/* Step numbers */}
                  <div className="seq-numbers">
                    {Array.from({ length: 16 }, (_, i) => (
                      <div key={i} className={`seq-num ${i % 4 === 0 ? "bar" : ""}`}>{i + 1}</div>
                    ))}
                  </div>

                  {/* Rows */}
                  {Object.entries(pattern).map(([track, steps], ti) => (
                    <div key={track} className="seq-row">
                      <div className="seq-info">
                        <div className="seq-dot" style={{ background: TRACK_COLORS[ti] }} />
                        <span className="seq-name">{track}</span>
                        <div className="seq-ms">
                          <button
                            className={`seq-ms-btn ${mixerChannels[ti]?.mute ? "m-on" : ""}`}
                            onClick={() => updateMixer(ti, "mute", !mixerChannels[ti]?.mute)}
                          >M</button>
                          <button
                            className={`seq-ms-btn ${mixerChannels[ti]?.solo ? "s-on" : ""}`}
                            onClick={() => updateMixer(ti, "solo", !mixerChannels[ti]?.solo)}
                          >S</button>
                        </div>
                      </div>
                      <div className="seq-steps">
                        {steps.map((on, si) => (
                          <div
                            key={si}
                            className={`seq-step${si % 4 === 0 ? " beat" : ""}${on ? " on" : ""}${si === currentStep && isPlaying ? " playing" : ""}`}
                            style={{ "--scolor": TRACK_COLORS[ti], "--glow": `${TRACK_COLORS[ti]}66` }}
                            onClick={() => toggleStep(track, si)}
                          />
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ── TIMELINE ── */}
            {activeView === "timeline" && (
              <div>
                <div className="seq-header">
                  <span className="seq-title">Arrangement</span>
                  <div style={{ display: "flex", gap: 6 }}>
                    <span className="seq-badge">Snap {snapValue}</span>
                  </div>
                </div>
                <div className="tl-ruler">
                  {Array.from({ length: 17 }, (_, i) => (
                    <div key={i} className="tl-mark">{i}</div>
                  ))}
                </div>
                {timelineData.map((tr) => (
                  <div key={tr.id} className="tl-track">
                    <div className="tl-label">
                      <div style={{ width: 6, height: 6, borderRadius: 2, background: tr.clips[0]?.color }} />
                      {tr.name}
                    </div>
                    <div className="tl-lane">
                      {tr.clips.map((clip, ci) => (
                        <div
                          key={ci}
                          className="tl-clip"
                          style={{
                            left: `${(clip.start / 16) * 100}%`,
                            width: `${(clip.length / 16) * 100}%`,
                            background: clip.color,
                          }}
                        >
                          <span>{clip.name}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* ── PIANO ROLL ── */}
            {activeView === "piano" && (
              <div>
                <div className="seq-header">
                  <span className="seq-title">Piano Roll</span>
                  <div style={{ display: "flex", gap: 6 }}>
                    <span className="seq-badge">Snap {snapValue}</span>
                    <span className="seq-badge">Vel 100</span>
                  </div>
                </div>
                <div className="pr-wrap">
                  <div className="pr-keys">
                    {["C5","B4","A#4","A4","G#4","G4","F#4","F4","E4","D#4","D4","C#4","C4","B3","A#3","A3","G#3","G3"].map((n) => (
                      <div key={n} className={`pr-key ${n.includes("#") ? "bk" : "wk"}`}>{n}</div>
                    ))}
                  </div>
                  <div className="pr-grid" style={{ width: 900 }}>
                    {["C5","B4","A#4","A4","G#4","G4","F#4","F4","E4","D#4","D4","C#4","C4","B3","A#3","A3","G#3","G3"].map((n, ri) => (
                      <div key={n} className={`pr-row ${n.includes("#") ? "bk-r" : "wk-r"}`}>
                        {/* Beat lines */}
                        {Array.from({ length: 17 }, (_, ci) => (
                          <div key={ci} className={`pr-beat ${ci % 4 === 0 ? "maj" : "min"}`} style={{ left: `${(ci / 16) * 100}%` }} />
                        ))}
                        {/* Demo notes */}
                        {ri === 2 && <div className="pr-note" style={{ left: "12%", width: "12%", background: "#22c55e" }} />}
                        {ri === 2 && <div className="pr-note" style={{ left: "50%", width: "18%", background: "#22c55e" }} />}
                        {ri === 5 && <div className="pr-note" style={{ left: "25%", width: "15%", background: "#5b8def" }} />}
                        {ri === 8 && <div className="pr-note" style={{ left: "0%", width: "10%", background: "#7c5cfc" }} />}
                        {ri === 8 && <div className="pr-note" style={{ left: "37%", width: "12%", background: "#7c5cfc" }} />}
                        {ri === 8 && <div className="pr-note" style={{ left: "75%", width: "12%", background: "#7c5cfc" }} />}
                        {ri === 12 && <div className="pr-note" style={{ left: "6%", width: "20%", background: "#e84855" }} />}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* ── MIXER ── */}
            {activeView === "mixer" && (
              <div>
                <div className="seq-header">
                  <span className="seq-title">Mixer Console</span>
                  <div style={{ display: "flex", gap: 6 }}>
                    <span className="seq-badge">{mixerChannels.length} Channels</span>
                    <span className="seq-badge">Master</span>
                  </div>
                </div>
                <div className="mixer-wrap">
                  {mixerChannels.map((ch) => (
                    <div key={ch.id} className="mx-strip">
                      <div className="mx-label">{ch.name}</div>

                      {/* VU */}
                      <div className="vu">
                        <div className="vu-fill" style={{ height: `${ch.mute ? 0 : ch.volume}%` }} />
                        {ch.volume > 90 && <div className="vu-peak" />}
                      </div>

                      {/* Fader */}
                      <div className="fader-box" onClick={(e) => {
                        const rect = e.currentTarget.getBoundingClientRect();
                        const pct = Math.round(100 - ((e.clientY - rect.top) / rect.height) * 100);
                        updateMixer(ch.id, "volume", Math.max(0, Math.min(100, pct)));
                      }}>
                        <div className="fader-fill" style={{ height: `${ch.volume}%` }} />
                        <div className="fader-thumb" style={{ bottom: `calc(${ch.volume}% - 4px)` }} />
                      </div>

                      <div className="fader-val">{ch.volume}</div>

                      {/* Pan knob */}
                      <div className="mx-knob" title={`Pan: ${ch.pan}`}>
                        <div className="mx-knob-ind" style={{ transform: `translateX(-50%) rotate(${ch.pan * 1.35}deg)` }} />
                      </div>

                      {/* M/S */}
                      <div className="ms-row">
                        <button className={`ms-btn ${ch.mute ? "m-on" : ""}`} onClick={() => updateMixer(ch.id, "mute", !ch.mute)}>M</button>
                        <button className={`ms-btn ${ch.solo ? "s-on" : ""}`} onClick={() => updateMixer(ch.id, "solo", !ch.solo)}>S</button>
                      </div>

                      {/* Footer */}
                      <div className="mx-color" style={{ background: ch.color }} />
                      <div className="mx-ch-name">Ch {ch.id + 1}</div>
                    </div>
                  ))}

                  {/* Master strip */}
                  <div className="mx-strip master">
                    <div className="mx-label">MASTER</div>
                    <div className="vu">
                      <div className="vu-fill" style={{ height: `${masterVolume}%`, background: "linear-gradient(to top, var(--daw-accent) 0%, #c77dff 60%, #ef4444 90%)" }} />
                    </div>
                    <div className="fader-box" onClick={(e) => {
                      const rect = e.currentTarget.getBoundingClientRect();
                      setMasterVolume(Math.max(0, Math.min(100, Math.round(100 - ((e.clientY - rect.top) / rect.height) * 100))));
                    }}>
                      <div className="fader-fill" style={{ height: `${masterVolume}%`, background: "linear-gradient(180deg, var(--daw-accent), rgba(124,92,252,.2))" }} />
                      <div className="fader-thumb" style={{ bottom: `calc(${masterVolume}% - 4px)` }} />
                    </div>
                    <div className="fader-val" style={{ color: "var(--daw-accent)" }}>{masterVolume}</div>
                    <div className="mx-color" style={{ background: "var(--daw-accent)" }} />
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* ── Right panel — Instrument Rack ── */}
        <div className="daw-rpanel">
          {instruments.map((inst) => (
            <div key={inst.id} className="rack-mod">
              <div className="rack-hdr">
                <span className="rack-title">{inst.name}</span>
                <span className="rack-type">{inst.type}</span>
              </div>
              <div className="rack-knobs">
                {Object.entries(inst.params).map(([k, v]) => (
                  <div key={k} className="rack-knob-wrap">
                    <div className="rack-knob">
                      <span className="rack-knob-val">{v}</span>
                      <input type="range" min={0} max={100} defaultValue={v} />
                    </div>
                    <span className="rack-knob-label">{k}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Bottom AI Panel ── */}
      <div className="daw-bottom">
        <div className="bottom-hdr">
          <div className="bottom-title">
            <span className="ai-dot" />
            {PULSE} AI Engine
          </div>
          <div style={{ display: "flex", gap: 6 }}>
            <button className="exp-btn" onClick={() => exportProject("json")}>↓ JSON</button>
            <button className="exp-btn" onClick={() => exportProject("midi")}>↓ MIDI</button>
          </div>
        </div>
        <div className="bottom-body">
          {/* Log */}
          <div className="ai-log">
            {aiMessages.map((m, i) => (
              <div key={i} className={`ai-msg ${m.type === "ai" ? "ai" : "usr"}`}>
                <span className="s">{m.type === "ai" ? `${PULSE}:` : "You:"}</span>
                {m.text}
              </div>
            ))}
            {aiLoading && (
              <div className="ai-msg ai">
                <span className="s">{PULSE}:</span>
                <span style={{ opacity: 0.6 }}>Generating…</span>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="ai-sidebar">
            <div style={{ fontSize: 9, fontWeight: 700, color: "var(--daw-text-muted)", textTransform: "uppercase", letterSpacing: 1, marginBottom: 2 }}>
              AI Generation
            </div>
            <div className="ai-genre-row">
              {["Boom Bap", "Trap"].map((s) => (
                <button key={s} className="ai-btn" disabled={aiLoading} onClick={() => generateAIBeat(s)}>✦ {s}</button>
              ))}
            </div>
            <div className="ai-genre-row">
              {["House", "Techno"].map((s) => (
                <button key={s} className="ai-btn" disabled={aiLoading} onClick={() => generateAIBeat(s)}>✦ {s}</button>
              ))}
            </div>
            <div className="ai-genre-row">
              {["Lo-Fi", "Drill"].map((s) => (
                <button key={s} className="ai-btn" disabled={aiLoading} onClick={() => generateAIBeat(s)}>✦ {s}</button>
              ))}
            </div>

            {/* ── Lyrics generator ── */}
            <div style={{ borderTop: "1px solid var(--daw-surface-4)", marginTop: 8, paddingTop: 8 }}>
              <div style={{ fontSize: 9, fontWeight: 700, color: "var(--daw-text-muted)", textTransform: "uppercase", letterSpacing: 1, marginBottom: 4 }}>
                AI Lyrics
              </div>
              <input
                type="text"
                placeholder="Theme (e.g. dreams and freedom)"
                value={lyricsTheme}
                onChange={(e) => setLyricsTheme(e.target.value)}
                style={{
                  width: "100%", background: "var(--daw-surface-3)", border: "1px solid var(--daw-surface-4)",
                  color: "var(--daw-text)", padding: "3px 6px", fontSize: 10, borderRadius: 3, boxSizing: "border-box", marginBottom: 4,
                }}
              />
              <input
                type="text"
                placeholder="Genre (optional)"
                value={lyricsGenre}
                onChange={(e) => setLyricsGenre(e.target.value)}
                style={{
                  width: "100%", background: "var(--daw-surface-3)", border: "1px solid var(--daw-surface-4)",
                  color: "var(--daw-text)", padding: "3px 6px", fontSize: 10, borderRadius: 3, boxSizing: "border-box", marginBottom: 4,
                }}
              />
              <button
                className="ai-btn"
                disabled={lyricsLoading || !lyricsTheme.trim()}
                onClick={handleGenerateLyrics}
                style={{ width: "100%" }}
              >
                {lyricsLoading ? "Generating…" : "✦ Generate Lyrics"}
              </button>
            </div>
          </div>
        </div>

        {/* ── Lyrics output ── */}
        {lyricsOutput && (
          <div style={{
            borderTop: "1px solid var(--daw-surface-4)", padding: "8px 12px",
            fontFamily: "'JetBrains Mono', monospace", fontSize: 10, color: "var(--daw-text-dim)",
            whiteSpace: "pre-wrap", maxHeight: 140, overflowY: "auto", background: "var(--daw-surface-2)",
          }}>
            {lyricsOutput}
          </div>
        )}
      </div>

      {/* ── Status bar ── */}
      <div className="daw-status">
        <div>
          <span className="st-dot ok" />
          Engine: WebAudio 48kHz &nbsp;|&nbsp; Backend: Railway &nbsp;|&nbsp; Snap: {snapValue}
        </div>
        <div>
          Beat Addicts v1.0 — AI-Powered DAW
        </div>
      </div>
    </div>
  );
}

export default App;
