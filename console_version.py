import numpy as np
#import sqlite3
    
MAX_ATTEMPTS = 10
    
def playgame():
    attempts = MAX_ATTEMPTS
    print ("Welcome! I have guessed an integer between 0 and 100. You have {} attempts to guess it. \nTo play, input your guess. To give up, enter -1.\n".format(attempts))
    
    number = np.random.randint(100)
    
    success = False
    
    while True:
        print ("\nEnter your guess : ", end="")
        try:
            guessed = int(input().strip())
        except ValueError:
            print ("Please enter an integer")
            continue
            
        if guessed == -1:
            print ("Sorry to see you go")
            break

        attempts -= 1
        if attempts==0:
            break
            
        if number == guessed:
            print ("Congrats! You guessed it.")
            success = True
            break
        elif number > guessed:
            print ("Try going higher. Attempts remaining = {}".format(attempts))
        else:
            print ("Try going lower. Attempts remaining = {}".format(attempts))
    
    if not success:
        print ("\nThe number was {}. Better luck next time!".format(number))
    
if __name__=='__main__':
    #playgame()
    from tbot_game import Game
    g1 = Game(1151)
    
    while g1.isLive():
        print ("Enter your guess: ", end="")
        g = int(input().strip())
        result = g1.play_turn(g)
        if result not in ["won", "lost"]:
            print (result)
        
    print (g1.status, g1.num, g1.guesses)