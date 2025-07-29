from patterns import CONSONANTS

def is_pronounceable(name):
    count = 0
    for c in name.upper():
        if c in CONSONANTS:
            count += 1
            if count > 3:
                return False
        else:
            count = 0
    return True
