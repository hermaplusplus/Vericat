import discord
from discord import app_commands
from discord import ui
from discord import utils
from typing import Optional
from datetime import datetime
import time
import json
import requests
import math
import os
from byond2json import player2dict as getPlayerData

SETTINGS = json.load(open("settings.json", "r"))

BOT_TOKEN = SETTINGS['BOT_TOKEN']
PRIORITY_GUILDS = [discord.Object(id=x) for x in SETTINGS['PRIORITY_GUILDS']]
APPLICATION_CHANNEL_ID = SETTINGS['APPLICATION_CHANNEL_ID']
APPLICATION_CHANNEL = discord.Object(id=APPLICATION_CHANNEL_ID)
REVIEW_CHANNEL_ID = SETTINGS['REVIEW_CHANNEL_ID']
REVIEW_CHANNEL = discord.Object(id=REVIEW_CHANNEL_ID)
APPROVER_ROLE_NAMES = [i[0] for i in SETTINGS['APPROVER_ROLES']]
APPROVER_ROLE_NAMES_STRING = ", ".join(APPROVER_ROLE_NAMES[:-2] + [", and ".join(APPROVER_ROLE_NAMES[-2:])])
APPROVER_ROLE_IDS = [i[1] for i in SETTINGS['APPROVER_ROLES']]
APPROVED_ROLE_IDS = SETTINGS['APPROVED_ROLE_IDS']
APPROVED_ROLES = [discord.Object(id=x) for x in APPROVED_ROLE_IDS]
REJECTED_ROLE_IDS = SETTINGS['REJECTED_ROLE_IDS']
REJECTED_ROLES = [discord.Object(id=x) for x in REJECTED_ROLE_IDS]
QUESTIONS = SETTINGS['QUESTIONS']
SS13_FEATURES_ENABLED = SETTINGS['SS13_FEATURES_ENABLED']
SS13_COMMAND_ROLE_IDS = SETTINGS['SS13_COMMAND_ROLE_IDS']

listToGrammar = lambda data : ", ".join(data[:-2] + [", and ".join(data[-2:])])

class Client(discord.Client):

    def __init__(self, *, intents: discord. Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        for i in PRIORITY_GUILDS:
            self.tree.copy_global_to(guild=i)
            await self.tree.sync(guild=i)
        print("Command tree sync completed")

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.messages = True
#intents.all = True
client = Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name="Psydon's Gate 3"
        )
    )

@client.tree.command(description="Displays a list of commands and how to use the bot.")
async def help(interaction:discord.Interaction):
    await interaction.response.send_message(f"**Commands:**\n"
                                            f"`/help` shows this message.\n"
                                            f"`/register` begins the registration process.\n"
                                            f"\n"
                                            f"**FAQ:**\n"
                                            f"\n"
                                            f"Q: *Who should I direct technical questions to?*\n"
                                            f"A: <@188796089380503555>.\n"
                                            f"\n"
                                            f"Q: *How can I help pay for the upkeep of the bot?*\n"
                                            f"A: https://github.com/sponsors/hermaplusplus",
                                            ephemeral=True)

@client.tree.error
async def on_app_command_error(interaction, error):
    if isinstance(error, app_commands.MissingAnyRole):
        await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
    else:
        #await interaction.response.send_message("⚠ An unknown error occurred! If this continues to happen, please contact <@188796089380503555>.", ephemeral=True)
        raise error

class Reg(ui.Modal, title="Registration"):
    q0 = ui.TextInput(label=QUESTIONS[0]['label'],
                        style=discord.TextStyle.short if QUESTIONS[0]['style_short'] else discord.TextStyle.long,
                        placeholder=QUESTIONS[0]['placeholder'],
                        min_length=QUESTIONS[0]['min_length'],
                        max_length=QUESTIONS[0]['max_length'])
    q1 = ui.TextInput(label=QUESTIONS[1]['label'],
                        style=discord.TextStyle.short if QUESTIONS[1]['style_short'] else discord.TextStyle.long,
                        placeholder=QUESTIONS[1]['placeholder'],
                        min_length=QUESTIONS[1]['min_length'],
                        max_length=QUESTIONS[1]['max_length'])
    q2 = ui.TextInput(label=QUESTIONS[2]['label'],
                        style=discord.TextStyle.short if QUESTIONS[2]['style_short'] else discord.TextStyle.long,
                        placeholder=QUESTIONS[2]['placeholder'],
                        min_length=QUESTIONS[2]['min_length'],
                        max_length=QUESTIONS[2]['max_length'])
    q3 = ui.TextInput(label=QUESTIONS[3]['label'],
                        style=discord.TextStyle.short if QUESTIONS[3]['style_short'] else discord.TextStyle.long,
                        placeholder=QUESTIONS[3]['placeholder'],
                        min_length=QUESTIONS[3]['min_length'],
                        max_length=QUESTIONS[3]['max_length'])
    q4 = ui.TextInput(label=QUESTIONS[4]['label'],
                        style=discord.TextStyle.short if QUESTIONS[4]['style_short'] else discord.TextStyle.long,
                        placeholder=QUESTIONS[4]['placeholder'],
                        min_length=QUESTIONS[4]['min_length'],
                        max_length=QUESTIONS[4]['max_length'])

    async def on_submit(self, interaction:discord.Interaction):
        if SS13_FEATURES_ENABLED:
            try:
                playerData = getPlayerData(self.q0.value)
            except:
                await interaction.response.send_message("The Ckey you specified couldn't be found.", ephemeral=True)
                return
        await interaction.response.send_message("Your registration has been submitted. Please await staff approval.", ephemeral=True)
        embs = []
        emb = discord.Embed()
        emb.add_field(name="Discord", value=f"{interaction.user.mention}\n`{interaction.user.name}`", inline=True)
        if SS13_FEATURES_ENABLED:
            ccdb = requests.get(f"https://centcom.melonmesa.com/ban/search/{self.q0.value.replace(' ', '%20')}")
            emb.add_field(name="Ckey", value=f"`{playerData['ckey']}`", inline=True)
        emb.add_field(name=QUESTIONS[0]['label'], value=f"```{self.q0.value}```", inline=False)
        emb.add_field(name=QUESTIONS[1]['label'], value=f"```{self.q1.value}```", inline=False)
        emb.add_field(name=QUESTIONS[2]['label'], value=f"```{self.q2.value}```", inline=False)
        emb.add_field(name=QUESTIONS[3]['label'], value=f"```{self.q3.value}```", inline=False)
        emb.add_field(name=QUESTIONS[4]['label'], value=f"```{self.q4.value}```", inline=False)
        if SS13_FEATURES_ENABLED:
            emb.add_field(name="Ckey Creation Date", value=f"<t:{str(int(time.mktime(datetime.strptime(playerData['joined'], '%Y-%m-%d').timetuple())))}:d> (<t:{str(int(time.mktime(datetime.strptime(playerData['joined'], '%Y-%m-%d').timetuple())))}:R>)", inline=False)
            if ccdb.status_code == 200:
                ccdbdata = ccdb.json()
                if len(ccdbdata) == 0:
                    emb.add_field(name="CCDB Bans", value=f"No bans found on CCDB.", inline=False)
                else:
                    activebans = 0
                    totalbans = 0
                    for ban in ccdbdata:
                        if ban['active']:
                            activebans += 1
                        totalbans += 1
                    emb.add_field(name="CCDB Bans", value=f"[{activebans} active, {totalbans-activebans} expired bans found on CCDB.](https://centcom.melonmesa.com/viewer/view/{self.q0.value})", inline=False)
        await client.get_channel(REVIEW_CHANNEL_ID).send(embed=emb, view=Verification(interaction.user.id, self.q0.value, self.q1.value, self.q2.value, self.q3.value, self.q4.value))

class Verification(ui.View):
    def __init__(self, uid, q0, q1, q2, q3, q4):
        super().__init__(timeout=None)
        self.uid = uid
        self.q0 = q0
        self.q1 = q1
        self.q2 = q2
        self.q3 = q3
        self.q4 = q4
    
    @ui.button(label="Accept", style=discord.ButtonStyle.green, custom_id=f"accept")
    async def accept_callback(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        if not any(item in APPROVER_ROLE_IDS for item in [r.id for r in interaction.user.roles]):
            await interaction.followup.send(f"Only {APPROVER_ROLE_NAMES_STRING} can approve registrations.", ephemeral=True)
            return
        u = interaction.guild.get_member(self.uid)
        if len(APPROVED_ROLES) > 0:
            await u.add_roles(APPROVED_ROLES)
        buttons = [b for b in self.children]
        buttons[0].disabled = True
        buttons[0].label = "Accepted"
        self.remove_item(buttons[1])
        await interaction.followup.edit_message(interaction.message.id, view=self)
        await interaction.followup.send(f"✅ <@{self.uid}>'s registration approved by {interaction.user.mention}.")
        os.system(f"echo {self.uid},{self.q0} >> accountlinks.csv")
        self.stop()

    @ui.button(label="Reject", style=discord.ButtonStyle.red, custom_id=f"reject")
    async def reject_callback(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        if not any(item in APPROVER_ROLE_IDS for item in [r.id for r in interaction.user.roles]):
            await interaction.followup.send(f"Only {APPROVER_ROLE_NAMES_STRING} can reject registrations.", ephemeral=True)
            return
        u = interaction.guild.get_member(self.uid)
        if len(REJECTED_ROLES) > 0:
            await u.add_roles(REJECTED_ROLES)
        buttons = [b for b in self.children]
        buttons[1].disabled = True
        buttons[1].label = "Rejected"
        self.remove_item(buttons[0])
        await interaction.followup.edit_message(interaction.message.id, view=self)
        await interaction.followup.send(f"⛔ <@{self.uid}>'s registration rejected by {interaction.user.mention}.")
        self.stop()

@client.tree.command(description="Fill out the registration form. This will be reviewed by staff.")
async def register(interaction: discord.Interaction):
    if any(item in APPROVED_ROLE_IDS for item in [r.id for r in interaction.user.roles]):
        await interaction.response.send_message("Approved members cannot use this command.", ephemeral=True)
        return
    if interaction.channel.id not in [381573551200796672, APPLICATION_CHANNEL_ID]:
        await interaction.response.send_message(f"This command can only be used in <#{APPLICATION_CHANNEL_ID}>.", ephemeral=True)
        return
    await interaction.response.send_modal(Reg())

if SS13_FEATURES_ENABLED:
    @app_commands.checks.has_any_role(APPROVER_ROLE_IDS)
    @client.tree.command(description="Shows the age of a BYOND account by Ckey.")
    async def ckey(interaction: discord.Interaction, ckey: str):
        await interaction.response.defer(ephemeral=True)
        try:
            playerData = getPlayerData(ckey)
        except:
            await interaction.followup.send("The Ckey you specified couldn't be found.", ephemeral=True)
            return
        ccdb = requests.get(f"https://centcom.melonmesa.com/ban/search/{ckey}")
        embs = []
        #emb = discord.Embed(title=playerData['key'])
        emb = discord.Embed()
        emb.add_field(name="Ckey", value=f"`{playerData['ckey']}`", inline=True)
        emb.add_field(name="Account Creation Date", value=f"<t:{str(int(time.mktime(datetime.strptime(playerData['joined'], '%Y-%m-%d').timetuple())))}:d> (<t:{str(int(time.mktime(datetime.strptime(playerData['joined'], '%Y-%m-%d').timetuple())))}:R>)", inline=True)
        if ccdb.status_code == 200:
            ccdbdata = ccdb.json()
            if len(ccdbdata) == 0:
                emb.add_field(name="CCDB Bans", value=f"No bans found on CCDB.", inline=True)
            else:
                activebans = 0
                totalbans = 0
                for ban in ccdbdata:
                    if ban['active']:
                        activebans += 1
                    totalbans += 1
                emb.add_field(name="CCDB Bans", value=f"{activebans} active, {totalbans-activebans} expired bans found on CCDB.", inline=True)
        embs.append(emb)
        await interaction.followup.send(embeds=embs, ephemeral=True)
    
    @app_commands.checks.has_any_role(APPROVER_ROLE_IDS)
    @client.tree.command(description="Lists CCDB bans for a BYOND account by Ckey. Pagination begins at 1. Times displayed are in UTC.")
    async def ccdb(interaction: discord.Interaction, ckey: str, page: Optional[int] = 1):
        await interaction.response.defer(ephemeral=True)
        try:
            playerData = getPlayerData(ckey)
        except:
            await interaction.followup.send("The Ckey you specified couldn't be found.", ephemeral=True)
            return
        ccdb = requests.get(f"https://centcom.melonmesa.com/ban/search/{ckey}")
        embs = []
        #emb = discord.Embed(title=playerData['key'])
        emb = discord.Embed()
        if ccdb.status_code == 200:
            ccdbdata = ccdb.json()
            for ban in ccdbdata:
                banstatus = "Active" if ban['active'] else "Expired"
                if "unbannedBy" in ban.keys():
                    banstatus = "Unbanned"
                emb = discord.Embed(title=f"{ban['type']} Ban | {ban['sourceName']} | {banstatus}", description=f"{ban['reason']}", colour=(discord.Colour.from_rgb(108, 186, 67) if banstatus == "Active" else (discord.Colour.from_rgb(213, 167, 70) if banstatus == "Expired" else discord.Colour.from_rgb(84, 151, 224))))
                emb.add_field(name="Banned", value=f"{ban['bannedOn'].replace('T',' ').replace('Z','')}", inline=True)
                emb.add_field(name="Admin", value=f"{ban['bannedBy']}", inline=True)
                if "expires" in ban.keys():
                    emb.add_field(name="Expires", value=f"{ban['expires'].replace('T',' ').replace('Z','')}", inline=True)
                if "banID" in ban.keys():
                    emb.add_field(name="Original Ban ID", value=f"`{ban['banID']}`", inline=True)
                if "unbannedBy" in ban.keys():
                    emb.add_field(name="Unbanned By", value=f"{ban['unbannedBy']}", inline=True)
                embs.append(emb)
        if len(embs) == 0:
            await interaction.followup.send(f"No bans found on CCDB for **`{ckey}`**.", embeds=embs, ephemeral=True)
        if len(embs) > 0 and len(embs) <= 10:
            await interaction.followup.send(f"{len(embs)} bans found on CCDB for **`{ckey}`**.", embeds=embs, ephemeral=True)
        if len(embs) > 10:
            maxpages = math.ceil(len(embs)/10)
            await interaction.followup.send(f"{len(embs)} bans found on CCDB for **`{ckey}`**. Displaying page {min(page, maxpages)} of {maxpages}", embeds=(embs[(page-1)*10:page*10] if page <= maxpages else embs[(maxpages-1)*10:maxpages*10]), ephemeral=True)

client.run(BOT_TOKEN)
