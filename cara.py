import config
import asyncio
import logging
import logging.config
import discord
import lineparser
import messagecomposer as mc
import helper
from idol import IdolsList


##############
# LOGGER SETUP
##############
def setup_logger(name, log_file, level):

    formatter = logging.Formatter('[%(asctime)s] - %(message)s')

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


class Cara:

    def __init__(self):
        log.info("####################")
        log.info("Initializing Cara")
        log.info("####################")
        self.client = discord.Client(loop=asyncio.get_event_loop())
        self.help = helper.Helper(config.PATH_HELP)
        self.idols = IdolsList()
        self.idols.load_from_json(config.IDOLS_FILE)
        self.input_author = None
        self.input_channel = None
        self.input_params = None
        self._connected = False

    async def call_function(self, name):
        fn = getattr(self, 'cmd_' + name, None)
        if fn is not None:
            await fn()

    def run(self):
        self.client.event(self.on_ready)
        self.client.event(self.on_message)
        self.client.run(config.DISCORD_TOKEN)

    async def on_ready(self):
        log.info(f"Cara Omnica connected to Discord ({config.DISCORD_TOKEN})")
        self._connected = True

    async def on_message(self, msg):
        # Assign temporary variables
        self.input_author = msg.author
        self.input_channel = msg.channel

        # Skip self messages and messages outside the dedicated channel
        if self.input_author == self.client.user:
            return False

        lp = lineparser.LineParser(msg.content)
        lp.process()
        if lp.get_action():
            log.debug(f"INPUT: {str(self.input_author)} - {msg.content}")

        action = lp.get_action()
        if not action:
            return False
        self.input_params = lp.get_params()
        try:
            await self.call_function(action)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            log.error(f"INPUT ERROR: {e}", exc_info=True)

        self.input_author = None
        self.input_channel = None
        self.input_params = None

    ####
    # ABOUT
    ####
    async def cmd_about(self):
        if not int(self.input_channel.id) == int(config.CHANNEL_ID):
            return False
        await self.input_author.send(self.help.get_about())

    ####
    # GET HELP
    ####
    async def cmd_help(self):
        if not int(self.input_channel.id) == int(config.CHANNEL_ID):
            return False
        cmd = ""
        if "help_command" in self.input_params:
            cmd = self.input_params["help_command"]
        await self.input_author.send(self.help.get_help(cmd))

    ####
    # ADD IDOL OWNER
    ####
    async def cmd_add_idol(self):
        input_channel = self.input_channel
        input_author = self.input_author
        input_params = self.input_params
        if not int(input_channel.id) == int(config.CHANNEL_ID):
            return False

        try:
            owner_to_add = input_params['owner_to_add']
        except KeyError:
            await input_channel.send(mc.prettify("No player inserted", "YELLOW"))
            return False

        if self.idols.has_idol(owner_to_add):
            await input_channel.send(mc.prettify(f"{owner_to_add} has already an idol", "YELLOW"))
            return False
        else:
            self.idols.add_idol(owner_to_add, str(input_author))
            await input_channel.send(mc.prettify(f"+ An idol was added to {owner_to_add}", "MD"))

        if 'owner_to_remove' in input_params:
            await self.cmd_del_idol()
        return True

    ####
    # DEL IDOL OWNER
    ####
    async def cmd_del_idol(self):

        input_channel = self.input_channel
        input_params = self.input_params
        if not input_channel.id == config.CHANNEL_ID:
            return False

        try:
            owner_to_remove = input_params['owner_to_remove']
        except KeyError:
            await input_channel.send(mc.prettify("No player inserted", "YELLOW"))
            return False

        if not self.idols.del_idol_by_owner(owner_to_remove):
            await input_channel.send(mc.prettify(f"{owner_to_remove} did not own any idol", "YELLOW"))
            return False
        else:
            await input_channel.send(mc.prettify(f"- An idol was removed from {owner_to_remove}", "MD"))
        return True

    ####
    # INFO IDOL
    ####
    async def cmd_info_idol(self):
        input_channel = self.input_channel
        input_params = self.input_params
        if not int(input_channel.id) == int(config.CHANNEL_ID):
            return False

        try:
            idol_owner = input_params['idol_owner']
        except KeyError:
            await input_channel.send(mc.prettify("No player inserted", "YELLOW"))
            return False
        idol = self.idols.has_idol(idol_owner)
        if not idol:
            await input_channel.send(mc.prettify(f"{idol_owner} has has no idol. Please type $idols for a list.", "YELLOW"))
            return False
        else:
            await input_channel.send(mc.prettify(str(idol), "MD"))
        return True

    ####
    # LIST IDOL OWNERS
    ####
    async def cmd_list_idols(self):
        input_channel = self.input_channel
        await input_channel.send(mc.prettify(mc.print_idol_owner_list(self.idols.get_all()), "MD"))


def main():

    linara = Cara()
    linara.run()


if __name__ == "__main__":

    # Generic logger
    if config.DEBUG:
        log = setup_logger('Cara', config.LOG_FILE, logging.DEBUG)
    else:
        log = setup_logger('Cara', config.LOG_FILE, logging.INFO)

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
    })
    main()

