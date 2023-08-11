from datetime import datetime, timedelta
import traceback
import pytz
import telebot
from telebot import types
import pymongo
from utils.base import (
    SPOTLIGHT_TIME,
    COORDS_DATA,
    COMMUNITY_DAY_TIME,
    MONGODB_URI,
    BOT_TOKEN,
)
from utils.helper import (
    get_pokemon_details,
    get_pokemon_species,
    get_pokemon_image_url,
    get_coords
)

bot = telebot.TeleBot(BOT_TOKEN)

# Connect to MongoDB Atlas
client = pymongo.MongoClient(MONGODB_URI)
db = client["pokedex"]
collection = db["pokemons"]


@bot.message_handler(commands=["start"])
def start_message(message):
    bot.reply_to(
        message, "Hello! I'm Pokémon bot. Type /help to see all the commands. 🎮"
    )


@bot.message_handler(commands=["help"])
def send_welcome(message):
    commands_text = (
        "Available commands:\n"
        "/help - Show available commands 📋\n"
        "/pokemon <pokemon_name> - Get details about a Pokémon 🐾\n"
        # "/moveset <pokemon_name> - Get moveset details of a Pokémon 🎯\n"
        "/stats <pokemon_name> - Get detailed stats of a Pokémon 📊\n"
        "/top10_little - Get the top 10 rank Pokémon for Little League with their stats 🏆\n"
        "/top10_gl - Get the top 10 rank Pokémon for Great League with their stats 🏆\n"
        "/top10_ul - Get the top 10 rank Pokémon for Ultra League with their stats 🏆\n"
        "/top10_ml - Get the top 10 rank Pokémon for Master League with their stats 🏆\n"
        "/coords <city_name> - Get coordinates of various cities around the world 🌍\n"
        "/current_spotlight_hour - Show cities and coordinates for the current spotlight hour 🕒\n"
        "/current_community_day - Show cities and coordinates for the current Community Day event 🌟"
    )

    bot.reply_to(message, commands_text)


@bot.message_handler(commands=["pokemon", "Pokemon"])
def pokedex_command(message):
    try:
        _, pokemon_name = message.text.split(" ", 1)
        searching_message = bot.send_message(
            message.chat.id, "Searching for Pokémon details... 🔍"
        )

        if pokemon_data := get_pokemon_details(pokemon_name.lower()):
            image_url = pokemon_data["sprites"]["front_default"]
            species_url = pokemon_data["species"]["url"]
            if species_data := get_pokemon_species(species_url):
                generation = species_data["generation"]["name"]
                poke_id = pokemon_data["id"]
                abilities = ", ".join(
                    [
                        ability["ability"]["name"]
                        for ability in pokemon_data["abilities"]
                    ]
                )
                pokemon_types = ", ".join(
                    [poke_type["type"]["name"] for poke_type in pokemon_data["types"]]
                )

                details = (
                    f"🔍 Name: {pokemon_name.capitalize()}\n"
                    f"📜 Pokédex Entry: {poke_id}\n"
                    f"🌍 Generation: {generation}\n"
                    f"📏 Height: {pokemon_data['height']} dm\n"
                    f"⚖️ Weight: {pokemon_data['weight']} hg\n"
                    f"🛡️ Abilities: {abilities}\n"
                    f"🔥 Types: {pokemon_types}"
                )

                bot.send_photo(message.chat.id, image_url, caption=details)
                bot.delete_message(message.chat.id, searching_message.message_id)
            else:
                bot.edit_message_text(
                    "Failed to fetch Pokémon details.",
                    message.chat.id,
                    searching_message.message_id,
                )
        else:
            bot.edit_message_text(
                "Pokémon not found.", message.chat.id, searching_message.message_id
            )
    except ValueError:
        bot.reply_to(message, "Invalid command format. Use /pokemon <pokemon_name>.")


@bot.message_handler(commands=["moveset"])
def moveset_command(message):
    try:
        _, pokemon_name = message.text.split(" ", 1)
        searching_message = bot.send_message(
            message.chat.id, "Searching for Pokémon moveset details... 🔍"
        )

        if pokemon_data := get_pokemon_details(pokemon_name):
            image_url = pokemon_data["sprites"]["front_default"]
            moves_url = pokemon_data["moves"]

            if moveset := [
                move_data["move"]["name"] for move_data in moves_url
            ]:
                top_moveset = ", ".join(moveset[:5])
                moveset_count = len(moveset)

                keyboard = types.InlineKeyboardMarkup()
                show_another_button = types.InlineKeyboardButton(
                    "Show Another 5", callback_data=f"show_another_{pokemon_name}_5"
                )
                show_all_button = types.InlineKeyboardButton(
                    "Show All", callback_data=f"show_all_{pokemon_name}"
                )
                keyboard.add(show_another_button, show_all_button)

                bot.send_photo(
                    message.chat.id,
                    image_url,
                    caption=f"Top 5 Moves: {top_moveset}\nTotal Moves: {moveset_count}",
                    reply_markup=keyboard,
                )
                bot.delete_message(message.chat.id, searching_message.message_id)
            else:
                bot.edit_message_text(
                    "No moveset details available.",
                    message.chat.id,
                    searching_message.message_id,
                )
        else:
            bot.edit_message_text(
                "Pokémon not found.", message.chat.id, searching_message.message_id
            )
    except ValueError:
        bot.reply_to(message, "Invalid command format. Use /moveset <pokemon_name>.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("show_another_"))
def show_another_moveset(call):
    pokemon_name = call.data.split("_")[-2]
    prev_count = int(call.data.split("_")[-1])
    pokemon_data = get_pokemon_details(pokemon_name)
    moves_url = pokemon_data["moves"]
    moveset = [move_data["move"]["name"] for move_data in moves_url]
    try:
        current_moves = call.message.caption.split("\n")[0].split(":")[-1]
    except:
        current_moves = call.message.text
    moves_to_show = 5
    next_moves = moveset[prev_count : prev_count + moves_to_show]

    if next_moves:
        new_position = prev_count + moves_to_show
        if new_position >= len(moveset):
            bot.answer_callback_query(call.id, text="No more moves to show.")
            return

        keyboard = types.InlineKeyboardMarkup()
        show_another_button = types.InlineKeyboardButton(
            "Show Another 5",
            callback_data=f"show_another_{pokemon_name}_{prev_count+moves_to_show}",
        )
        show_all_button = types.InlineKeyboardButton(
            "Show All", callback_data=f"show_all_{pokemon_name}"
        )
        keyboard.add(show_another_button, show_all_button)

        bot.send_message(
            call.message.chat.id, ", ".join(next_moves), reply_markup=keyboard
        )
    else:
        bot.answer_callback_query(call.id, text="No more moves to show.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("show_all_"))
def show_all_moveset(call):
    pokemon_name = call.data[len("show_all_") :]

    pokemon_data = get_pokemon_details(pokemon_name)
    if pokemon_data:
        moves_url = pokemon_data["moves"]
        moveset = [move_data["move"]["name"] for move_data in moves_url]

        if moveset:
            all_moveset = ", ".join(moveset)
            bot.send_message(call.message.chat.id, f"All Moves: {all_moveset}")
        else:
            bot.send_message(call.message.chat.id, "No moveset details available.")


@bot.message_handler(commands=["stats"])
def stats_command(message):
    try:
        pokemon_name = message.text.split(" ", 1)[1].strip().lower()
        searching_message = bot.send_message(
            message.chat.id, "Searching for Pokémon stats... 🔍"
        )
        # Query the collection for the requested Pokémon
        pokemon = collection.find_one({"speciesId": pokemon_name})

        if pokemon:
            # Extract and format relevant data
            info_text = f"🔍 Name: {pokemon['speciesName']}\n"
            info_text += f"📜 Pokédex Entry: {pokemon['dex']}\n"
            info_text += f"🔥 Types: {', '.join(pokemon['types'])}\n"
            info_text += f"⚔️ Base Stats: ATK {pokemon['baseStats']['atk']}, DEF {pokemon['baseStats']['def']}, HP {pokemon['baseStats']['hp']}\n"

            # IV stats
            iv_500 = pokemon["defaultIVs"]["cp500"]
            iv_1500 = pokemon["defaultIVs"]["cp1500"]
            iv_2500 = pokemon["defaultIVs"]["cp2500"]
            iv_500_text = f"🎮 IV Stats (500 CP): LVL {iv_500[0]}, {iv_500[1]}/{iv_500[2]}/{iv_500[3]}\n"
            iv_1500_text = f"🎮 IV Stats (1500 CP): LVL {iv_1500[0]}, {iv_1500[1]}/{iv_1500[2]}/{iv_1500[3]}\n"
            iv_2500_text = f"🎮 IV Stats (2500 CP): LVL {iv_2500[0]}, {iv_2500[1]}/{iv_2500[2]}/{iv_2500[3]}\n"

            if pokemon["released"] is False:
                info_text += "❗️ This Pokémon hasn't been released yet in Pokémon GO!\n"

            # Fetch Pokémon image URL from PokeAPI v2
            image_url = get_pokemon_image_url(pokemon["dex"])

            # Send image, text, and entry
            bot.send_photo(
                message.chat.id,
                image_url,
                caption=info_text + iv_500_text + iv_1500_text + iv_2500_text,
            )
            bot.delete_message(message.chat.id, searching_message.message_id)
        else:
            bot.reply_to(message, "❌ Pokémon not found.")
            bot.delete_message(message.chat.id, searching_message.message_id)
    except IndexError:
        bot.reply_to(message, "❗️ Please provide a Pokémon name after the command.")


@bot.message_handler(commands=["top10_500", "top10_little"])
def top10_command(message):
    try:
        top_pokemons = (
            collection.find({"rank_500": {"$exists": True}})
            .sort("rank_500", pymongo.ASCENDING)
            .limit(10)
        )

        if top_pokemons:
            response = "Top 10 Ranked Pokémon in Little Cup (CP 500):\n"
            for idx, pokemon in enumerate(top_pokemons, start=1):
                stats_500 = pokemon["defaultIVs"]["cp500"]
                stats_text = (
                    f"LV: {stats_500[0]} ({stats_500[1]}/{stats_500[2]}/{stats_500[3]})"
                )
                response += f"{idx}. {pokemon['speciesName']} {stats_text}\n"

            bot.reply_to(message, response)
        else:
            bot.reply_to(message, "No ranked Pokémon found.")
    except Exception:
        bot.reply_to(message, "An error occurred while fetching top 10 ranked Pokémon.")


@bot.message_handler(commands=["top10_1500", "top10_gl"])
def top10_command(message):
    try:
        if top_pokemons := (
            collection.find({"rank_1500": {"$exists": True}})
            .sort("rank_1500", pymongo.ASCENDING)
            .limit(10)
        ):
            response = "Top 10 Ranked Pokémon in Great League (CP 1500):\n"
            for idx, pokemon in enumerate(top_pokemons, start=1):
                stats_1500 = pokemon["defaultIVs"]["cp1500"]
                stats_text = f"LV: {stats_1500[0]} ({stats_1500[1]}/{stats_1500[2]}/{stats_1500[3]})"
                response += f"{idx}. {pokemon['speciesName']} {stats_text}\n"

            bot.reply_to(message, response)
        else:
            bot.reply_to(message, "No ranked Pokémon found.")
    except Exception:
        bot.reply_to(message, "An error occurred while fetching top 10 ranked Pokémon.")


@bot.message_handler(commands=["top10_2500", "top10_ul"])
def top10_command(message):
    try:
        if top_pokemons := (
            collection.find({"rank_2500": {"$exists": True}})
            .sort("rank_2500", pymongo.ASCENDING)
            .limit(10)
        ):
            response = "Top 10 Ranked Pokémon in Ultra League (CP 2500):\n"
            for idx, pokemon in enumerate(top_pokemons, start=1):
                stats_2500 = pokemon["defaultIVs"]["cp2500"]
                stats_text = f"LV: {stats_2500[0]} ({stats_2500[1]}/{stats_2500[2]}/{stats_2500[3]})"
                response += f"{idx}. {pokemon['speciesName']} {stats_text}\n"

            bot.reply_to(message, response)
        else:
            bot.reply_to(message, "No ranked Pokémon found.")
    except Exception:
        bot.reply_to(message, "An error occurred while fetching top 10 ranked Pokémon.")


@bot.message_handler(commands=["top10_10000", "top10_ml"])
def top10_command(message):
    try:
        if top_pokemons := (
            collection.find({"rank_10000": {"$exists": True}})
            .sort("rank_10000", pymongo.ASCENDING)
            .limit(10)
        ):
            response = "Top 10 Ranked Pokémon in Master League (CP 10000):\n"
            stats_text = "LV: 50 (15/15/15)"
            for idx, pokemon in enumerate(top_pokemons, start=1):
                response += f"{idx}. {pokemon['speciesName']} {stats_text}\n"

            bot.reply_to(message, response)
        else:
            bot.reply_to(message, "No ranked Pokémon found.")
    except Exception:
        bot.reply_to(message, "An error occurred while fetching top 10 ranked Pokémon.")


@bot.message_handler(commands=["rank"])
def pokemon_rank_command(message):
    try:
        _, pokemon_name = message.text.split(" ", 1)
        if pokemon := collection.find_one({"speciesId": pokemon_name}):
            rank = pokemon.get("rank", "Not Ranked")
            cp500 = pokemon["defaultIVs"]["cp500"]

            response = (
                f"Rank of Pokémon {pokemon_name.capitalize()}: {rank}\n"
                f"Perfect Stats for Rank {rank} (500 CP): ATK {cp500[1]}, DEF {cp500[2]}, STA {cp500[3]}"
            )

            bot.reply_to(message, response)
        else:
            bot.reply_to(message, "Pokémon not found.")
    except ValueError:
        bot.reply_to(message, "Invalid command format. Use /rank <pokemon_name>.")


@bot.message_handler(commands=["coords"])
def coords_command(message):
    try:
        city_name = message.text.split(" ", 1)[1].strip().title()

        coords_text = f"Coordinates of {city_name}:\n```{get_coords(city_name)}```"
        bot.reply_to(message, coords_text, parse_mode="MarkdownV2")
    except IndexError:
        bot.reply_to(message, "Please provide a city name after the command.")


@bot.message_handler(commands=["current_spotlight_hour"])
def current_spotlight_hour_command(message):
    try:
        # Get the current time in India
        india_timezone = pytz.timezone("Asia/Kolkata")
        current_time_in_india = datetime.now(india_timezone)

        # Calculate the end time as current time + 1 hour

        response_text = (
            "Current Spotlight Hour Times\(the time is based upon IST\):\n\n"
        )

        # Iterate through the cities and their times
        counter = 0
        for city, city_time in SPOTLIGHT_TIME.items():
            # Convert city time to datetime
            city_timezone = pytz.timezone(
                "Asia/Kolkata"
            )  # Assuming all city times are in IST
            city_time = datetime.strptime(city_time, "%I:%M %p").time()

            # Calculate the current city time
            current_city_time = datetime.combine(datetime.now(), city_time)
            current_city_time = city_timezone.localize(current_city_time)
            end_time = current_city_time + timedelta(hours=1)
            # Check if the current city time is within the desired range
            if current_city_time <= current_time_in_india <= end_time:
                counter += 1
                coordinates = COORDS_DATA.get(city, "N/A")
                time_left = end_time - current_time_in_india
                response_text += f"{counter}\. {city}: ```{coordinates}``` \- {str(time_left).split(':')[0]}hrs {str(time_left).split(':')[1]}mins Left\n\n"

        bot.reply_to(message, response_text, parse_mode="MarkdownV2")

    except Exception:
        bot.reply_to(message, "An error occurred while fetching the current time.")


@bot.message_handler(commands=["current_community_day"])
def current_community_day_command(message):
    try:
        # Get the current time in India
        india_timezone = pytz.timezone("Asia/Kolkata")
        current_time_in_india = datetime.now(india_timezone)

        # Calculate the end time as current time + 1 hour

        response_text = (
            "Current Spotlight Hour Times\(the time is based upon IST\):\n\n"
        )

        # Iterate through the cities and their times
        counter = 0
        for city, city_time in COMMUNITY_DAY_TIME.items():
            # Convert city time to datetime
            city_timezone = pytz.timezone(
                "Asia/Kolkata"
            )  # Assuming all city times are in IST
            city_time = datetime.strptime(city_time, "%I:%M %p").time()

            # Calculate the current city time
            current_city_time = datetime.combine(datetime.now(), city_time)
            current_city_time = city_timezone.localize(current_city_time)
            end_time = current_city_time + timedelta(hours=3)
            # Check if the current city time is within the desired range
            if current_city_time <= current_time_in_india <= end_time:
                counter += 1
                coordinates = COORDS_DATA.get(city, "N/A")
                time_left = end_time - current_time_in_india
                response_text += f"{counter}\. {city}: ```{coordinates}``` \- {str(time_left).split(':')[0]}hrs {str(time_left).split(':')[1]}mins Left\n\n"

        bot.reply_to(message, response_text, parse_mode="MarkdownV2")

    except Exception:
        bot.reply_to(message, "An error occurred while fetching the current time.")


# @bot.message_handler(func=lambda message: True)
# def echo_message(message):
#     bot.reply_to(
#         message,
#         "I don't understand that command. Type /help to see available commands.",
#     )


# Run the bot
if __name__ == "__main__":
    bot.polling()
