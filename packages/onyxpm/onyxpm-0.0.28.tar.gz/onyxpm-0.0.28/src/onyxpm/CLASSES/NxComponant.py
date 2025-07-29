import json

class NxComponant:
    def __init__(self, object_type: str, primary_key: str, content:json, action_required: str, list_of_diff: str):
        self.object_type = object_type
        self.primary_key = primary_key
        self.content = content
        self.action_required = action_required
        self.list_of_diff = list_of_diff
        self.trg_id= None