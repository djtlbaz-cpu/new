import { useEffect, useState } from "react";
import { aiWorkflow } from "./ai/AIWorkflow";
import { localLearning } from "./ai/LocalLearning";
import "./App.css";
import { Badge } from "./components/ui/badge";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./components/ui/card";
import { Progress } from "./components/ui/progress";
import { Slider } from "./components/ui/slider";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";

const API_BASE_URL = "/api";
const PULSE_AGENT_NAME = "Pulse";

function App() {
  // Core state management
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [bpm, setBpm] = useState(128);
  const [masterVolume, setMasterVolume] = useState(75);
  const [currentTime, setCurrentTime] = useState("00:00");
  const [projectName, setProjectName] = useState("Untitled Project");

  // Advanced state for premium features
  const [cpuUsage, setCpuUsage] = useState(23);
  const [ramUsage, setRamUsage] = useState(45);
  const [activeView, setActiveView] = useState("timeline");
  const [selectedTrack, setSelectedTrack] = useState(0);
  const [zoomLevel, setZoomLevel] = useState(100);
  const [snapValue, setSnapValue] = useState("1/16");

  // Pattern sequencer state (16x8 grid = 128 steps)
  const [pattern, setPattern] = useState(() => {
    const initialPattern = {};
    const tracks = [
      "Kick",
      "Snare",
      "Hi-Hat",
      "Open Hat",
      "Crash",
      "Ride",
      "Clap",
      "Perc",
    ];
    tracks.forEach((track) => {
      initialPattern[track] = new Array(16).fill(false);
    });
    return initialPattern;
  });

  // Professional mixer state (8 channels)
  const [mixerChannels, setMixerChannels] = useState(() => {
    const tracks = [
      "Kick",
      "Snare",
      "Hi-Hat",
      "Open Hat",
      "Crash",
      "Ride",
      "Clap",
      "Perc",
    ];
    return tracks.map((name, index) => ({
      id: index,
      name,
      volume: 75,
      pan: 0,
      mute: false,
      solo: false,
      highEQ: 0,
      midEQ: 0,
      lowEQ: 0,
      compressor: 0,
      gate: 0,
      send1: 0,
      send2: 0,
      color: [
        "#FF6B6B",
        "#4ECDC4",
        "#45B7D1",
        "#96CEB4",
        "#FFEAA7",
        "#DDA0DD",
        "#98D8C8",
        "#F7DC6F",
      ][index],
    }));
  });

  // Premium instrument modules
  const [instruments, setInstruments] = useState([
    {
      id: 1,
      name: "Vintage Keys",
      type: "Synthesizer",
      params: {
        cutoff: 75,
        resonance: 25,
        attack: 30,
        decay: 60,
        sustain: 70,
        release: 40,
      },
    },
    {
      id: 2,
      name: "Analog Bass",
      type: "Synthesizer",
      params: {
        cutoff: 60,
        resonance: 40,
        attack: 10,
        decay: 50,
        sustain: 80,
        release: 30,
      },
    },
    {
      id: 3,
      name: "Studio Reverb",
      type: "Effect",
      params: {
        roomSize: 50,
        damping: 30,
        wetLevel: 25,
        preDelay: 20,
        diffusion: 70,
        modulation: 15,
      },
    },
    {
      id: 4,
      name: "Vintage Delay",
      type: "Effect",
      params: {
        time: 250,
        feedback: 35,
        wetLevel: 20,
        highCut: 80,
        lowCut: 10,
        modulation: 5,
      },
    },
  ]);

  // AI Assistant state
  const [aiMessages, setAiMessages] = useState([
    {
      type: "ai",
      text: `${PULSE_AGENT_NAME} online. Ready for browser-native composition with your local AI engine.`,
    },
    {
      type: "ai",
      text: "I will route your prompts to the secure backend, respect Phase 0 policies, and keep everything synced for offline work.",
    },
  ]);
  const [aiLoading, setAiLoading] = useState(false);

  // Timeline/Arrangement view state
  const [timelineData, setTimelineData] = useState([
    {
      id: 1,
      name: "Track 1 - Drums",
      clips: [
        { start: 0, length: 4, color: "#FF6B6B", name: "Drum Pattern 1" },
        { start: 8, length: 4, color: "#FF6B6B", name: "Drum Pattern 2" },
      ],
    },
    {
      id: 2,
      name: "Track 2 - Bass",
      clips: [{ start: 4, length: 8, color: "#4ECDC4", name: "Bass Line" }],
    },
    {
      id: 3,
      name: "Track 3 - Lead",
      clips: [
        { start: 2, length: 6, color: "#45B7D1", name: "Lead Melody" },
        { start: 10, length: 4, color: "#45B7D1", name: "Lead Solo" },
      ],
    },
    {
      id: 4,
      name: "Track 4 - Pads",
      clips: [{ start: 0, length: 16, color: "#96CEB4", name: "Ambient Pads" }],
    },
  ]);

  // Playback simulation
  useEffect(() => {
    let interval;
    if (isPlaying) {
      interval = setInterval(
        () => {
          setCurrentStep((prev) => (prev + 1) % 16);
          setCurrentTime((prev) => {
            const [minutes, seconds] = prev.split(":").map(Number);
            const totalSeconds = minutes * 60 + seconds + 1;
            const newMinutes = Math.floor(totalSeconds / 60);
            const newSeconds = totalSeconds % 60;
            return `${newMinutes.toString().padStart(2, "0")}:${newSeconds.toString().padStart(2, "0")}`;
          });
        },
        (60 / bpm / 4) * 1000,
      );
    }
    return () => clearInterval(interval);
  }, [isPlaying, bpm]);

  // System monitoring simulation
  useEffect(() => {
    const interval = setInterval(() => {
      setCpuUsage((prev) =>
        Math.max(10, Math.min(90, prev + (Math.random() - 0.5) * 10)),
      );
      setRamUsage((prev) =>
        Math.max(20, Math.min(80, prev + (Math.random() - 0.5) * 8)),
      );
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const toggleStep = (track, step) => {
    setPattern((prev) => ({
      ...prev,
      [track]: prev[track].map((active, index) =>
        index === step ? !active : active,
      ),
    }));
  };

  const updateMixerChannel = (channelId, param, value) => {
    setMixerChannels((prev) =>
      prev.map((channel) =>
        channel.id === channelId ? { ...channel, [param]: value } : channel,
      ),
    );
  };

  const updateInstrumentParam = (instrumentId, param, value) => {
    setInstruments((prev) =>
      prev.map((instrument) =>
        instrument.id === instrumentId
          ? { ...instrument, params: { ...instrument.params, [param]: value } }
          : instrument,
      ),
    );
  };

  // Pulse orchestrates backend calls through aiWorkflow (AIClient under the hood)
  const generateAIBeat = async (style) => {
    const userPrompt = `${PULSE_AGENT_NAME}, craft a ${style} groove.`;
    const userEntry = { type: "user", text: userPrompt };

    if (!localLearning.canGenerate()) {
      setAiMessages((prev) => [
        ...prev,
        userEntry,
        {
          type: "ai",
          text: `${PULSE_AGENT_NAME} reached the current Phase 0 generation limit. Please refresh credits or adjust your legal settings.`,
        },
      ]);
      return;
    }

    setAiLoading(true);
    setAiMessages((prev) => [...prev, userEntry]);

    try {
      const result = await aiWorkflow.generateBeat({
        style,
        bpm,
        user: localLearning.getUserContext(),
        timeline: timelineData,
        allowLearning: true,
      });

      if (result?.sequencerPattern) {
        setPattern(result.sequencerPattern);
      }

      if (result?.timeline) {
        setTimelineData(result.timeline);
      }

      const preferenceMetadata = {
        ...result?.metadata,
        patternId: result?.sections?.drums?.pattern_id,
        arrangementId: result?.arrangement?.metadata?.arrangement_id,
      };

      localLearning.recordGeneration({ style, metadata: preferenceMetadata });
      localLearning.recordPreference({
        style,
        accepted: true,
        metadata: preferenceMetadata,
      });

      const generatedSections = result?.metadata?.sectionsGenerated?.length
        ? result.metadata.sectionsGenerated.join(", ")
        : "fresh layers";

      setAiMessages((prev) => [
        ...prev,
        {
          type: "ai",
          text: `${PULSE_AGENT_NAME} deployed ${generatedSections} via ${result?.metadata?.workflow ?? "Pulse workflow"}.`,
        },
      ]);
    } catch (error) {
      console.error("Pulse AI workflow error:", error);
      setAiMessages((prev) => [
        ...prev,
        {
          type: "ai",
          text: `${PULSE_AGENT_NAME} could not reach the AI engine. Your previous pattern stays active.`,
        },
      ]);
    } finally {
      setAiLoading(false);
    }
  };

  const exportProject = async (format) => {
    try {
      const projectData = {
        name: projectName,
        bpm,
        pattern,
        mixerChannels,
        instruments,
        timeline: timelineData,
        timestamp: new Date().toISOString(),
      };

      const response = await fetch(`${API_BASE_URL}/export/${format}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(projectData),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${projectName}.${format}`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error("Export error:", error);
      // Fallback: create and download JSON
      const projectData = {
        name: projectName,
        bpm,
        pattern,
        mixerChannels,
        instruments,
        timeline: timelineData,
      };
      const blob = new Blob([JSON.stringify(projectData, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${projectName}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Premium Header Bar - Fixed */}
      <div className="sticky top-0 z-50 h-16 bg-gradient-to-r from-slate-800/95 to-slate-700/95 backdrop-blur-xl border-b border-slate-600/30 flex items-center justify-between px-6 shadow-2xl">
        <div className="flex items-center space-x-6">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            Beat Addicts
          </h1>
          <Badge
            variant="outline"
            className="bg-gradient-to-r from-yellow-400/20 to-orange-400/20 border-yellow-400/50 text-yellow-300"
          >
            $10K Enterprise Edition
          </Badge>
          <Badge
            variant="outline"
            className="bg-gradient-to-r from-blue-400/20 to-cyan-400/20 border-blue-400/50 text-blue-300"
          >
            Ultra Professional
          </Badge>
          <Badge
            variant="outline"
            className="bg-gradient-to-r from-green-400/20 to-emerald-400/20 border-green-400/50 text-green-300"
          >
            Enterprise Grade
          </Badge>
        </div>

        <div className="flex items-center space-x-6">
          <div className="text-sm text-slate-300">
            <span className="text-blue-400">BPM:</span> {bpm} |
            <span className="text-green-400 ml-2">Vol:</span> {masterVolume}% |
            <span className="text-purple-400 ml-2">Time:</span> {currentTime}
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
            <span className="text-xs text-slate-400">LIVE</span>
          </div>
        </div>
      </div>

      {/* Main Content Area - Scrollable */}
      <div className="flex flex-col lg:flex-row min-h-[calc(100vh-4rem)]">
        {/* Left Master Control Panel - Scrollable */}
        <div className="w-full lg:w-80 bg-gradient-to-b from-slate-800/50 to-slate-900/50 backdrop-blur-xl border-r border-slate-600/30 overflow-y-auto">
          <div className="p-6 space-y-6">
            {/* Transport Controls */}
            <Card className="bg-gradient-to-br from-slate-700/50 to-slate-800/50 backdrop-blur-xl border-slate-600/30">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg text-slate-200 flex items-center">
                  <span className="w-2 h-2 bg-blue-400 rounded-full mr-3"></span>
                  Master Control
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-center space-x-3">
                  <Button
                    onClick={() => setIsPlaying(!isPlaying)}
                    className={`w-16 h-16 rounded-full text-2xl transition-all duration-300 ${
                      isPlaying
                        ? "bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 shadow-lg shadow-red-500/25"
                        : "bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 shadow-lg shadow-green-500/25"
                    }`}
                  >
                    {isPlaying ? "⏸️" : "▶️"}
                  </Button>
                  <Button className="w-12 h-12 rounded-full bg-gradient-to-r from-slate-600 to-slate-700 hover:from-slate-700 hover:to-slate-800">
                    ⏹️
                  </Button>
                  <Button className="w-12 h-12 rounded-full bg-gradient-to-r from-slate-600 to-slate-700 hover:from-slate-700 hover:to-slate-800">
                    ⏺️
                  </Button>
                </div>

                <div className="space-y-3">
                  <div>
                    <label className="text-sm text-slate-400 mb-2 block">
                      Tempo (BPM)
                    </label>
                    <div className="flex items-center space-x-3">
                      <Button
                        onClick={() => setBpm(Math.max(60, bpm - 1))}
                        className="w-8 h-8 rounded-full bg-slate-700 hover:bg-slate-600 text-xs"
                      >
                        -
                      </Button>
                      <span className="text-2xl font-mono text-blue-400 min-w-[60px] text-center">
                        {bpm}
                      </span>
                      <Button
                        onClick={() => setBpm(Math.min(200, bpm + 1))}
                        className="w-8 h-8 rounded-full bg-slate-700 hover:bg-slate-600 text-xs"
                      >
                        +
                      </Button>
                    </div>
                  </div>

                  <div>
                    <label className="text-sm text-slate-400 mb-2 block">
                      Master Volume
                    </label>
                    <Slider
                      value={[masterVolume]}
                      onValueChange={(value) => setMasterVolume(value[0])}
                      max={100}
                      step={1}
                      className="w-full"
                    />
                    <div className="text-center text-sm text-slate-400 mt-1">
                      {masterVolume}%
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* System Monitoring */}
            <Card className="bg-gradient-to-br from-slate-700/50 to-slate-800/50 backdrop-blur-xl border-slate-600/30">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg text-slate-200 flex items-center">
                  <span className="w-2 h-2 bg-green-400 rounded-full mr-3"></span>
                  System Monitor
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm text-slate-400 mb-2">
                    <span>CPU Usage</span>
                    <span>{cpuUsage.toFixed(2)}%</span>
                  </div>
                  <Progress value={cpuUsage} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between text-sm text-slate-400 mb-2">
                    <span>RAM Usage</span>
                    <span>{ramUsage.toFixed(2)}%</span>
                  </div>
                  <Progress value={ramUsage} className="h-2" />
                </div>
                <div className="text-xs text-slate-500 space-y-1">
                  <div>Latency: 2.3ms</div>
                  <div>Sample Rate: 48kHz</div>
                  <div>Buffer: 256 samples</div>
                </div>
              </CardContent>
            </Card>

            {/* Track Mixer Preview */}
            <Card className="bg-gradient-to-br from-slate-700/50 to-slate-800/50 backdrop-blur-xl border-slate-600/30">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg text-slate-200 flex items-center">
                  <span className="w-2 h-2 bg-purple-400 rounded-full mr-3"></span>
                  Track Mixer
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-3">
                  {mixerChannels.slice(0, 4).map((channel) => (
                    <div key={channel.id} className="space-y-2">
                      <div className="text-xs text-slate-400 truncate">
                        {channel.name}
                      </div>
                      <div className="flex items-center space-x-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: channel.color }}
                        ></div>
                        <div className="text-xs text-slate-300">
                          {channel.volume}
                        </div>
                      </div>
                      <div className="w-full bg-slate-700 rounded-full h-1">
                        <div
                          className="h-1 rounded-full bg-gradient-to-r from-green-400 to-blue-400"
                          style={{ width: `${channel.volume}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Main Content Area - Scrollable */}
        <div className="flex-1 overflow-y-auto bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
          <div className="p-4">
            {/* Navigation Tabs */}
            <Tabs
              defaultValue="timeline"
              value={activeView}
              onValueChange={setActiveView}
              className="w-full"
            >
              <TabsList className="w-full mb-4">
                <TabsTrigger value="timeline">🎵 Timeline</TabsTrigger>
                <TabsTrigger value="sequencer">🎛️ Sequencer</TabsTrigger>
                <TabsTrigger value="piano">🎹 Piano Roll</TabsTrigger>
                <TabsTrigger value="mixer">🎚️ Professional Mixer</TabsTrigger>
              </TabsList>

              {/* Timeline View */}
              <TabsContent value="timeline" className="mt-6">
                <Card className="bg-gradient-to-br from-slate-700/30 to-slate-800/30 backdrop-blur-xl border-slate-600/30">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-xl text-slate-200 flex items-center">
                        <span className="w-2 h-2 bg-blue-400 rounded-full mr-3"></span>
                        Professional Timeline & Arrangement
                      </CardTitle>
                      <div className="flex items-center space-x-4">
                        <Badge variant="outline" className="text-slate-300">
                          Zoom: {zoomLevel}%
                        </Badge>
                        <Badge variant="outline" className="text-slate-300">
                          Snap: {snapValue}
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {/* Timeline Ruler */}
                    <div className="flex items-center mb-4 text-xs text-slate-400">
                      {Array.from({ length: 17 }, (_, i) => (
                        <div
                          key={i}
                          className="flex-1 text-center border-r border-slate-600/30 last:border-r-0 py-2"
                        >
                          {i}
                        </div>
                      ))}
                    </div>

                    {/* Timeline Tracks */}
                    <div className="space-y-3">
                      {timelineData.map((track) => (
                        <div key={track.id} className="flex items-center">
                          <div className="w-32 text-sm text-slate-300 pr-4">
                            {track.name}
                          </div>
                          <div className="flex-1 relative h-12 bg-slate-800/50 rounded border border-slate-600/30">
                            {track.clips.map((clip, clipIndex) => (
                              <div
                                key={clipIndex}
                                className="absolute top-1 bottom-1 rounded text-xs text-white flex items-center justify-center font-medium shadow-lg"
                                style={{
                                  left: `${(clip.start / 16) * 100}%`,
                                  width: `${(clip.length / 16) * 100}%`,
                                  backgroundColor: clip.color,
                                }}
                              >
                                {clip.name}
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Sequencer View - FL Studio Style */}
              <TabsContent value="sequencer" className="mt-4">
                <Card className="bg-gradient-to-br from-slate-800/95 to-slate-900/95">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-2xl font-bold bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent flex items-center">
                        🎛️ Channel Rack - Pattern Sequencer
                      </CardTitle>
                      <div className="flex items-center space-x-2">
                        <Badge className="bg-green-500/20 text-green-400 border-green-500/50">
                          Pattern 1
                        </Badge>
                        <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/50">
                          16 Steps
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="p-3">
                    {/* Step Numbers */}
                    <div className="flex items-center mb-2 pl-28">
                      <div className="flex space-x-1">
                        {Array.from({ length: 16 }, (_, i) => (
                          <div
                            key={i}
                            className={`w-10 h-6 flex items-center justify-center text-xs font-bold rounded-t ${
                              i % 4 === 0
                                ? "bg-slate-700/80 text-yellow-400"
                                : "bg-slate-800/50 text-slate-400"
                            }`}
                          >
                            {i + 1}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Sequencer Tracks */}
                    <div className="space-y-2">
                      {Object.entries(pattern).map(
                        ([track, steps], trackIndex) => {
                          const colors = [
                            {
                              bg: "from-red-500 to-red-600",
                              shadow: "shadow-red-500/50",
                              inactive: "bg-red-900/20 border-red-700/30",
                            },
                            {
                              bg: "from-orange-500 to-orange-600",
                              shadow: "shadow-orange-500/50",
                              inactive: "bg-orange-900/20 border-orange-700/30",
                            },
                            {
                              bg: "from-yellow-500 to-yellow-600",
                              shadow: "shadow-yellow-500/50",
                              inactive: "bg-yellow-900/20 border-yellow-700/30",
                            },
                            {
                              bg: "from-green-500 to-green-600",
                              shadow: "shadow-green-500/50",
                              inactive: "bg-green-900/20 border-green-700/30",
                            },
                            {
                              bg: "from-cyan-500 to-cyan-600",
                              shadow: "shadow-cyan-500/50",
                              inactive: "bg-cyan-900/20 border-cyan-700/30",
                            },
                            {
                              bg: "from-blue-500 to-blue-600",
                              shadow: "shadow-blue-500/50",
                              inactive: "bg-blue-900/20 border-blue-700/30",
                            },
                            {
                              bg: "from-purple-500 to-purple-600",
                              shadow: "shadow-purple-500/50",
                              inactive: "bg-purple-900/20 border-purple-700/30",
                            },
                            {
                              bg: "from-pink-500 to-pink-600",
                              shadow: "shadow-pink-500/50",
                              inactive: "bg-pink-900/20 border-pink-700/30",
                            },
                          ];
                          const color = colors[trackIndex % colors.length];

                          return (
                            <div
                              key={track}
                              className="flex items-center space-x-2 bg-slate-800/40 p-2 rounded-lg border border-slate-700/50"
                            >
                              {/* Track Label */}
                              <div className="w-24 flex items-center space-x-2">
                                <div
                                  className={`w-3 h-3 rounded-full bg-gradient-to-br ${color.bg}`}
                                ></div>
                                <span className="text-sm font-semibold text-slate-200 truncate">
                                  {track}
                                </span>
                              </div>

                              {/* Step Buttons */}
                              <div className="flex space-x-1">
                                {steps.map((active, stepIndex) => (
                                  <button
                                    key={stepIndex}
                                    onClick={() => toggleStep(track, stepIndex)}
                                    className={`w-10 h-10 rounded border-2 transition-all duration-150 ${
                                      active
                                        ? `bg-gradient-to-br ${color.bg} ${color.shadow} shadow-lg border-white/20 transform scale-105`
                                        : `${color.inactive} border-slate-700/50 hover:bg-slate-700/40 hover:border-slate-600`
                                    } ${
                                      stepIndex === currentStep && isPlaying
                                        ? "ring-4 ring-yellow-400/60 ring-offset-2 ring-offset-slate-900"
                                        : ""
                                    }`}
                                  >
                                    {active && (
                                      <div className="w-full h-full flex items-center justify-center text-white font-bold text-xs">
                                        ●
                                      </div>
                                    )}
                                  </button>
                                ))}
                              </div>
                            </div>
                          );
                        },
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Piano Roll View - FL Studio Style */}
              <TabsContent value="piano" className="mt-4">
                <Card className="bg-gradient-to-br from-slate-800/95 to-slate-900/95">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent flex items-center">
                        🎹 Piano Roll Editor
                      </CardTitle>
                      <div className="flex items-center space-x-2">
                        <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/50">
                          Snap: {snapValue}
                        </Badge>
                        <Badge className="bg-pink-500/20 text-pink-400 border-pink-500/50">
                          Velocity: 100
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="p-3">
                    <div className="flex border-2 border-slate-700/50 rounded-lg overflow-hidden">
                      {/* Piano Keys */}
                      <div className="w-20">
                        {[
                          "C5",
                          "B4",
                          "A#4",
                          "A4",
                          "G#4",
                          "G4",
                          "F#4",
                          "F4",
                          "E4",
                          "D#4",
                          "D4",
                          "C#4",
                          "C4",
                          "B3",
                          "A#3",
                          "A3",
                        ].map((note, index) => {
                          const isBlackKey = note.includes("#");
                          return (
                            <div
                              key={note}
                              className={`h-8 flex items-center justify-center text-xs font-bold border-b border-slate-700/30 cursor-pointer transition-all ${
                                isBlackKey
                                  ? "bg-gradient-to-r from-slate-900 to-slate-800 text-slate-400 hover:from-slate-800 hover:to-slate-700"
                                  : "bg-gradient-to-r from-slate-200 to-slate-300 text-slate-900 hover:from-slate-300 hover:to-slate-400"
                              }`}
                            >
                              {note}
                            </div>
                          );
                        })}
                      </div>

                      {/* Note Grid */}
                      <div className="flex-1 overflow-x-auto">
                        <div className="relative" style={{ width: "800px" }}>
                          {/* Grid Lines */}
                          <div className="grid grid-rows-16">
                            {Array.from({ length: 16 }, (_, rowIndex) => {
                              const isBlackKey =
                                ["A#4", "G#4", "F#4", "D#4", "C#4", "A#3"][
                                  rowIndex % 6
                                ] !== undefined;
                              return (
                                <div
                                  key={rowIndex}
                                  className={`h-8 border-b border-slate-700/30 relative ${
                                    isBlackKey
                                      ? "bg-slate-900/60"
                                      : "bg-slate-800/40"
                                  }`}
                                >
                                  {/* Vertical Beat Lines */}
                                  {Array.from({ length: 17 }, (_, colIndex) => (
                                    <div
                                      key={colIndex}
                                      className={`absolute top-0 bottom-0 ${
                                        colIndex % 4 === 0
                                          ? "border-l-2 border-slate-600/60"
                                          : "border-l border-slate-700/30"
                                      }`}
                                      style={{
                                        left: `${(colIndex / 16) * 100}%`,
                                      }}
                                    ></div>
                                  ))}

                                  {/* Example Notes */}
                                  {rowIndex === 2 && (
                                    <>
                                      <div
                                        className="absolute top-1 h-6 bg-gradient-to-r from-green-500 to-emerald-500 rounded shadow-lg border border-green-400/30"
                                        style={{ left: "12.5%", width: "12%" }}
                                      ></div>
                                      <div
                                        className="absolute top-1 h-6 bg-gradient-to-r from-green-500 to-emerald-500 rounded shadow-lg border border-green-400/30"
                                        style={{ left: "50%", width: "18%" }}
                                      ></div>
                                    </>
                                  )}
                                  {rowIndex === 5 && (
                                    <div
                                      className="absolute top-1 h-6 bg-gradient-to-r from-blue-500 to-cyan-500 rounded shadow-lg border border-blue-400/30"
                                      style={{ left: "25%", width: "15%" }}
                                    ></div>
                                  )}
                                  {rowIndex === 8 && (
                                    <>
                                      <div
                                        className="absolute top-1 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded shadow-lg border border-purple-400/30"
                                        style={{ left: "0%", width: "10%" }}
                                      ></div>
                                      <div
                                        className="absolute top-1 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded shadow-lg border border-purple-400/30"
                                        style={{ left: "37.5%", width: "12%" }}
                                      ></div>
                                      <div
                                        className="absolute top-1 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded shadow-lg border border-purple-400/30"
                                        style={{ left: "75%", width: "12%" }}
                                      ></div>
                                    </>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="mt-3 flex items-center justify-between text-xs text-slate-400 bg-slate-800/40 p-2 rounded">
                      <span>🎼 Click and drag to create notes</span>
                      <span>⌨️ Use keyboard shortcuts for quick editing</span>
                      <span>🎵 MIDI ready</span>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Professional Mixer View - FL Studio Style */}
              <TabsContent value="mixer" className="mt-4">
                <Card className="bg-gradient-to-br from-slate-800/95 to-slate-900/95">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-2xl font-bold bg-gradient-to-r from-orange-400 to-red-400 bg-clip-text text-transparent flex items-center">
                        🎚️ Mixer - 8 Channel Console
                      </CardTitle>
                      <div className="flex items-center space-x-2">
                        <Badge className="bg-orange-500/20 text-orange-400 border-orange-500/50">
                          Master
                        </Badge>
                        <Badge className="bg-red-500/20 text-red-400 border-red-500/50">
                          8 Channels
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="p-4">
                    <div className="flex space-x-3 overflow-x-auto pb-4">
                      {mixerChannels.map((channel) => (
                        <div
                          key={channel.id}
                          className="flex flex-col items-center space-y-3 bg-slate-800/60 p-3 rounded-xl border-2 border-slate-700/50 min-w-[100px] hover:border-slate-600 transition-all"
                        >
                          {/* Channel Meter & Fader */}
                          <div className="flex flex-col items-center space-y-2">
                            {/* VU Meter */}
                            <div className="w-12 h-40 bg-slate-900/80 rounded-lg border-2 border-slate-700/50 relative overflow-hidden">
                              {/* Meter Graduations */}
                              <div className="absolute inset-0 flex flex-col justify-between py-1">
                                {[0, -3, -6, -9, -12, -18, -24].map((db, i) => (
                                  <div
                                    key={db}
                                    className="h-px bg-slate-600/30 relative"
                                  >
                                    <span className="absolute right-full mr-1 text-[8px] text-slate-500">
                                      {db}
                                    </span>
                                  </div>
                                ))}
                              </div>

                              {/* Level Indicator */}
                              <div
                                className="absolute bottom-0 w-full transition-all duration-75"
                                style={{
                                  height: `${channel.volume}%`,
                                  background:
                                    "linear-gradient(to top, #10b981 0%, #10b981 70%, #fbbf24 70%, #fbbf24 85%, #ef4444 85%, #ef4444 100%)",
                                }}
                              ></div>

                              {/* Peak Indicator */}
                              {channel.volume > 90 && (
                                <div className="absolute top-0 left-0 right-0 h-2 bg-red-500 animate-pulse"></div>
                              )}
                            </div>

                            {/* Vertical Fader */}
                            <div className="relative h-40 w-8">
                              <input
                                type="range"
                                orient="vertical"
                                min="0"
                                max="100"
                                value={channel.volume}
                                onChange={(e) =>
                                  updateMixerChannel(
                                    channel.id,
                                    "volume",
                                    parseInt(e.target.value),
                                  )
                                }
                                className="vertical-slider absolute left-1/2 -translate-x-1/2"
                                style={{
                                  writingMode: "bt-lr",
                                  WebkitAppearance: "slider-vertical",
                                  height: "160px",
                                  width: "24px",
                                }}
                              />
                            </div>

                            <div className="text-xs font-mono text-slate-300 font-bold">
                              {channel.volume}
                            </div>
                          </div>

                          {/* Pan Knob */}
                          <div className="flex flex-col items-center space-y-1">
                            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-slate-700 to-slate-800 border-2 border-slate-600 relative shadow-lg">
                              <div
                                className="absolute top-1/2 left-1/2 w-8 h-8 -translate-x-1/2 -translate-y-1/2 rounded-full bg-gradient-to-br from-slate-600 to-slate-700 border border-slate-500"
                                style={{
                                  transform: `translate(-50%, -50%) rotate(${channel.pan * 1.35}deg)`,
                                }}
                              >
                                <div className="absolute top-1 left-1/2 w-1 h-2 bg-blue-400 rounded-full -translate-x-1/2"></div>
                              </div>
                            </div>
                            <span className="text-[10px] text-slate-400 font-semibold">
                              PAN
                            </span>
                          </div>

                          {/* Mute/Solo */}
                          <div className="flex space-x-1 w-full">
                            <button
                              onClick={() =>
                                updateMixerChannel(
                                  channel.id,
                                  "mute",
                                  !channel.mute,
                                )
                              }
                              className={`flex-1 h-7 text-xs font-bold rounded transition-all ${
                                channel.mute
                                  ? "bg-red-500 text-white shadow-lg shadow-red-500/30"
                                  : "bg-slate-700 text-slate-400 hover:bg-slate-600"
                              }`}
                            >
                              M
                            </button>
                            <button
                              onClick={() =>
                                updateMixerChannel(
                                  channel.id,
                                  "solo",
                                  !channel.solo,
                                )
                              }
                              className={`flex-1 h-7 text-xs font-bold rounded transition-all ${
                                channel.solo
                                  ? "bg-yellow-500 text-slate-900 shadow-lg shadow-yellow-500/30"
                                  : "bg-slate-700 text-slate-400 hover:bg-slate-600"
                              }`}
                            >
                              S
                            </button>
                          </div>

                          {/* Channel Info */}
                          <div className="flex flex-col items-center space-y-1 pt-2 border-t border-slate-700/50 w-full">
                            <div
                              className="w-3 h-3 rounded-full shadow-lg"
                              style={{ backgroundColor: channel.color }}
                            ></div>
                            <div className="text-xs font-semibold text-slate-300 text-center truncate w-full px-1">
                              {channel.name}
                            </div>
                            <div className="text-[10px] text-slate-500">
                              Ch {channel.id + 1}
                            </div>
                          </div>
                        </div>
                      ))}

                      {/* Master Channel */}
                      <div className="flex flex-col items-center space-y-3 bg-gradient-to-br from-orange-900/40 to-red-900/40 p-3 rounded-xl border-2 border-orange-700/50 min-w-[100px]">
                        <div className="w-12 h-40 bg-slate-900/80 rounded-lg border-2 border-orange-700/50 relative overflow-hidden">
                          <div
                            className="absolute bottom-0 w-full"
                            style={{
                              height: `${masterVolume}%`,
                              background:
                                "linear-gradient(to top, #f97316 0%, #fb923c 50%, #fbbf24 100%)",
                            }}
                          ></div>
                        </div>
                        <div className="text-xs font-mono text-orange-400 font-bold">
                          {masterVolume}
                        </div>
                        <div className="text-sm font-bold text-orange-400">
                          MASTER
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>

        {/* Right Premium Instrument Rack - Scrollable */}
        <div className="w-full lg:w-80 bg-gradient-to-b from-slate-800/50 to-slate-900/50 backdrop-blur-xl border-l border-slate-600/30 overflow-y-auto">
          <div className="p-6">
            <Card className="bg-gradient-to-br from-slate-700/50 to-slate-800/50 backdrop-blur-xl border-slate-600/30">
              <CardHeader>
                <CardTitle className="text-lg text-slate-200 flex items-center">
                  <span className="w-2 h-2 bg-cyan-400 rounded-full mr-3"></span>
                  Premium Instrument Rack
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {instruments.map((instrument) => (
                  <div key={instrument.id} className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-sm font-medium text-slate-200">
                          {instrument.name}
                        </div>
                        <div className="text-xs text-slate-400">
                          {instrument.type}
                        </div>
                      </div>
                      <div className="flex space-x-1">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-r from-cyan-400 to-blue-400 flex items-center justify-center">
                          <span className="text-xs">🎹</span>
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      {Object.entries(instrument.params).map(
                        ([param, value]) => (
                          <div key={param} className="space-y-1">
                            <div className="text-xs text-slate-400 capitalize">
                              {param.replace(/([A-Z])/g, " $1").toLowerCase()}
                            </div>
                            <div className="relative">
                              <div className="w-12 h-12 rounded-full bg-slate-700 border-2 border-slate-600 flex items-center justify-center mx-auto">
                                <div className="text-xs text-slate-300">
                                  {value}
                                </div>
                              </div>
                              <input
                                type="range"
                                min="0"
                                max="100"
                                value={value}
                                onChange={(e) =>
                                  updateInstrumentParam(
                                    instrument.id,
                                    param,
                                    parseInt(e.target.value),
                                  )
                                }
                                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                              />
                            </div>
                          </div>
                        ),
                      )}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* AI Assistant Panel - Fixed at Bottom */}
      <div className="bg-gradient-to-r from-slate-800/95 to-slate-700/95 backdrop-blur-xl border-t border-slate-600/30 p-6">
        <Card className="bg-gradient-to-br from-slate-700/50 to-slate-800/50 backdrop-blur-xl border-slate-600/30">
          <CardHeader>
            <CardTitle className="text-lg text-slate-200 flex items-center">
              <span className="w-2 h-2 bg-pink-400 rounded-full mr-3"></span>
              AI Studio Assistant
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* AI Chat */}
              <div className="lg:col-span-2 space-y-3">
                <div className="h-24 overflow-y-auto space-y-2 bg-slate-800/30 rounded p-3">
                  {aiMessages.map((message, index) => (
                    <div
                      key={index}
                      className={`text-sm ${
                        message.type === "ai"
                          ? "text-blue-300"
                          : "text-green-300"
                      }`}
                    >
                      <span className="font-medium">
                        {message.type === "ai"
                          ? `${PULSE_AGENT_NAME}:`
                          : "You:"}
                      </span>{" "}
                      {message.text}
                    </div>
                  ))}
                  {aiLoading && (
                    <div className="text-sm text-blue-300">
                      <span className="font-medium">{PULSE_AGENT_NAME}:</span>{" "}
                      <span className="animate-pulse">Generating...</span>
                    </div>
                  )}
                </div>

                <div className="space-y-3">
                  <div>
                    <div className="text-sm text-slate-400 mb-2">
                      AI Beat Generation
                    </div>
                    <div className="flex space-x-2">
                      {["Boom Bap", "Trap", "House", "Techno"].map((style) => (
                        <Button
                          key={style}
                          onClick={() => generateAIBeat(style)}
                          disabled={aiLoading}
                          className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-xs"
                        >
                          {style}
                        </Button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Export & Share */}
              <div className="space-y-3">
                <div className="text-sm text-slate-400">Export & Share</div>
                <div className="space-y-2">
                  <Button
                    onClick={() => exportProject("json")}
                    className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-sm"
                  >
                    JSON
                  </Button>
                  <Button
                    onClick={() => exportProject("midi")}
                    className="w-full bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-sm"
                  >
                    MIDI
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default App;
