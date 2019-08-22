import re
import logging

log = logging.getLogger("Linara")


class LineParser:

    def __init__(self, line: str):
        self.line = line
        self.low_line = self.line.lower()
        self.result = {'action': '', 'params': {}}
        self.command_list = {'$about': 'about',
                             '$help': 'help',
                             '+': 'add_idol',
                             '-': 'del_idol',
                             '?': 'info_idol',
                             '$idols': 'list_idols'
                             }

    def consume_line(self, string):
        if string:
            try:
                split_line = self.line.split(string)
                self.line = split_line[0] + split_line[1]
                self.line = self.line.strip()
                self.low_line = self.line.lower()
            except IndexError:
                pass

    def parse_command(self, cmd_list):
        for cmd in cmd_list:
            if self.low_line.startswith(cmd):
                self.result['action'] = cmd_list[cmd]
                # Consume the line
                self.line = self.line[len(cmd):].strip()
                self.low_line = self.low_line[len(cmd):].strip()
        return False

    def get_action(self):
        if self.result['action']:
            return self.result['action']
        return False

    def is_action(self, action):
        if action == self.result['action']:
            return True
        return False

    def get_params(self):
        return self.result['params']

    def set_param(self, name, value):
        if name and value:
            self.result['params'][name] = value
            return True
        return False

    def parse_first_word(self):
        first_word = self.low_line.split(' ', 1)[0]
        if first_word:
            self.consume_line(first_word)
            return first_word
        return ""

    def parse_snippet(self):
        reg = re.search(r"(['\"](.*?)['\"])", self.line)
        if reg:
            self.consume_line(reg.group(1))
            return reg.group(2)
        return ""

    def parse_square_brackets(self):
        reg = re.search(r"([\[](.*?)[\]])", self.line)
        if reg:
            self.consume_line(reg.group(1))
            return reg.group(2)
        return ""

    def parse_word(self, word):
        regex = r"\b(%s)\b" % word
        reg = re.search(regex, self.low_line)
        if reg:
            self.consume_line(reg.group(1))
            return True
        return False

    def process(self):
        if not self.line:
            return False

        self.parse_command(self.command_list)

        ##
        # PARSING COMMAND SPECIFIC PARAMS
        ##
        if self.is_action('help'):
            self.set_param("help_command", self.parse_first_word())

        if self.is_action('add_idol'):
            reg = re.search(r"^(([A-Za-z]+)([^A-Za-z]+)?)(from (\w+))?", self.low_line)
            if reg:
                if reg.group(2):
                    self.set_param('owner_to_add', reg.group(2).capitalize())
                if reg.group(5):
                    self.set_param('owner_to_remove', reg.group(5).capitalize())

        if self.is_action('del_idol'):
            self.set_param('owner_to_remove', self.parse_first_word().capitalize())

        if self.is_action('info_idol'):
            self.set_param('idol_owner', self.parse_first_word().capitalize())
