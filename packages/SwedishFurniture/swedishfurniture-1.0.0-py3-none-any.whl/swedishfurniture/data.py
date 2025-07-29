import datetime

ITEM_TYPES = [
    'Shelf', 'Hook', 'Dog Brush', 'Nightstand',
    'Holder', 'Stand', 'Chair', 'Cushion'
]

def generate_item_data(name, rng):
    item_type = rng.choice(ITEM_TYPES)
    date = datetime.date(
        rng.randint(2000, 2025), 
        rng.randint(1, 12), 
        rng.randint(1, 28)
    ).isoformat()
    weight = round(rng.uniform(0.1, 25.0), 1)
    dims = f"{rng.randint(10, 120)}×{rng.randint(10, 80)}×{rng.randint(5, 60)} см"

    return {
        'name': name,
        'type': item_type,
        'introduced': date,
        'weight_kg': weight,
        'dimensions': dims
    }
