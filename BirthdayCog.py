import discord
from discord.ext import commands
import datetime
import os
import schedule
import jsons
import asyncio
import time


class BirthdayCog(commands.Cog):

    def __init__(self, bot):
        self.birthdays = dict()
        self.target_channel = None
        self.debug_channel = None
        self.hour = "13:00"
        self.schedule_job()
        self.bot = bot
        self.sleep_time = 10  # in seconds

    @commands.Cog.listener()
    async def on_connect(self):
        self.connected = True
        print("Connected!")
        try:
            while self.connected:
                print("Run pending")
                schedule.run_pending()
                await asyncio.sleep(self.sleep_time)
            self.send_debug("disconnected")
        except Exception as err:
            self.connected = False
            print(f"An error of type {type(err)} occured {err}")
            await self.send_debug(
                f"An error of type {type(err)} occured {err}")

    @commands.Cog.listener()
    async def on_disconnect(self):
        print("Disconnected")
        self.connected = False

    @commands.command("add")
    async def add_birthday(self, ctx,  user: discord.Member, day: int, month: int, *message: str):
        bd = Birthday(day, month, " ".join(message), user)
        if len(ctx.message.attachments) > 0:
            bd.add_attachment(ctx.message.attachments[0])
        self.birthdays[user.id] = bd
        await ctx.send("Se agregó el cumpleaños de {}!".format(user))

    @commands.command("hour")
    async def set_hour(self, ctx,  h: int, m: int):
        if h > 24 or h < 0 or m < 0 or m > 60:
            await ctx.send("Que chistosito{}, no existe esta hora".format(ctx.author.mention))
            return
        minutes = "{}".format(m).zfill(2)
        self.hour = "{}:{}".format(h, minutes)
        schedule.cancel_job(self.job)
        self.schedule_job()
        await ctx.send("La hora cambió a {}".format(self.hour))

    @commands.command("channel")
    async def set_channel(self, ctx,  channel: discord.TextChannel):
        self.target_channel = channel
        await ctx.send("Se cambió el canal a {}".format(self.target_channel.name))

    @commands.command("debug_channel")
    async def set_channel_debug(self, ctx,  channel: discord.TextChannel):
        self.debug_channel = channel
        await ctx.send("Se cambió el canal a {}".format(self.debug_channel.name))
        if self.target_channel is None:
            self.target_channel = channel

    @commands.command("future")
    async def check_birthdays(self, ctx):
        j = jsons.dumps(self.birthdays, strip_privates=True)
        await ctx.send(j)

    @commands.command("time")
    async def check_time(self, ctx):
        await ctx.send(datetime.datetime.today())

    @commands.command("next")
    async def next_job(self, ctx):
        await ctx.send(schedule.idle_seconds())

    @commands.command("force")
    async def force_job(self, ctx):
        schedule.run_all()

    @commands.command("view_settings")
    async def status(self, ctx):
        await ctx.send(f"Channel: {self.target_channel} Debug Channel: {self.debug_channel} Running thread: {self.connected}")

    def start_check(self):
        print("schedule")
        task = asyncio.create_task(self.check_birthday())

    async def check_birthday(self):
        today = datetime.datetime.today()
        print("Checking birthdays for {}".format(today))
        delete = list()
        for key in self.birthdays:
            print("Checking birthday for: {}".format(key))
            bd = self.birthdays[key]
            if bd.day == today.day and bd.month == today.month:
                print("Happy birthday!")
                await self.say_happy_birthday(bd)
                delete.append(key)
        for key in delete:
            del self.birthdays[key]

    async def say_happy_birthday(self, birthday):
        await self.send_target(birthday.get_message(), birthday.get_attachment())
        if len(self.birthdays) == 0:
            await self.send_debug("¡No hay más cumpleaños registrados!")

    def schedule_job(self):
        self.job = schedule.every().day.at(self.hour).do(self.start_check)

    async def send_target(self, message, attachment):
        if self.target_channel is None:
            print("No target channel")
            return
        if attachment is None:
            await self.target_channel.send(message)
        else:
            filename = "birthday.png"
            await attachment.save(filename)
            await self.target_channel.send(message, file=discord.File(filename))

    async def send_debug(self, message):
        if self.debug_channel is None:
            print("No debug channel")
            return
        await self.debug_channel.send(message)


class Birthday:
    def __init__(self, day, month, message, user):
        self.day = day
        self.month = month
        self.message = message
        self.__user = user
        self.__attachment = None

    def add_attachment(self, attachment):
        self.attachment = attachment

    def get_attachment(self):
        return self.attachment

    def get_message(self):
        return "{} {}".format(self.__user.mention, self.message)

    def get_user_id(self):
        return self.__user.id
