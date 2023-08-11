from .base import BASE_URL


def get_pokemon_details(pokemon_name):
    api_url = f"{BASE_URL}{pokemon_name}/"

    try:
        response = requests.get(api_url)
        return response.json() if response.status_code == 200 else None
    except Exception:
        return None


def get_pokemon_species(pokemon_species_url):
    try:
        response = requests.get(pokemon_species_url)
        return response.json() if response.status_code == 200 else None
    except Exception:
        return None


def get_pokemon_image_url(pokemon_name):
    response = requests.get(f"{BASE_URL}{pokemon_name}/")
    if response.status_code != 200:
        return None
    data = response.json()
    return data["sprites"]["front_default"]
