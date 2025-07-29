import json

class NxComponantAttributes:
    def __init__(self, json_object: str, comparable_attributes: []):
        self.json_object = json_object
        self.comparable_attributes = comparable_attributes

