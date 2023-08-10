from decouple import config
import requests
import telebot
from util import PokedexHelper

BOT_TOKEN = config('TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)
pokedex = PokedexHelper(version='v1', user_agent='ExampleApp (https://example.com, v2.0.1)')

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Hello! I'm Pokémon bot. Type /pokemon <pokémon_name> to get information about a Pokémon.")

@bot.message_handler(commands=['pokemon'])
def get_pokemon_info(message):
    args = message.text.split(maxsplit=1)
    if len(args) == 2:
        pokemon_name = args[1].lower()
        try:
            response = pokedex.get_pokemon_by_name(pokemon_name)

            if response[0] == 200:
                print(response)
                data = response[1][0]
                if "name" in data and "sprite" in data:
                    bot.send_photo(message.chat.id, data['sprite'], caption=f"Name: {data['name'].capitalize()}\nType: {', '.join(data['types'])}\nEntry: {data['number']}\nGeneration: {data['gen']}\nSpecies: {data['species']}\nDescription: {data['description']}")
                else:
                    bot.reply_to(message, "Pokémon not found.")
            else:
                bot.reply_to(message, "Failed to fetch Pokémon information.")
        except Exception as e:
            print(e)
            bot.reply_to(message, "An error occurred.")
    else:
        bot.rep


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, "I don't understand that command. Type /start to see available commands.")

# Run the bot
if __name__ == '__main__':
    bot.polling()