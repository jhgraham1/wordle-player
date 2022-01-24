from datetime import datetime
import operator
import random
import pandas

#------------ SET GAME MODE HERE ------------------- #
HardMode = input("Hard Mode On (y/n)?") == 'y'
Debug = True
gamemode = int(input("Please enter game mode:\n(1) User guesses computer's word\n(2) Computer guesses user's word\n(3) Loop through all games with a starting word\n(4) Loop through all games with all starting words\n(5) Full demo mode, you specify both words\n"))

if gamemode == 1:  # User guesses computer word
    User_Guesses = True
    User_Thinks = False
    Random_Words = True
    Specify_FirstGuess = False
elif gamemode == 2: # Computer guesses user (or website) word
    User_Guesses = False
    User_Thinks = True
    Random_Words = False
    Specify_FirstGuess = False
elif gamemode == 3:  # Loop through 2470 games with one starting word
    User_Guesses = False
    User_Thinks = True
    Random_Words = False
    Specify_FirstGuess = True
    Loop_All_Words = False
elif gamemode == 4: # Loop through all 6,100,900 games with all starting words
    User_Guesses = False
    User_Thinks = False
    Random_Words = False
    Specify_FirstGuess = True
    Loop_All_Words = True
else: # User specifies both the secret word and all guesses
    User_Guesses = True
    User_Thinks = True
    Random_Words = False
    Specify_FirstGuess = False
    Loop_All_Words = False

#------------- READ IN FILE OF WORDS --------------- #
def load_words():
    with open('svn-words.txt') as word_file:
    #with open('words_alpha.txt') as word_file:
    #with open('google-10000-english-no-swears.txt') as word_file:
        valid_words = word_file.read().split()
    return valid_words

#---------- CHECK FOR ANY PUNCTUATION IN A WORD ---------#
def check_punc(word):
    punc = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    for ele in word:
        if ele in punc:
            return False
    return True

# -------------- SELECT A RANDOM WORD FROM LIST ---------------- #
def choose_random_word():
    global ALL_WORDS
    word = random.choice(ALL_WORDS)
    if Debug == True:
        print(f"The secret word is {word}.")
    return word

# --------------- CHOOSE A SPECIFIC WORD FROM A LIST ---- #
def choose_word(x):
    global ALL_WORDS
    word = ALL_WORDS[x]
    return word

# ------------- INITIALIZE EACH GAME BY RESETTING LISTS ----------#
def initialize_game():
    pass

# ---------- GET THE KEY FOR A VALUE ------------- #
def get_key(dict, val):
    for key, value in dict.items():
        if val == value:
            return key
    return "key doesn't exist"

# ------------- INPUT SOLUTION WORD FROM USER-------- #
def user_thinks():
    word = ""
    while len(word) != 5:
        word = input("What word do you want to be the Secret Word?")
    return word

#----------- GET FEEDBACK FROM USER (OR WEBSITE) ------ #
def user_feedback():
    global unfamiliar_symbol
    Feedback_Needed = True
    while Feedback_Needed == True:
        unfamiliar_symbol = False
        feedback = input(f"What is the feedback from you/the website? \n({WRONG_SYMBOL}  if not in word, {CORRECT_SYMBOL} if correct place, {WRONGPLACE_SYMBOL} if wrong place):\n").upper()

        if len(feedback) != 5:
            print("Your feedback should be exactly 5 characters.")
        else:
            for symbol in feedback:
                if symbol not in SYMBOLS:
                    unfamiliar_symbol = True
            if unfamiliar_symbol is True:
                print("Unfamiliar symbol entered.")
            else:
                Feedback_Needed = False
    return feedback

# ----------- GIVE FEEDBACK -------------- #
# This part is a little inelegant, mainly due to how we need to handle duplicated letters in either
#  the guess or the solution word. For this reason, we need to count how many letters we've gotten
#  correct (either "on target", which means in the right position, or "unsure", which means we're
#  not sure where it goes. When the same letter appears more than once in the guess, or the solution,
#  or both, we adjust whether the tile turns gray or yellow depending on how many (if any) of that
#  letter have already been correctly positioned. We loop through the letters twice for this reason, 
#  first making any letters "gray" if they are somewhere in the word but not in the right spot, and
#  then looping through again to adjust this feedback if needed, based on repeated letters having
#  already been correctly or incorrectly placed.
# feedback_list keeps track of the color tiles that will be given as feedback
# ontarget_dict is a dictionary that keeps track of what letters, and how many, have been correctly positioned
# unsure_dict is a dictionary that keeps track of what letters, and how many, have been identified but not correctly placed. We ha

def give_feedback():
    global secretword, bestword, unsure_dict, sdict
    feedback_list = ["_", "_", "_", "_", "_"]
    sdict = {item:secretword.count(item) for item in secretword}
    ontarget_dict = {}
    unsure_dict = {}
    for i in range(5):
        if bestword[i] == secretword[i]:
            feedback_list[i] = CORRECT_SYMBOL
            if bestword[i] in ontarget_dict:
                ontarget_dict[bestword[i]] += 1
            else:
                ontarget_dict[bestword[i]] = 1
        elif bestword[i] not in sdict:
            feedback_list[i] = WRONG_SYMBOL
        else:
            feedback_list[i] = WRONGPLACE_SYMBOL
            if bestword[i] in unsure_dict:
                unsure_dict[bestword[i]] += 1
            else:
                unsure_dict[bestword[i]] = 1

    for i in range(5):
        if feedback_list[i] == WRONGPLACE_SYMBOL:
            try:
                if sdict[bestword[i]] - ontarget_dict[bestword[i]] == 0:
                    feedback_list[i] = WRONG_SYMBOL
                    try:
                        unsure_dict[bestword[i]] -= 1
                        if unsure_dict[bestword[i]] == 0:
                            del(unsure_dict[bestword[i]])
                    except:
                        pass
                elif sdict[bestword[i]] - ontarget_dict[bestword[i]] > 0:
                    if unsure_dict[bestword[i]] > (sdict[bestword[i]] - ontarget_dict[bestword[i]]):
                        feedback_list[i] = WRONG_SYMBOL
                        try:
                            unsure_dict[bestword[i]] -= 1
                            if unsure_dict[bestword[i]] == 0:
                                del(unsure_dict[bestword[i]])
                        except:
                            pass
            except KeyError:
                try:
                    if unsure_dict[bestword[i]] > sdict[bestword[i]]:
                        feedback_list[i] = WRONG_SYMBOL
                        unsure_dict[bestword[i]] -= 1
                except KeyError:
                    pass
    feedback = "".join(feedback_list)
    return feedback

# ---------------- SCORE REMAINING WORDS AND CHOOSE NEXT BEST GUESS--------------#
# This uses "Strategy #1" which is to first create the frequency distribution of all letters that
#   could still be in the solution word, and assign points to each letter equal to the number
#   of words still on the eligible list that contain that letter.  Then, for every eligible word,
#   find the sum of points for the letters in that word (but don't count the same letter more than
#   once).  Rank the words in descending order of points, and the word with the highest points should
#   contain as many of the most frequently-appearing letters as possible.
def guessnewword():
    global guess, guessnum, bestword, wordlist, wordlist2, gameOn, secretword, freq, last_freq
    if guessnum > 0:
        last_freq = freq
        #print(f"Last freq was {freq}")
    freq = {letter: 0 for letter in LETTERS}
    if len(wordlist) == 0:
        gameOn = False
        print(f"You LOST {secretword.upper()} since no more words fit the pattern")
        guessnum = 7
    else:
        for word in wordlist:
             for letter in LETTERS:
                if letter in word:
                    freq[letter] += 1

        #This is not strictly necessary for the algorithm, but produces an elegant little string of the letters in frequency order
        sorted_d = dict(sorted(freq.items(), key = operator.itemgetter(1), reverse=True))
        if Debug == True or gamemode in [1,5]:
            freqchart_list = []
            for key in sorted_d:
                if sorted_d[key] > 0:
                    freqchart_list.append(key.upper())
            freqchart = "".join(freqchart_list)
            print(f"Most frequent letters in remaining words: {freqchart}")

        score_dict = {}
        for word in wordlist:
            wordscore = [freq[item] for item in set(word)]
            score_dict[word] = sum(wordscore)
        #print(f"Wordlist is {wordlist}")
        if guessnum == 1:
            #print(f"This is guess 1, so wordlist2 is {wordlist2}")
            score_dict2 = {}
            for word in wordlist2:
                wordscore = [last_freq[item] for item in set(word)]
                score_dict2[word] = sum(wordscore)
            sorted_d = dict(sorted(score_dict2.items(), key=operator.itemgetter(1), reverse=True))
            #print(score_dict2)

        if HardMode == False and guessnum == 1:
            sorted_d = dict(sorted(score_dict2.items(), key=operator.itemgetter(1), reverse=True))
            #print(f"Sorted_D is {sorted_d}")
            all_scores = score_dict2.values()
        else:
            sorted_d = dict(sorted(score_dict.items(), key=operator.itemgetter(1), reverse=True))
            all_scores = score_dict.values()
        if gamemode not in [3,4]:
            print(f"The computer suggests these words: {sorted_d}")

        try:
            max_score = max(all_scores)
            if User_Guesses == True:
                bestword = input(">>>> What word would you like to guess?").lower()
            else:
                if HardMode is False and guessnum == 1:
                    bestword = get_key(score_dict2, max_score)
                else:
                    bestword = get_key(score_dict, max_score)
            for i in range(1, 6):
                guess[i] = bestword[i - 1]
            guessnum += 1

            if Debug == True or gamemode in [1,2,5]:
                print(f"Guess {guessnum} should be {bestword.upper()}")
        except ValueError:
            gameOn = False

# -------- SPECIFY A WORD TO BE GUESSED (VIA INDEX)------ #
def guess_specific_word(x):
    global bestword, guess, guessnum, freq
    for word in wordlist:
        for letter in LETTERS:
            if letter in word:
                freq[letter] += 1
    bestword = choose_word(x)
    for i in range(1, 6):
        guess[i] = bestword[i - 1]
    guessnum += 1
    if Debug == True:
        print(f"Guess {guessnum} is {bestword.upper()}")

# ------- UPDATE SLOT (DICT OF POSSIBLE LETTERS IN EACH POSITION) AND REQ'D LETTER DICTIONARY BASED ON FEEDBACK ------ #
def update_reqd_slots():
    global slot, required_dict, guess, feedback_dict, unsure_dict
    gy_list = []  #list of green and yellow spaces only (GY)

    # GREEN SPACES
    for k in guess:
        if feedback_dict[k] == CORRECT_SYMBOL:
            slot[k] = [guess[k]]
            gy_list.append(guess[k])

    for k in guess:
        # GRAY SPACES (MAKING SURE TO DEAL WITH REPEATED LETTERS)
        if feedback_dict[k] == WRONG_SYMBOL:
            for i in range(1,6):
                try:
                    if len(slot[i]) > 1 and guess[k] not in unsure_dict:
                        newlist = [item for item in slot[i] if item != guess[k]]
                        slot[i] = newlist
                except ValueError:
                    pass
                except AttributeError:
                    pass
        # YELLOW SPACES (DEALING WITH REPEATED LETTERS)
        elif feedback_dict[k] == WRONGPLACE_SYMBOL:
            newlist = [item for item in slot[k] if item != guess[k]]
            slot[k] = newlist
            gy_list.append(guess[k])

    # Update list of Required letters based on green and yellow spaces
    gy_string = "".join(gy_list)
    gy_set = set(gy_string)
    gy_dict = {item: gy_string.count(item) for item in gy_set}
    for item in gy_dict:
        try:
            if required_dict[item] < gy_dict[item]:
                required_dict[item] = gy_dict[item]
        except:
            required_dict[item] = gy_dict[item]

#-------------- FILTER WORD LIST ------------------------ #
def filter_wordlist():
    global wordlist, wordlist2, slot, required_dict, guess_list, bestword
    if guessnum == 1:
        last_bestword = bestword
        #print(f"The last word was {last_bestword}")

    if guessnum == 1:
        newwordlist = []
        for word in wordlist:
            word_ok = True

            #Check each letter to see if it was guessed in the first word:
            for letter in word:
                if letter in last_bestword:
                    word_ok = False
                    #print(f"{word} is no good")
            if word_ok is True:
                newwordlist.append(word)
                #print(f"{word} is good")
        wordlist2 = newwordlist
        #print(f"Wordlist2 is {wordlist2}")

    newwordlist = []
    for word in wordlist:
        word_ok = True

        #Check each letter to see if it's allowed to be in slot
        for k in range(1,6):
            if word[k-1] not in slot[k]:
                word_ok = False
        #Check Required to remove word if it does not include required letters
        proposed = {letter:word.count(letter) for letter in word}
        for item in required_dict:
            try:
                if required_dict[item] > proposed[item]:
                    word_ok = False
            except KeyError:
                word_ok = False
        if word_ok == True:
            newwordlist.append(word)
    wordlist = newwordlist

    if Debug == True or gamemode in [1,2,5]:
        print(f"After guess {guessnum} the word list has been reduced to a length of {len(wordlist)}.")
    if gamemode in [3,4] and guessnum == 1:
        #print(f"At guess {guessnum} the length of wordlist is {len(wordlist)} and the length of wordlist2 is {len(wordlist2)}")
        if HardMode == True:
            guess_list.append(len(wordlist))
        else:
            guess_list.append(len(wordlist2))

# ------------- START MAIN PROGRAM ------------------------------------------------------------------ #
# ------------- INITIALIZE CONSTANTS AND WORDLIST --- #
WRONG_SYMBOL = "W"
CORRECT_SYMBOL = "R"
WRONGPLACE_SYMBOL = "?"
SYMBOLS = WRONG_SYMBOL + CORRECT_SYMBOL + WRONGPLACE_SYMBOL

if __name__ == '__main__':
    english_words = load_words()

LETTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
ALL_WORDS = [word.lower() for word in english_words if len(word) == 5 and (check_punc(word) == True) and (word == word.lower())]
topword_list = [532,390,528,2256,1208,2276,384,1909,2261,1911,2048,2260,1722,2271,2259,1890,2009,2066,554,1951,984,2239,386,2041,1121,1345,1464,1962,2159,2272,1963,368,1607,2083,370,2282,1836,2039,2165,1205,394,488,967,1039,2078,1562,45,1752,1985,2267,477,1713,114,1974,1601,1949,119,1906,50]

def play_game():
    global guess, guess_list, steps, wordno, clock, gameOn, User_Thinks, Random_Words, Specify_FirstGuess, wordlist, \
        freq, guessnum, slot, feedback_dict, required_dict, unsure_dict, STARTING_GUESSWORD, secretword, bestword
    # Initialize variables for looping, if any

    wordlist = ALL_WORDS
    wordlist2 = []

    required_dict = {}
    unsure_dict = {}
    freq = {letter:0 for letter in LETTERS}
    guessnum = 0

    guess = {1: None,
             2: None,
             3: None,
             4: None,
             5: None
    }
    slot = {1: LETTERS,
            2: LETTERS,
            3: LETTERS,
            4: LETTERS,
            5: LETTERS
    }

    gameOn = True

    #### SELECT THE SECRET WORD  ####
    if gamemode == 1:
        secretword = choose_random_word()
    elif gamemode == 2:
        pass
    elif gamemode == 5:
        secretword = user_thinks()
    else:
        secretword = choose_word(wordno)

    #### SELECT THE FIRST GUESS  ###
    if Specify_FirstGuess == True:
        guess_specific_word(STARTING_GUESSWORD)
    else:
        guessnewword()
    for i in range(1, 6):
        guess[i] = bestword[i - 1]
    #print(guess)

    ### CONTINUE GAME AFTER THE FIRST GUESS ###
    while gameOn == True:
        ### GET FEEDBACK EITHER FROM USER OR COMPUTER
        if gamemode == 2:
            feedback = user_feedback()
        else:
            feedback = give_feedback()

        if gamemode in[1,2,5] or Debug == True:
            print(f"Your feedback is {feedback}")

        ### CHECK TO SEE IF GAME HAS BEEN WON
        if feedback == f"{CORRECT_SYMBOL}{CORRECT_SYMBOL}{CORRECT_SYMBOL}{CORRECT_SYMBOL}{CORRECT_SYMBOL}":
            gameOn = False
            if gamemode == 1:
                print(f"\n####################\nYOU WON THE GAME! It took you {guessnum} guesses.\n####################")
            elif gamemode in [2,5]:
                print(f"\n####################\nCOMPUTER WON THE GAME! It took it {guessnum} guesses.\n####################")
            elif gamemode in [3,4] and guessnum == 1:
                guess_list.append(0)
        else:
            feedback_dict = {i: feedback[i - 1] for i in range(1, 6)}

        if gameOn == True:
            update_reqd_slots()
            filter_wordlist()
            guessnewword()

            for i in range(1, 6):
                guess[i] = bestword[i - 1]

            ### CHECK TO SEE IF GAME HAS BEEN LOST
            if guessnum >= 7:
                gameOn = False

# ----------- FINALLY ACTUALLY PLAY THE GAME NOW, BASED ON MODE SELECTED ------------------- #
if gamemode in [1,2,5]:
    playagain = "y"
    while playagain == "y":
        play_game()
        playagain = input("Play again (y/n)?")

elif gamemode in [3,4]:
    wordno = 0
    steps = ''
    guess_list = []
    guesses_to_win = {}
    words_remaining = {}

    if gamemode == 3:
        STARTING_GUESSWORD = ALL_WORDS.index(input("What would you like the Starting Word to be?").lower())
        print(f"STARTING_GUESSWORD is {STARTING_GUESSWORD}.")
        while wordno < len(ALL_WORDS):
            play_game()
            print(f"Trying to guess the word {ALL_WORDS[wordno].upper()}.... Got it in {guessnum} guesses!")
            wordno += 1
            steps += str(guessnum)
            #print(steps)
            p1 = steps.count('1') / (wordno + 1) * 100
            p2 = steps.count('2') / (wordno + 1) * 100
            p3 = steps.count('3') / (wordno + 1) * 100
            p4 = steps.count('4') / (wordno + 1) * 100
            p5 = steps.count('5') / (wordno + 1) * 100
            p6 = steps.count('6') / (wordno + 1) * 100
            p7 = (100 - (p1 + p2 + p3 + p4 + p5 + p6))

            guesses_to_win[ALL_WORDS[STARTING_GUESSWORD]] = {"p1": p1,
                                                          "p2": p2,
                                                          "p3": p3,
                                                          "p4": p4,
                                                          "p5": p5,
                                                          "p6": p6,
                                                          "p7": p7,
                                                          }
            words_remaining[ALL_WORDS[STARTING_GUESSWORD]] = guess_list

    if gamemode == 4:
        #bottomword_list = [1642, 1390, 2362, 357, 1133, 892, 267, 1177, 1286, 1656, 1127]
        #for STARTING_GUESSWORD in range(len(ALL_WORDS)):
        #for STARTING_GUESSWORD in range(500,900):
        for STARTING_GUESSWORD in topword_list[0:5]:
        # for STARTING_GUESSWORD in bottomword_list:
            print(f"Starting guessword is now {STARTING_GUESSWORD}: {ALL_WORDS[STARTING_GUESSWORD].upper()}")
            wordno = 0
            steps = ''
            guess_list = []
            while wordno < len(ALL_WORDS) - 1:
                play_game()
                print(f"Trying to guess the word {ALL_WORDS[wordno].upper()}.... Got it in {guessnum} guesses!")
                wordno += 1
                steps += str(guessnum)
                p1 = steps.count('1') / (wordno + 1) * 100
                p2 = steps.count('2') / (wordno + 1) * 100
                p3 = steps.count('3') / (wordno + 1) * 100
                p4 = steps.count('4') / (wordno + 1) * 100
                p5 = steps.count('5') / (wordno + 1) * 100
                p6 = steps.count('6') / (wordno + 1) * 100
                p7 = (100 - (p1 + p2 + p3 + p4 + p5 + p6))

                guesses_to_win[ALL_WORDS[STARTING_GUESSWORD]] = {"p1": p1,
                                                                 "p2": p2,
                                                                 "p3": p3,
                                                                 "p4": p4,
                                                                 "p5": p5,
                                                                 "p6": p6,
                                                                 "p7": p7,
                                                                 }
                words_remaining[ALL_WORDS[STARTING_GUESSWORD]] = guess_list

    print(guesses_to_win)
    print(words_remaining)
    outdata1 = pandas.DataFrame.from_dict(guesses_to_win, orient='index')
    outdata2 = pandas.DataFrame.from_dict(words_remaining, orient='index')
    outdata1.to_csv("guesses_to_win.csv")
    outdata2.to_csv("words_remaining.csv")
