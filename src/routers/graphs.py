import requests
from datetime import datetime
from config.variables import THIS_SERVICE
from config.redis_conf import redis_stream
from fastapi import APIRouter, Response, status

ROOT = "http://127.0.0.1/8002"

router = APIRouter(
    prefix="/followups"
)


@router.get("/node/{primary_key}", status_code=status.HTTP_200_OK)
async def get_node_by_primary_key(primary_key: str) -> list:
    """ Given a primary key this endpoint will return
    its corresponding node

    Args:
        primary_key (str): Entity primary key

    Returns:
        list: A list containing the graph's entity data
    """
    endpoint = f"{ROOT}/node/{primary_key}"
    r = requests.get(endpoint)
    return r.json()


@router.get("/graph/", status_code=status.HTTP_200_OK)
async def get_graph() -> list:
    """ Returns a graph (nodes with all their relationships)
    whithin a list

    Returns:
        list: List with nodes and edges
    """
    endpoint = f"{ROOT}/node"
    r = requests.get(endpoint)
    return r.json()


@router.post("/edge/", status_code=status.HTTP_202_ACCEPTED)
async def create_edge(node_follower_pk: str, node_followed_pk: str, properties: dict = { "date time": datetime.now() }) -> Response:
    """ Given two nodes by their primary keys, this endpoint sends
    an event regarding the edge creation

    Args:
        node_follower_pk (str): Primary key of the follower node
        node_followed_pk (str): Primary key of the followed node
        properties (dict, optional): Dictionary with the edge properties
        to store in the edge. Defaults to { "date time": datetime.now() }.

    Returns:
        Response: HTTP 202 Accepted
    """
    event = {
        'SENDER':THIS_SERVICE,
        'OP':'CREATE',
        'DATA':'NODE_FOLLOWER_PK, NODE_FOLLOWED_PK, PROPERTIES',
        'NODE_FOLLOWER_PK': node_follower_pk,
        'NODE_FOLLOWED_PK': node_followed_pk,
        'PROPERTIES': properties
    }
    await redis_stream.xadd('graph', event)
    return Response(
        content="Request sent",
        status_code=status.HTTP_202_ACCEPTED
    )


@router.delete("/edge/", status_code=status.HTTP_202_ACCEPTED)
async def delete_edge(node1_primary_key: str, node2_primary_key: str) -> Response:
    """ Given and edge, it will send an event regarding
    its deletion

    Args:
        node1_primary_key (str): One node of the edge
        node2_primary_key (str): The other node of the edge
    
    Return:
        Response: HTTP 202 Accepted
    """
    event = {
        'SENDER':THIS_SERVICE,
        'OP':'CREATE',
        'DATA':'NODE1_PRIMARY_KEY,NODE2_PRIMARY_KEY',
        'NODE1_PRIMARY_KEY':node1_primary_key,
        'NODE2_PRIMARY_KEY':node2_primary_key
    }
    await redis_stream.xadd('graph', event)
    return Response(
        content="Request sent",
        status_code=status.HTTP_202_ACCEPTED
    )
