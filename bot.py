from discord import Intents
from discord.ext.commands import Bot, Context
import asyncio
import random
import dotenv
import validators
from os import environ

if __name__ == '__main__':
    # Load .env variables
    dotenv.load_dotenv()

    # Ballot dictionary
    ballots = {}

    # youtube links dictionary
    yt_links = {}

    # Prepare bot intents
    intents = Intents.default()
    intents.messages = True
    intents.message_content = True

    # Create a bot requires
    my_bot = Bot(command_prefix='//', intents=intents)

    # Runs when the bot is ready
    @my_bot.event
    async def on_ready():
        print(f'Logged on as {my_bot.user}!')

    # Calls the user sad lol
    @my_bot.command()
    async def sad(ctx: Context):
        # Delete user's message because commands aren't fun to look at
        await ctx.message.delete()

        # Send them their picture showing how sad they look 😠
        async with ctx.typing():
            await ctx.send(f'You sure do look sad 🙂', file = await ctx.author.display_avatar.to_file())

    # Greets the user, unless there are no emojis
    @my_bot.command()
    async def hello(ctx: Context):
        # Delete user's message because commands aren't fun to look at
        await ctx.message.delete()

        # Nicely greet the user with an emoji from their server or tell them to add some
        if ctx.guild.emojis:
            emoji = random.choice(ctx.guild.emojis)
            await ctx.send(f'Hello, {ctx.author.display_name} from the {ctx.guild} server {emoji} I\'m so STUPID 😃', delete_after=5)
            return
        
        await ctx.send(f"{ctx.guild} has no emojis ☹️ what are you waiting for {ctx.author.display_name} 🤨", delete_after=5)

    # Casts a vote for whatever they want
    @my_bot.command()
    async def vote(ctx: Context, *, arg: str):
        # Delete user's message for CONFIDENTIALITY REASONS
        await ctx.message.delete()

        # Check for required role to be able to vote
        if not [role for role in ctx.author.roles if role.name == 'Registered Voter' and role.guild == ctx.guild] and not ctx.author.id == ctx.guild.owner_id:
             await ctx.send(f"{ctx.author.display_name} is not a 'Registered Voter' in {ctx.guild} 😏", delete_after=5)
             return
        try:
            votes = ballots.get(ctx.guild.id)
            name = arg.upper()
            
            if votes:
                if name in votes:
                    votes[name] += 1
                    ballots[ctx.guild.id] = votes
                    await ctx.send(f"{name} has received one more vote 🤩", delete_after=5)
                    return

                votes[name] = 1
                ballots[ctx.guild.id] = votes
                await ctx.send(f"{name} has received one vote and is now in the running :face_with_peeking_eye:", delete_after=5)
                return

            ballots[ctx.guild.id] = {}
            ballots[ctx.guild.id][name] = 1
            await ctx.send(f"{name} has received one vote and is now in the running :face_with_peeking_eye:", delete_after=5)
            return

        except Exception:
            await ctx.send('Voting kinda broke 🤓', delete_after=5)

    # Lists all candidates that have received votes
    @my_bot.command()
    async def candidates(ctx: Context):
        # Delete user's message for CONFIDENTIALITY REASONS
        await ctx.message.delete()

        try:
            votes = ballots.get(ctx.guild.id)

            if votes:
                all_names = '❗Current candidates❗\n'
                for each in votes:
                    all_names += f"◻️ {each}\n"
                await ctx.send(all_names, delete_after=5+len(votes))
                return

            await ctx.send(f"{ctx.guild} is currently not voting for anything 😐", delete_after=5)
            return
        except Exception:
            await ctx.send('Voting kinda broke 🤓', delete_after=5)

    # Announce the winner(s) with the most votes and delete the current ballot
    @my_bot.command()
    async def results(ctx: Context):
        # Delete user's message for CONFIDENTIALITY REASONS
        await ctx.message.delete()

        # Check for required role to be able to show results
        if not [role for role in ctx.author.roles if role.name == 'Voting Official' and role.guild == ctx.guild] and not ctx.author.id == ctx.guild.owner_id:
            await ctx.send(f"{ctx.author.display_name} is not a 'Voting Official' in {ctx.guild} 😝", delete_after=5)
            return
        try:
            votes = ballots.get(ctx.guild.id)

            if votes:
                highest_count = 0
                for each in votes:
                    if votes[each] > highest_count:
                        highest_count = votes[each]
                
                winners = [x for x in votes if votes[x] == highest_count]
                async with ctx.typing():
                    await ctx.send('The results are in...😳', delete_after=2)
                    await asyncio.sleep(2.0)

                    if len(winners) == 1:
                        await ctx.send(f"🏆 {winners[0]} 🏆 has won with {highest_count} votes 🥳")
                        ballots.pop(ctx.guild.id)
                        return

                    await ctx.send(f"A {len(winners)}-way tie with {highest_count} votes 😲", delete_after=5)
                    await asyncio.sleep(1.0)
                    results = '🏆 WINNERS 🏆\n'
                    for each in winners:
                        results += f"✨ {each}\n"
                    await ctx.send(results)
                    ballots.pop(ctx.guild.id)
                    return
            await ctx.send('No votes have been casted 😂', delete_after=5)
            return

        except Exception:
            await ctx.send('Voting kinda broke 🤓', delete_after=5)
            return

    # Add a yt link to list
    @my_bot.command()
    async def addyt(ctx: Context, arg:str):
        # Delete user's message because commands aren't fun to look at
        await ctx.message.delete()

        # Check for required role to be able to show results
        if not [role for role in ctx.author.roles if role.name == 'yt admin' and role.guild == ctx.guild] and not ctx.author.id == ctx.guild.owner_id:
            await ctx.send(f"{ctx.author.display_name} is not a 'yt admin' in {ctx.guild} 😒", delete_after=5)
            return

        # Check if the url is valid
        if not validators.url(arg.strip()) or not (arg.find('www.youtube.com/') or arg.find('/youtu.be/')):
            await ctx.send(f" {ctx.author.display_name} did not send a valid youtube link 😧", delete_after=5)
            return

        # Add link to the list for the server
        if yt_links.get(ctx.guild.id):
            yt_links[ctx.guild.id].append(arg.strip())
            await ctx.send(f"{arg.strip()} was added to the list of yt links by {ctx.author.display_name}😨", delete_after=5)
            return

        yt_links[ctx.guild.id] = [arg.strip()]
        await ctx.send(f"{arg.strip()} was added to the list of yt links by {ctx.author.display_name}😨", delete_after=5)

    # Get a random yt link
    @my_bot.command()
    async def getyt(ctx: Context):
        # Delete user's message because commands aren't fun to look at
        await ctx.message.delete()

        if yt_links.get(ctx.guild.id):
            if yt_links[ctx.guild.id]:
                link = random.choice(yt_links[ctx.guild.id])
                yt_links[ctx.guild.id].remove(link)
                await ctx.send(f"{link} 🤔")
                return

        await ctx.send(f"There are no yt links 😊", delete_after=5)
        return

    # Clear yt links
    @my_bot.command()
    async def clearyt(ctx: Context):
        # Delete user's message because commands aren't fun to look at
        await ctx.message.delete()

        # Check for required role to be able to show results
        if not [role for role in ctx.author.roles if role.name == 'yt admin' and role.guild == ctx.guild] and not ctx.author.id == ctx.guild.owner_id:
            await ctx.send(f"{ctx.author.display_name} is not a 'yt admin' in {ctx.guild} 😒", delete_after=5)
            return

        await ctx.send(f"{ctx.author.display_name} has cleared the yt links 😉")
        yt_links.pop(ctx.guild.id)

    # Run the bot requires TOKEN in .env file/environment variables
    my_bot.run(environ['TOKEN'])

    # A way to keep the bot on that JUST WORKS
    from threading import Thread
    from flask import Flask

    t = Thread(target=Flask('').run())
    t.start()