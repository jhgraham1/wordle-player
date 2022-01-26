# wordle-player
This is a project I started to measure the effectiveness of different starting words in Wordle.  It gives the user the option to choose among 5 game modes (1, 2, or 5 are more "playable" versions, 3 and 4 are the ones I used to run simulation loops).  For modes where the computer is guessing words, it also gives the option to apply the Hard mode restriction.

The code is pretty well-commented throughout, I think.  There are a lot of functions defined up front. The general schema is:

1--Initialize all variables
2--Establish what the solution (secret) word will be
3--Establish what the first guess word will be
4--Generate the string of feedback for the 5 letters guessed
5--Use that feedback to update the lists of letters that could be in each slot 1-5, and letters that need to be in the word somewhere
6--Use those requirements to filter down the list of remaining possible solution words
7--Choose the best word from that list
8--Guess again, and repeat til the game is won or lost

The most complicated sections of code are in steps 5 and 6 because of how repeated letters need to be accounted for -- it is not enough to make one pass through the 5 guessed letters; multiple passes are needed.  Otherwise everything should be pretty straightforward.

I have been programming a long time but Python is not my first language, so I realize that there are some aspects of dictionary comprehension and dealing with strings vs. lists vs. dictionaries that I probably did not program as elegantly as possible.

Thanks for reading, and while I infrequently use Twitter, I can be reached there at @j0v1wan

-JG
