import datetime
import random
import time
import json
import os
from threading import Thread, Event
import gemini_file as gemini  # Assuming this exists for Gemini API integration

# Define the stick figure stages for the hangman visualization
STICK_FIGURES = [
    """
______
|    0
| ---|---
|   / \\ 
|  /   \\ 
|_____""",
    """
______
|    0 
| ---|---
|
|
|_____""",
    """
______
|    0
|
|
|
|_____""",
    """
______
|
|
|
|
|_____""",
    """
|
|
|
|
|_____""",
    """
|
|
|
|
|______""",
    """
|
|
|
______""",
    """
|
|
______""",
    """
|
______""",
    """
______"""
]

# Configure difficulty settings
DIFFICULTY_LEVELS = {
    1: "easy", 
    2: "medium", 
    3: "hard", 
    4: "challenger", 
    5: "master", 
    6: "creator"
}

DIFFICULTY_TIME = {
    "easy": {"game_time_limit": 600, "turn_time_limit": 60},
    "medium": {"game_time_limit": 540, "turn_time_limit": 45},
    "hard": {"game_time_limit": 480, "turn_time_limit": 30},
    "challenger": {"game_time_limit": 420, "turn_time_limit": 25},
    "master": {"game_time_limit": 360, "turn_time_limit": 15},
    "creator": {"game_time_limit": 900, "turn_time_limit": 120}  # Default for creator mode
}

DIFFICULTY_SCORE = {
    "easy": {"letter_guess_score": 10, "word_guess_score": 10},
    "medium": {"letter_guess_score": 15, "word_guess_score": 15},
    "hard": {"letter_guess_score": 20, "word_guess_score": 30},
    "challenger": {"letter_guess_score": 25, "word_guess_score": 45},
    "master": {"letter_guess_score": 30, "word_guess_score": 60},
    "creator": {"letter_guess_score": 20, "word_guess_score": 30}  # Default for creator mode
}

DIFFICULTY_SETTINGS = {
    "easy": {"attempts": 9, "start_index": 0},       # Stages 0-8 (9 steps)
    "medium": {"attempts": 8, "start_index": 1},     # Stages 1-8 (8 steps)
    "hard": {"attempts": 7, "start_index": 2},       # Stages 2-8 (7 steps)
    "challenger": {"attempts": 6, "start_index": 3}, # Stages 3-8 (6 steps)
    "master": {"attempts": 5, "start_index": 4},     # Stages 4-8 (5 steps)
    "creator": {"attempts": 10, "start_index": 0}    # Default for creator mode
}

# Utility function to communicate with Gemini API
def gemini_prompt(prompt):
    """Send a prompt to the Gemini API and return the response."""
    try:
        return gemini.google_gemini(prompt=prompt)
    except Exception as e:
        print(f"Error communicating with Gemini API: {e}")
        return "Unable to get response from Gemini at this time. "

'''Accessing the dictionary.json file and gathering the words dictionary accordingly'''

def load_word_dictionary():
    """Load the dictionary of words from a JSON file."""
    json_file_path = os.path.join("python", "game", "hangman", "dictionary.json")
    try:
        with open(json_file_path, "r") as file:
            print("Loading word list from JSON file...\n") 
            words_dictionary = json.load(file)
            return words_dictionary
    except FileNotFoundError:
        print(f"Error: The file '{json_file_path}' was not found.")
        # Create a basic dictionary if file is not found
        return create_basic_dictionary()
    except json.JSONDecodeError:
        print(f"Error: The file '{json_file_path}' contains invalid JSON.")
        return create_basic_dictionary()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return create_basic_dictionary()

'''Had we not been able to gain accessed to the original dictionary file we can access it through this function'''

def create_basic_dictionary():
    """Create a basic dictionary with a few words for each difficulty level."""
    return {
        "easy": {
            "words": ["apple", "banana", "orange", "grapes", "kiwi"],
            "attempts": 9,
            "time_limit_minutes": 10,
            "word_length": "5-8"
        },
        "medium": {
            "words": ["elephant", "giraffe", "hippopotamus", "crocodile", "zebra"],
            "attempts": 8,
            "time_limit_minutes": 9,
            "word_length": "8-11"
        },
        "hard": {
            "words": ["extraordinary", "magnificent", "catastrophic", "phenomenal", "inconceivable"],
            "attempts": 7,
            "time_limit_minutes": 8,
            "word_length": "11-15"
        },
        "challenger": {
            "phrases": ["quantum physics", "molecular biology", "artificial intelligence", "virtual reality", "machine learning"],
            "attempts": 6,
            "time_limit_minutes": 7,
            "word_length": "15-20"
        },
        "master": {
            "phrases": ["theory of relativity", "quantum field theory", "computational fluid dynamics", "molecular orbital theory", "statistical thermodynamics"],
            "attempts": 5,
            "time_limit_minutes": 6,
            "word_length": "20-25"
        },
        "creator": {
            "words": ["customword"],
            "attempts": 10,
            "time_limit_minutes": 15,
            "word_length": "any"
        }
    }

'''If Sir Rom Zamora decides to add his own custom word into creator mode, the word will be appended accordingly through this function'''

def save_custom_word(word, attempts, time_limit, turn_time_limit):
    """Save a custom word to the creator mode in the dictionary."""
    try:
        words_dictionary = load_word_dictionary()
        
        # Update creator mode settings
        if "words" not in words_dictionary["creator"]:
            words_dictionary["creator"]["words"] = []
        
        if word not in words_dictionary["creator"]["words"]:
            words_dictionary["creator"]["words"].append(word)
        
        words_dictionary["creator"]["attempts"] = attempts
        words_dictionary["creator"]["time_limit_minutes"] = time_limit // 60  # Convert seconds to minutes
        
        # Update global settings
        DIFFICULTY_TIME["creator"]["game_time_limit"] = time_limit
        DIFFICULTY_TIME["creator"]["turn_time_limit"] = turn_time_limit
        DIFFICULTY_SETTINGS["creator"]["attempts"] = attempts
        
        # Save updated dictionary
        json_file_path = os.path.join("python", "game", "hangman", "dictionary.json")
        with open(json_file_path, "w") as file:
            json.dump(words_dictionary, file, indent=4)
        
        print(f"Custom word '{word}' saved successfully!")
        return True
    except Exception as e:
        print(f"Error saving custom word: {e}")
        return False

'''Displays all the rules concisely into this game'''

def display_rules():
    """Display the rules of the Hangman game."""
    print(
    """
    All Rules/Features Of Hangman Game:

    1: The player has the choice and will to resign at any moment when defaulting at the difficulty of the game, 
    this will reset their score, google gemini will downplay/taunt their progress and they will get the full word and the total time elapsed. 
    Note: Clearly, had the player run out of attempts, time or merely resigned as stated prior then they will reset score to 0 and tells the word accordingly.

    2: The player has the choice between 5 difficulties: (easy | medium | hard | challenger | master), each decreasing in the number
    of attempts and the time limit by an increment of 1. By choosing the difficulty they too set the tone of google gemini api through
    the gameplay of Hangman.

    3: If The game is played specifically on the 2nd of March (Sir Rom Zamora's birthday) then it will activate the easter egg, this will
    enable acess to the most secretive and hidden feature of the game. Custom/Creator mode, where you can set the number of attempts, the word
    that will be chosen and the tone of the AI throughout the game.

    4: All of the player's scores, time processes (time elapsed and time remaining) will lead all the data being saved into a JSON file. Along with the score totalling up the time you saved into the final score. They can retrieve
    this data to show and flex your achievements as a Hangman specialist. There will be a ranking to demonstrate the best players and the total cumulative score they achieved. Note: 
    This includes the highest score they ever conceptually achieved in the game. The high score they achieved throughout ALL their runs and the score they achieved in the run they were CURRENTLY playing.

    5: All of Google Gemini's responses, hinting and words it uses will be done through the access of multiple prompts (made with Deep Seek) along with consistency of structural prompting. Depending on the difficulty, it can
    mix or match between 3-4 words (a phrase) and the complexity of the word will logarithmically increase as the difficulty racks up in magnitude. (easy to hard to master etc).

    6: The entirety or fractions of the word can be guessed to activate bonus points (guess = number of underscores guessed multipled by 10,15,30,45,60 depending on the difficulty easy, medium, hard, challenger and master respectively). Note: technically no bonus points are awarded in easy difficulty
    as this will indeed fill in the underscores it matched as a word in its respective place. However, it will not count as the individual letter guessed for the program and doesn't fill out each letter that would of been guessed had you used 
    the letter.

    7: Three kinds of hints will be in the duration of the Hangman Game:
        1st kind - Describes the definition of the word or the meaning associated with the phrase
        2nd kind - Provides the letter for the word pushing the player to understand what the word could be
        3rd kind - Contextually puts the word into a sentence to help expand your understanding of the word

        Note: For the first three modes, you can use use the hints an unlimited number of times, of course this will go on your high score record that a hint was used.
        In challenger/master mode, you can only use the hint once, in challenger you can use it once your down to your last 2 attempts and for master mode only when your down to your last attempt.
        If a hint is used, Google Gemini will mock/insult for using a hint rather than merely trying to guess the word.

    """)

class HangmanGame:
    def __init__(self, name, word, difficulty, remaining_attempts, game_time_limit, turn_time_limit):
        self.name = name
        self.word = word
        self.difficulty = difficulty  # String name of difficulty
        self.difficulty_level = next(key for key, value in DIFFICULTY_LEVELS.items() if value == difficulty)  # Number of difficulty
        self.remaining_attempts = remaining_attempts
        self.game_time_limit = game_time_limit
        self.turn_time_limit = turn_time_limit
        self.game_start_time = None
        self.turn_start_time = None
        self.timeout_event = Event()
        self.timer_thread = None
        self.guessed_letters = []
        self.vetoed_letters = []
        self.valid_letters = []
        self.guessed_phrases = []
        self.current_score = 0
        self.high_score = self.load_high_score()
        self.outstanding_score = 0
        self.hints_used = 0
        self.max_hints = 3 if difficulty in ["easy", "medium", "hard"] else 1
        '''When playing in easy, medium or hard difficulty you maximum of three hints else in challenger and master you only get 1'''

    def load_high_score(self):
        """Load the player's high score from saved player stats."""
        player_stats = self.load_player_stats()
        if self.name in player_stats:
            return player_stats[self.name].get("high_score", 0)
        
        '''get the player's high score through thier name accessing their high score via a key, if its 0 it returns 0 accordingly'''
        return 0

    def start_game_timer(self):
        """Start the timer for the entire game."""
        self.game_start_time = time.time()

    def get_elapsed_time(self):
        """Get the elapsed time since the game started."""
        if self.game_start_time is None:
            return 0
        return time.time() - self.game_start_time

    def get_remaining_time(self):
        """Get the remaining time for the game."""
        if self.game_start_time is None:
            return self.game_time_limit
        elapsed = self.get_elapsed_time()
        return max(0, self.game_time_limit - elapsed)

    def start_turn_timer(self):
        """Start the timer for the current turn."""
        self.turn_start_time = time.time()
        self.timeout_event.clear()
        
        # Create and start a new timer thread
        if self.timer_thread is not None and self.timer_thread.is_alive():
            self.timeout_event.set()  # Stop the previous timer
            self.timer_thread.join(0.5)
        
        self.timer_thread = Thread(target=self._countdown_timer, daemon=True)
        self.timer_thread.start()

    def end_turn_timer(self):
        """End the timer for the current turn."""
        if self.turn_start_time is None:
            return 0
        
        self.timeout_event.set()
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join(0.5)
        
        turn_time = time.time() - self.turn_start_time
        self.turn_start_time = None
        return turn_time

    def is_turn_timeout(self):
        """Check if the turn has timed out."""
        if self.turn_start_time is None:
            return False
        return time.time() - self.turn_start_time >= self.turn_time_limit

    def _countdown_timer(self):
        """Background thread that counts down the turn time."""
        start_time = time.time()
        while not self.timeout_event.is_set():
            elapsed = time.time() - start_time
            remaining = max(0, self.turn_time_limit - elapsed)
            
            # Update every 0.5 seconds to avoid console spam
            if int(remaining * 2) % 2 == 0:
                # Instead of using \r which returns to beginning of line,
                # clear the whole line and print the timer with extra space padding
                print(f"\rTime remaining for turn: {remaining:.1f}s                    ", end='')
            
            if remaining <= 0:
                print("\nTime's up for this turn!")
                self.timeout_event.set()
                break
            
            time.sleep(0.1)

    def score_system(self, surplus, deficit):
        """Update scores based on game actions."""
        # Update current score
        old_score = self.current_score
        self.current_score += surplus
        self.current_score = max(0, self.current_score + deficit)  # Don't go below zero
        
        # Keep track of outstanding_score (accumulative positive points only)
        if surplus > 0:
            self.outstanding_score += surplus
        
        # Update high score if current score is higher
        if self.current_score > self.high_score:
            self.high_score = self.current_score
        
        return old_score, self.current_score

    def word_display(self):
        """Display the word with guessed letters revealed and underscores for hidden letters."""
        result = []
        
        for i, letter in enumerate(self.word):
            if letter in self.guessed_letters or letter == " ":
                result.append(letter)
            else:
                # Check if the letter is part of any guessed phrase
                display_letter = False
                for phrase in self.guessed_phrases:
                    if phrase in self.word:
                        start = self.word.find(phrase)
                        end = start + len(phrase)
                        if start <= i < end:
                            display_letter = True
                            break
                
                if display_letter:
                    result.append(letter)
                else:
                    result.append("_")
        
        return " ".join(result)

    def hangman_display(self):
        """Display the hangman figure based on wrong attempts and difficulty."""
        settings = DIFFICULTY_SETTINGS[self.difficulty]
        max_attempts = settings["attempts"]
        start_index = settings["start_index"]
        
        # Calculate wrong attempts
        wrong_attempts = max_attempts - self.remaining_attempts
        
        # Calculate which stage to show
        if wrong_attempts <= 0:
            return STICK_FIGURES[start_index]
        
        # Calculate progression through available figures
        figures_range = len(STICK_FIGURES) - start_index - 1
        step_size = figures_range / max_attempts if max_attempts > 0 else 0
        
        # Ensure the index is within bounds
        index = min(start_index + int(wrong_attempts * step_size), len(STICK_FIGURES) - 1)
        return STICK_FIGURES[index]

    def letter_guess(self, letter):
        """Process a letter guess."""
        if letter in self.guessed_letters:
            return "You've already guessed this letter."
        
        self.guessed_letters.append(letter)
        
        if letter in self.word:
            self.valid_letters.append(letter)
            # Count occurrences for better scoring
            occurrences = self.word.count(letter)
            score_gain = occurrences * DIFFICULTY_SCORE[self.difficulty]["letter_guess_score"]
            old_score, new_score = self.score_system(score_gain, 0)
            return f"Correct! '{letter}' is in the word {occurrences} time(s). Score: {old_score} → {new_score}"
        else:
            self.vetoed_letters.append(letter)
            self.remaining_attempts -= 1
            old_score, new_score = self.score_system(
                0, -DIFFICULTY_SCORE[self.difficulty]["letter_guess_score"]
            )
            return f"Wrong! '{letter}' is not in the word. Attempts left: {self.remaining_attempts}. Score: {old_score} → {new_score}"

    def word_guess(self, guess):
        """Process a word or phrase guess."""
        if guess in self.guessed_phrases:
            return "You've already guessed this word/phrase."
        
        self.guessed_phrases.append(guess)
        
        # Check for exact match
        if guess.lower() == self.word.lower():
            # Add all letters to guessed_letters for display
            for letter in self.word:
                if letter not in self.guessed_letters and letter != " ":
                    self.guessed_letters.append(letter)
                    
            # Calculate bonus based on remaining hidden letters
            hidden_letters = sum(1 for c in self.word if c not in self.guessed_letters and c != " ")
            score_gain = hidden_letters * DIFFICULTY_SCORE[self.difficulty]["word_guess_score"]
            old_score, new_score = self.score_system(score_gain, 0)
            return f"Correct! The word was '{self.word}'. Score: {old_score} → {new_score}"
        
        # Check for partial match (substring)
        if guess.lower() in self.word.lower():
            # Calculate bonus for partial match
            match_length = len(guess)
            score_gain = match_length * (DIFFICULTY_SCORE[self.difficulty]["word_guess_score"] // 2)
            old_score, new_score = self.score_system(score_gain, 0)
            return f"Partial match! '{guess}' is part of the word. Score: {old_score} → {new_score}"
        
        # Wrong guess
        self.remaining_attempts -= 1
        old_score, new_score = self.score_system(
            0, -DIFFICULTY_SCORE[self.difficulty]["word_guess_score"]
        )
        return f"Wrong! '{guess}' is not the word. Attempts left: {self.remaining_attempts}. Score: {old_score} → {new_score}"

    def gemini_hinting(self):
        """Provide a hint to the player using Gemini API."""
        # Check if hints are allowed
        if self.hints_used >= self.max_hints:
            return "You've used all your available hints!"
        
        # In harder difficulties, check attempts remaining
        if self.difficulty == "challenger" and self.remaining_attempts > 2:
            return "In Challenger mode, hints are only available when you have 2 or fewer attempts left."
        elif self.difficulty == "master" and self.remaining_attempts > 1:
            return "In Master mode, hints are only available when you have 1 attempt left."
        
        hint_type = 0
        while hint_type not in [1, 2, 3]:
            try:
                hint_type = int(input("What kind of hint do you want? (1: definition | 2: letter | 3: context in a sentence): "))
                if hint_type not in [1, 2, 3]:
                    print("Please enter 1, 2, or 3.")
            except ValueError:
                print("Please enter a number (1, 2, or 3).")
        
        hint_prompts = {
            1: f"Provide the definition of the word '{self.word}'. (Note: Since this is a Hangman Game, you are NOT allowed to mention the word itself only its definition of the word in simple terms).",
            2: f"Provide a letter from the word '{self.word}' that hasn't been guessed yet. (Note: Since this is a Hangman Game, you are NOT allowed to mention the word itself only a specific letter).",
            3: f"Use the word '{self.word}' in a sentence. (Note: Since this is a Hangman Game, you are NOT allowed to mention the word itself only contextually in a sentence of phrase in everyday life)."
        }
        
        # Add difficulty-specific taunting for harder levels
        if self.difficulty in ["challenger", "master"]:
            hint_prompts[hint_type] += " Also, mock/taunt the player for needing a hint."
        
        hint = gemini_prompt(hint_prompts[hint_type])
        self.hints_used += 1
        
        # Penalize score for using hints
        penalty = DIFFICULTY_SCORE[self.difficulty]["letter_guess_score"]
        old_score, new_score = self.score_system(0, -penalty)
        
        return f"{hint}\n(Hint penalty: Score {old_score} → {new_score})"

    def resignation(self):
        """Handle player resignation."""
        if self.difficulty_level >= 4:  # Challenger, Master, Creator
            message = gemini_prompt(f"Taunt the player for giving up on trying to find the word '{self.word}' while simultaneously encouraging them that they could have found it (note: this is in {self.difficulty} difficulty).")
        else:  # Easy, Medium, Hard
            message = gemini_prompt(f"Encourage the player that they could have found the word '{self.word}' had they kept trying, and to give the game another go (note: this is in {self.difficulty} difficulty).")
        
        # Reset score
        old_score = self.current_score
        self.current_score = 0
        
        # Still save the high score before reset
        if old_score > self.high_score:
            self.high_score = old_score
            
        return f"{message}\n\nThe word was: '{self.word}'\nYour score has been reset: {old_score} → 0"

    def game_finished(self):
        """Check if the game is over and provide outcome message."""
        # Check for win condition - all letters are revealed
        won = True
        for letter in self.word:
            if letter != " " and letter not in self.guessed_letters:
                # Check if letter is part of a guessed phrase
                revealed_by_phrase = False
                for phrase in self.guessed_phrases:
                    if phrase in self.word and letter in phrase:
                        revealed_by_phrase = True
                        break
                
                if not revealed_by_phrase:
                    won = False
                    break
        
        if won:
            # Add time bonus for quick completion
            time_taken = self.get_elapsed_time()
            time_bonus = int((self.game_time_limit - time_taken) * 0.1)  # 10% of remaining time as bonus
            if time_bonus > 0:
                old_score, new_score = self.score_system(time_bonus, 0)
                bonus_message = f"Time bonus: +{time_bonus} points! Score: {old_score} → {new_score}"
            else:
                bonus_message = ""
                
            return True, f"Congratulations! You won with {self.remaining_attempts} attempts left!\n" \
                   f"Word: '{self.word}'\n" \
                   f"Time: {time_taken:.1f} seconds\n" \
                   f"{bonus_message}\n" \
                   f"Final score: {self.current_score} | High score: {self.high_score}"
        
        # Check for loss conditions
        if self.remaining_attempts <= 0:
            return True, f"Game over! You've run out of attempts.\n" \
                   f"The word was: '{self.word}'\n" \
                   f"Final score: {self.current_score} | High score: {self.high_score}"
                   
        if self.get_remaining_time() <= 0:
            return True, f"Time's up! The game is over.\n" \
                   f"The word was: '{self.word}'\n" \
                   f"Final score: {self.current_score} | High score: {self.high_score}"
        
        # Game still in progress
        return False, None

    def save_player_stats(self):
        """Save the player's statistics to a JSON file."""
        try:
            player_stats = self.load_player_stats()
            
            # Update player's stats
            if self.name not in player_stats:
                player_stats[self.name] = {}
            
            player_stats[self.name]["high_score"] = self.high_score
            player_stats[self.name]["outstanding_score"] = self.outstanding_score
            player_stats[self.name]["games_played"] = player_stats[self.name].get("games_played", 0) + 1
            player_stats[self.name]["last_played"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open("player_stats.json", "w") as file:
                json.dump(player_stats, file, indent=4)
            
            return True
        except Exception as e:
            print(f"Error saving player stats: {e}")
            return False

    def load_player_stats(self):
        """Load player statistics from a JSON file."""
        try:
            with open("player_stats.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            print("Error: Invalid player stats file. Creating a new one.")
            return {}

def creator_mode():
    """Allow the player to create custom words and settings."""
    print("\n=== CREATOR MODE ===")
    print("Welcome to Creator Mode! Here you can set up custom words and game settings.")
    
    while True:
        print("\nCREATOR MODE OPTIONS:")
        print("1. Add a custom word")
        print("2. Set game parameters")
        print("3. Return to main game")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == "1":
            word = input("Enter the custom word or phrase: ").strip().lower()
            if not word:
                print("Word cannot be empty.")
                continue
                
            attempts = int(input(f"Enter number of attempts (default: 10): ") or "10")
            time_limit = int(input(f"Enter game time limit in seconds (default: 900): ") or "900")
            turn_time = int(input(f"Enter turn time limit in seconds (default: 120): ") or "120")
            
            save_custom_word(word, attempts, time_limit, turn_time)
            
        elif choice == "2":
            # Update global settings for creator mode
            attempts = int(input(f"Enter default number of attempts for Creator mode (current: {DIFFICULTY_SETTINGS['creator']['attempts']}): ") 
                         or str(DIFFICULTY_SETTINGS['creator']['attempts']))
            time_limit = int(input(f"Enter default game time limit in seconds (current: {DIFFICULTY_TIME['creator']['game_time_limit']}): ")
                           or str(DIFFICULTY_TIME['creator']['game_time_limit']))
            turn_time = int(input(f"Enter default turn time limit in seconds (current: {DIFFICULTY_TIME['creator']['turn_time_limit']}): ")
                          or str(DIFFICULTY_TIME['creator']['turn_time_limit']))
            
            # Update settings
            DIFFICULTY_SETTINGS['creator']['attempts'] = attempts
            DIFFICULTY_TIME['creator']['game_time_limit'] = time_limit
            DIFFICULTY_TIME['creator']['turn_time_limit'] = turn_time
            
            print("Creator mode settings updated!")
            
        elif choice == "3":
            return
        
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def display_leaderboard():
    """Display the leaderboard of players sorted by high score."""
    try:
        with open("player_stats.json", "r") as file:
            player_stats = json.load(file)
            
        if not player_stats:
            print("No player statistics available yet.")
            return
            
        print("\n=== HANGMAN LEADERBOARD ===")
        print("Rank | Player Name | High Score | Outstanding Score | Games Played | Last Played")
        print("-" * 80)
        
        # Sort players by high score
        sorted_players = sorted(player_stats.items(), key=lambda x: x[1].get("high_score", 0), reverse=True)
        
        for rank, (name, stats) in enumerate(sorted_players, 1):
            high_score = stats.get("high_score", 0)
            outstanding_score = stats.get("outstanding_score", 0)
            games_played = stats.get("games_played", 0)
            last_played = stats.get("last_played", "Unknown")
            
            print(f"{rank:<4} | {name:<15} | {high_score:<10} | {outstanding_score:<17} | {games_played:<12} | {last_played}")
            
    except FileNotFoundError:
        print("No player statistics available yet.")
    except Exception as e:
        print(f"Error displaying leaderboard: {e}")

def main():
    """Main function to run the Hangman game."""
    print("\n===== WELCOME TO HANGMAN =====")
    print("A game of word guessing with a twist!")
    
    while True:
        print("\nMAIN MENU:")
        print("1. Play Game")
        print("2. View Rules")
        print("3. View Leaderboard")
        print("4. Quit")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == "1":
            play_game()
        elif choice == "2":
            display_rules()
        elif choice == "3":
            display_leaderboard()
        elif choice == "4":
            print("Thanks For Playing!!! \n")

def play_game(game):
    """Main game loop function."""
    print(f"\nPlaying Hangman on {game.difficulty.capitalize()} difficulty!")
    print(f"Word to guess: {game.word_display()}")
    
    # Start game timer
    game.start_game_timer()
    
    while True:
        # Check if game is over
        is_finished, message = game.game_finished()
        if is_finished:
            print(message)
            game.save_player_stats()
            return
        
        # Display game state
        print("\n" + game.hangman_display())
        print(f"Word: {game.word_display()}")
        print(f"Guessed letters: {', '.join(sorted(game.guessed_letters)) if game.guessed_letters else 'None'} ")
        print(f"Guessed letters that were validated: : {', '.join(sorted(game.valid_letters))} ")
        print(f"Guessed letters that were vetoed: {", ".join(sorted(game.vetoed_letters))} ")
        print(f"Guessed phrases/words: {game.guessed_phrases} ")
        print(f"Attempts remaining: {game.remaining_attempts}")
        print(f"Time remaining: {game.get_remaining_time():.1f}s")
        print(f"Current score: {game.current_score} | High score: {game.high_score} | Outstanding score: {game.outstanding_score} ")
        
        # Display options
        print("\nOptions:")
        print("1. Guess a letter (vowel or constantant) ")
        print("2. Guess part of a word or/and phrase ")
        print("3. Get a hint (three kinds of hints): ")
        print("4. Resign ")
        
        # Start turn timer
        game.start_turn_timer()
        
        # Get player choice - Use a separate line for input, far from the timer display
        try:
            # Print a full line with padding before taking input
            print("\n" + "-" * 50)
            choice = input(f"Your choice (1-4) [Time: {game.turn_time_limit}s]: ")
            print("-" * 50)
            
            # Check for turn timeout
            if game.is_turn_timeout():
                print("\nTime's up for this turn!")
                game.remaining_attempts -= 1
                old_score, new_score = game.score_system(0, -5)
                print(f"Penalty for timeout: Score {old_score} → {new_score}")
                game.end_turn_timer()
                continue
            
            # End turn timer
            game.end_turn_timer()
            
            if choice == "1":
                letter = input("Enter a letter: ").lower().strip()
                if len(letter) != 1 or not letter.isalpha():
                    print("Please enter a single letter.")
                    continue
                
                result = game.letter_guess(letter)
                print(result)
                
            elif choice == "2":
                word_guess = input("Enter your guess: ").lower().strip()
                if not word_guess:
                    print("Please enter a valid guess.")
                    continue
                
                result = game.word_guess(word_guess)
                print(result)
                
                # Check if the exact word was guessed
                if word_guess.lower() == game.word.lower():
                    is_finished, message = game.game_finished()
                    if is_finished:
                        print(message)
                        game.save_player_stats()
                        return
                
            elif choice == "3":
                hint = game.gemini_hinting()
                print(hint)
                
            elif choice == "4":
                resignation_message = game.resignation()
                print(resignation_message)
                game.save_player_stats()
                return
                
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")
                
        except KeyboardInterrupt:
            print("\nGame interrupted by player.")
            game.resignation()
            game.save_player_stats()
            return
            
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

def run_game():
    """Setup and run the Hangman game."""
    while True:
        print("\n===== HANGMAN GAME ===== \n")
        print("1. Play Game")
        print("2. View Rules")
        print("3. View Player Stats")
        print("4. Exit \n")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == "1":
            # Start main game setup and play
            main_game()
            
        elif choice == "2":
            display_rules()
            
        elif choice == "3":
            view_player_stats()
            
        elif choice == "4":
            print("Thanks for playing Hangman!")
            break
            
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

def view_player_stats():
    """Display player statistics."""
    try:
        # Create a dummy game object to access the load_player_stats method
        dummy_game = HangmanGame("temp", "temp", "easy", 9, 600, 60)
        player_stats = dummy_game.load_player_stats()
        
        if not player_stats:
            print("No player statistics available yet.")
            return
            
        print("\n===== PLAYER STATISTICS =====")
        # Sort players by high score in descending order
        sorted_players = sorted(player_stats.items(), key=lambda x: x[1].get('high_score', 0), reverse=True)
        
        print(f"{'Rank':<5}{'Name':<15}{'High Score':<15}{'Games Played':<15}{'Last Played':<20}")
        print("-" * 70)
        
        for rank, (name, stats) in enumerate(sorted_players, 1):
            high_score = stats.get('high_score', 0)
            games_played = stats.get('games_played', 0)
            last_played = stats.get('last_played', 'Unknown')
            
            print(f"{rank:<5}{name:<15}{high_score:<15}{games_played:<15}{last_played:<20}")
            
    except Exception as e:
        print(f"Error displaying player stats: {e}")

# Fix for main_game() function to properly integrate play_game()
def main_game():
    global game
    """Main function to run the Hangman game."""
    # Check for creator mode unlocked by date
    present = datetime.datetime.now()

    '''
    
    creator_mode_unlocked = present.month == 3 and present.day == 2

    If the date the game is played is specifically 2nd Of March then creator mode is unlocked (Sir Rom Zamora's Birthday)
    Otherwise or debugging purposes you can do:

    creator_mode_unlcoked = True

    '''

    creator_mode_unlocked = True # specifically for debugging purposes.
    
    if creator_mode_unlocked:
        print("Happy Birthday, Sir Rom Zamora! You have unlocked the secret Custom/Creator Hangman Difficulty Mode! \n")
    
    # Get player name
    name = input("Enter your name: ").strip()

    if not name: # if no name is given then its automatically se as the following:
        name = "Hangman Player"
    
    # specifically for difficulty selection , if creator mode exists then its 6 otherwise its set as 5 (as its a hidden feature)
    max_difficulty = 6 if creator_mode_unlocked else 5
    
    difficulty_prompt = f"Select difficulty (1: Easy | 2: Medium | 3: Hard | 4: Challenger | 5: Master"
    if creator_mode_unlocked:
        difficulty_prompt += " | 6: Creator" # adds the prompt accordingly if creator mode is unlocked
    difficulty_prompt += "): " # regardless it will finish it off with (1: Easy | 2: Medium | 3: Hard | 4: Challenger | 5: Master"):
    
    while True:
        try:
            difficulty = int(input(difficulty_prompt))
            if 1 <= difficulty <= max_difficulty:
                break # completed processing the difficulty input
            else: 
                print(f"Please enter a number between 1 and {max_difficulty}.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Creator mode handling
    if difficulty == 6:
        creator_mode()
        # After creator mode setup, let them choose a word from creator dictionary accordingly
        words_dictionary = load_word_dictionary()
        creator_words = words_dictionary.get("creator", {}).get("words", ["default"])
        
        print("\nAvailable words in Creator mode: ")
        for i, word in enumerate(creator_words, 1):
            print(f"{i}. {word}")
        # prints/displays all of the word choies through enumerate()

        word_choice = 0

        # while a word choice hasn't been made this while loop keeps running and safe guarded with a try & except.
        while not (1 <= word_choice <= len(creator_words)):
            try:
                word_choice = int(input(f"Choose a word (1-{len(creator_words)}): "))
            except ValueError:
                print("Please enter a valid number.")
        
        secret_word = creator_words[word_choice-1] # enables it into a secret word
        mode = "creator" # sets the difficulty into creator

    else:
        # Normal difficulty word selection
        mode = DIFFICULTY_LEVELS[difficulty]
        words_dictionary = load_word_dictionary()
        difficulty_data = words_dictionary[mode]
        
        # Get the word list for the difficulty
        if "words" in difficulty_data:
            word_list = difficulty_data["words"]
        else:
            word_list = difficulty_data["phrases"]
        
        # Chooses a random word accordingly
        secret_word = random.choice(word_list)
    
    # Configure game settings
    remaining_attempts = DIFFICULTY_SETTINGS[mode]["attempts"]
    game_time_limit = DIFFICULTY_TIME[mode]["game_time_limit"]
    turn_time_limit = DIFFICULTY_TIME[mode]["turn_time_limit"]
    
    # Create game instance
    game = HangmanGame(name, secret_word, mode, remaining_attempts, game_time_limit, turn_time_limit)
    
    # Start the game
    print(f"\nWelcome, {name}! Are you ready to begin?")
    time.sleep(1)
    
    if difficulty >= 4:  # For harder difficulties, add taunting
        taunt_msg = gemini_prompt("Taunt the player that regardless of if they're reading when the game is starting that it's going to start anyway.")
        print(taunt_msg)
    else:
        encouragement_msg = gemini_prompt(f"Encourage the player to try their best in this game of Hangman at {mode} difficulty.")
        print(encouragement_msg)
    
    # Start the game loop
    play_game(game)

# Add this at the end of the script to run the game when executed directly
if __name__ == "__main__":
    run_game()
