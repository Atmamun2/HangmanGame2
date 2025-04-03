from google import genai

rules = "Welcome to the Hangman Game! Explain the rules of the Hangman Game, you will guess letters to uncover a hidden word. The game has five difficulty levels: Easy, Medium, Hard, Challenger, and Master. Each difficulty level changes the number of attempts you have, the time limit, and the complexity of the words. Easy: You have 9 attempts and a 10-minute time limit. The words are simple and common. Medium: You have 8 attempts and a 9-minute time limit. The words are slightly more challenging. Hard: You have 7 attempts and an 8-minute time limit. The words are more complex and less common. Challenger: You have 6 attempts and a 7-minute time limit. The words are quite challenging and may include uncommon terms. Master: You have 5 attempts and a 6-minute time limit. The words are very complex and may include rare or technical terms. You can type 'hint' at any time to get a hint, but remember that hints cost attempts. If you choose to give up, your score will default to 0, and the man will be hung. Your goal is to guess the word before you run out of attempts or time. Good luck! Please choose your difficulty level by typing the corresponding number: ( Easy | Medium | Hard | Challenger | Master ) Once you choose your difficulty, the game will begin. Let's see how well you can guess the hidden word!"
api_key = "AIzaSyB7HJR0OhR0thVSbFZ4WMdrDS06cF3SnJc"
tone = ""
dictionary = ""

def google_gemini(prompt):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )
    return print(response.text)

if __name__ == "__main__":
    # if you directly run this file it will match and run this accordingly:
    print("This is the API key file. \n")


