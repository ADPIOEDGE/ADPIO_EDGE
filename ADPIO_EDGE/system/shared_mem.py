from multiprocessing.shared_memory import ShareableList

server_mem_name = 'server_mem'
STATUS_MEM_ADDR     = 0
#WORKERS_MEM_ADDR   = 1 3 #depreciated
DB_REBUILD_MEM_ADDR = 1
#TERMINAL_MEM_ADDR  = 3 #depreciated
LORA_MEM_ADDR       = 2

BCNT_DB_MEM_ADDR    = 3
BCNT_CMD_MEM_ADDR   = 4

def init_server_mem(lora_alloc = 100, bacnet_alloc = 250, terminal = False, auto_rebuild = False):
    try:
        SERVER_MEM = ShareableList(name=server_mem_name) 
        SERVER_MEM.shm.close()
        SERVER_MEM.shm.unlink()
    except:
        if __debug__:
            print("Server Memory Not Exists")

    SERVER_MEM = ShareableList( [
        0,              # Server Status 0 - Not Init, 1 - Run Signal, 2 - Shutdown Signal
        #0,              # Workers Count
        auto_rebuild,   # First DB Init
        #terminal,       # Ouput into Terminal or into GUI
        " " * 1024 * lora_alloc,   # LoRaWAN Serialized Size may be too small (in 1024 x kb = bytes )
        " " * 1024 * bacnet_alloc, # BACnet DB  Serialized Size may be too small  (in 1024 x kb = bytes )
        " " * 512  * bacnet_alloc, # BACnet CMD Serialized Size may be too small  (in 1024 x kb = bytes / 2 )
    ], name=server_mem_name)

    SERVER_MEM[LORA_MEM_ADDR]       = "[]"
    SERVER_MEM[BCNT_DB_MEM_ADDR]    = "[]"
    SERVER_MEM[BCNT_CMD_MEM_ADDR]   = "[]"

    if __debug__:
        print("Shared Mem Initialized")
        


def clear_server_mem():
    SERVER_MEM = get_server_mem()

    SERVER_MEM.shm.close()
    SERVER_MEM.shm.unlink()


def get_server_mem():
    try:
        return ShareableList(name=server_mem_name) 
    except:
        print("Server Memory Does not exist")
        return [
            2,   # Server Status 0 - Not Init, 1 - Run Signal, 2 - Shutdown Signal
            #-1,  # Workers Count
            False,# First DB Init
            #False,
            "[]",
            "[]",
            "[]",
        ]
