PREFIXES = ['blä', 'krü', 'snö', 'trä', 'flö']
SUFFIXES = ['ön', 'üd', 'bär', 'ska', 'nå']

def maybe_add_morphemes(base, rng, chance=0.5):
    parts = []
    if rng.random() < chance:
        parts.append(rng.choice(PREFIXES))
    parts.append(base.lower()) 
    if rng.random() < chance:
        parts.append(rng.choice(SUFFIXES))
    
    full_name = ''.join(parts)
    return full_name.capitalize()
