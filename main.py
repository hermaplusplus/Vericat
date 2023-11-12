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

SETTINGS = json.load(open("settings.json", "r"))

from byond2json import player2dict as getPlayerData

PRIORITY_GUILDS = [discord.Object(id=342787099407155202), discord.Object(id=1167235329951027291)]
#PRIORITY_GUILDS = [discord.Object(id=342787099407155202)]
VERIFICATION_CHANNEL_ID = 1172294781850898432
VERIFICATION_CHANNEL = discord.Object(id=VERIFICATION_CHANNEL_ID)
VERIFICATION_QUEUE_ID = 1171888348948877443
VERIFICATION_QUEUE = discord.Object(id=1171888348948877443)
HIGH_STAFF_REFER = "Dungeon Masters"
HIGH_STAFF_ROLE_ID = 1169980778919231669
OTHER_APPROVER_REFER = "Chatmods"
OTHER_APPROVER_ROLE_ID = 1167969157053161522
APPROVED_ROLE_ID = 1172295904229851229
REJECT_ROLE_ID = 1168480230638358538

PROD = True

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

"""
@app_commands.checks.has_any_role(
    342788067297329154,  # woof
    1130594155597402172  # council
)
@client.tree.command(description="Shows the age of a BYOND account by Ckey.")
async def ckey(interaction: discord.Interaction, ckey: str):
    await interaction.response.defer(ephemeral=True)
    if PROD or interaction.guild.id == 342787099407155202:
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
    else:
        await interaction.followup.send("This command isn't currently available in this server - check back later!", ephemeral=True)

@app_commands.checks.has_any_role(
    342788067297329154,  # woof
    1130594155597402172  # council
)
@client.tree.command(description="Lists CCDB bans for a BYOND account by Ckey. Pagination begins at 1. Times displayed are in UTC.")
async def ccdb(interaction: discord.Interaction, ckey: str, page: Optional[int] = 1):
    await interaction.response.defer(ephemeral=True)
    if PROD or interaction.guild.id == 342787099407155202:
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
    else:
        await interaction.followup.send("This command isn't currently available in this server - check back later!", ephemeral=True)
"""

@client.tree.command(description="Displays a list of commands and how to use the bot.")
async def help(interaction:discord.Interaction):
    if PROD or interaction.guild.id == 342787099407155202:
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
    else:
        await interaction.response.send_message("This command isn't currently available in this server - check back later!", ephemeral=True)

@client.tree.error
async def on_app_command_error(interaction, error):
    if isinstance(error, app_commands.MissingAnyRole):
        await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
    else:
        #await interaction.response.send_message("⚠ An unknown error occurred! If this continues to happen, please contact <@188796089380503555>.", ephemeral=True)
        raise error

class Reg(ui.Modal, title="Registration"):
    ckey = ui.TextInput(label="What is your Ckey (BYOND username)?)",
                            style=discord.TextStyle.short,
                            placeholder="",
                            max_length=100)
    origin      = ui.TextInput(label="How did you find EnigmaTown?",
                            style=discord.TextStyle.long,
                            placeholder="",
                            max_length=1000)
    experience  = ui.TextInput(label="If invited by a friend, who are they?",
                            style=discord.TextStyle.long,
                            placeholder="",
                            max_length=1000)
    interest    = ui.TextInput(label="Why do you want to join EnigmaTown?",
                            style=discord.TextStyle.long,
                            placeholder="",
                            max_length=1000)
    agreement    = ui.TextInput(label="Do you agree to abide by the rules?",
                            style=discord.TextStyle.short,
                            placeholder="Yes",
                            min_length=3,
                            max_length=3)

    async def on_submit(self, interaction:discord.Interaction):
        try:
            playerData = getPlayerData(self.ckey.value)
        except:
            await interaction.response.send_message("The Ckey you specified couldn't be found.", ephemeral=True)
            return
        await interaction.response.send_message("Your registration has been submitted. Please await staff approval.", ephemeral=True)
        ccdb = requests.get(f"https://centcom.melonmesa.com/ban/search/{self.ckey.value}")
        embs = []
        #emb = discord.Embed(title=playerData['key'])
        emb = discord.Embed()
        emb.add_field(name="Discord", value=f"{interaction.user.mention}", inline=True)
        emb.add_field(name="Ckey", value=f"`{playerData['ckey']}`", inline=True)
        emb.add_field(name="How did you find EnigmaTown?", value=f"```{self.origin.value}```", inline=False)
        emb.add_field(name="If invited by a friend, who are they?", value=f"```{self.experience.value}```", inline=False)
        emb.add_field(name="Why do you want to join EnigmaTown?", value=f"```{self.interest.value}```", inline=False)
        emb.add_field(name="Do you agree to abide by the rules?", value=f"```{self.agreement.value}```", inline=False)
        #emb.add_field(name='\u200b', value='``` ```')
        emb.add_field(name="Account Creation Date", value=f"<t:{str(int(time.mktime(datetime.strptime(playerData['joined'], '%Y-%m-%d').timetuple())))}:d> (<t:{str(int(time.mktime(datetime.strptime(playerData['joined'], '%Y-%m-%d').timetuple())))}:R>)", inline=False)
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
                emb.add_field(name="CCDB Bans", value=f"[{activebans} active, {totalbans-activebans} expired bans found on CCDB.](https://centcom.melonmesa.com/viewer/view/{self.ckey.value})", inline=False)
        await client.get_channel(VERIFICATION_QUEUE_ID).send(embed=emb, view=Verification(interaction.user.id, self.ckey.value, self.origin.value, self.experience.value, self.interest.value, self.agreement.value))

class Verification(ui.View):
    def __init__(self, uid, ckey, origin, experience, interest, agreement):
        super().__init__(timeout=None)
        self.uid = uid
        self.ckey = ckey
        self.origin = origin
        self.experience = experience
        self.interest = interest
        self.agreement = agreement
    
    @ui.button(label="Accept", style=discord.ButtonStyle.green, custom_id=f"accept")
    async def accept_callback(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        if not ( (HIGH_STAFF_ROLE_ID in [r.id for r in interaction.user.roles]) or (OTHER_APPROVER_ROLE_ID in [r.id for r in interaction.user.roles]) ):
            await interaction.followup.send(f"Only {HIGH_STAFF_REFER} and {OTHER_APPROVER_REFER} can approve registrations.", ephemeral=True)
            return
        u = interaction.guild.get_member(self.uid)
        await u.add_roles(discord.Object(APPROVED_ROLE_ID))
        buttons = [b for b in self.children]
        buttons[0].disabled = True
        buttons[0].label = "Accepted"
        self.remove_item(buttons[1])
        await interaction.followup.edit_message(interaction.message.id, view=self)
        await interaction.followup.send(f"✅ <@{self.uid}>'s registration approved by {interaction.user.mention}.")
        os.system(f"echo {self.uid},{self.ckey} >> accountlinks.csv")
        self.stop()

    @ui.button(label="Reject", style=discord.ButtonStyle.red, custom_id=f"reject")
    async def reject_callback(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        if not ( (HIGH_STAFF_ROLE_ID in [r.id for r in interaction.user.roles]) or (OTHER_APPROVER_ROLE_ID in [r.id for r in interaction.user.roles]) ):
            await interaction.followup.send(f"Only {HIGH_STAFF_REFER} and {OTHER_APPROVER_REFER} can reject registrations.", ephemeral=True)
            return
        u = interaction.guild.get_member(self.uid)
        await u.add_roles(discord.Object(REJECT_ROLE_ID))
        buttons = [b for b in self.children]
        buttons[1].disabled = True
        buttons[1].label = "Rejected"
        self.remove_item(buttons[0])
        await interaction.followup.edit_message(interaction.message.id, view=self)
        await interaction.followup.send(f"⛔ <@{self.uid}>'s registration rejected by {interaction.user.mention}.")
        self.stop()

@client.tree.command(description="Fill out the registration form. This will be reviewed by staff.")
async def register(interaction: discord.Interaction):
    if APPROVED_ROLE_ID in [r.id for r in interaction.user.roles]:
        await interaction.response.send_message("Approved members cannot use this command.", ephemeral=True)
        return
    if interaction.channel.id not in [381573551200796672, VERIFICATION_CHANNEL_ID]:
        await interaction.response.send_message(f"This command can only be used in <#{VERIFICATION_CHANNEL_ID}>.", ephemeral=True)
        return
    await interaction.response.send_modal(Reg())

client.run(SETTINGS['TOKEN'])
#print(SETTINGS['TOKEN'])
