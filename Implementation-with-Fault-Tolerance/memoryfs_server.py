from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from memoryfs_client import *
import sys, hashlib

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

port = int(sys.argv[1])
error_content = bytearray('error', 'utf-8')
error_flag = bytearray(error_content.ljust(BLOCK_SIZE, b'\x00'))

# Create server
with SimpleXMLRPCServer(('localhost', port), requestHandler=RequestHandler) as server:

    block = []
    checksums = []
    # Initialize raw blocks
    for i in range(0, TOTAL_NUM_BLOCKS):
        putdata = bytearray(BLOCK_SIZE)
        block.insert(i, putdata)
        checksums.insert(i, hashlib.md5(block[i]).hexdigest())

    if len(sys.argv) == 3:
        damage_block_number = int(sys.argv[2])
        block.insert(damage_block_number, error_flag)

    ## Put: interface to write a raw block of data to the block indexed by block number
    ## Blocks are padded with zeroes up to BLOCK_SIZE
    def Put(block_number, putdata):
        # Write block
        if len(sys.argv) == 3 and block_number == sys.argv[2]:
            return 0
        block[block_number] = putdata
        return 0
    server.register_function(Put, 'Put')

    ## Get: interface to read a raw block of data from block indexed by block number
    ## Equivalent to the textbook's BLOCK_NUMBER_TO_BLOCK(b)
    def Get(block_number):
        return block[block_number]
    server.register_function(Get, 'Get')

    def Put_Checksum(block_number, checksum):
        checksums[block_number] = checksum
        return 0
    server.register_function(Put_Checksum, 'Put_Checksum')

    def Get_Checksum(block_number):
        return checksums[block_number]
    server.register_function(Get_Checksum, 'Get_Checksum')

    # Run the server's main loop
    server.serve_forever()