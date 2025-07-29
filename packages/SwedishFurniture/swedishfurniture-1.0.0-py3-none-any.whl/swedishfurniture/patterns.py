VOWELS = 'AÅÄOÖUÜEIY'
CONSONANTS = 'BCDFGHJKLMNPRSTVXZ'
DEFAULT_PATTERNS = ["CV",
                    "CVC",
                    "CVV",
                    "VC",
                    "VCV",
                    "CCV",
                    "CVCV",
                    "CVCC",
                    "VCC",
                    "CVVC",
                    "CCVC",
                    "CVCCC",
                    "CCVCC",
                    "VCVCC",
                    "CVCVC",
                    "CVCCV",
                    "CCVCV",
                    "CVCCVC",
                    "CVCVCC",
                    "VCCVC",
                    "CCVCCC",
                    "CVVCC",
                    "VVC",
                    "VVCV", 
                    "CVVCV",
]

def generate_from_pattern(pattern, rng, vowels, consonants):
    pattern = pattern or rng.choice(DEFAULT_PATTERNS)
    result = ''
    for char in pattern:
        if char == 'C':
            result += rng.choice(consonants)
        elif char == 'V':
            result += rng.choice(vowels)
        else:
            result += char
    return result.capitalize()
