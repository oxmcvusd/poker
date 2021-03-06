import deck
import player as P
import probability
import bet as B
import copy

from multiprocessing import Process, Queue

def get_number_of_players():
    number_of_players = int(input("How many opponents? "))
    
    if (number_of_players > 5):
        print("Too many players.")
        exit(1)

    return number_of_players

def deal_cards(players_remaining_in_round, the_deck):
    for player in players_remaining_in_round:
        c1 = the_deck.pop_card()
        c2 = the_deck.pop_card()
        player.assign_hand(c1, c2)
    state = 1

#checks if every element of list is equal
def check_equal(lst):
    return lst[1:] == lst[:-1]


#defines and executes the entire betting sequence
def betting(players_remaining_in_round, ante_value, community_cards, pot):
    current_bet = 0
    
    # if 0<bet and bet < ante_value
    still_betting = True
    i = 0
    
    bet_list = [0] * len(players_remaining_in_round)
    
    while still_betting == True:
        
        #for spacing purposes
        print("")

        #to iterate over players_remaining_in_round
        #have to do it like this because must the "first person" resets any time someone raises
        i = i % len(players_remaining_in_round)
        
        #if everyone has bet, checks if everyone has equal bets
        if bet_list[-1] != 0:
            if check_equal(bet_list):
                still_betting = False
                return pot
        
        #if there's one player left 
        if len(players_remaining_in_round) == 1:
            return pot
        
        player = players_remaining_in_round[i]

        if player.get_name() == 0:
            if (current_bet == 0):
                rcf = input("Raise, check, or fold? (r,c,f) ").lower()
                while True:
                    if rcf == "r" or rcf == "raise":
                        break
                    elif rcf == "c" or rcf == "check":
                        break
                    elif rcf == "f" or rcf == "fold":
                        break
                    else:
                        print("Please input a correct answer.")
                        rcf = input("Raise, check, or fold? (r,c,f) ").lower()

                if rcf == "r" or rcf == "raise":
                    print("Current bet is %s" % current_bet)
                    raised = (input("Raise to what? "))
                    
                    while ((not raised.isdigit()) and int(raised) - current_bet > ante_value) :
                        print("Did not input a legal number.")
                        print("Raise must be greater than ante.")
                        print("Current bet is %s" % current_bet)
                        print("Current ante is %s" % ante_value)
                        raised = input("Raise to what? ")
                    
                    raised = int(int(raised)/100)*100
                    current_bet = raised
                   
                    player.loss(current_bet - bet_list[i])
                    
                    pot += current_bet - bet_list[i]
                    bet_list[i] = current_bet

                elif rcf == "c" or rcf == "check":
                    print("You check.") 
                elif rcf == "f" or rcf == "fold":
                    print("You Fold.")
                    del(bet_list[i])
                    del(players_remaining_in_round[i])
                    continue
            
            elif (current_bet > 0):
                rcf = input("Raise, call, or fold? (r,c,f) ").lower()
                while True:
                    if rcf == "r" or rcf == "raise":
                        break
                    elif rcf == "c" or rcf == "check":
                        break
                    elif rcf == "f" or rcf == "fold":
                        break
                    else:
                        print("Please input a correct answer.")
                        rcf = input("Raise, check, or fold? (r,c,f) ").lower()
                if rcf == "r" or rcf == "raise":
                    print("Current bet is %s" % current_bet)
                    raised = (input("Raise to what? "))
                    while ((not raised.isdigit()) and int(raised) - current_bet > ante_value) :
                        print("Did not input a legal number.")
                        print("Raise must be greater than ante.")
                        print("Current bet is %s" % current_bet)
                        print("Current ante is %s" % ante_value)
                        raised = input("Raise to what? ")
                    raised = int(int(raised)/100)*100
                    current_bet = raised
                    player.loss(current_bet - bet_list[i])
                    pot += current_bet - bet_list[i]
                    bet_list[i] = current_bet

                if rcf == "c" or rcf == "call":
                    print("You call.")
                    player.loss(current_bet - bet_list[i])

                    pot += current_bet - bet_list[i]
                    bet_list[i] = current_bet

                if rcf == "f" or rcf == "fold":
                    print("You Fold.")
                    del(bet_list[i])
                    del(players_remaining_in_round[i])
                    continue

        #for AI
        else:
            amount_bet = B.bet(pot, ante_value, current_bet, player, community_cards)
            if (amount_bet == -1):
                print("Player %s folds" % player.get_name())
                del(bet_list[i])
                del(players_remaining_in_round[i])
                continue
            
            #check
            elif(amount_bet == 0):
                print("Player %s checks" % player.get_name())

            #amount_bet > 0 aka a raise or call
            else:
                current_bet += amount_bet
                print("Player %s raises to $%s" % (player.get_name(), current_bet))

                player.loss(current_bet - bet_list[i])
                print("Player %s has $%s left" %(player.get_name(), player.get_cash()))
               
                pot += current_bet
                bet_list[i] = current_bet
                

        #for if everyone checks
        if i == len(players_remaining_in_round) -1:
            if bet_list[0] == 0:
                if check_equal(bet_list):
                    still_betting = False
                    return pot

        i += 1

def ante(players, pot, ante_value):
    for player in players:
        
        #this should never happen but just in case
        if player.get_cash() < ante_value:
            print("ERROR: SOMEONE DOES NOT HAVE ENOUGH FOR ANTE")
            exit(1)
        
        player.loss(ante_value)
        pot += ante_value
    return pot


def check_for_human_loss(players):
    for player in players:
        if player.get_name() == 0:
            if (len(players) == 1):
                #human is only player so they won game
                #game over, human won
                return (0,1)
            else:
                #human is not only player so game is not over
                #(game not over, human didn't win (yet))
                return (1,0)
    #human is not in game so they lost game
    #(game over, human didn't win)
    return (0,0)

#for showing player cash
#works for both players and players_remaining_in_round
def player_information(players):
    for player in players:
        print("Player %s has $%s" % (player.get_name(), player.get_cash()))
        
        
class Game_state(object):
    def __init__(self, number_of_players, starting_cash, ante_value):
        self.number_of_players = number_of_players
        self.starting_cash = starting_cash
        self.ante_value = ante_value
        
        self.human_win  = False
        self.game       = 1
        self.round_n    = 1
        self.pot        = 0
    
    
    def change_ante(self, new_ante):
        self.ante_value = new_ante
    
    def get_round(self):
        return self.round_n
    def increment_round(self):
        self.round_n += 1
    
    def change_pot(self, n):
        self.pot = n
    def reset_pot(self):
        self.pot = 0
    def get_pot(self):
        return self.pot


def check_all_in(players_remaining_in_round):
    all_in = False
    for a_player in players_remaining_in_round:
        if a_player.get_cash() <= 0:
            all_in = True
            break
    return all_in

def game():
    
    #get number of players
    #there is always one player, the rest are AI
    
    #number_of_players = get_number_of_players() + 1

    number_of_players = 2
    starting_cash     = 10000 #input("How much starting cash? ")
    ante_value             = 100 # input("What is the blind? ")

    game_state = Game_state(number_of_players, starting_cash, ante_value)

    print("\nGAME START")
    print("========================================\n")

    #player creation
    players = []
    #player0 is always the human
    for i in range(0, number_of_players):
        players.append( P.Player(i, starting_cash) )
    
    #human player, making variable for ease of reference
    human = players[0]

    game = 1
    win  = 0 

    while (game == 1):
        
        if game_state.get_round() % 5 == 0:
            game_state.change_ante_value(game_state.ante_value() * 2)   

        player_information(players)
       
        print("\n---------------------------------------------")
        print("New Round:\n")

        game_state.reset_pot()
        the_deck = deck.Deck()
        the_deck.shuffle()
        
        community_cards = []
        state = 0

        players_remaining_in_round = []
        for a_player in players:
            players_remaining_in_round.append(a_player)
        
        #getting ante
        game_state.change_pot( ante(players_remaining_in_round, game_state.get_pot(), ante_value))

        print("After Ante:")
        player_information(players_remaining_in_round)
        print("Pot is currently $%s" % game_state.get_pot())

        #hand out cards and take ante
        deal_cards(players_remaining_in_round, the_deck)

        print("\nYour cards: %s" % str(human.get_hand()))
        # first state of betting
        
        if (check_all_in(players_remaining_in_round) == False):
            game_state.change_pot( betting(players_remaining_in_round, ante_value, community_cards, game_state.get_pot()))
            print("Pot is currently $%s" % game_state.get_pot())
        
        if (len(players_remaining_in_round) == 1):
            print(community_cards)
            players[players_remaining_in_round[0].get_name()].win(game_state.get_pot())
            player = players[players_remaining_in_round[0].get_name()]
            player.win(game_state.get_pot())
            print("\nPlayer %s wins the round and $%s " % (player.get_name(), game_state.get_pot()))
            continue
        
            #flop and flop betting

        community_cards.append(the_deck.pop_card())
        community_cards.append(the_deck.pop_card())
        community_cards.append(the_deck.pop_card())
        print("Community cards:", community_cards)

        player_information(players_remaining_in_round)
        
        if (check_all_in(players_remaining_in_round) == False):
            bet = betting(players_remaining_in_round, ante_value, community_cards, game_state.get_pot())
            game_state.change_pot(bet)
            print("Pot is currently $%s" % game_state.get_pot())

        if (len(players_remaining_in_round) == 1):
            print(community_cards)
            player = players[players_remaining_in_round[0].get_name()]
            
            player.win(game_state.get_pot())

            
            print("\nPlayer %s wins the round and $%s " % (player.get_name(), game_state.get_pot()))
            
            continue
       
       # turn and turn betting
        community_cards.append(the_deck.pop_card())
        print("Community cards:", community_cards)

        player_information(players_remaining_in_round)
        
        if (check_all_in(players_remaining_in_round) == False):
            bet = betting(players_remaining_in_round, ante_value, community_cards, game_state.get_pot())
            game_state.change_pot(bet)
            print("Pot is currently $%s" % game_state.get_pot())
        
        if (len(players_remaining_in_round) == 1):
            print(community_cards)
            player = players[players_remaining_in_round[0].get_name()]
            player.win(game_state.get_pot())
            print("\nPlayer %s wins the round and $%s " % (player.get_name(), game_state.get_pot()))
            continue
        
        # river and river betting
        community_cards.append(the_deck.pop_card())
        print("Community cards:", community_cards)
        
        player_information(players_remaining_in_round)
        if (check_all_in(players_remaining_in_round) == False):
            bet = betting(players_remaining_in_round, ante_value, community_cards, game_state.get_pot())
            game_state.change_pot(bet)
            print("Pot is currently $%s" % game_state.get_pot())
        
        # card reveal 
        print("Community cards:", community_cards)
        for player in players_remaining_in_round:
            if player.get_name() == 0:
                print("Your cards:", player.get_hand())
            else:
                print("Player %s cards: %s" % (player.get_name(), str(player.get_hand())))

        #determine winner aka eliminate losers from players_remaining_in_round
               
        hole_cards = [x.get_hand() for x in players_remaining_in_round]


        #a way to get list of winners would be dual compare everyone with everyone else,
        #and keep list of number of wins
        #whoever has most wins, wins
        winner_index = probability.get_winner(hole_cards, community_cards)

        #payout
        for winner in winner_index:
            player = players[players_remaining_in_round[winner-1].get_name()]
            player.win(int(game_state.get_pot()/len(winner_index)))
            print("\nPlayer %s wins the round and $%s " % (player.get_name(), game_state.get_pot()))
        

        #player elimination
        players = player_elimination(players, ante_value)

        #check for human loss
        (game,win) = check_for_human_loss(players)
        
        #reorder players
        reorder_players(players) 
       
        reset_players(players)

        print("\nRound end!\n")


    if (win == 0):
        print("You lose!")
    if (win == 1):
        print("You win!")

    game_state.increment_round()

def reset_players(players):
    for player in players:
        player.empty_hand()


def player_elimination(players, ante_value):
    new_players = [s for s in players if s.get_cash() > ante_value]
    return new_players


def reorder_players(players):
    players.append(players.pop(0))


if __name__ == "__main__":
    game()

