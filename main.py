from interactions import Client, Intents, listen
from interactions import slash_command, SlashContext
import asyncio
from google.cloud import bigquery
import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize the Discord bot with intents
bot = Client(intents=Intents.DEFAULT)

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

@listen()  # this decorator tells snek that it needs to listen for the corresponding event, and run this coroutine
async def on_ready():
    # This event is called when the bot is ready to respond to commands
    print("Ready")
    print(f"This bot is owned by {bot.owner}")

@slash_command(name="qb_quote", description="Retrieve a random quote")
async def qb_quote(ctx: SlashContext):
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
    print("Response: ",formatted_result)

@slash_command(name="qb_add", description="Add a new quote")
async def qb_add(ctx: SlashContext):
    # need to defer it, otherwise, it fails
    await ctx.defer()

    # do stuff for a bit
    await asyncio.sleep(3)

    await ctx.send("Add quote functionality is not yet working...")

@slash_command(name="qb_edit", description="Edit an existing quote")
async def qb_edit(ctx: SlashContext):
    # need to defer it, otherwise, it fails
    await ctx.defer()

    # do stuff for a bit
    await asyncio.sleep(3)

    await ctx.send("Edit quote functionality is not yet working...")

# Run the bot with the Discord bot token in .env file
bot.start(os.getenv("DISCORD_TOKEN"))