from memoryfs_client import *
import time

## This class implements an interactive shell to navigate the file system

class FSShell():
  def __init__(self, file):
    # cwd stored the inode of the current working directory
    # we start in the root directory
    self.cwd = 0
    self.FileObject = file

  # implements cd (change directory)
  def cd(self, dir):
    i = self.FileObject.GeneralPathToInodeNumber(dir,self.cwd)
    if i == -1:
      print ("Error: not found\n")
      return -1
    inobj = InodeNumber(self.FileObject.RawBlocks,i)
    inobj.InodeNumberToInode()
    if inobj.inode.type != INODE_TYPE_DIR:
      print ("Error: not a directory\n")
      return -1
    self.cwd = i
    return 0

  # implements mkdir
  def mkdir(self, dir):
    i = self.FileObject.Create(self.cwd, dir, INODE_TYPE_DIR)
    if i == -1:
      print ("Error: cannot create directory\n")
      return -1
    return 0

  # implements create
  def create(self, file):
    i = self.FileObject.Create(self.cwd, file, INODE_TYPE_FILE)
    if i == -1:
      print ("Error: cannot create file\n")
      return -1
    return 0

  # implements append
  def append(self, filename, string):
    i = self.FileObject.Lookup(filename, self.cwd)
    if i == -1:
      print ("Error: not found\n")
      return -1
    inobj = InodeNumber(self.FileObject.RawBlocks,i)
    inobj.InodeNumberToInode()
    if inobj.inode.type != INODE_TYPE_FILE:
      print ("Error: not a file\n")
      return -1
    # time.sleep(3)
    written = self.FileObject.Write(i, inobj.inode.size, bytearray(string,"utf-8"))
    print ("Successfully appended " + str(written) + " bytes.")
    return 0
    
  # implements link
  def link(self, target, name):
    # time.sleep(3)
    i = self.FileObject.Link(target, name, self.cwd)
    if i == -1:
      print ("Error: cannot create link\n")
      return -1
    return 0

  # implements ls (lists files in directory)
  def ls(self):
    inobj = InodeNumber(self.FileObject.RawBlocks, self.cwd)
    inobj.InodeNumberToInode()
    block_index = 0
    while block_index <= (inobj.inode.size // BLOCK_SIZE):
      block = self.FileObject.RawBlocks.Get(inobj.inode.block_numbers[block_index])
      if block_index == (inobj.inode.size // BLOCK_SIZE):
        end_position = inobj.inode.size % BLOCK_SIZE
      else:
        end_position = BLOCK_SIZE
      current_position = 0
      while current_position < end_position:
        entryname = block[current_position:current_position+MAX_FILENAME]
        entryinode = block[current_position+MAX_FILENAME:current_position+FILE_NAME_DIRENTRY_SIZE]
        entryinodenumber = int.from_bytes(entryinode, byteorder='big')
        inobj2 = InodeNumber(self.FileObject.RawBlocks, entryinodenumber)
        inobj2.InodeNumberToInode()
        if inobj2.inode.type == INODE_TYPE_DIR:
          print ("[" + str(inobj2.inode.refcnt) + "]:" + entryname.decode() + "/")
        else:
          print ("[" + str(inobj2.inode.refcnt) + "]:" + entryname.decode())
        current_position += FILE_NAME_DIRENTRY_SIZE
      block_index += 1
    return 0

  # implements cat (print file contents)
  def cat(self, filename):
    i = self.FileObject.Lookup(filename, self.cwd)
    if i == -1:
      print ("Error: not found\n")
      return -1
    inobj = InodeNumber(self.FileObject.RawBlocks,i)
    inobj.InodeNumberToInode()
    if inobj.inode.type != INODE_TYPE_FILE:
      print ("Error: not a file\n")
      return -1
    data = self.FileObject.Read(i, 0, MAX_FILE_SIZE)
    print (data.decode())
    return 0

  def ACQUIRE(self):
    lock_block = 0
    lock_flag = b'\x01'
    cur_lock = self.FileObject.RawBlocks.server.ReadSetBlock(lock_block, lock_flag)
    while cur_lock == lock_flag:
      cur_lock = self.FileObject.RawBlocks.server.ReadSetBlock(lock_block, lock_flag)

  def RELEASE(self):
    lock_block = 0
    unlock_flag = b'\x00'
    self.FileObject.RawBlocks.server.Put(lock_block, unlock_flag)

  def show_request(self):
    print("")
    print("Put() request number: " + str(self.FileObject.RawBlocks.servers_put))
    print("Get() request number: " + str(self.FileObject.RawBlocks.servers_get))

  def Interpreter(self):
    try:
      while (True):
        command = input("[cwd=" + str(self.cwd) + "]:")
        splitcmd = command.split()
        if len(splitcmd) >= 1:
          self.ACQUIRE()
          if splitcmd[0] == "cd":
            if len(splitcmd) != 2:
              print("Error: cd requires one argument")
            else:
              self.cd(splitcmd[1])
          elif splitcmd[0] == "cat":
            if len(splitcmd) != 2:
              print("Error: cat requires one argument")
            else:
              self.cat(splitcmd[1])
          elif splitcmd[0] == "mkdir":
            if len(splitcmd) != 2:
              print("Error: mkdir requires one argument")
            else:
              self.mkdir(splitcmd[1])
          elif splitcmd[0] == "create":
            if len(splitcmd) != 2:
              print("Error: create requires one argument")
            else:
              self.create(splitcmd[1])
          elif splitcmd[0] == "ln":
            if len(splitcmd) != 3:
              print("Error: ln requires two arguments")
            else:
              self.link(splitcmd[1], splitcmd[2])
          elif splitcmd[0] == "append":
            if len(splitcmd) != 3:
              print("Error: append requires two arguments")
            else:
              self.append(splitcmd[1], splitcmd[2])
          elif splitcmd[0] == "ls":
            self.ls()
          elif splitcmd[0] == "exit":
            return
          elif splitcmd[0] == "show_request":
            self.show_request()
          else:
            print("command " + splitcmd[0] + "not valid.\n")
        self.RELEASE()
    except EOFError:
      self.show_request()


if __name__ == "__main__":

  # Initialize file for logging
  # Changer logging level to INFO to remove debugging messages
  logging.basicConfig(filename='memoryfs.log', filemode='w', level=logging.DEBUG)

  # Replace with your UUID, encoded as a byte array
  UUID = b'\x12\x34\x56\x78'

  # Initialize file system data
  logging.info('Initializing data structures...')
  RawBlocks = DiskBlocks('http://localhost:8080')

  flag = RawBlocks.server.GetFlag()
  if flag == 0:
    # Load blocks from dump file
    unlock_flag = b'\x00'
    # RawBlocks.InitializeBlocks(False,UUID)
    RawBlocks.InitializeBlocks(True, UUID)
    RawBlocks.server.Put(0, unlock_flag)
    RawBlocks.server.SetFlag()

  # Show file system information and contents of first few blocks
  RawBlocks.PrintFSInfo()
  RawBlocks.PrintBlocks("Initialized",0,16)

  # Initialize FileObject inode
  FileObject = FileName(RawBlocks)
  FileObject.InitRootInode()

  myshell = FSShell(FileObject)
  myshell.Interpreter()
