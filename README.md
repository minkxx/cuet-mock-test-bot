# CUET Mock Test Bot 🤖

A Telegram bot designed to help students prepare for the Common University Entrance Test (CUET) through interactive mock tests and detailed explanations.

## Features ✨

- Take subject-wise mock tests 📝
- Get instant feedback on answers ✅
- View detailed explanations for each question 📚
- Track your progress across multiple attempts 📊
- User-friendly interface with button-based navigation 🎯

## How to Use 🚀

1. Find the bot on Telegram: [@MockTestCuetBot](https://t.me/MockTestCuetBot)
2. Start the bot by sending `/start`
3. Use `/mock_test` to begin a practice test
4. Select your subject and answer questions
5. Use `/explain` during the test to see explanations
6. Use `/end_test` to finish and see your results

## Setting Up Your Own Instance 🛠️

### Prerequisites

- Python 3.7+
- MongoDB
- Telegram Bot Token

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/minkxx/cuet-mock-test-bot
   cd cuet-mock-test-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with the following variables:
   ```
   BOT_TOKEN=your_telegram_bot_token
   MONGO_URI=your_mongodb_connection_string
   ```

4. Set up the MongoDB database:
   - Create a database named "cuet_bot"
   - Import question sets using the JSON file handler

5. Run the bot:
   ```bash
   python bot.py
   ```

## Project Structure 📁

- `bot.py` - Main bot initialization and handler registration
- `handlers/` - Command and callback handlers
- `database/` - Database connection and operations
- `config.py` - Configuration and environment variables

## Contributing 🤝

Contributions are welcome! Feel free to:
- Add more question sets
- Improve explanations
- Enhance bot features
- Fix bugs

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Support 💬

For support or queries, reach out through:
- GitHub Issues
- Email: aryuokk@gmail.com

Happy Learning! 📚✨
