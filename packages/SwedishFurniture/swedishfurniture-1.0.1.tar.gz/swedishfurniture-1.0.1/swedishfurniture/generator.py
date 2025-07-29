from patterns import generate_from_pattern
from morphemes import maybe_add_morphemes
from data import generate_item_data
from utils import is_pronounceable
from patterns import VOWELS, CONSONANTS
import random

class SwedishNameGenerator:
    def __init__(self, seed=None, pattern=None, vowels=None, consonants=None, morpheme_chance=0.5):
        self.rng = random.Random(seed)
        self.pattern = pattern
        self.morpheme_chance = morpheme_chance
        self.vowels = vowels or VOWELS
        self.consonants = consonants or CONSONANTS

    def generate_name(self):
        for _ in range(10):
            base = generate_from_pattern(self.pattern, self.rng, self.vowels, self.consonants)
            full = maybe_add_morphemes(base, self.rng, self.morpheme_chance)
            if is_pronounceable(full):
                return full
        return base

    def generate_full_entry(self):
        name = self.generate_name()
        return generate_item_data(name, self.rng)
