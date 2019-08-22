import config
import json
import timehandler as timeh
from datetime import datetime
import logging

log = logging.getLogger("Cara")


class Idol:

    def __init__(self, owner, author, date=None):
        self.owner = owner
        if not date:
            self.date_added = timeh.now()
        else:
            self.date_added = datetime.strptime(date, config.DATE_FORMAT)
        self.added_by = author

    def __repr__(self):
        return f"IDOL\n- owner: {self.owner}\n- date added: {self.date_added}\n- added by: {self.added_by}\n"

    def get(self):
        return self.owner

    def serialize(self):
        return {"owner": self.owner, "date": self.date_added.strftime(config.DATE_FORMAT), "author": self.added_by}


class IdolsList:

    def __init__(self):
        self.idols = []
        self.json_file_url = ""

    def __repr__(self):
        output = "# IDOLS\n------\n\n"
        for idol in self.idols:
            output += str(idol)
        return output

    def load_from_json(self, json_file_url):
        self.json_file_url = json_file_url
        with open(json_file_url) as f:
            for idol in json.load(f):
                try:
                    self.idols.append(Idol(idol["owner"], idol["author"], idol["date"]))
                except KeyError:
                    log.error("IDOLS LOAD: Error loading from json file")

    def save_to_json(self):
        json_output = []
        for idol in self.idols:
            json_output.append(idol.serialize())

        with open(self.json_file_url, "w") as outfile:
            json.dump(json_output, outfile, indent=4)

    def add_idol(self, owner, author):
        self.idols.append(Idol(owner, author))
        self.save_to_json()

    def del_idol_by_owner(self, owner):
        before_len = len(self.idols)
        self.idols = [idol for idol in self.idols if not idol.owner.lower() == owner.lower()]
        if before_len == len(self.idols):
            return False
        self.save_to_json()
        return True

    def has_idol(self, owner):
        for idol in self.idols:
            if owner.lower() == idol.owner.lower():
                return idol
        return False

    def get_all(self):
        return self.idols
