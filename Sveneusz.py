import asyncio
import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import nacl
from collections import deque
import random

from collections import defaultdict
from datetime import datetime


f = open("figo", "r", encoding="utf-8")
figoList = [x.strip() for x in f if x.strip()]
f.close()

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='.', intents=intents)

is_looping = False
is_queue_looping = False
current_song = None
yt_dlp_lock = asyncio.Lock()  # Blokada dla operacji yt-dlp

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -reconnect_at_eof 1'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
song_queue = deque()

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        try:
            async with yt_dlp_lock:
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

            if data is None:
                raise ValueError("Błąd: yt-dlp zwrócił `None` podczas pobierania danych o utworze.")

            if 'entries' in data:
                data = data['entries'][0]

            filename = data['url'] if stream else ytdl.prepare_filename(data)
            return cls(discord.FFmpegPCMAudio(executable="ffmpeg", source=filename, options=ffmpeg_options['options']), data=data)

        except Exception as e:
            raise ValueError(f"Nie udało się znaleźć utworu. Błąd: {e}")



async def play_next(ctx):
    global current_song, is_queue_looping

    if is_looping and current_song:
        song_queue.appendleft(current_song)

    if song_queue:
        next_song = song_queue.popleft()
        current_song = next_song

        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            await join(ctx)
            voice_client = ctx.voice_client

        if voice_client and len(voice_client.channel.members) == 1:  # Tylko bot jest na kanale
            for i in range(60):
                await asyncio.sleep(5)  # Czeka 5 minut (300 sekund) przed opuszczeniem kanału
                if len(voice_client.channel.members) > 1:
                    break
            # Jeśli po 5 minutach kanał jest nadal pusty, bot wychodzi
            if len(voice_client.channel.members) == 1:
                await voice_client.disconnect()
                print(f"📤 Bot opuścił kanał {voice_client.channel} z powodu braku aktywności.")


        player = await YTDLSource.from_url(next_song["query"], loop=bot.loop)
        voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))

        f=open("stats.txt", "a", encoding="utf-8")
        f.write(player.title+" 8===D "+next_song["ctx"].author.name+" 8===D "+str(datetime.now())+"\n")
        f.close()

        await ctx.send(f"🎵 Now playing: **{player.title}**")

        if is_queue_looping:
            song_queue.append(next_song)

@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id and before.channel is not None and after.channel is None:
        voice_client = member.guild.voice_client
        if voice_client:
            try:
                await voice_client.disconnect()
            except Exception as e:
                print(f"⚠️ Error during disconnection: {e}")

@bot.command(name='join')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("⚠️ You need to be connected to a voice channel.")
        return

    channel = ctx.message.author.voice.channel
    if ctx.voice_client is None:
        voice_client = await channel.connect()
        await voice_client.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)

@bot.command(name='play', aliases=['p', 'PLAY'])
async def play(ctx, *, query):
    voice_client = ctx.voice_client
    if not voice_client or not voice_client.is_connected():
        await join(ctx)
        voice_client = ctx.voice_client

    song_queue.append({"query": query, "ctx": ctx})
    if not voice_client.is_playing():
        await play_next(ctx)
    else:
        await ctx.send(f"🎶 **Added to queue:** {query}")

@bot.command(name='figo', aliases=['f', 'FIGO', 'fagot', 'FAGOT', 'figo_fagot','bff'])
async def figo(ctx):
    voice_client = ctx.voice_client
    if not voice_client or not voice_client.is_connected():
        await join(ctx)
        voice_client = ctx.voice_client

    random.shuffle(figoList)
    for songFigo in figoList:
        song_queue.append({"query": songFigo, "ctx": ctx})
    await ctx.send(f"🎶 JESTEŚCIE GOTOWI NA DISCO?")
    if not voice_client.is_playing():
        await play_next(ctx)
    else:
        await ctx.send(f"🎶 JESTEŚCIE GOTOWI NA DISCO?")

@bot.command(name='bania')
async def bania(ctx):
    voice_client = ctx.voice_client
    if not voice_client or not voice_client.is_connected():
        await join(ctx)
        voice_client = ctx.voice_client

    song_queue.appendleft({"query": "brunetki i blondynki", "ctx": ctx})

    if not voice_client.is_playing():
        await play_next(ctx)

@bot.command(name='play_first')
async def play_first(ctx, *, query):
    voice_client = ctx.voice_client
    if not voice_client or not voice_client.is_connected():
        await join(ctx)
        voice_client = ctx.voice_client

    song_queue.appendleft({"query": query, "ctx": ctx})
    if not voice_client.is_playing():
        await play_next(ctx)
    else:
        await ctx.send(f"🎶 **Added to the front of the queue:** {query}")

@bot.command(name='skip')
async def skip(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()

@bot.command(name='stop')
async def stop(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_playing():
        voice_client.stop()
        song_queue.clear()

@bot.command(name='leave')
async def leave(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        song_queue.clear()

@bot.command(name='queue')
async def show_queue(ctx):
    if song_queue:
        queue_list = [f"{index + 1}. {item['query']}" for index, item in enumerate(song_queue)]
        await ctx.send("📃 **Current Queue:**\n" + "\n".join(queue_list))
    else:
        await ctx.send("🚫 The queue is currently empty.")

@bot.command(name='pause')
async def pause(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await ctx.send("⏸️ **Playback paused.**")
        for i in range(60):
            await asyncio.sleep(5)  # Czeka 5 minut (300 sekund) przed opuszczeniem kanału
            if voice_client.is_playing():
                break
        if not voice_client.is_playing():
            await voice_client.disconnect()
            print(f"📤 Bot opuścił kanał {voice_client.channel} z powodu braku aktywności.")
    else:
        await ctx.send("⚠️ The bot is not playing anything right now.")

@bot.command(name='resume')
async def resume(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await ctx.send("▶️ **Playback resumed.**")
    else:
        await ctx.send("⚠️ The bot is not paused or nothing is playing.")

@bot.command(name='loop')
async def loop(ctx):
    global is_looping
    is_looping = not is_looping
    await ctx.send(f"🔄 **Looping** is now {'enabled' if is_looping else 'disabled'}.")



@bot.command(name='stats')
async def stats(ctx):
    # Wczytaj dane z pliku
    with open("stats.txt", "r", encoding="utf-8") as f:
        stats = f.readlines()

    # Słowniki do przechowywania danych
    song_play_counts = defaultdict(int)
    user_play_counts = defaultdict(int)
    song_user_play_counts = defaultdict(lambda: defaultdict(int))
    user_song_play_counts = defaultdict(lambda: defaultdict(int))
    daily_play_counts = defaultdict(int)
    most_recent_plays = []

    # Analizuj każdy wpis
    for line in stats:
        if " 8===D " in line:
            try:
                title, author, date_str = line.strip().split(" 8===D ")
                date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")

                # Liczenie odtworzeń piosenek
                song_play_counts[title] += 1

                # Liczenie odtworzeń przez użytkowników
                user_play_counts[author] += 1

                # Liczenie odtworzeń piosenek przez użytkowników
                song_user_play_counts[title][author] += 1
                user_song_play_counts[author][title] += 1

                # Liczenie odtworzeń z dnia
                daily_play_counts[date_obj.date()] += 1

                # Przechowywanie najnowszych 10 odtworzeń
                most_recent_plays.append((title, author, date_obj))

            except ValueError:
                continue

    # Sortowanie najnowszych odtworzeń
    most_recent_plays.sort(key=lambda x: x[2], reverse=True)
    most_recent_plays = most_recent_plays[:10]

    # Najczęściej odtwarzana piosenka
    most_played_song = max(song_play_counts, key=song_play_counts.get, default="Brak danych")

    # Najczęściej słuchający użytkownik
    most_active_user = max(user_play_counts, key=user_play_counts.get, default="Brak danych")

    # Tworzenie raportu
    report = f"📊 **Statystyki odtworzeń:**\n\n"

    report += f"🎵 **Najczęściej odtwarzana piosenka:** {most_played_song} - {song_play_counts[most_played_song]} odtworzeń\n"
    report += f"👤 **Najbardziej aktywny użytkownik:** {most_active_user} - {user_play_counts[most_active_user]} odtworzeń\n"

    report += "\n📅 **Odtworzenia w dniach:**\n"
    for day, count in sorted(daily_play_counts.items(), reverse=True)[:7]:
        report += f"- {day}: {count} odtworzeń\n"

    report += "\n🎶 **Top piosenek:**\n"
    top_songs = sorted(song_play_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for title, count in top_songs:
        report += f"- {title}: {count} odtworzeń\n"

    report += "\n👥 **Top użytkowników:**\n"
    top_users = sorted(user_play_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    for user, count in top_users:
        report += f"- {user}: {count} odtworzeń\n"

    # Wyślij raport do użytkownika
    if len(report) > 2000:  # Discord ma limit 2000 znaków na wiadomość
        for i in range(0, len(report), 2000):
            await ctx.send(report[i:i + 2000])
    else:
        await ctx.send(report)


@bot.event
async def on_ready():
    print("✅ Bot is online and ready to use!")

DISCORD_TOKEN = "MTExMzQ5MjU0NjE0NDk3NjkwNg.GNxY-w.s_R1wbL85jB9amS4pE6g9JNXYSm5ToB5xMKPHM"

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
