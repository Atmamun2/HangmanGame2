import json
import math

# Unique words and phrases for each difficulty level
words_data = {
    "easy": [
        "apple", "banana", "cat", "dog", "elephant", "fish", "grape", "house", "ice", "juice",
        "kite", "lemon", "mango", "nest", "orange", "pear", "queen", "rabbit", "sun", "tree",
        "umbrella", "van", "water", "xylophone", "yogurt", "zebra", "ant", "bird", "car", "duck",
        "egg", "frog", "goat", "hat", "ink", "jump", "kitten", "lion", "moon", "owl", "pig",
        "quail", "rose", "ship", "tiger", "unicorn", "vase", "whale", "yarn", "zoo"
    ],
    "medium": [
        "ambition", "breeze", "cascade", "dazzle", "echo", "flourish", "glimmer", "harbor", "illusion", "jubilee",
        "kaleidoscope", "luminous", "mystic", "nectar", "oasis", "pinnacle", "quasar", "radiant", "serene", "tranquil",
        "utopia", "vivid", "whisper", "xenon", "yearn", "zenith", "alchemy", "benevolent", "crescendo", "dynamo",
        "effervescent", "finesse", "gossamer", "halcyon", "incandescent", "jovial", "kismet", "labyrinth", "mellifluous",
        "nostalgia", "oblivion", "paradox", "quintessence", "resplendent", "symphony", "talisman", "umbra", "verisimilitude",
        "whimsical", "xylography"
    ],
    "hard": [
        "abstruse", "belligerent", "cogent", "debilitate", "ebullient", "facetious", "gregarious", "harangue", "iconoclast", "juxtapose",
        "knavery", "languid", "mendacious", "nefarious", "obfuscate", "perfidious", "quixotic", "recalcitrant", "sagacious", "taciturn",
        "ubiquitous", "vacuous", "winsome", "xeric", "yoke", "zealous", "abrogate", "bellicose", "cogitate", "deleterious", "ebullience",
        "facetiousness", "gregariousness", "harangue", "iconoclastic", "juxtaposition", "knavery", "languor", "mendacity", "nefariousness",
        "obfuscation", "perfidy", "quixotism", "recalcitrance", "sagacity", "taciturnity", "ubiquity", "vacuity", "winsomeness", "xerophyte"
    ],
    "challenger": [
        "thermostat calibration", "kaleidoscope patterns", "ventriloquist performance", "parallelogram geometry", "quintessential example",
        "sophisticated technology", "unprecedented event", "xylophonist musician", "zoological studies", "bibliography compilation",
        "cryptography algorithm", "demographic analysis", "electromagnetic spectrum", "fluorescence effect", "geopolitical strategy",
        "hydroelectric power", "idiosyncratic behavior", "jurisprudence principles", "lexicography techniques", "metamorphosis process",
        "neuroplasticity research", "oscilloscope measurements", "quintessential example", "sophisticated technology", "unprecedented event",
        "thermodynamic equilibrium", "astrobiological research", "nanotechnological advancements", "epidemiological modeling", "pharmacokinetic properties",
        "geopolitical instability", "meteorological phenomena", "psycholinguistic analysis", "socioeconomic disparities", "immunological responses",
        "paleontological discoveries", "astrophysical observations", "biotechnological innovations", "cryptocurrency mining", "epidemiological surveillance",
        "neuropharmacological effects", "radiocarbon dating", "spectroscopic analysis", "thermonuclear reactions", "algorithmic complexity",
        "biomechanical engineering", "cryptographic protocols", "thermodynamic equilibrium", "astrobiological research", "nanotechnological advancements"
    ],
    "master": [
        "quantum entanglement theory", "neuroplasticity mechanisms research", "electromagnetic radiation spectrum",
        "algorithmic complexity analysis", "biomechanical engineering principles", "cryptographic protocols design",
        "thermodynamic equilibrium states", "astrobiological research findings", "nanotechnological advancements overview",
        "epidemiological modeling techniques", "pharmacokinetic properties analysis", "geopolitical instability factors",
        "meteorological phenomena forecasting", "psycholinguistic analysis methods", "socioeconomic disparities impact",
        "immunological responses study", "paleontological discoveries report", "astrophysical observations summary",
        "biotechnological innovations review", "cryptocurrency mining operations", "epidemiological surveillance systems",
        "neuropharmacological effects research", "radiocarbon dating techniques", "spectroscopic analysis methods",
        "thermonuclear reactions study", "quantum computing advancements", "neuroplasticity research insights",
        "electromagnetic spectrum analysis", "algorithmic efficiency optimization", "biomechanical systems design",
        "cryptographic security protocols", "thermodynamic principles exploration", "astrobiological discoveries update",
        "nanotechnological applications review", "epidemiological studies summary", "pharmacokinetic modeling techniques",
        "geopolitical strategies analysis", "meteorological forecasting models", "psycholinguistic research findings",
        "socioeconomic policies impact", "immunological therapies development", "paleontological excavations report",
        "astrophysical theories exploration", "biotechnological breakthroughs overview", "cryptocurrency trading strategies",
        "epidemiological investigations summary", "neuropharmacological studies review", "radiocarbon analysis techniques",
        "spectroscopic techniques overview", "thermonuclear fusion research"
    ]
}

# Add metadata and scoring parameters for each difficulty level
game_data = {
    "easy": {
        "attempts": 9,
        "time_limit_minutes": 10,
        "word_length": "5-8 letters",
        "words": words_data["easy"],
        "scoring": {
            "time_value": 1/50,  # Points per second saved
            "guess_penalty": 1,  # Points lost per incorrect guess
            "bonus_multiplier": 1.0  # Score multiplier for this difficulty
        }
    },
    "medium": {
        "attempts": 8,
        "time_limit_minutes": 9,
        "word_length": "8-11 letters",
        "words": words_data["medium"],
        "scoring": {
            "time_value": 1/20,
            "guess_penalty": 1,
            "bonus_multiplier": 1.2
        }
    },
    "hard": {
        "attempts": 7,
        "time_limit_minutes": 8,
        "word_length": "11-15 letters",
        "words": words_data["hard"],
        "scoring": {
            "time_value": 1/15,
            "guess_penalty": 1,
            "bonus_multiplier": 1.5
        }
    },
    "challenger": {
        "attempts": 6,
        "time_limit_minutes": 7,
        "word_length": "15-20 letters",
        "phrases": words_data["challenger"],
        "scoring": {
            "time_value": 1/12,
            "guess_penalty": 1,
            "bonus_multiplier": 2.0
        }
    },
    "master": {
        "attempts": 5,
        "time_limit_minutes": 6,
        "word_length": "15-25 letters",
        "phrases": words_data["master"],
        "scoring": {
            "time_value": 1/10,
            "guess_penalty": 1,
            "bonus_multiplier": 3.0
        }
    }
}


def calculate_score(difficulty, time_used_seconds, incorrect_guesses):
    """Calculate score based on game parameters"""
    params = game_data[difficulty.lower()]
    scoring = params["scoring"]
    
    # Calculate time saved (cannot be negative)
    time_limit_seconds = params["time_limit_minutes"] * 60
    time_saved = max(0, time_limit_seconds - time_used_seconds)
    
    # Calculate time-based score component (always round up)
    time_score = math.ceil(time_saved * scoring["time_value"])
    
    # Calculate penalty for incorrect guesses
    guess_penalty = incorrect_guesses * scoring["guess_penalty"]
    
    # Calculate base score (cannot be negative)
    base_score = max(0, time_score - guess_penalty)
    
    # Apply difficulty multiplier
    total_score = math.ceil(base_score * scoring["bonus_multiplier"])
    
    return {
        "difficulty": difficulty.capitalize(),
        "time_used": f"{time_used_seconds//60}m {time_used_seconds%60}s",
        "time_saved": time_saved,
        "time_score": time_score,
        "incorrect_guesses": incorrect_guesses,
        "guess_penalty": guess_penalty,
        "base_score": base_score,
        "bonus_multiplier": scoring["bonus_multiplier"],
        "total_score": total_score
    }

# Save the dictionary as a JSON file
with open('dictionary.json', 'w') as json_file:
    json.dump(game_data, json_file, indent=4)

print("Enhanced dictionary saved as dictionary.json")

# Example usage:
if __name__ == "__main__":
    example_score = calculate_score("master", 175, 3)  # 2m55s used, 3 incorrect guesses
    print("\nExample Score Calculation (Master Difficulty):")
    for key, value in example_score.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
