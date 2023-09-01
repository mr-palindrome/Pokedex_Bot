# Pokémon Telegram Bot

## Introduction

Welcome to the Pokémon Telegram Bot project! This bot is designed to provide users with information about various Pokémon, movesets, time zones, and more. It's a fun and informative tool built using Python and the Telegram Bot API.

## How to Run the Project Locally

To run the project locally, follow these steps:

1. Clone the repository:
```
git clone https://github.com/your-username/pokemon-telegram-bot.git
cd pokemon-telegram-bot
```
2. Create a virtual environment to isolate project dependencies:
```
python -m venv venv
```
3. Activate the virtual environment:
- On Windows:
  ```
  venv\Scripts\activate
  ```
- On macOS and Linux:
  ```
  source venv/bin/activate
  ```

4. Install dependencies:
```
pip install -r requirements.txt
```

5. Set up your Telegram bot:
- Create a bot on Telegram using the BotFather.
- Copy your bot token and paste it in the `utils/base.py` file.

6. Set up MongoDB:
- Create a MongoDB Atlas account.
- Get your connection URI and add it to the `utils/base.py` file.

7. Run the bot:
```
python main.py
```

8. Start chatting with your bot on Telegram!

## How to Contribute

We welcome contributions from the community to enhance the features and functionality of the Pokémon Telegram Bot. To contribute, follow these steps:

1. Fork the repository.

2. Create a new branch:
```
git checkout -b feature/your-feature-name
```


3. Make your changes and test them thoroughly.

4. Commit your changes:
```
git commit -m "Add your commit message here"
```


5. Push your changes to your forked repository:
```
git push origin feature/your-feature-name
```

6. Open a pull request to the main repository. Provide a detailed description of your changes.

## Code of Conduct

Please adhere to our [Code of Conduct](CODE_OF_CONDUCT.md) when participating in this project.

## Support Me

If you find this project helpful and would like to support its development, you can:
- Star the repository
- Share the project with others
- Contribute to the project by adding new features or improving existing ones

Thank you for your support!

---

Feel free to contact us if you have any questions or suggestions. Happy coding!
