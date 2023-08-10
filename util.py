from pokedex import pokedex
import requests

class PokedexHelper(pokedex.Pokedex):
    def make_request(self, path):
        res = requests.get(path, headers=self.headers)
        if res.ok or res.status_code == 404:
            return (res.status_code, res.json())
        else:
            return (res.raise_for_status())
