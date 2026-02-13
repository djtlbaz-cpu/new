from flask import Blueprint, request, jsonify
import random

ai_music_bp = Blueprint('ai_music', __name__)

# Predefined drum patterns for AI generation
DRUM_PATTERNS = {
    'boom_bap': {
        'kick': [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
        'snare': [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
        'hihat': [1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
        'openhat': [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1]
    },
    'trap': {
        'kick': [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0],
        'snare': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        'hihat': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        'openhat': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    'house': {
        'kick': [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
        'snare': [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
        'hihat': [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        'openhat': [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
    },
    'techno': {
        'kick': [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
        'snare': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        'hihat': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        'openhat': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]
    }
}

MELODY_PATTERNS = {
    'major_scale': [0, 2, 4, 5, 7, 9, 11],
    'minor_scale': [0, 2, 3, 5, 7, 8, 10],
    'pentatonic': [0, 2, 4, 7, 9],
    'blues': [0, 3, 5, 6, 7, 10]
}

@ai_music_bp.route('/generate-beat', methods=['POST'])
def generate_beat():
    """Generate an AI-powered drum pattern"""
    try:
        data = request.get_json() or {}
        style = data.get('style', 'boom_bap')
        variation = data.get('variation', 0.1)  # Amount of randomization

        # Get base pattern or use random if style not found
        if style in DRUM_PATTERNS:
            base_pattern = DRUM_PATTERNS[style].copy()
        else:
            base_pattern = random.choice(list(DRUM_PATTERNS.values())).copy()

        # Add variation to the pattern
        generated_pattern = {}
        for track, pattern in base_pattern.items():
            new_pattern = []
            for step in pattern:
                if step == 1:
                    # Keep active steps with some probability
                    new_pattern.append(1 if random.random() > variation * 0.3 else 0)
                else:
                    # Add new steps with low probability
                    new_pattern.append(1 if random.random() < variation * 0.1 else 0)
            generated_pattern[track] = new_pattern

        return jsonify({
            'success': True,
            'pattern': generated_pattern,
            'style': style,
            'bpm': random.randint(80, 140),
            'message': f'Generated {style} beat pattern'
        })

    except (KeyError, ValueError, TypeError) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_music_bp.route('/generate-melody', methods=['POST'])
def generate_melody():
    """Generate an AI-powered melody"""
    try:
        data = request.get_json() or {}
        scale = data.get('scale', 'major_scale')
        length = data.get('length', 16)
        root_note = data.get('root_note', 60)  # Middle C

        # Get scale notes
        if scale in MELODY_PATTERNS:
            scale_notes = MELODY_PATTERNS[scale]
        else:
            scale_notes = MELODY_PATTERNS['major_scale']

        # Generate melody
        melody = []
        for i in range(length):
            if random.random() > 0.2:  # 80% chance of note
                note = root_note + random.choice(scale_notes) + random.choice([0, 12, 24])
                velocity = random.randint(60, 100)
                melody.append({
                    'step': i,
                    'note': note,
                    'velocity': velocity,
                    'duration': random.choice([0.25, 0.5, 1.0])
                })

        return jsonify({
            'success': True,
            'melody': melody,
            'scale': scale,
            'root_note': root_note,
            'message': f'Generated {scale} melody'
        })

    except (KeyError, ValueError, TypeError) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_music_bp.route('/generate-bassline', methods=['POST'])
def generate_bassline():
    """Generate an AI-powered bassline"""
    try:
        data = request.get_json() or {}
        style = data.get('style', 'simple')
        root_note = data.get('root_note', 36)  # Low C

        bassline = []

        if style == 'simple':
            # Simple root note pattern
            pattern = [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
            for i, active in enumerate(pattern):
                if active:
                    bassline.append({
                        'step': i,
                        'note': root_note + random.choice([0, 7, 12]),  # Root, fifth, octave
                        'velocity': random.randint(70, 90),
                        'duration': 0.5
                    })
        elif style == 'walking':
            # Walking bassline
            notes = [root_note, root_note + 2, root_note + 4, root_note + 5,
                    root_note + 7, root_note + 9, root_note + 11, root_note + 12]
            for i in range(16):
                if i % 4 == 0 or random.random() > 0.3:
                    bassline.append({
                        'step': i,
                        'note': random.choice(notes),
                        'velocity': random.randint(60, 80),
                        'duration': 0.25
                    })

        return jsonify({
            'success': True,
            'bassline': bassline,
            'style': style,
            'root_note': root_note,
            'message': f'Generated {style} bassline'
        })

    except (KeyError, ValueError, TypeError) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_music_bp.route('/suggest-arrangement', methods=['POST'])
def suggest_arrangement():
    """Suggest song arrangement structure"""
    try:
        data = request.get_json() or {}
        genre = data.get('genre', 'electronic')
        _duration = data.get('duration', 180)  # 3 minutes default

        arrangements = {
            'electronic': [
                {'section': 'intro', 'duration': 16, 'description': 'Ambient intro with filtered elements'},
                {'section': 'buildup', 'duration': 16, 'description': 'Add drums and bass gradually'},
                {'section': 'drop', 'duration': 32, 'description': 'Full energy with all elements'},
                {'section': 'breakdown', 'duration': 16, 'description': 'Remove drums, keep melody'},
                {'section': 'buildup', 'duration': 16, 'description': 'Build tension again'},
                {'section': 'drop', 'duration': 32, 'description': 'Second drop with variations'},
                {'section': 'outro', 'duration': 16, 'description': 'Fade out with ambient elements'}
            ],
            'hip_hop': [
                {'section': 'intro', 'duration': 8, 'description': 'Simple drum loop'},
                {'section': 'verse', 'duration': 32, 'description': 'Main beat with bass'},
                {'section': 'chorus', 'duration': 16, 'description': 'Add melodic elements'},
                {'section': 'verse', 'duration': 32, 'description': 'Variation of main beat'},
                {'section': 'chorus', 'duration': 16, 'description': 'Full arrangement'},
                {'section': 'bridge', 'duration': 16, 'description': 'Different chord progression'},
                {'section': 'chorus', 'duration': 16, 'description': 'Final chorus'},
                {'section': 'outro', 'duration': 8, 'description': 'Fade out'}
            ]
        }

        if genre in arrangements:
            arrangement = arrangements[genre]
        else:
            arrangement = arrangements['electronic']

        return jsonify({
            'success': True,
            'arrangement': arrangement,
            'genre': genre,
            'total_bars': sum(section['duration'] for section in arrangement),
            'message': f'Generated {genre} arrangement structure'
        })

    except (KeyError, ValueError, TypeError) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_music_bp.route('/analyze-pattern', methods=['POST'])
def analyze_pattern():
    """Analyze a drum pattern and provide suggestions"""
    try:
        data = request.get_json() or {}
        pattern = data.get('pattern', {})

        analysis = {
            'complexity': 0,
            'groove': 'unknown',
            'suggestions': []
        }

        if pattern:
            # Calculate complexity
            total_hits = sum(sum(track) for track in pattern.values())
            total_steps = len(list(pattern.values())[0]) * len(pattern)
            analysis['complexity'] = total_hits / total_steps

            # Detect groove type
            if 'kick' in pattern:
                kick_pattern = pattern['kick']
                if kick_pattern[0] == 1 and kick_pattern[8] == 1:
                    analysis['groove'] = 'four_on_floor'
                elif sum(kick_pattern[::4]) >= 3:
                    analysis['groove'] = 'boom_bap'
                else:
                    analysis['groove'] = 'syncopated'

            # Generate suggestions
            if analysis['complexity'] < 0.3:
                analysis['suggestions'].append('Try adding more hi-hat variations')
                analysis['suggestions'].append('Consider adding percussion elements')
            elif analysis['complexity'] > 0.7:
                analysis['suggestions'].append('Pattern might be too busy, try simplifying')
                analysis['suggestions'].append('Focus on the main groove elements')
            else:
                analysis['suggestions'].append('Good balance! Try subtle variations')
                analysis['suggestions'].append('Experiment with velocity changes')

        return jsonify({
            'success': True,
            'analysis': analysis,
            'message': 'Pattern analysis complete'
        })

    except (KeyError, ValueError, TypeError) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_music_bp.route('/get-suggestions', methods=['GET'])
def get_suggestions():
    """Get random AI suggestions for music production"""
    suggestions = [
        {
            'type': 'beat',
            'title': 'Boom Bap Groove',
            'description': 'Classic hip-hop drum pattern with punchy kick and snare',
            'bpm': 85,
            'style': 'boom_bap'
        },
        {
            'type': 'melody',
            'title': 'Chill Keys',
            'description': 'Relaxed piano melody in minor scale',
            'bpm': 90,
            'style': 'ambient'
        },
        {
            'type': 'bass',
            'title': '808 Sub Bass',
            'description': 'Deep sub bass with trap-style pattern',
            'bpm': 140,
            'style': 'trap'
        },
        {
            'type': 'arrangement',
            'title': 'Build & Drop',
            'description': 'Electronic arrangement with tension and release',
            'bpm': 128,
            'style': 'electronic'
        }
    ]

    # Return 2-3 random suggestions
    selected = random.sample(suggestions, random.randint(2, 3))

    return jsonify({
        'success': True,
        'suggestions': selected,
        'message': 'AI suggestions ready'
    })

