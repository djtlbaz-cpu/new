from flask import Blueprint, request, jsonify
import json
import tempfile
import time
from datetime import datetime

audio_processing_bp = Blueprint('audio_processing', __name__)

# Audio effects presets
EFFECTS_PRESETS = {
    'reverb': {
        'hall': {'room_size': 0.8, 'damping': 0.5, 'wet_level': 0.3, 'dry_level': 0.7},
        'room': {'room_size': 0.5, 'damping': 0.3, 'wet_level': 0.2, 'dry_level': 0.8},
        'plate': {'room_size': 0.6, 'damping': 0.7, 'wet_level': 0.4, 'dry_level': 0.6}
    },
    'delay': {
        'short': {'delay_time': 0.125, 'feedback': 0.3, 'wet_level': 0.2},
        'medium': {'delay_time': 0.25, 'feedback': 0.4, 'wet_level': 0.3},
        'long': {'delay_time': 0.5, 'feedback': 0.5, 'wet_level': 0.4}
    },
    'distortion': {
        'light': {'drive': 0.3, 'tone': 0.5, 'level': 0.8},
        'medium': {'drive': 0.6, 'tone': 0.6, 'level': 0.7},
        'heavy': {'drive': 0.9, 'tone': 0.7, 'level': 0.6}
    },
    'filter': {
        'lowpass': {'cutoff': 1000, 'resonance': 0.3, 'type': 'lowpass'},
        'highpass': {'cutoff': 200, 'resonance': 0.3, 'type': 'highpass'},
        'bandpass': {'cutoff': 500, 'resonance': 0.5, 'type': 'bandpass'}
    }
}

# Mixer channel settings
DEFAULT_CHANNEL_SETTINGS = {
    'volume': 0.75,
    'pan': 0.0,
    'mute': False,
    'solo': False,
    'eq': {
        'high': 0.0,
        'mid': 0.0,
        'low': 0.0
    },
    'effects': []
}

@audio_processing_bp.route('/get-effects-presets', methods=['GET'])
def get_effects_presets():
    """Get available audio effects presets"""
    return jsonify({
        'success': True,
        'presets': EFFECTS_PRESETS,
        'message': 'Effects presets loaded'
    })

@audio_processing_bp.route('/apply-effect', methods=['POST'])
def apply_effect():
    """Apply an audio effect to a track"""
    try:
        data = request.get_json() or {}
        track_id = data.get('track_id')
        effect_type = data.get('effect_type')
        preset = data.get('preset', 'medium')
        custom_params = data.get('params', {})

        if not track_id or not effect_type:
            return jsonify({
                'success': False,
                'error': 'Missing track_id or effect_type'
            }), 400

        # Get effect parameters
        if effect_type in EFFECTS_PRESETS and preset in EFFECTS_PRESETS[effect_type]:
            effect_params = EFFECTS_PRESETS[effect_type][preset].copy()
            effect_params.update(custom_params)
        else:
            effect_params = custom_params

        # Simulate effect processing
        processing_time = 0.5  # Simulate processing delay
        time.sleep(processing_time)

        return jsonify({
            'success': True,
            'track_id': track_id,
            'effect_type': effect_type,
            'preset': preset,
            'params': effect_params,
            'message': f'Applied {effect_type} ({preset}) to track {track_id}'
        })

    except (KeyError, ValueError, TypeError) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@audio_processing_bp.route('/update-mixer-channel', methods=['POST'])
def update_mixer_channel():
    """Update mixer channel settings"""
    try:
        data = request.get_json() or {}
        channel_id = data.get('channel_id')
        settings = data.get('settings', {})

        if not channel_id:
            return jsonify({
                'success': False,
                'error': 'Missing channel_id'
            }), 400

        # Merge with default settings
        channel_settings = DEFAULT_CHANNEL_SETTINGS.copy()
        channel_settings.update(settings)

        # Validate settings
        if 'volume' in channel_settings:
            channel_settings['volume'] = max(0.0, min(1.0, channel_settings['volume']))
        if 'pan' in channel_settings:
            channel_settings['pan'] = max(-1.0, min(1.0, channel_settings['pan']))

        return jsonify({
            'success': True,
            'channel_id': channel_id,
            'settings': channel_settings,
            'message': f'Updated mixer channel {channel_id}'
        })

    except (KeyError, ValueError, TypeError) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@audio_processing_bp.route('/export-pattern', methods=['POST'])
def export_pattern():
    """Export a pattern as JSON or MIDI"""
    try:
        data = request.get_json() or {}
        pattern = data.get('pattern', {})
        export_format = data.get('format', 'json')
        project_name = data.get('project_name', 'beat_addicts_pattern')
        bpm = data.get('bpm', 120)

        if not pattern:
            return jsonify({
                'success': False,
                'error': 'No pattern data provided'
            }), 400

        # Create export data
        export_data = {
            'project_name': project_name,
            'created_at': datetime.now().isoformat(),
            'bpm': bpm,
            'pattern': pattern,
            'metadata': {
                'total_tracks': len(pattern),
                'total_steps': len(list(pattern.values())[0]) if pattern else 0,
                'active_steps': sum(sum(track) for track in pattern.values()) if pattern else 0
            }
        }

        if export_format == 'json':
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(export_data, f, indent=2)
                _temp_file = f.name

            return jsonify({
                'success': True,
                'export_data': export_data,
                'format': export_format,
                'message': f'Pattern exported as {export_format.upper()}'
            })

        elif export_format == 'midi':
            # Simulate MIDI export
            midi_data = {
                'tracks': [],
                'tempo': bpm,
                'time_signature': [4, 4]
            }

            for track_name, steps in pattern.items():
                track_data = {
                    'name': track_name,
                    'channel': list(pattern.keys()).index(track_name),
                    'notes': []
                }

                for step, active in enumerate(steps):
                    if active:
                        # Convert step to MIDI note
                        note_map = {
                            'kick': 36,    # C1
                            'snare': 38,   # D1
                            'hihat': 42,   # F#1
                            'openhat': 46  # A#1
                        }

                        note = note_map.get(track_name, 60)
                        start_time = step * (60.0 / bpm / 4)  # 16th notes

                        track_data['notes'].append({
                            'note': note,
                            'velocity': 100,
                            'start_time': start_time,
                            'duration': 0.1
                        })

                midi_data['tracks'].append(track_data)

            return jsonify({
                'success': True,
                'midi_data': midi_data,
                'format': export_format,
                'message': f'Pattern exported as {export_format.upper()}'
            })

        else:
            return jsonify({
                'success': False,
                'error': f'Unsupported export format: {export_format}'
            }), 400

    except (KeyError, ValueError, TypeError) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@audio_processing_bp.route('/save-project', methods=['POST'])
def save_project():
    """Save a complete project"""
    try:
        data = request.get_json() or {}
        project_data = data.get('project_data', {})
        project_name = data.get('project_name', 'beat_addicts_project')

        if not project_data:
            return jsonify({
                'success': False,
                'error': 'No project data provided'
            }), 400

        # Create project file structure
        project_file = {
            'project_name': project_name,
            'version': '1.0.0',
            'created_at': datetime.now().isoformat(),
            'last_modified': datetime.now().isoformat(),
            'data': project_data,
            'metadata': {
                'total_patterns': len(project_data.get('patterns', {})),
                'bpm': project_data.get('bpm', 120),
                'key': project_data.get('key', 'C'),
                'scale': project_data.get('scale', 'major')
            }
        }

        return jsonify({
            'success': True,
            'project_file': project_file,
            'project_name': project_name,
            'message': f'Project "{project_name}" saved successfully'
        })

    except (KeyError, ValueError, TypeError) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@audio_processing_bp.route('/load-project', methods=['POST'])
def load_project():
    """Load a project from file data"""
    try:
        data = request.get_json() or {}
        project_file = data.get('project_file', {})

        if not project_file:
            return jsonify({
                'success': False,
                'error': 'No project file provided'
            }), 400

        # Validate project file structure
        required_fields = ['project_name', 'version', 'data']
        for field in required_fields:
            if field not in project_file:
                return jsonify({
                    'success': False,
                    'error': f'Invalid project file: missing {field}'
                }), 400

        project_data = project_file['data']
        project_name = project_file['project_name']

        return jsonify({
            'success': True,
            'project_data': project_data,
            'project_name': project_name,
            'metadata': project_file.get('metadata', {}),
            'message': f'Project "{project_name}" loaded successfully'
        })

    except (KeyError, ValueError, TypeError) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@audio_processing_bp.route('/master-effects', methods=['POST'])
def apply_master_effects():
    """Apply effects to the master channel"""
    try:
        data = request.get_json() or {}
        effects_chain = data.get('effects_chain', [])
        master_volume = data.get('master_volume', 0.75)

        # Process effects chain
        processed_effects = []
        for effect in effects_chain:
            effect_type = effect.get('type')
            params = effect.get('params', {})
            enabled = effect.get('enabled', True)

            if enabled and effect_type in EFFECTS_PRESETS:
                processed_effects.append({
                    'type': effect_type,
                    'params': params,
                    'enabled': enabled
                })

        return jsonify({
            'success': True,
            'effects_chain': processed_effects,
            'master_volume': master_volume,
            'message': f'Applied {len(processed_effects)} master effects'
        })

    except (KeyError, ValueError, TypeError) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@audio_processing_bp.route('/analyze-audio', methods=['POST'])
def analyze_audio():
    """Analyze audio characteristics"""
    try:
        data = request.get_json() or {}
        pattern = data.get('pattern', {})
        bpm = data.get('bpm', 120)

        if not pattern:
            return jsonify({
                'success': False,
                'error': 'No pattern data provided'
            }), 400

        # Analyze pattern characteristics
        analysis = {
            'tempo': bpm,
            'complexity': 0,
            'density': 0,
            'groove_type': 'unknown',
            'recommendations': []
        }

        if pattern:
            # Calculate complexity and density
            total_steps = len(list(pattern.values())[0]) * len(pattern)
            active_steps = sum(sum(track) for track in pattern.values())

            analysis['complexity'] = active_steps / total_steps if total_steps > 0 else 0
            analysis['density'] = active_steps / len(pattern) if len(pattern) > 0 else 0

            # Detect groove type
            if 'kick' in pattern:
                kick_pattern = pattern['kick']
                if kick_pattern[0] == 1 and kick_pattern[8] == 1:
                    analysis['groove_type'] = 'four_on_floor'
                elif sum(kick_pattern[::4]) >= 3:
                    analysis['groove_type'] = 'boom_bap'
                else:
                    analysis['groove_type'] = 'syncopated'

            # Generate recommendations
            if analysis['complexity'] < 0.3:
                analysis['recommendations'].extend([
                    'Add more hi-hat variations for groove',
                    'Consider adding percussion elements',
                    'Try syncopated kick patterns'
                ])
            elif analysis['complexity'] > 0.7:
                analysis['recommendations'].extend([
                    'Simplify the pattern for better groove',
                    'Focus on main rhythm elements',
                    'Remove unnecessary fills'
                ])
            else:
                analysis['recommendations'].extend([
                    'Good balance! Try subtle variations',
                    'Experiment with velocity changes',
                    'Add swing or humanization'
                ])

            # BPM-specific recommendations
            if bpm < 90:
                analysis['recommendations'].append('Consider adding sub-bass for low tempo')
            elif bpm > 140:
                analysis['recommendations'].append('Keep patterns simple for high tempo')

        return jsonify({
            'success': True,
            'analysis': analysis,
            'message': 'Audio analysis complete'
        })

    except (KeyError, ValueError, TypeError) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

