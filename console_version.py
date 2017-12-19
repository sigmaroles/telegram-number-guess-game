import numpy as np
    
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