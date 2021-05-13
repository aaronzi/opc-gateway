import sys
sys.path.insert(0, "..")

import logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

from IPython import embed

from asyncua import Client, Node, ua
from asyncua.tools import application_to_strings
from asyncua.tools import add_minimum_args
from asyncua.tools import parse_args
from asyncua.tools import endpoint_to_strings

import numpy as np
import asyncio
import argparse
import concurrent.futures

class SubscriptionHandler:
    """
    The SubscriptionHandler is used to handle the data that is received for the subscription.
    """
    def datachange_notification(self, node: Node, val, data):
        """
        Callback for asyncua Subscription.
        This method will be called when the Client received a data change message from the Server.
        """
        _logger.info('datachange_notification %r %s', node, val)



async def read(data):
    client = Client(data['opcUrl'])
    client.name = "TOTO"
    client.application_uri = "urn:freeopcua:clientasync"
    async with client:
        struct = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.stringStatus")
        readVal = await struct.read_value()
        return readVal

async def writeX(data):
    client = Client(data['opcUrl'])
    client.name = "TOTO"
    client.application_uri = "urn:freeopcua:clientasync"
    async with client:
        struct = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.intXPos")
        await struct.write_value(data['xPos'], ua.VariantType.Int16)

async def writeY(data):
    client = Client(data['opcUrl'])
    client.name = "TOTO"
    client.application_uri = "urn:freeopcua:clientasync"
    async with client:
        struct = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.intYPos")
        await struct.write_value(data['yPos'], ua.VariantType.Int16)

async def subscribe(data):
    url = data['opcUrl']
    async with Client(url=url) as client:
        # get the root Node (this is the url itself acting as root to all sub/child-Nodes)
        _logger.info("Root node is: %r", client.nodes.root)
        # get Objects Node (located one beneath the root node; contains all of the opc data in variables)
        _logger.info("Objects node is: %r", client.nodes.objects)
        # get child Nodes (includes the Objects Node plus the Types and the View Node)
        _logger.info("Children of root are: %r", await client.nodes.root.get_children())

        # return 'Root Node: ' + str(client.nodes.root) + '; Objects Node: ' + str(client.nodes.objects) + '; Child Nodes: ' + str(await client.nodes.root.get_children())

        myvar = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.stringStatus")
        # myvar = await client.nodes.objects.get_child(["Server", "2:CODESYS Control Win V3 x64", "2:Resources", "2:Application", "2:GlobalVars", "2:GVL", "2:stringStatus"])
        _logger.info("myvar is: %r", myvar)
        
        
        _logger.info("Children of objects Node are: %r", await client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.stringStatus").get_children())

        # handler = SubscriptionHandler()
        # # create a Client Subscription.
        # subscription = await client.create_subscription(1000, handler)
        # # nodes that will be listened to
        # nodes = [
        #     myvar,
        #     client.get_node(ua.ObjectIds.Server_ServerStatus_CurrentTime),
        # ]
        # # subscribe to data changes for nodes (variables).
        # await subscription.subscribe_data_change(nodes)
        # # subscription runs for x seconds
        # x = 1000
        # await asyncio.sleep(x)
        # # delete the subscription (this un-subscribes from the data changes of the variables).
        # # This is optional since closing the connection will also delete all subscriptions.
        # await subscription.delete()
        # # exit the Client context manager after one second - this will close the connection.
        # await asyncio.sleep(1)

async def connectUa(data):
    print(data['url'])
    client = Client(data['url'])
    client.name = "TOTO"
    client.application_uri = "urn:freeopcua:clientasync"
    try:
        async with client:
            struct = client.get_node(ua.ObjectIds.Server_ServerStatus_CurrentTime)
            time = await struct.read_value()
            return time
    except:
        return 'failed'