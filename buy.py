import discord
from discord.ext import commands
from discord.ui import View
from dotenv import load_dotenv
import asyncio
import os

# =========================================
# LOAD ENV
# =========================================
load_dotenv()

TOKEN = os.getenv("TOKEN")

# =========================================
# CHANNEL ID
# =========================================
TICKET_CHANNEL_ID = 1504503272654770277

# =========================================
# CATEGORY NAME
# =========================================
CATEGORY_NAME = "🎫 AXB SUPPORT"

# =========================================
# INTENTS
# =========================================
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# =========================================
# BOT READY
# =========================================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

    # PERSISTENT BUTTONS
    bot.add_view(TicketPanel())
    bot.add_view(ClosePanel())

# =========================================
# CLOSE BUTTON
# =========================================
class ClosePanel(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Close Ticket",
        emoji="🔒",
        style=discord.ButtonStyle.danger,
        custom_id="close_ticket_btn"
    )
    async def close_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_message(
            "🔒 Closing Ticket In 5 Seconds...",
            ephemeral=True
        )

        await asyncio.sleep(5)

        await interaction.channel.delete()

# =========================================
# CREATE TICKET BUTTON
# =========================================
class TicketPanel(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Create Ticket",
        emoji="💎",
        style=discord.ButtonStyle.success,
        custom_id="create_ticket_btn"
    )
    async def create_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        try:
            guild = interaction.guild
            user = interaction.user

            # CHECK EXISTING TICKET
            existing_ticket = discord.utils.get(
                guild.channels,
                name=f"ticket-{user.name.lower()}"
            )

            if existing_ticket:
                await interaction.response.send_message(
                    f"❌ You Already Have A Ticket:\n{existing_ticket.mention}",
                    ephemeral=True
                )
                return

            # CREATE CATEGORY
            category = discord.utils.get(
                guild.categories,
                name=CATEGORY_NAME
            )

            if category is None:
                category = await guild.create_category(CATEGORY_NAME)

            # PERMISSIONS
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    view_channel=False
                ),

                user: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                ),

                guild.me: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                )
            }

            # CREATE CHANNEL
            ticket_channel = await guild.create_text_channel(
                name=f"ticket-{user.name}",
                category=category,
                overwrites=overwrites
            )

            # EMBED
            embed = discord.Embed(
                title="💎 AXB STORE VIP SUPPORT",
                description=(
                    f"Welcome {user.mention} 👋\n\n"
                    f"🎫 Your Ticket Has Been Created Successfully.\n"
                    f"📩 Please Send Your Message Below.\n\n"
                    f"⚡ AXB Support Team Will Reply Soon.\n"
                    f"💖 Thank You For Choosing AXB STORE."
                ),
                color=0x8B5CF6
            )

            embed.set_footer(
                text="AXB STORE • Premium Support"
            )

            # SEND MESSAGE
            await ticket_channel.send(
                content=f"{user.mention}",
                embed=embed,
                view=ClosePanel()
            )

            # SUCCESS MESSAGE
            await interaction.response.send_message(
                f"✅ Ticket Created Successfully:\n{ticket_channel.mention}",
                ephemeral=True
            )

        except Exception as e:
            print(f"ERROR: {e}")

# =========================================
# PANEL COMMAND
# =========================================
@bot.command()
async def panel(ctx):

    # ONLY BUY-NOW CHANNEL
    if ctx.channel.id != TICKET_CHANNEL_ID:
        await ctx.send(
            "❌ This Command Only Works In BUY-NOW Channel."
        )
        return

    embed = discord.Embed(
        title="💎 AXB STORE SUPPORT",
        description=(
            "━━━━━━━━━━━━━━━━━━\n"
            "🎫 CREATE SUPPORT TICKET\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "📩 Need Help?\n"
            "🛒 Purchase Problem?\n"
            "⚡ Fast Support Available\n\n"
            "Click The Button Below\n"
            "To Create Your Private Ticket 💖"
        ),
        color=0x8B5CF6
    )

    embed.set_footer(
        text="AXB STORE "
    )

    await ctx.send(
        embed=embed,
        view=TicketPanel()
    )

# =========================================
# RUN BOT
# =========================================
bot.run(TOKEN)