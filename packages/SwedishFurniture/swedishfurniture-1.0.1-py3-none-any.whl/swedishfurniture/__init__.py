import random
from patterns import VOWELS, CONSONANTS

class SwedishNameGenerator:
    def __init__(self, 
                 seed=None, 
                 pattern=None, 
                 morpheme_chance=0.5,
                 vowels=None,
                 consonants=None):
        self.rng = random.Random(seed) if seed is not None else random.Random()
        self.pattern = pattern
        self.morpheme_chance = morpheme_chance
        self.vowels = vowels or VOWELS
        self.consonants = consonants or CONSONANTS
