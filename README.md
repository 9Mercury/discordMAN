# 🔧 Discord Washing Machine Support Bot

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Discord.py](https://img.shields.io/badge/discord.py-2.3+-blue.svg)](https://discordpy.readthedocs.io/)
[![Gemini API](https://img.shields.io/badge/Google-Gemini%20API-orange.svg)](https://ai.google.dev/)
[![Mantis Hub](https://img.shields.io/badge/Mantis-Hub-green.svg)](https://mantishub.com/)

An intelligent Discord bot that provides automated washing machine support using AI-powered issue analysis and integrated ticketing system.

## 🌟 Features

- **🤖 AI-Powered Analysis**: Uses Google Gemini API to intelligently categorize washing machine problems
- **🎫 Smart Ticketing**: Automatically creates support tickets in Mantis Hub for complex issues
- **💬 Natural Conversations**: Supports both direct messages and channel mentions
- **🔧 Instant Solutions**: Provides immediate troubleshooting steps for common problems
- **📊 Ticket Tracking**: Tracks all tickets with unique IDs and status checking
- **⚡ Interactive UI**: Rich embeds with reaction-based ticket creation
- **🏷️ Issue Classification**: Categorizes issues by severity, type, and urgency

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Discord Bot Token
- Google Gemini API Key
- Mantis Hub Instance with API access

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/discord-washing-machine-bot.git
   cd discord-washing-machine-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the bot**
   ```bash
   python washing_machine_bot.py
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Discord Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token_here

# Google Gemini Configuration  
GEMINI_API_KEY=your_gemini_api_key_here

# Mantis Hub Configuration
MANTIS_BASE_URL=https://your-instance.mantishub.io/api/rest
MANTIS_API_TOKEN=your_mantis_api_token_here
MANTIS_PROJECT_ID=0
```

### API Keys Setup

#### Discord Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create new application → Add Bot
3. Copy the Bot Token
4. Enable "Message Content Intent" in Bot settings

#### Google Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create API Key
3. Copy the generated key

#### Mantis Hub API Token
1. Log into your Mantis Hub instance
2. Go to Account Settings → API Tokens
3. Generate new token for bot usage

## 🎯 Usage

### Basic Commands

| Command | Description | Example |
|---------|-------------|---------|
| `@Bot help` | Show help information | `@WashingMachineBot help` |
| `!wm status` | Check latest ticket status | `!wm status` |
| `!wm status <id>` | Check specific ticket | `!wm status 12345` |
| `!wm tickets` | List all your tickets | `!wm tickets` |

### Interaction Examples

#### Simple Issue (Gets Troubleshooting)
```
User: @WashingMachineBot my detergent isn't dispensing properly

Bot: 🔧 Troubleshooting Steps
Here are steps to fix detergent dispensing issues:
1. Check the detergent drawer for clogs...
2. Verify detergent type and amount...
3. Check water pressure...

If this doesn't solve your problem, react with 🎫 to create a support ticket.
```

#### Complex Issue (Creates Ticket)
```
User: @WashingMachineBot my machine has electrical problems and won't turn on

Bot: 🎫 Support Ticket Created
Ticket ID: 12345
Status: Open
Severity: High

Our support team will review your electrical issue and get back to you soon.
Use '!wm status 12345' to check status.
```

### Issue Categories

The bot automatically categorizes issues:

| Category | Examples | Action |
|----------|----------|--------|
| **Detergent** | Not dispensing, residue left | Troubleshooting |
| **Drainage** | Won't drain, slow drainage | Troubleshooting |
| **Mechanical** | Strange noises, vibration | Troubleshooting |
| **Door/Lid** | Won't open/close, lock issues | Troubleshooting |
| **Electrical** | Won't turn on, power issues | Create Ticket |
| **Other** | Complex or unclear issues | Create Ticket |

## 🛠️ Development

### Project Structure

```
discord-washing-machine-bot/
├── washing_machine_bot.py      # Main bot application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── .env                       # Your configuration (not in git)
├── washing_machine_tickets.db # SQLite database (auto-created)
├── README.md                  # This file
└── tests/
    ├── test_mantis.py         # Mantis Hub API tests
    ├── test_gemini.py         # Gemini API tests
    └── find_api_endpoint.py   # API endpoint discovery
```

### Key Components

#### `WashingMachineAnalyzer`
- Handles Google Gemini API integration
- Analyzes user issues and determines appropriate responses
- Returns structured JSON with action, severity, and category

#### `MantisHubIntegration`
- Manages Mantis Hub API connections
- Creates and retrieves tickets
- Handles authentication and error management

#### `TicketDatabase`
- Local SQLite database for ticket tracking
- Stores user tickets with metadata
- Enables ticket history and status checking

#### `DiscordWashingMachineBot`
- Main Discord bot class
- Handles user interactions and commands
- Coordinates between AI analysis and ticket creation

### Testing

Test individual components:

```bash
# Test Mantis Hub connection
python tests/test_mantis.py

# Test Gemini API
python tests/test_gemini.py

# Find correct API endpoint
python tests/find_api_endpoint.py
```

## 🐛 Troubleshooting

### Common Issues

#### Bot Not Responding
- ✅ Check Discord bot token is correct
- ✅ Ensure "Message Content Intent" is enabled
- ✅ Verify bot has "Send Messages" permission
- ✅ Check console logs for errors

#### Gemini API Errors
- ✅ Verify API key is valid
- ✅ Check rate limits aren't exceeded
- ✅ Ensure proper JSON formatting in responses

#### Mantis Hub Connection Issues
- ✅ Test API endpoint manually
- ✅ Verify authentication token
- ✅ Check project permissions
- ✅ Confirm correct project ID

#### Permission Errors
- ✅ Re-invite bot with updated permissions
- ✅ Check channel-specific permission overrides
- ✅ Ensure bot role hierarchy is correct

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

1. **Check the logs**: Console output shows detailed error information
2. **Test APIs individually**: Use the test scripts in `/tests/`
3. **Verify configuration**: Double-check all environment variables
4. **Check permissions**: Ensure all Discord/Mantis permissions are correct

## 📊 Monitoring

### Database Queries

View stored tickets:
```sql
sqlite3 washing_machine_tickets.db
.tables
SELECT * FROM tickets ORDER BY created_at DESC LIMIT 10;
```

### Health Checks

The bot logs important events:
- ✅ Successful API connections
- ✅ Ticket creations
- ✅ User interactions
- ❌ API failures
- ❌ Permission issues

## 🔒 Security

### Best Practices

- ✅ Never commit `.env` file to version control
- ✅ Use environment variables for all sensitive data
- ✅ Rotate API tokens regularly
- ✅ Monitor bot permissions and access
- ✅ Implement rate limiting if needed

### Token Management

```bash
# Secure token storage
chmod 600 .env

# Environment variable validation
python -c "import os; print('Tokens configured:' if all([
    os.getenv('DISCORD_BOT_TOKEN'),
    os.getenv('GEMINI_API_KEY'), 
    os.getenv('MANTIS_API_TOKEN')
]) else 'Missing tokens!')"
```

## 🤝 Contributing

### Development Setup

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Install dev dependencies**: `pip install -r requirements-dev.txt`
4. **Make changes and test**
5. **Submit pull request**

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Include error handling
- Write tests for new features

### Contribution Guidelines

- 🐛 **Bug Reports**: Include steps to reproduce, expected vs actual behavior
- 💡 **Feature Requests**: Describe use case and proposed implementation
- 🔧 **Code Changes**: Ensure tests pass and documentation is updated
- 📝 **Documentation**: Keep README and docstrings current

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Discord.py** - Excellent Python Discord API wrapper
- **Google Gemini** - Powerful AI for natural language processing
- **Mantis Hub** - Robust issue tracking platform
- **Contributors** - Thank you to all who help improve this project

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/9Mercury/discord-washing-machine-bot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/9Mercury/discord-washing-machine-bot/discussions)
- **Email**: singhyuvi916@gmail.com

---

Made with ❤️ for better washing machine support

[![GitHub stars](https://img.shields.io/github/stars/9Mercury/discord-washing-machine-bot.svg)](https://github.com/9Mercury/discord-washing-machine-bot/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/9Mercury/discord-washing-machine-bot.svg)](https://github.com/9Mercury/discord-washing-machine-bot/network)
[![GitHub issues](https://img.shields.io/github/issues/9Mercury/discord-washing-machine-bot.svg)](https://github.com/9Mercury/discord-washing-machine-bot/issues)
