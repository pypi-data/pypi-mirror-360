"""Games of probability (Vietnamese: Trò chơi xác suất)

This module provides some games of chance and things that based on probability, using the `random` module.
There are also data types for each type of game.

This module could be imported as `gop` or `tcxs`.

Classes: `Coin`, `FiftyTwoCardPack`, `Dice`, `UnoPack`, `Revolver`.

Functions: `flip_the_coin()`, `shuffle_pack()`, `shuffle_reveal_pack()`, `roll_the_dice()`, `roll_the_dice()`, `shuffle_uno_pack()`,
`shuffle_reveal_uno_pack()`, `russian_roulette()`, `russian_roulette_reveal()`."""

# Functions and classes are sorted by time created

import random

class Coin:
    """A coin. Appears in `flip_the_coin()` function. Does not have any parameter"""
    def __str__(self): return random.choice(['heads', 'tails'])

class FiftyTwoCardPack:
    """A Standard 52-card pack. Appears in `shuffle_pack()` and `shuffle_reveal_pack()` functions. Parameters:
    - `shuffle_times` — the number of times the pack will be shuffled
    - `reveal` — if True, the pack will be revealed; `drawn_card` will be disabled
    - `drawn_card` — the card which will be returned, it will also be removed from the pack;
    `drawn_card = 0` will return the top card, `drawn_card = -1` will return the bottom card"""
    def __init__(self, shuffle_times, reveal, drawn_card):
        if shuffle_times < 0: raise ValueError("'shuffle_times' parameter must not have a negative value")
        self.shuffle_times = shuffle_times
        self.reveal = bool(reveal)
        self.drawn_card = int(drawn_card)
    def __str__(self): 
        self.pack = ['A♠','2♠','3♠','4♠','5♠','6♠','7♠','8♠','9♠','10♠','J♠','Q♠','K♠',
                     'A♣','2♣','3♣','4♣','5♣','6♣','7♣','8♣','9♣','10♣','J♣','Q♣','K♣',
                     'A♦','2♦','3♦','4♦','5♦','6♦','7♦','8♦','9♦','10♦','J♦','Q♦','K♦',
                     'A♥','2♥','3♥','4♥','5♥','6♥','7♥','8♥','9♥','10♥','J♥','Q♥','K♥']
        self.shuffled_times = 0
        while self.shuffled_times < self.shuffle_times:
            random.shuffle(self.pack)
            self.shuffled_times += 1
        if self.reveal == True: return f'{self.pack}'
        else: return self.pack.pop(self.drawn_card)

class Dice:
    """(A) regular dice. Appears in `roll_the_dice()` function. Parameters:
    - `number_of_dice` — the number of dice that will be used
    - `add_all_results` — if True, the sum of all results will be returned;
    otherwise, the list of all results will be returned instead"""
    def __init__(self, number_of_dice, add_all_results):
        if number_of_dice < 0: raise ValueError("'number_of_dice' parameter must not have a negative value")
        self.number_of_dice = int(number_of_dice)
        self.add_all_results = bool(add_all_results)
    def __str__(self):
        if self.add_all_results == True: self.final_result = 0
        else: self.final_result = []
        self.dice_used = 0
        while self.dice_used < self.number_of_dice:
            self.result = random.choice([1, 2, 3, 4, 5, 6])
            if self.add_all_results == True: self.final_result += self.result
            else: self.final_result.append(self.result)
            self.dice_used += 1
        return f'{self.final_result}'

class UnoPack:
    """An UNO pack. Appears in `shuffle_uno_pack()` and `shuffle_reveal_uno_pack()` functions.
    Shares similar parameters with `FiftyTwoCardPack` class.
    The order of the cards is based on https://commons.wikimedia.org/wiki/File:UNO_cards_deck.svg"""
    def __init__(self, shuffle_times, reveal, drawn_card):
        if shuffle_times < 0: raise ValueError("'shuffle_times' parameter must not have a negative value")
        self.shuffle_times = shuffle_times
        self.reveal = bool(reveal)
        self.drawn_card = int(drawn_card)
    def __str__(self): 
        self.pack = ['Red 0','Red 1','Red 2','Red 3','Red 4','Red 5','Red 6','Red 7','Red 8','Red 9','Red Skip','Red Reverse',
                         'Red Draw 2','Wild',
                     'Yellow 0','Yellow 1','Yellow 2','Yellow 3','Yellow 4','Yellow 5','Yellow 6','Yellow 7','Yellow 8','Yellow 9',
                         'Yellow Skip','Yellow Reverse','Yellow Draw 2','Wild',
                     'Green 0','Green 1','Green 2','Green 3','Green 4','Green 5','Green 6','Green 7','Green 8','Green 9','Green Skip',
                         'Green Reverse','Green Draw 2','Wild',
                     'Blue 0','Blue 1','Blue 2','Blue 3','Blue 4','Blue 5','Blue 6','Blue 7','Blue 8','Blue 9','Blue Skip',
                         'Blue Reverse','Blue Draw 2','Wild',
                     'Red 1','Red 2','Red 3','Red 4','Red 5','Red 6','Red 7','Red 8','Red 9','Red Skip','Red Reverse','Red Draw 2',
                         'Wild Draw 4',
                     'Yellow 1','Yellow 2','Yellow 3','Yellow 4','Yellow 5','Yellow 6','Yellow 7','Yellow 8','Yellow 9','Yellow Skip',
                         'Yellow Reverse','Yellow Draw 2','Wild Draw 4',
                     'Green 1','Green 2','Green 3','Green 4','Green 5','Green 6','Green 7','Green 8','Green 9','Green Skip',
                         'Green Reverse','Green Draw 2','Wild Draw 4',
                     'Blue 1','Blue 2','Blue 3','Blue 4','Blue 5','Blue 6','Blue 7','Blue 8','Blue 9','Blue Skip','Blue Reverse',
                         'Blue Draw 2','Wild Draw 4']
        # The order is based on https://commons.wikimedia.org/wiki/File:UNO_cards_deck.svg
        self.shuffled_times = 0
        while self.shuffled_times < self.shuffle_times:
            random.shuffle(self.pack)
            self.shuffled_times += 1
        if self.reveal == True: return f'{self.pack}'
        else: return self.pack.pop(self.drawn_card)

class Revolver:
    """THESE ARE JUST GAMES OF CHANCE. I DO NOT SUPPORT VIOLENCE.

    A revolver has a cylinder contains 7 chambers.
    Appears in `russian_roulette()` and `russian_roulette_reveal()` function. Parameters:
    - `rotate_times` — the number of times the cylinder will be rotated
    - `reveal` — if True, all the chambers of the cylinder will be revealed"""
    def __init__(self, rotate_times, reveal):
        if rotate_times < 0: raise ValueError("'shuffle_times' parameter must not have a negative value")
        self.rotate_times = rotate_times
        self.reveal = bool(reveal)
    def __str__(self):
        self.cylinder = ['Empty', 'Empty', 'Empty', 'Empty', 'Empty', 'Empty', 'Empty']
        self.cylinder[random.choice([0, 1, 2, 3, 4, 5])] = 'Cartridge'
        self.rotated_times = 0
        while self.rotated_times < self.rotate_times:
            self.cylinder.insert(0, self.cylinder.pop())
            self.rotated_times += 1
        if self.reveal == True: return f'{self.cylinder}'
        else: return self.cylinder[0]
            
def flip_the_coin():
    """Flips the coin, and return either 'heads' or 'tails'."""
    return Coin()

def shuffle_pack(shuffle_times, drawn_card):
    """Shuffles the 52-card pack a number of times based on the `shuffle_times` parameter,
    and return a card based on the `drawn_card` parameter. The returned card will also be removed from the pack.
    `drawn_card = 0` will return the top card, `drawn_card = -1` will return the bottom card."""
    return FiftyTwoCardPack(shuffle_times, False, drawn_card)

def shuffle_reveal_pack(shuffle_times):
    """Shuffles the 52-card pack a number of times based on the `shuffle_times` parameter, and return the ordered list of all cards."""
    return FiftyTwoCardPack(shuffle_times, True, 0)

def roll_the_dice(number_of_dice, add_all_results):
    """Rolls the dice, the number of dice is based on the `number_of_dice` parameter,
    and return the result which can be the list or the sum of all the results based on the `add_all_results` parameter."""
    return Dice(number_of_dice, add_all_results)

def shuffle_uno_pack(shuffle_times, drawn_card):
    """Shuffles the UNO pack a number of times based on the `shuffle_times` parameter,
    and return a card based on the `drawn_card` parameter. The returned card will also be removed from the pack.
    `drawn_card = 0` will return the top card, `drawn_card = -1` will return the bottom card."""
    return UnoPack(shuffle_times, False, drawn_card)

def shuffle_reveal_uno_pack(shuffle_times):
    """Shuffles the UNO pack a number of times based on the `shuffle_times` parameter, and return the ordered list of all cards."""
    return UnoPack(shuffle_times, True, 0)

def russian_roulette(rotate_times):
    """THESE ARE JUST GAMES OF CHANCE. I DO NOT SUPPORT VIOLENCE.
    
    Places a single cartridge in the revolver, spins the cylinder,
    rotates it a number of times based on the `rotate_times` parameter, and return what is inside the current (first) chamber,
    which can be either 'Empty' or 'Cartridge'."""
    return Revolver(rotate_times, False)

def russian_roulette_reveal(rotate_times):
    """THESE ARE JUST GAMES OF CHANCE. I DO NOT SUPPORT VIOLENCE.
    
    Places a single cartridge in the revolver, spins the cylinder,
    rotates it a number of times based on the `rotate_times` parameter, and return the ordered list of all chambers."""
    return Revolver(rotate_times, True)