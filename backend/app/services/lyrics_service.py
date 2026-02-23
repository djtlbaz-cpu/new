"""Genre-aware template-based lyrics generator."""
from __future__ import annotations

import random
from typing import Optional

# Genre-specific verse and chorus templates, mirroring the NewBeats LyricsGenerator style
_GENRE_TEMPLATES: dict[str, dict] = {
    "hip hop": {
        "keywords": ["flow", "beat", "rhyme", "street", "hustle", "real"],
        "verses": [
            [
                "In the rhythm of the night we hustle to survive",
                "Every beat we make is keeping hope alive",
                "From the streets we rise, chasing every dream",
                "Nothing's what it was, nothing's what it seems",
            ],
            [
                "We grind from dusk to dawn, never stop the flow",
                "Through every battle scar, watch our spirit grow",
                "Real recognize real, that's the only code",
                "We carry heavy weight but we bear the load",
            ],
        ],
        "choruses": [
            [
                "We rise up, we shine bright, like stars in the sky",
                "No limits, no fears, we're ready to fly",
                "Together we stand, divided we fall",
                "Music unites us, one voice, one call",
            ],
        ],
    },
    "pop": {
        "keywords": ["love", "heart", "dreams", "tonight", "forever"],
        "verses": [
            [
                "In the early morning light I find my way to you",
                "Every little thing you do makes skies so blue",
                "Dancing through the raindrops, laughing in the sun",
                "We were meant for this, you and I as one",
            ],
            [
                "Memories we've made will last a lifetime through",
                "Every breath I take reminds me more of you",
                "Holding on to moments, never letting go",
                "In this world together, watching our love grow",
            ],
        ],
        "choruses": [
            [
                "Baby you're the light that guides me home",
                "Never want to leave, never want to roam",
                "With you by my side I feel so alive",
                "Together we're destined to love and thrive",
            ],
        ],
    },
    "rock": {
        "keywords": ["fire", "freedom", "fight", "loud", "rebel"],
        "verses": [
            [
                "Standing on the edge of something new tonight",
                "Every scar we bear is proof we won the fight",
                "Burning through the darkness, reaching for the flame",
                "Nothing's going to stop us, nothing's ever the same",
            ],
            [
                "Electric guitars roar through the stormy night",
                "We were born to rock, born to burn so bright",
                "Defy the forces trying to keep us down",
                "We're the kings and queens of this rebel town",
            ],
        ],
        "choruses": [
            [
                "We rock this world with everything we've got",
                "Turn it up loud and give it all we've got",
                "Burning like a fire, loud and wild and free",
                "This is who we are, this is what we'll be",
            ],
        ],
    },
    "country": {
        "keywords": ["home", "road", "heart", "family", "memories"],
        "verses": [
            [
                "Down a dusty old road where the wildflowers grow",
                "Mama's on the porch watching the sunset glow",
                "Simple life we lived, every day a gift",
                "Country hearts and souls give our spirits lift",
            ],
            [
                "Old truck on the highway heading home again",
                "Counting all the blessings, counting on my kin",
                "Stars above the pasture, fireflies at night",
                "Everything feels perfect, everything feels right",
            ],
        ],
        "choruses": [
            [
                "Home is where the heart is, home is where I belong",
                "Singing to the country, singing an old song",
                "Dirt roads and deep roots keep me staying true",
                "Every single memory brings me back to you",
            ],
        ],
    },
    "r&b": {
        "keywords": ["soul", "groove", "smooth", "baby", "love"],
        "verses": [
            [
                "In the candlelight your eyes are all I see",
                "Every gentle touch sets my spirit free",
                "Smooth like velvet, sweet like summer rain",
                "Baby come closer and ease away my pain",
            ],
            [
                "Your love is like a melody that plays all night",
                "Every moment with you, everything feels right",
                "Soul to soul we move in perfect harmony",
                "Baby you're the only one for me",
            ],
        ],
        "choruses": [
            [
                "Baby let me love you through the night",
                "Hold you close and make everything alright",
                "Soul and body moving with the groove",
                "Baby let me show you every move",
            ],
        ],
    },
    "electronic": {
        "keywords": ["electric", "neon", "digital", "pulse", "energy"],
        "verses": [
            [
                "Neon lights flash through the digital night",
                "Synthesizers pulse with electric light",
                "We rise together in the rhythm of the beat",
                "Every drop of energy making it complete",
            ],
            [
                "Circuit boards and melodies, the future's now",
                "Dancing in the data stream, take a bow",
                "Electric energy flowing through our veins",
                "Breaking all the barriers, breaking all the chains",
            ],
        ],
        "choruses": [
            [
                "Feel the beat, feel the pulse, feel alive",
                "Electric energy, watch us rise and thrive",
                "Drop the bass, feel the wave, lose control",
                "Digital dreams are feeding every soul",
            ],
        ],
    },
    "reggae": {
        "keywords": ["peace", "love", "unity", "rhythm", "island"],
        "verses": [
            [
                "Sun rises over the island, warm and bright",
                "Feel the reggae rhythm, everything's alright",
                "Peace and love and unity, that's the way",
                "Positive vibrations guide us through the day",
            ],
            [
                "Ocean waves are calling, breezes soft and free",
                "Roots and culture running deep inside of me",
                "Natural living, natural way of life",
                "Love and understanding, cutting through the strife",
            ],
        ],
        "choruses": [
            [
                "One love, one heart, one destiny",
                "United in the rhythm, we are free",
                "Rise up, give thanks for another day",
                "Reggae music lighting up our way",
            ],
        ],
    },
}

_GENRE_KEYWORDS: dict[str, list[str]] = {
    "hip hop": ["rap", "hip hop", "hiphop", "trap", "bars", "flow"],
    "pop": ["pop", "catchy", "mainstream", "radio", "commercial"],
    "rock": ["rock", "metal", "punk", "guitar", "heavy"],
    "country": ["country", "folk", "acoustic", "americana", "nashville"],
    "r&b": ["r&b", "rnb", "soul", "smooth", "groove"],
    "electronic": ["electronic", "edm", "techno", "house", "dubstep", "synth"],
    "reggae": ["reggae", "ska", "caribbean", "jamaica", "rasta"],
}


def _detect_genre(prompt: str) -> str:
    """Detect the most likely genre from a free-text prompt."""
    prompt_lower = prompt.lower()
    for genre, keywords in _GENRE_KEYWORDS.items():
        if any(kw in prompt_lower for kw in keywords):
            return genre
    return "pop"


class LyricsGenerator:
    """Generate song lyrics using genre-specific templates.

    Mirrors the template-based approach of the NewBeats LyricsGenerator,
    providing structured verse/chorus output without requiring a local LLM.
    """

    def generate(self, theme: str, genre: Optional[str] = None) -> str:
        """Return structured lyrics for *theme*, optionally locked to *genre*.

        Args:
            theme: A free-text description of the song's theme or style.
            genre: Optional genre override (already normalised to lowercase);
                   auto-detected from *theme* if omitted.

        Returns:
            A multi-line string with [Verse 1], [Chorus], [Verse 2], [Chorus]
            sections.
        """
        resolved_genre = genre if genre else _detect_genre(theme)
        template = _GENRE_TEMPLATES.get(resolved_genre, _GENRE_TEMPLATES["pop"])

        verses = template["verses"]
        verse1 = random.choice(verses)
        remaining = [v for v in verses if v != verse1]
        verse2 = random.choice(remaining) if remaining else verse1
        chorus = random.choice(template["choruses"])

        sections = [
            "[Verse 1]",
            *verse1,
            "",
            "[Chorus]",
            *chorus,
            "",
            "[Verse 2]",
            *verse2,
            "",
            "[Chorus]",
            *chorus,
        ]
        return "\n".join(sections)
