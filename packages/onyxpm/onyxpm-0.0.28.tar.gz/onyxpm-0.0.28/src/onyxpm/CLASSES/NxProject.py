import json


class NxProject:
    def __init__(self, id: str, name:str, content:json, componants:[]):
        self.id = id
        self.name = name
        self.content = content
        self.componants = componants
