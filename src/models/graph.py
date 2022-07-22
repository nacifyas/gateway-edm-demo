from pydantic import BaseModel
from redis.commands.graph.node import Node

class User(BaseModel):
    pk: str
    username: str
    age: int


    def to_node(self):
        properties = dict(self)
        pk = properties.get("pk")
        return Node(node_id=pk, label="User", properties=properties)