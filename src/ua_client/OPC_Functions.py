import sys
sys.path.insert(0, "..")

import logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

from IPython import embed
import uuid

from asyncua import Client, Node, ua
from asyncua.tools import application_to_strings
from asyncua.tools import add_minimum_args
from asyncua.tools import parse_args
from asyncua.tools import endpoint_to_strings

import numpy as np
import asyncio
import argparse
import concurrent.futures

import time


sys.path.append('d:\\Main Folders (important)\\Dokumente\\Schule+Uni\\HTW\\Praktikum\\opc-communication\\opc-gateway\\src\\ua_client\\snippets')
from objects import ObjectIds

changedData = []

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
        test = {"NodeID": str(node), "Value": str(val)}
        changedData.append(test)

# Method to connect with the OPC Server
async def connectUa(data):
    client = Client(data['opcUrl'])
    client.name = "TOTO"
    client.application_uri = "urn:freeopcua:clientasync"
    try:
        async with client:
            struct = client.get_node(ua.ObjectIds.Server_ServerStatus_CurrentTime)
            time = await struct.read_value()
            return time
    except:
        return 'failed'

# Method to get the OPC Data Structure
async def getStructure(data):
    url = data['opcUrl']
    async with Client(url=url) as client:
        nodes = []
        async def getStruct(pNode):
            if(await pNode.get_children() != []):
                for node in await pNode.get_children():
                    attrs = await node.read_attributes(
                        [
                            ua.AttributeIds.DisplayName,
                            ua.AttributeIds.BrowseName,
                            ua.AttributeIds.NodeClass,
                            ua.AttributeIds.WriteMask,
                            ua.AttributeIds.UserWriteMask,
                            ua.AttributeIds.DataType,
                            ua.AttributeIds.Value,
                        ]
                    )
                    name, bname, nclass, mask, umask, dtype, val = [attr.Value.Value for attr in attrs]
                    # print(str(dtype)[-1])
                    data_type = ''
                    for datype, num in ObjectIds.items():
                        if str(num) == str(dtype)[-1]:
                            data_type = datype
                    if(await node.get_children() != []):
                        if nclass == ua.NodeClass.Variable:
                            nodes.append(
                                {
                                    "name": bname.to_string()[2:],
                                    "DisplayName": name.to_string(), 
                                    "NodeID": node.nodeid.to_string(),
                                    "NodeClass": str(nclass),
                                    "id": str(uuid.uuid4()),
                                    "dataType": str(data_type), 
                                    "Value": str(val).replace("'","").replace('"',''),
                                    "icon": "variable",
                                    "children": []
                                }
                            )
                        else:
                            nodes.append(
                                {
                                    "name": bname.to_string()[2:],
                                    "DisplayName": name.to_string(), 
                                    "NodeID": node.nodeid.to_string(),
                                    "NodeClass": str(nclass),
                                    "id": str(uuid.uuid4()), 
                                    "icon": "folder",
                                    "children": []
                                }
                            )
                    else:
                        if nclass == ua.NodeClass.Variable:
                            nodes.append(
                                {
                                    "name": bname.to_string()[2:],
                                    "DisplayName": name.to_string(), 
                                    "NodeID": node.nodeid.to_string(),
                                    "NodeClass": str(nclass),
                                    "id": str(uuid.uuid4()),
                                    "dataType": str(data_type), 
                                    "Value": str(val).replace("'","").replace('"',''),
                                    "icon": "variable"
                                }
                            )
                        else:
                            nodes.append(
                                {
                                    "name": bname.to_string()[2:],
                                    "DisplayName": name.to_string(), 
                                    "NodeID": node.nodeid.to_string(),
                                    "NodeClass": str(nclass),
                                    "id": str(uuid.uuid4()),
                                    "icon": "folder"
                                }
                            )
        if(data['nodeID'] == 'root'):
            await getStruct(client.nodes.root) # start building opc structure tree with root node (childs of root)
        else:
            otherNode = client.get_node(data['nodeID'])
            await getStruct(otherNode)
        return nodes

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

# async def subscribe(data):
#     url = data['opcUrl']
#     nodeIDs = data['NodeIDS']
#     async with Client(url=url) as client:
#         # nodes that will be listened to
#         nodes = []
#         for nodeID in nodeIDs:
#             nodes.append(client.get_node(nodeID))
#         # handler for data subscription
#         handler = SubscriptionHandler()
#         # create a Client Subscription. Update rate in ms
#         subscription = await client.create_subscription(100, handler)
#         # subscribe to data changes for nodes (variables).
#         await subscription.subscribe_data_change(nodes)
#         # subscription time in seconds
#         x = 28.90
#         await asyncio.sleep(x)
#         # delete the subscription (this un-subscribes from the data changes of the variables).
#         # This is optional since closing the connection will also delete all subscriptions.
#         await subscription.delete()
#         client.disconnect()

async def readSubscribed(data):
    oldVals = data['oldVals']
    oldData = []
    for val in oldVals:
        dataOld = {'NodeID': val['NodeID'], 'Value': val['Value']}
        oldData.append(dataOld)
    client = Client(data['opcUrl'])

    client.name = "TOTO"
    client.application_uri = "urn:freeopcua:clientasync"

    async with client:
        for i in range(290):
            returnVal = []
            for nodeID in oldData:
                struct = client.get_node(nodeID['NodeID'])
                readVal = await struct.read_value()
                data = {'NodeID': nodeID['NodeID'], 'Value': str(readVal)}
                returnVal.append(data)
            for i in returnVal:
                if i not in oldData:
                    return returnVal
            asyncio.sleep(0.1)
        return
    
