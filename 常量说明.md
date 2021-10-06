# File-System-Design
RAID-5 file system implementation.

# _常量说明：_
## _固定值常量：_
TOTAL_NUM_BLOCKS = 256 -> _文件数据储存底层的数据块总数_

BLOCK_SIZE = 128 -> _单个数据块容量（单位为bytes）_

MAX_NUM_INODES = 16 -> _最大innode数量_

INODE_SIZE = 16 -> _单个inode大小（单位为bytes）_

MAX_FILENAME = 12 -> _最大文件名长度，单位为字符_

INODE_NUMBER_DIRENTRY_SIZE = 4 -> _储存一个inode编号的大小_

INODES_PER_BLOCK = BLOCK_SIZE // INODE_SIZE -> _一个数据块中可以放置的inode数量_

## _推导值：_
_（文件系统假定数据块0为root block，数据块1为super block）_<br>
_因此可用数据块的bitmap的偏移地址从2开始_<br>
FREEBITMAP_BLOCK_OFFSET = 2

_bitmap所需要的数据块数量（为简化系统设计，避免位操作，bitmap的每个entry都是1 byte），总数据块数量 / 单个数据块大小_<br>
FREEBITMAP_NUM_BLOCKS = TOTAL_NUM_BLOCKS // BLOCK_SIZE

_inode的起始数据块从2+bitmap所需数据块数量_<br>
INODE_BLOCK_OFFSET = 2 + FREEBITMAP_NUM_BLOCKS

_inode表所占的数据块数量 = （inode数量 * 单个inode大小）/ 单个数据块大小_<br>
INODE_NUM_BLOCKS = (MAX_NUM_INODES * INODE_SIZE) // BLOCK_SIZE

_假定一个inode中，4 bytes容量记录inode代表的文件或目录大小，2 bytes记录inode类型，2 bytes记录引用计数，剩余bytes即可记录inode中含有的数据块的块编号_<br>
_一个inode中最大的数据块编号数量:_<br>
MAX_INODE_BLOCK_NUMBERS = (INODE_SIZE - 8) // 4

_单个文件最大大小，inode中最大数据块编号的数量 * 单个数据块大小_<br>
MAX_FILE_SIZE = MAX_INODE_BLOCK_NUMBERS * BLOCK_SIZE

_储存数据的数据块为：inode数据块偏移地址 + inode数据块的数量_<br>
DATA_BLOCKS_OFFSET = INODE_BLOCK_OFFSET + INODE_NUM_BLOCKS

_储存数据的数据块总数为：总数据块数量 - data数据块起始位置_<br>
DATA_NUM_BLOCKS = TOTAL_NUM_BLOCKS - DATA_BLOCKS_OFFSET

_directory entry是文件名+inode number_<br>
FILE_NAME_DIRENTRY_SIZE = MAX_FILENAME + INODE_NUMBER_DIRENTRY_SIZE

_单个数据块中最大的directory entry_<br>
FILE_ENTRIES_PER_DATA_BLOCK = BLOCK_SIZE // FILE_NAME_DIRENTRY_SIZE


_inode的类型_<br>
INODE_TYPE_INVALID = 0 -> 无效<br>
INODE_TYPE_FILE = 1 -> 文件<br>
INODE_TYPE_DIR = 2 -> 文件夹<br>
INODE_TYPE_SYM = 3 -> 系统<br>
