# Music Bot

A Python-based music bot for Discord that provides automated music playback, queue management, and streaming capabilities.

## Features

- 🎵 Music playback from multiple sources
- 📋 Queue management system
- 🔄 Shuffle and repeat functionality
- 🐳 Docker containerization for easy deployment
- ⚙️ Background task processing

## Installation

### Prerequisites

- Python 3.8+
- Discord account and bot token
- ffmpeg (for audio processing)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/witw2/bot.git
cd bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. **Configure your bot token:**
   - Create a `.env` file in the project root
   - Add your Discord bot token:
   ```
   DISCORD_TOKEN=your_bot_token_here
   ```
   - Replace `your_bot_token_here` with your actual bot token from [Discord Developer Portal](https://discord.com/developers/applications)

4. Run the bot:
```bash
python main.py
```

## Docker Deployment

Build and run using Docker:

```bash
docker build -t music-bot .
docker run -e DISCORD_TOKEN=your_bot_token_here music-bot
```

## Configuration

Update the following in your bot configuration:
- **Bot Token**: Set in `.env` file (never commit this file)
- **Prefix**: Customize command prefix in config
- **Permissions**: Adjust bot permissions as needed

- Alternatively you can put it in Sveneusz.py file - only for local deployements!!!

## Usage

Invite your bot to a server using the OAuth2 URL from Discord Developer Portal, then use commands like:
- `!play <song>` - Play a song
- `!queue` - View current queue
- `!skip` - Skip current song
- `!shuffle` - Shuffle queue

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.
