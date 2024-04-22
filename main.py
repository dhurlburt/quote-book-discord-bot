import discord
from discord.ext import commands
from google.cloud import bigquery
import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Declare intents for Discord bot
intents = discord.Intents.all()

# Enable the messages intent
intents.messages = True

# Initialize the Discord bot with intents
bot = commands.Bot(command_prefix='!', intents=intents)

def query_bigquery(project_id, dataset_id, table_id, query):
    # Initialize BigQuery client
    client = bigquery.Client(project=project_id)

    # Construct the query
    query_job = client.query(query)

    # Execute the query
    result = query_job.result()

    # Get the single result
    single_result = None
    for row in result:
        single_result = row
        break  # Assuming you only need the first result, you can break after the first row

    return single_result

# Discord command to query BigQuery and return the result
@bot.command()
async def quote(ctx):
    # Delete the initial prompt message
    await ctx.message.delete()

    # Project ID, dataset ID, table ID, and query needed to retrieve quote in BigQuery table
    project = os.getenv("PROJECT_ID")
    dataset = os.getenv("DATASET_ID")
    table = os.getenv("TABLE_ID")
    query = "SELECT quote, author, context, spoken_into_existence_on FROM `{project_id}.{dataset_id}.{table_id}` ORDER BY RAND() LIMIT 1".format(
        project_id=project, dataset_id=dataset, table_id=table
    )

    # Call the function to query BigQuery
    result = query_bigquery(project, dataset, table, query)

    # Extract values from the result row
    quote = result[0]
    author = result[1]
    rawcontext = str(result[2])  # Convert context to a string
    context = rawcontext[0].lower() + rawcontext[1:] # Convert context to lowercase
    qdate = result[3]

    # Mention the user who initiated the command
    user_mention = ctx.author.mention

    # Format the result as <"quote" --author, --with context --on date>
    if qdate != datetime.date(1, 1, 1):
        if context != '':
            formatted_result = f'{user_mention} \n```"{quote}"  \n\n  - {author}, {context} On {qdate}.```\n' 
        else:
            formatted_result = f'{user_mention} \n```"{quote}"  \n\n  -{author} on {qdate}```\n' 
    else:
        if context != 'none':
            formatted_result = f'{user_mention} \n```"{quote}"  \n\n  -{author}, {context}```\n' 
        else:
            formatted_result = f'{user_mention} \n```"{quote}"  \n\n  -{author}```\n'

    # Send the result as a message in Discord
    await ctx.send(formatted_result)

# Run the bot with the Discord bot token in .env file
bot.run(os.getenv("DISCORD_TOKEN"))