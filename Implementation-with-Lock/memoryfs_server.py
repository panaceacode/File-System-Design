from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from memoryfs_client import *

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server
with SimpleXMLRPCServer(('localhost', 8080), requestHandler=RequestHandler) as server:

    block = []
    initialized = {'flag': 0}
    # Initialize raw blocks
    for i in range(0, TOTAL_NUM_BLOCKS):
        putdata = bytearray(BLOCK_SIZE)
        block.insert(i, putdata)

    def GetFlag():
        return initialized['flag']
    server.register_function(GetFlag, 'GetFlag')

    def SetFlag():
        initialized['flag'] = 1
        return 0
    server.register_function(SetFlag, 'SetFlag')

    ## Put: interface to write a raw block of data to the block indexed by block number
    ## Blocks are padded with zeroes up to BLOCK_SIZE
    def Put(block_number, putdata):
        # Write block
        block[block_number] = putdata
        return 0
    server.register_function(Put, 'Put')

    ## Get: interface to read a raw block of data from block indexed by block number
    ## Equivalent to the textbook's BLOCK_NUMBER_TO_BLOCK(b)
    def Get(block_number):
        return block[block_number]
    server.register_function(Get, 'Get')

    def ReadSetBlock(block_number, lock_flag):
        lock = block[block_number]
        Put(block_number, lock_flag)
        return lock
    server.register_function(ReadSetBlock, 'ReadSetBlock')

    # Run the server's main loop
    server.serve_forever()