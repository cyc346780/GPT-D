import discord
import openai
import datetime
import config


intents = discord.Intents().all()
client = discord.Client(intents=intents)

openai.api_key = config.OPENAI_API_KEY

text_channels = {}


async def initialize_categories(guild):
    create_room_category = await guild.create_category("CREATE A ROOM", position=1)
    chat_rooms_category = await guild.create_category("CHAT ROOMS", position=2)

    create_room_voice_channel = await guild.create_voice_channel(
        "+ New chat", category=create_room_category
    )

    return chat_rooms_category, create_room_voice_channel


def generate_chat_response(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": text},
        ],
        max_tokens=2000,
        stop=None,
        temperature=0.7,
    )

    return response["choices"][0]["message"]["content"]


@client.event
async def on_guild_join(guild):
    chat_rooms_category, create_room_voice_channel = await initialize_categories(guild)

    @client.event
    async def on_voice_state_update(member, before, after):
        if after.channel == create_room_voice_channel:
            await member.move_to(None)

            text_channel = await guild.create_text_channel(
                "new_chat", category=chat_rooms_category
            )

            text_channels[text_channel.id] = True

            response = generate_chat_response("Hello")

            await text_channel.send(response)

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if message.channel.id not in text_channels:
            return

        response = generate_chat_response(message.content)

        await message.channel.send(response)

        now = datetime.datetime.now()

        await message.channel.edit(name=now.strftime("%Y-%m-%d_%H%M"))

    @client.event
    async def on_guild_channel_delete(channel):
        if channel.id in text_channels:
            del text_channels[channel.id]


if __name__ == "__main__":
    client.run(config.DISCORD_BOT_TOKEN)
