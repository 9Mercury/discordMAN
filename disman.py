import discord
from discord.ext import commands
import asyncio
import aiohttp
import json
import os
from typing import Optional, Dict, Any
import requests
from datetime import datetime
import sqlite3
import logging
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TicketInfo:
    ticket_id: str
    user_id: str
    issue_description: str
    status: str
    created_at: str

class WashingMachineAnalyzer:
    """Handles LLM processing for washing machine issues using Google Gemini"""
    
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.gemini_api_key}"
        
        if not self.gemini_api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
        
    async def analyze_issue(self, user_message: str) -> Dict[str, Any]:
        """Analyze user message and determine appropriate response using Gemini API"""
        
        system_prompt = """
        You are an expert washing machine support assistant. Analyze user queries about washing machine problems.
        
        Categorize issues as either:
        1. SIMPLE - Can be resolved with basic troubleshooting (detergent issues, minor clogs, settings problems)
        2. COMPLEX - Requires professional support (electrical, major mechanical, warranty, repairs)
        
        Common washing machine issues and their categories:
        SIMPLE:
        - Detergent not dispensing properly
        - Clothes not getting clean
        - Water not draining completely
        - Door won't open/close properly
        - Strange noises during wash
        - Clothes coming out wrinkled
        - Spin cycle issues
        
        COMPLEX:
        - Electrical problems (won't turn on, power issues)
        - Water leaking extensively
        - Major mechanical failures
        - Error codes that persist
        - Warranty claims
        - Installation problems
        - Repeated failures after troubleshooting
        
        Respond in JSON format:
        {
            "action": "provide_solution" or "create_ticket",
            "response": "Your helpful response with specific troubleshooting steps or explanation",
            "severity": "low", "medium", or "high",
            "category": "detergent", "mechanical", "electrical", "door", "cleaning", "drainage", "other",
            "urgency": "normal" or "high"
        }
        
        For simple issues: Provide clear, step-by-step troubleshooting instructions.
        For complex issues: Explain why professional help is needed and what to expect.
        """
        
        try:
            # Construct the full prompt
            full_prompt = f"{system_prompt}\n\nUser issue: {user_message}"
            
            # Prepare chat history for Gemini API
            chat_history = []
            chat_history.append({"role": "user", "parts": [{"text": full_prompt}]})
            
            # Payload for the API request
            payload = {"contents": chat_history}
            
            # Make the API call
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers={'Content-Type': 'application/json'},
                    json=payload,
                    timeout=30
                ) as response:
                    
                    if response.status != 200:
                        logger.error(f"Gemini API error: {response.status}")
                        return self._fallback_response()
                    
                    result = await response.json()
                    
                    # Extract the generated text
                    if (result.get("candidates") and len(result["candidates"]) > 0 and 
                        result["candidates"][0].get("content") and 
                        result["candidates"][0]["content"].get("parts") and 
                        len(result["candidates"][0]["content"]["parts"]) > 0):
                        
                        text = result["candidates"][0]["content"]["parts"][0]["text"]
                        
                        # Try to parse JSON from the response
                        try:
                            return json.loads(text)
                        except json.JSONDecodeError:
                            # If not valid JSON, try to extract JSON from the text
                            import re
                            json_match = re.search(r'\{.*\}', text, re.DOTALL)
                            if json_match:
                                return json.loads(json_match.group())
                            else:
                                logger.error("No valid JSON found in Gemini response")
                                return self._fallback_response()
                    else:
                        logger.error("No content generated by Gemini")
                        return self._fallback_response()
                        
        except asyncio.TimeoutError:
            logger.error("Gemini API timeout")
            return self._fallback_response()
        except Exception as e:
            logger.error(f"Gemini API processing error: {e}")
            return self._fallback_response()
    
    def _fallback_response(self) -> Dict[str, Any]:
        """Fallback response when Gemini API fails"""
        return {
            "action": "create_ticket",
            "response": "I'm having trouble analyzing your issue right now. Let me create a support ticket so our team can help you directly.",
            "severity": "medium",
            "category": "other",
            "urgency": "normal"
        }

class MantisHubIntegration:
    """Handles Mantis Hub ticketing system integration"""
    
    def __init__(self):
        self.base_url = os.getenv('MANTIS_BASE_URL')
        self.api_token = os.getenv('MANTIS_API_TOKEN')
        self.project_id = int(os.getenv('MANTIS_PROJECT_ID', '1'))
        
        if not self.base_url or not self.api_token:
            logger.error("Mantis Hub credentials not configured properly")
    
    async def create_ticket(self, title: str, description: str, severity: str = "minor", 
                          category: str = "general", user_id: str = None) -> Optional[str]:
        """Create a new ticket in Mantis Hub"""
        
        if not self.base_url or not self.api_token:
            logger.error("Mantis Hub not configured")
            return None
            
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        # Map severity levels
        severity_map = {
            "low": "trivial",
            "medium": "minor", 
            "high": "major"
        }
        
        ticket_data = {
            'summary': title,
            'description': description,
            'category': {'name': 'Washing Machine Support'},
            'project': {'id': self.project_id},
            'priority': {'name': 'normal'},
            'severity': {'name': severity_map.get(severity, 'minor')},
            'reproducibility': {'name': 'always'},
            'additional_information': f'Discord User ID: {user_id}' if user_id else ''
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/issues",
                    headers=headers,
                    json=ticket_data,
                    timeout=30
                ) as response:
                    
                    if response.status == 201:
                        data = await response.json()
                        issue_id = data.get('issue', {}).get('id')
                        logger.info(f"Created Mantis ticket: {issue_id}")
                        return str(issue_id)
                    else:
                        error_text = await response.text()
                        logger.error(f"Mantis API error {response.status}: {error_text}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error("Mantis API timeout")
            return None
        except Exception as e:
            logger.error(f"Mantis integration error: {e}")
            return None
    
    async def get_ticket_status(self, ticket_id: str) -> Optional[Dict]:
        """Get ticket status and details from Mantis Hub"""
        
        if not self.base_url or not self.api_token:
            return None
            
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/issues/{ticket_id}",
                    headers=headers,
                    timeout=30
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        issues = data.get('issues', [])
                        return issues[0] if issues else None
                    else:
                        logger.error(f"Failed to fetch ticket {ticket_id}: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error fetching ticket status: {e}")
            return None

class TicketDatabase:
    """Handles local ticket tracking database"""
    
    def __init__(self, db_path: str = 'washing_machine_tickets.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for ticket tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                username TEXT,
                issue_description TEXT NOT NULL,
                status TEXT DEFAULT 'Open',
                severity TEXT,
                category TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                UNIQUE(ticket_id)
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def save_ticket(self, ticket_id: str, user_id: str, username: str, 
                   issue_description: str, severity: str, category: str):
        """Save ticket information to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT OR REPLACE INTO tickets 
            (ticket_id, user_id, username, issue_description, severity, category, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ticket_id, user_id, username, issue_description, severity, category, now, now))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved ticket {ticket_id} to database")
    
    def get_user_tickets(self, user_id: str) -> list:
        """Get all tickets for a specific user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ticket_id, issue_description, severity, created_at 
            FROM tickets 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        ''', (user_id,))
        
        tickets = cursor.fetchall()
        conn.close()
        return tickets

class DiscordWashingMachineBot(commands.Bot):
    """Main Discord bot class"""
    
    def __init__(self):
        # Configure Discord intents
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix='!wm ',
            intents=intents,
            help_command=None,
            description="Washing Machine Support Bot"
        )
        
        # Initialize components
        self.analyzer = WashingMachineAnalyzer()
        self.mantis = MantisHubIntegration()
        self.database = TicketDatabase()
        
        # Track user sessions
        self.user_tickets = {}  # user_id: latest_ticket_id
        
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="washing machine problems | !wm help"
            )
        )
    
    async def on_message(self, message):
        """Handle incoming messages"""
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Handle DMs or mentions
        if isinstance(message.channel, discord.DMChannel) or self.user.mentioned_in(message):
            await self.handle_support_request(message)
        
        # Process commands
        await self.process_commands(message)
    
    async def handle_support_request(self, message):
        """Handle washing machine support requests"""
        # Clean message content
        content = message.content
        if self.user.mentioned_in(message):
            content = content.replace(f'<@{self.user.id}>', '').strip()
        
        if not content or content.lower() in ['hi', 'hello', 'help']:
            embed = discord.Embed(
                title="🔧 Washing Machine Support Bot",
                description="I'm here to help with washing machine problems!\n\n"
                           "Just describe your issue and I'll either:\n"
                           "• Provide troubleshooting steps\n"
                           "• Create a support ticket for complex issues\n\n"
                           "**Example:** *My washing machine won't drain water*",
                color=0x4CAF50
            )
            embed.add_field(
                name="Commands",
                value="`!wm status` - Check your latest ticket\n"
                      "`!wm tickets` - View all your tickets\n"
                      "`!wm help` - Show this help message",
                inline=False
            )
            await message.reply(embed=embed)
            return
        
        # Show typing indicator while processing
        async with message.channel.typing():
            try:
                # Analyze the issue with LLM
                analysis = await self.analyzer.analyze_issue(content)
                
                if analysis['action'] == 'provide_solution':
                    await self.send_solution_response(message, analysis)
                else:
                    await self.create_support_ticket(message, content, analysis)
                    
            except Exception as e:
                logger.error(f"Error handling support request: {e}")
                await message.reply("❌ Sorry, I encountered an error. Please try again or contact support directly.")
    
    async def send_solution_response(self, message, analysis):
        """Send troubleshooting solution with ticket option"""
        embed = discord.Embed(
            title="🔧 Troubleshooting Steps",
            description=analysis['response'],
            color=0x2196F3
        )
        
        embed.add_field(
            name="Severity",
            value=analysis['severity'].title(),
            inline=True
        )
        embed.add_field(
            name="Category", 
            value=analysis['category'].title(),
            inline=True
        )
        
        embed.set_footer(text="If this doesn't solve your problem, react with 🎫 to create a support ticket.")
        
        msg = await message.reply(embed=embed)
        await msg.add_reaction('🎫')
        
        # Store message for ticket creation
        self.pending_tickets = getattr(self, 'pending_tickets', {})
        self.pending_tickets[msg.id] = {
            'user_id': message.author.id,
            'issue': message.content,
            'analysis': analysis
        }
    
    async def create_support_ticket(self, message, issue_description, analysis):
        """Create a support ticket in Mantis Hub"""
        # Create ticket title
        category = analysis.get('category', 'general')
        title = f"Washing Machine Issue - {category.title()}"
        
        # Create detailed description
        description = f"""
**User:** {message.author.mention} ({message.author.display_name})
**Issue:** {issue_description}
**Severity:** {analysis.get('severity', 'medium')}
**Category:** {category}
**Urgency:** {analysis.get('urgency', 'normal')}
**Channel:** {message.channel.mention if hasattr(message.channel, 'mention') else 'DM'}

**AI Analysis:** {analysis.get('response', 'No additional analysis available')}
        """.strip()
        
        # Create ticket in Mantis Hub
        ticket_id = await self.mantis.create_ticket(
            title=title,
            description=description,
            severity=analysis.get('severity', 'medium'),
            category=category,
            user_id=str(message.author.id)
        )
        
        if ticket_id:
            # Save to database
            self.database.save_ticket(
                ticket_id=ticket_id,
                user_id=str(message.author.id),
                username=message.author.display_name,
                issue_description=issue_description,
                severity=analysis.get('severity', 'medium'),
                category=category
            )
            
            # Store latest ticket for user
            self.user_tickets[message.author.id] = ticket_id
            
            # Send success response
            embed = discord.Embed(
                title="🎫 Support Ticket Created",
                description=f"Your support ticket has been created successfully!",
                color=0x4CAF50
            )
            embed.add_field(name="Ticket ID", value=f"`{ticket_id}`", inline=True)
            embed.add_field(name="Status", value="Open", inline=True)
            embed.add_field(name="Severity", value=analysis.get('severity', 'medium').title(), inline=True)
            embed.add_field(name="Next Steps", value=analysis.get('response', 'Our support team will review your issue and get back to you soon.'), inline=False)
            embed.set_footer(text=f"Use '!wm status {ticket_id}' to check ticket status")
            
            await message.reply(embed=embed)
            
        else:
            # Ticket creation failed
            embed = discord.Embed(
                title="❌ Ticket Creation Failed",
                description="Sorry, I couldn't create a support ticket right now. Please try again later or contact support directly.",
                color=0xF44336
            )
            await message.reply(embed=embed)
    
    async def on_reaction_add(self, reaction, user):
        """Handle ticket creation via reaction"""
        if user.bot or str(reaction.emoji) != '🎫':
            return
        
        # Check if this is a pending ticket message
        pending_tickets = getattr(self, 'pending_tickets', {})
        ticket_info = pending_tickets.get(reaction.message.id)
        
        if ticket_info and ticket_info['user_id'] == user.id:
            # Create ticket for this user
            original_message = reaction.message
            await self.create_support_ticket(
                type('obj', (object,), {
                    'author': user,
                    'content': ticket_info['issue'],
                    'channel': original_message.channel,
                    'reply': original_message.reply
                })(),
                ticket_info['issue'],
                ticket_info['analysis']
            )
            
            # Clean up pending ticket
            del pending_tickets[reaction.message.id]
    
    @commands.command(name='status')
    async def check_status(self, ctx, ticket_id: str = None):
        """Check ticket status"""
        if not ticket_id:
            # Get user's latest ticket
            ticket_id = self.user_tickets.get(ctx.author.id)
            if not ticket_id:
                await ctx.reply("❌ No ticket ID provided and no recent tickets found. Use `!wm tickets` to see all your tickets.")
                return
        
        # Get status from Mantis Hub
        async with ctx.typing():
            ticket_info = await self.mantis.get_ticket_status(ticket_id)
            
        if ticket_info:
            embed = discord.Embed(
                title=f"🎫 Ticket Status: {ticket_id}",
                color=0x2196F3
            )
            embed.add_field(name="Summary", value=ticket_info.get('summary', 'N/A'), inline=False)
            embed.add_field(name="Status", value=ticket_info.get('status', {}).get('name', 'Unknown'), inline=True)
            embed.add_field(name="Priority", value=ticket_info.get('priority', {}).get('name', 'Unknown'), inline=True)
            embed.add_field(name="Severity", value=ticket_info.get('severity', {}).get('name', 'Unknown'), inline=True)
            
            await ctx.reply(embed=embed)
        else:
            await ctx.reply(f"❌ Couldn't find ticket `{ticket_id}` or access was denied.")
    
    @commands.command(name='tickets')
    async def list_tickets(self, ctx):
        """List all user tickets"""
        tickets = self.database.get_user_tickets(str(ctx.author.id))
        
        if not tickets:
            await ctx.reply("📋 You don't have any support tickets yet.")
            return
        
        embed = discord.Embed(
            title=f"📋 Your Support Tickets",
            description=f"Found {len(tickets)} ticket(s)",
            color=0x9C27B0
        )
        
        for ticket_id, description, severity, created_at in tickets[:5]:  # Show max 5 tickets
            created_date = datetime.fromisoformat(created_at).strftime("%Y-%m-%d %H:%M")
            embed.add_field(
                name=f"Ticket {ticket_id}",
                value=f"**Issue:** {description[:50]}{'...' if len(description) > 50 else ''}\n"
                      f"**Severity:** {severity}\n"
                      f"**Created:** {created_date}",
                inline=False
            )
        
        if len(tickets) > 5:
            embed.set_footer(text=f"Showing latest 5 tickets out of {len(tickets)} total")
        
        await ctx.reply(embed=embed)
    
    @commands.command(name='help')
    async def help_command(self, ctx):
        """Show help information"""
        embed = discord.Embed(
            title="🔧 Washing Machine Support Bot Help",
            description="I help diagnose and create tickets for washing machine problems!",
            color=0x4CAF50
        )
        
        embed.add_field(
            name="💬 Getting Help",
            value="Just mention me or send a DM describing your washing machine problem.\n"
                  "**Example:** `@WashingMachineBot my machine won't drain`",
            inline=False
        )
        
        embed.add_field(
            name="🎫 Commands",
            value="`!wm status [ticket_id]` - Check ticket status\n"
                  "`!wm tickets` - List all your tickets\n"
                  "`!wm help` - Show this help message",
            inline=False
        )
        
        embed.add_field(
            name="🔧 What I Can Help With",
            value="• Detergent dispensing issues\n"
                  "• Drainage problems\n"
                  "• Strange noises\n"
                  "• Door/lid issues\n"
                  "• Cleaning problems\n"
                  "• Error codes\n"
                  "• And much more!",
            inline=False
        )
        
        await ctx.reply(embed=embed)

# Main execution function
async def main():
    """Main function to start the Discord bot"""
    
    # Check required environment variables
    required_vars = {
        'DISCORD_BOT_TOKEN': os.getenv('DISCORD_BOT_TOKEN'),
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'MANTIS_BASE_URL': os.getenv('MANTIS_BASE_URL'),
        'MANTIS_API_TOKEN': os.getenv('MANTIS_API_TOKEN'),
        'MANTIS_PROJECT_ID': os.getenv('MANTIS_PROJECT_ID', '1')
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please check your .env file or environment configuration")
        return
    
    # Create and start bot
    bot = DiscordWashingMachineBot()
    
    try:
        logger.info("Starting Discord Washing Machine Bot...")
        await bot.start(required_vars['DISCORD_BOT_TOKEN'])
    except discord.LoginFailure:
        logger.error("Invalid Discord bot token")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())