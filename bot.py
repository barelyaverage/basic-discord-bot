from discord import Intents
from discord.ext.commands import Bot, Context
import asyncio
import random
import dotenv
import validators
from os import environ

def main():
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

    # Calls the user sad
    @my_bot.command()
    async def me(ctx: Context):
        # Delete user's message because commands aren't fun to look at
        await ctx.message.delete()

        # Send them their picture showing how sad they look
        async with ctx.typing():
            await ctx.send(f'@{ctx.author.display_name} is this you 🤔', file = await ctx.author.display_avatar.to_file())

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

    # Add candidates to the ballot
    @my_bot.command()
    async def add(ctx: Context, *args: str):
        # Delete user's message for CONFIDENTIALITY REASONS
        await ctx.message.delete()

        # Check for required role to be able to show results
        if not [role for role in ctx.author.roles if role.name == 'Voting Official' and role.guild == ctx.guild] and not ctx.author.id == ctx.guild.owner_id:
            await ctx.send(f"{ctx.author.display_name} is not a 'Voting Official' in {ctx.guild} 😝", delete_after=5)
            return

        if not ballots.get(ctx.guild.id):
            ballots[ctx.guild.id] = {}

        votes = ballots[ctx.guild.id]

        new_count = 0
        for name in args:
            if name not in votes:
                votes[name] = 0
                new_count += 1

        await ctx.send(f"{new_count} new candidates have been added 😬", delete_after=5)
        return        

    # Casts a vote for an option on the ballot
    @my_bot.command()
    async def vote(ctx: Context, *, arg: str):
        # Delete user's message for CONFIDENTIALITY REASONS
        await ctx.message.delete()

        # Check for required role to be able to vote
        if not [role for role in ctx.author.roles if role.name == 'Registered Voter' and role.guild == ctx.guild] and not ctx.author.id == ctx.guild.owner_id:
             await ctx.send(f"{ctx.author.display_name} is not a 'Registered Voter' in {ctx.guild} 😏", delete_after=5)
             return

        votes = ballots.get(ctx.guild.id)
        name = arg.strip()
        
        if votes:
            if name in votes:
                votes[name] += 1
                ballots[ctx.guild.id] = votes
                await ctx.send(f"{name} has received a vote 🤩", delete_after=5)
                return

            votes[name] = 1
            ballots[ctx.guild.id] = votes
            await ctx.send(f"{name} is currently not a candidate 🤗", delete_after=5)
            return
        
        await ctx.send(f"{ctx.guild} does not have a vote going on right now 😅", delete_after=5)
        return

    # Lists all candidates on the ballot
    @my_bot.command()
    async def candidates(ctx: Context):
        # Delete user's message for CONFIDENTIALITY REASONS
        await ctx.message.delete()

        votes = ballots.get(ctx.guild.id)

        if votes:
            all_names = 'Current candidates 💬\n'
            for each in votes:
                all_names += f"◻️ {each}\n"
            await ctx.send(all_names, delete_after=5*len(votes))
            return

        await ctx.send(f"{ctx.guild} is not voting for anything 😐", delete_after=5)
        return

    # Announce the winner(s) with the most votes and delete the current ballot
    @my_bot.command()
    async def results(ctx: Context):
        # Delete user's message for CONFIDENTIALITY REASONS
        await ctx.message.delete()

        # Check for required role to be able to show results
        if not [role for role in ctx.author.roles if role.name == 'Voting Official' and role.guild == ctx.guild] and not ctx.author.id == ctx.guild.owner_id:
            await ctx.send(f"{ctx.author.display_name} is not a 'Voting Official' in {ctx.guild} 😝", delete_after=5)
            return

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
                    await ctx.send(f"🏆 {winners[0]} 🏆 has won the vote 🥳")
                    ballots.pop(ctx.guild.id)
                    return

                await ctx.send(f"A {len(winners)}-way tie 😲")
                await asyncio.sleep(1.0)
                results = '🏆 WINNERS 🏆\n'
                for each in winners:
                    results += f"✨ {each}\n"
                await ctx.send(results)
                ballots.pop(ctx.guild.id)
                return

        await ctx.send(f"{ctx.guild} has not voted for anything 😂", delete_after=5)
        return

    # List all candidates with their vote count
    @my_bot.command()
    async def standings(ctx: Context):
        # Delete user's message for CONFIDENTIALITY REASONS
        await ctx.message.delete()

        votes = ballots.get(ctx.guild.id)
        if votes:
            current = 'CURRENT VOTE COUNT 🗳️\n'
            for name in votes:
                current += f"☑️{votes[name]} - {name}\n"

            await ctx.send(current, delete_after=5*len(votes))
            return

        await ctx.send(f"{ctx.guild} has no votes to check 😴", delete_after=5)
            

    try:
        # Run the bot requires TOKEN in .env file/environment variables
        my_bot.run(environ['TOKEN'])
    except KeyError:
        print('You have not set a TOKEN environment variable')

# A way to keep the bot on that JUST WORKS hopefully?
from threading import Thread

t = Thread(target=main())
t.start()