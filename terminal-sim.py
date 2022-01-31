import asyncio
import random

import discord
import config
from discord.ext import commands
import subprocess

current_path = "/home/ubuntu/src/game-bot/terminal-main"

class Terminal(commands.Cog):
    """ A collection of the commands related to gameplay.

        Attributes:
            bot: The instance of the bot that is executing the commands.
    """

    def __init__(self, bot):
        self.bot = bot
        self.ROOT_PATH = "/terminal-main"
        self.PATH_FILE = "/home/ubuntu/src/game-bot/terminal-path.txt"
        self.allowed_commands = ['ls', 'cat', 'cd']
        self.INVALID_COMMAND_MSG = "ERROR: INVALID COMMAND"
        self.OVERRIDE_COMMAND_FILTER = True

    @commands.Cog.listener()
    async def on_message(self, message):
        #Check for correct channel
        if not (message.channel.name == "terminal-main"):
            return
        
        #Check if bot is author (ignore if true)
        if message.author == self.bot.user:
            return

        _message = message.content

        #Check if command is help
        if _message == "help":
            pass

        #Check if command is allowed
        command_allowed = self.OVERRIDE_COMMAND_FILTER
        for _command in self.allowed_commands:
            if _message.split()[0] == _command:
                command_allowed = True
            if ';' in _message:
                command_allowed = False
        if command_allowed == False:
            await message.channel.send(self.INVALID_COMMAND_MSG)
            return
        print("DEBUG: _message = " + _message)

        #Retrieve stored path
        with open(self.PATH_FILE, mode='r+') as f:
            current_path = f.read()
        print("DEBUG: current_path = " + current_path)

        #Check if path is empty, load default path if true
        if current_path == "":
            current_path = self.ROOT_PATH

        #Bash command
        #Construct bash command
        command = 'eval \"cd ' + current_path + ';' + _message + ';echo -e \'\\n\';pwd\"'
        print("DEBUG: command = " + command)

        #try command, get reply
        try:
            output = subprocess.run(command, stdout=subprocess.PIPE, input="".encode('utf-8'), shell=True, executable='/bin/bash', check=True).stdout.decode('utf-8')
        except:
            output = self.INVALID_COMMAND_MSG
            reply = "main-term: " + current_path + ">>>\n" + output
            print("*"*40)
            await message.channel.send(reply)
            return

        while output[-1] =='\n':
            output = output[:-1]
        while output[0] == '\n':
            output = output[1:]
        print("DEBUG: raw_output: " + "\n" + output)
        print("DEBUG: output.split = " + str(output.splitlines()))
        print("LINES:  "+ str(len(output.splitlines())))
        if len(output.splitlines()) == 1:
            current_path = output
            output = ""
        else:
            current_path = output[output.rfind('\n'):][1:]
            output = output[:output.rfind('\n')]
        print("DEBUG: new_path = " + current_path)
        print("DEBUG: output:" + "\n" + output)

        #check if path is outside sandbox, if so return to default directory
        if current_path[:len(self.ROOT_PATH)] != self.ROOT_PATH:
            current_path = self.ROOT_PATH
            output = "ERROR: INVALID DIRECTORY"

        #store current path
        else:
            with open('terminal-path.txt', mode='r+') as f:
                f.write(current_path)

        #Construct reply and send
        reply = "main-term: " + current_path + ">>>\n" + output
        print("*"*40)
        await message.channel.send(reply)


def setup(bot):
    bot.add_cog(Terminal(bot))