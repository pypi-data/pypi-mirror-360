import random

def startguessing(start, end):
  number_to_guess = random.randint(start, end)
  attempts = 0

  print(f"I've thought of a number between {start} and {end}.")
  print("Guess the number I've thought of. Let the games begin! 🌀")

  while True:
    attempts += 1
    guess = input(f"[Attempt {attempts}] Enter your guess: ")

    guessNumber = None  # Initialize guess to ensure it's always defined
    try:
      guessNumber = int(guess)
      if guessNumber < start or guessNumber > end:
        raise ValueError("Guess out of range.")
    except ValueError:
      print(f"Please enter a valid number between {start} and {end}.")
      attempts -= 1
      continue
    except EOFError:
      print(f"Quitting the game. The number was {guess}")
      break

    if guessNumber < number_to_guess:
      print("Too low! Try again.")
    elif guessNumber > number_to_guess:
      print("Too high! Try again.")
    else:
      print(f"You win! You've guessed the number {number_to_guess} in {attempts} attempts! Can you do better?")
      break
    

    
