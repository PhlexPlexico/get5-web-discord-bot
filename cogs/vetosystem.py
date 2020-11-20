import asyncio
import discord
import cogs.utils.configloader as configloader
import random
from discord.ext import commands
from discord.ext.commands import bot
import os
discordConfig = configloader.getDiscordValues()

mapList = discordConfig['vetoMapPool'].split(' ')
# Set in readysystem first, then here.
currentVeto = None
match = None
firstCaptain = None
secondCaptain = None
inProgress = False


class VetoSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['ban'])
    async def veto(self, ctx, arg):
        """Strikes a map from the given veto list in the config.

        If the bot maintainer has chosen to install Get5-Web, it will also add the vetoes to the match database.
        Once the vetoes are completed, the users will then wait for the bot to configure either the given server,
        or a publically available server on the webpanel(first available). Some variables within this module
        are modified from the readysystem, since we need to pass over the match and captains.

        Paramaters
        ----------
        ctx : Context
            Represents the context in which a command is being invoked under.
        arg : str
            Usually the map to strike from the veto."""

        global mapList
        global currentVeto
        global match
        global firstCaptain
        global secondCaptain
        global inProgress
        # make sure they're using the bot setup channel
        if(ctx.message.channel.id != int(discordConfig['setupTextChannelID'])):
            # if they aren't using an appropriate channel, return
            return
        if(inProgress and len(mapList) != 1):
            # Who's turn is it to veto? Check if it's the captain and if it's their turn.
            # await ctx.send("Our captain name {} current veto {}".format(firstCaptain.name, currentVeto))
            if (__debug__):
                if (ctx.author.id != firstCaptain or ctx.author.id != secondCaptain):
                    embed = discord.Embed(
                        description="**{}, you are not a captain. Can you don't?**".format(ctx.author.mention), color=0xff0000)
                    await ctx.send(embed=embed)
                    return
                elif (ctx.author.id == firstCaptain and currentVeto == 'team2'):
                    embed = discord.Embed(
                        description="**{} It is not your turn to veto. C'mon dude.**".format(ctx.author.mention), color=0xff0000)
                    await ctx.send(embed=embed)
                    return
                elif (ctx.author.id == secondCaptain and currentVeto == 'team1'):
                    embed = discord.Embed(
                        description="**{} It is not your turn to veto. C'mon dude.**".format(ctx.author.mention), color=0xff0000)
                    await ctx.send(embed=embed)
                    return
            else:
                embed = discord.Embed(
                    description="**{} is currently selecting, but captain is {} or {}**".format(ctx.author.mention, firstCaptain, secondCaptain), color=0xff0000)
                await ctx.send(embed=embed)
            # Check to see if map exists in our message. Let users choose to use de or not.
            try:
                if(arg.startswith("de_")):
                    mapList.remove(str(arg).lower())
                else:
                    mapList.remove(str("de_"+arg).lower())
            except ValueError:
                embed = discord.Embed(
                    description="**{} does not exist in the map pool. Please try again.**".format(arg), color=0xff0000)
                await ctx.send(embed=embed)
                return
            # Now that everything is checked and we're successful, let's move on.
            embed = discord.Embed(
                description="**Maps**\n" + " \n ".join(str(x) for x in mapList), color=0x03f0fc)
            await ctx.send(embed=embed)

            if(currentVeto == 'team1'):
                currentVeto = 'team2'
                embed = discord.Embed(description="team_{} please make your ban.".format(
                    secondCaptain.name), color=0x03f0fc)
            else:
                currentVeto = 'team1'
                embed = discord.Embed(description="team_{} please make your ban.".format(
                    firstCaptain.name), color=0x03f0fc)
            if(len(mapList) != 1):
                await ctx.send(embed=embed)
            else:
                # Decider map. Update match if we have database, present to users.
                embed = discord.Embed(
                    description="**Map**\n" + mapList[0] + "\nNow that the map has been decided, go to your favourite 10man service and set it up.", color=0x03f0fc)
                await ctx.send(embed=embed)
                inProgress = False
                firstCaptain = None
                secondCaptain = None
                mapList = discordConfig['vetoMapPool'].split(' ')
                currentVeto = None
                match = None
                firstCaptain = None
                secondCaptain = None
                inProgress = False
            return

    @commands.command()
    async def maps(self, ctx):
        global mapList
        """ Returns the current maps that can be striken from the veto """
        # make sure they're using the bot setup channel
        if(ctx.message.channel.id != int(discordConfig['setupTextChannelID'])):
            # if they aren't using an appropriate channel, return
            return
        embed = discord.Embed(
            description=" \n ".join(str(x) for x in mapList), title="Remaining Maps", color=0xff0000)
        await ctx.send(embed=embed)
        return

    @commands.command()
    async def stop(self, ctx):
        global mapList
        global currentVeto
        global match
        global firstCaptain
        global secondCaptain
        global inProgress
        """ Remove the vetoes and match from the database. """
        # make sure they're using the bot setup channel
        if(ctx.message.channel.id != int(discordConfig['setupTextChannelID'])):
            # if they aren't using an appropriate channel, return
            return
        if (ctx.author.id != firstCaptain or ctx.author.id != secondCaptain):
            embed = discord.Embed(
                description="**{}, you are not a captain. Can you don't?**".format(ctx.author.mention), color=0xff0000)
            await ctx.send(embed=embed)
        elif(inProgress):
            if(databasePresent):
                db.delete_vetoes(match.id)
                db.delete_match(match.id)
                match = None
            mapList = discordConfig['vetoMapPool'].split(' ')
            currentVeto = None
            firstCaptain = None
            secondCaptain = None
            inProgress = False
        else:
            embed = discord.Embed(
                description="Can't stop what hasn't been started.", color=0xff0000)
            await ctx.send(embed=embed)
        return

    @commands.command()
    async def captains(self, ctx):
        global firstCaptain
        global secondCaptain
        embed = discord.Embed(
            description="Your captains today are: {} and {}".format(firstCaptain, secondCaptain), color=0x03f0fc)
        await ctx.send(embed=embed)
        return

    @commands.command()
    async def matchadd(self, ctx, arg):
        # make sure they're using the bot setup channel
        if(ctx.message.channel.id != int(discordConfig['setupTextChannelID'])):
            # if they aren't using an appropriate channel, return
            return
        if(inProgress and len(mapList) != 1):
            if (__debug__):
                if (ctx.author.id != firstCaptain or ctx.author.id != secondCaptain):
                    embed = discord.Embed(
                        description="**{}, you are not a captain. Can you don't?**".format(ctx.author.mention), color=0xff0000)
                    await ctx.send(embed=embed)
                    return
            else:
                embed = discord.Embed(
                    description="**{} you are not a captain, and cannot add users to your own team. The captains are: {} and {}**".format(ctx.author.mention, firstCaptain, secondCaptain), color=0xff0000)
                await ctx.send(embed=embed)
        try:
            if(ctx.author.id == firstCaptain):
                team = databaseConfig["team1ScrimID"]
            else:
                team = databaseConfig["team2ScrimID"]
            steam_id = int(arg)
            if (db.get_total_team_auth(team) > 5):
                embed = discord.Embed(
                    description="We already have 5 memebers in your team. Don't do that you cheater.", color=0xff0000)
                await ctx.send(embed=embed)
            else:
                # Successful steam ID to add into the game.
                db.append_auths_in_team(steam_id, team)
                embed = discord.Embed(
                    description="Player has been successfully added to team.", color=0xff0000)
                await ctx.send(embed=embed)
        except ValueError:
            embed = discord.Embed(
                    description="We can't insert a non-integer value into the database. Please don't.", color=0xff0000)
            await ctx.send(embed=embed)
        return

def setup(bot):
    bot.add_cog(VetoSystem(bot))
