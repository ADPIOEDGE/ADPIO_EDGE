import asyncio
import os

from py_compile             import compile
from system.settings_server import settings_cfg
from system.globals         import ROOT_FOLDER, WORKSPACE, APPS_FOLDER

from multiprocessing.shared_memory import ShareableList

from content.app_ide_datapoints import load_datapoints, save_mem_alloc
from content.app_ide_graphics   import reorder_graphics
from content.app_ide_logic      import load_blocks, save_bind_alloc
from assets.dataconversion      import set_mem_value, get_mem, get_binds

from drivers.loraWAN_conn_sever import add_app_loraWAN_sync, free_app_loraWAN_sync
from drivers.bacnet_server      import add_app_BACnet_sync, free_app_BACnet_sync


from content.logger import print_app_event

PYTHON_SYS = ""

def init_settings():
    global PYTHON_SYS

    settings = settings_cfg()
    settings.read_settings()
    PYTHON_SYS = settings.python


async def build_app(app):
    APP_SRC  = f'{ROOT_FOLDER}/assets/app_main_src.py' #do not confuse with assets in workfolder
    APP_EXE  = f'{APPS_FOLDER}/{app}/app_main.py'

    print(f'>>>> Building {app} <<<<')  

    datapoints      = load_datapoints(app)
    datapoints      = save_mem_alloc(app, datapoints) #Allocate Memory

    block_list      = load_blocks(app)

    libimport, getters, setters, constants, blocks, binds = sort_blocks(block_list)   

#read contents
    with open(APP_SRC, "r") as src_file:
        src_code = src_file.read()
        src_file.close()

#Do code shenanigans 
    src_code = build_header_app_info(app, src_code, libimport, datapoints)
    src_code = build_datapoints     (src_code, datapoints)

    src_code, binds = build_binds  (app, src_code, binds)   #, constants, block_list)
    
    src_code = build_sets   (src_code, datapoints, setters, binds)
    src_code = build_gets   (src_code, datapoints, getters, constants, binds)
    src_code = build_blocks (src_code, blocks, binds)
    
    src_code = build_trends (src_code, datapoints)

#write contents    
    with open(APP_EXE, "w") as app_file:
        app_file.write(src_code)
        app_file.close()

    compile(APP_EXE) #compile from pycompiller stuff

#graphics
    reorder_graphics(app)

    print(f'>>>> {app} Done <<<<')  
    print(' ')

#***** Build Header *****
def build_header_app_info(app, src_code, libimport_list, datapoints):
    src_code = src_code.replace('APP_NAME   = "nonameapp"', f'APP_NAME   = "{app}"')
    src_code = src_code.replace('#<DATAPOINTS_LENGTH/>',    f'{len(datapoints)},')

    libimport_src = ''
    libimport_src += f"sys.path.append('{WORKSPACE}') #Fix for parent folder import embed_lib\n"
    
    for rec in libimport_list:
        libimport_src += f'{rec}\n'

    src_code = src_code.replace('#<LIBIMPORT/>', libimport_src)    

    return src_code

def find_bind(b_list, f_id, io_indx):
    return next((rec for rec in b_list if (rec['f_id'] == f_id and rec['io'] == io_indx)), None)


#***** Datapoints *****
def build_datapoints(src_code, datapoints):
    inject_code_mem = '\n'

    for dp in datapoints:         
        match dp['datatype']: #this one used only to set allocation
            case "bool":
                inject_code_mem += f'            {False}, #{dp['group']}: {dp['name']} [{dp['memalloc']}] - bool\n'
            case "int":
                inject_code_mem += f'            {10},    #{dp['group']}: {dp['name']} [{dp['memalloc']}] - int\n'
            case "float":
                inject_code_mem += f'            {0.1},   #{dp['group']}: {dp['name']} [{dp['memalloc']}] - float\n'
            case "str":
                inject_code_mem += f'            "{'PLACEHOLDER'}",     #{dp['group']}: {dp['name']} [{dp['memalloc']}] - str\n'  #Need length to setup correctly
            case _: 
                print(f'Unknown Data Type  {dp['datatype']}')
                inject_code_mem += f'            {None},    #{dp['group']}: {dp['name']} [{dp['memalloc']}] - {dp['datatype']}\n'  #Need length to setup correctly
            
        
    src_code = src_code.replace('            #<DATAPOINTS_DEF/>',   inject_code_mem) #Make Shared Mem List

    return src_code    


def build_gets(src_code, datapoints, g_list, cons_list, b_list): 
    inject_code = ''

    for g_rec in g_list:
        bnd = find_bind(b_list, g_rec['id'], 0)

        for dp in datapoints:
            if f'{dp['group']}:{dp['name']}' == f'{g_rec['name']}':
                inject_code += f'            bind_mem[{bnd['mem']}] = shared_mem[{dp['memalloc']}] #{dp['group']}: {dp['name']}\n'

    for c_rec in cons_list:
        bnd = find_bind(b_list, c_rec['id'], 0)
        inject_code += f'            bind_mem[{bnd['mem']}] = {c_rec['io'][0]['value']}\n'

    src_code = src_code.replace('            #<GETTERS_CODE/>',          inject_code) #Define Defaults
    return src_code  


def build_sets(src_code, datapoints, s_list, b_list):
    inject_code = ''

    for s_rec in s_list:
        for dp in datapoints:
            if f'{dp['group']}:{dp['name']}' == f'{s_rec['name']}':

                bnd = find_bind(b_list, s_rec['io'][0]['bind']['bind_id'], s_rec['io'][0]['bind']['bind_io_index'])
                inject_code += f'            shared_mem[{dp['memalloc']}] = bind_mem[{bnd['mem']}] #{dp['group']}: {dp['name']} = {bnd['name']}\n'

    src_code = src_code.replace('            #<SETTERS_CODE/>',          inject_code) #Define Defaults    
    return src_code  


def build_blocks(src_code,  block_list, bind_list):
    inject_code = ''

    for b_rec in block_list:
        code = b_rec['function']
        out_code = ''
        for indx, io_rec in enumerate(b_rec['io']):

            match io_rec['type']:
                case 'input':
                    if io_rec['bind'] != {}:
                        bnd = find_bind(bind_list, io_rec['bind']['bind_id'], io_rec['bind']['bind_io_index'])
                        
                        code_splt = code.split( "(" ) #Make sure that we replace only in (var1, var2 ...)
                        code_splt[1] = code_splt[1].replace(io_rec['id'], f'bind_mem[{bnd['mem']}]')  

                        code = f"{code_splt[0]}({code_splt[1]}" 

                case 'output':
                    bnd = find_bind(bind_list, b_rec['id'], indx)
                    if out_code == '':
                        out_code += f'bind_mem[{bnd['mem']}]'
                    else:
                        out_code += f', bind_mem[{bnd['mem']}]'
                case _:
                    print('Err, unknown input/output type')

        code = f'{out_code} = {code}'
        inject_code += f'            {code}\n'

    src_code = src_code.replace('            #<BLOCK_CODE/>',          inject_code) #Define Defaults
    return src_code  


def build_binds(app, src_code, b_list):# c_list, block_list):
    inject_code_mem = ''

    mem = 1
    for b_rec in b_list: #Binds
        b_rec['mem'] = mem
        inject_code_mem += f'            None, #{b_rec['name']}, alloc = {b_rec['mem']}\n'
        save_bind_alloc(app, b_rec['f_id'], b_rec['io'], mem - 1) #need -1 because we do not send array length
        mem += 1

    src_code = src_code.replace('#<BINDS_LENGTH/>',    f'{len(b_list)},') #Define Defaults
    src_code = src_code.replace('            #<BINDS_DEF/>',   inject_code_mem) #Make Bind Mem List

    return src_code,  b_list


def build_trends(src_code, datapoints):
    inject_code_def = ''

    for dp in datapoints:
        if dp['trend']['enable'] == True:
            inject_code_def += f'        {{"name": "{dp["name"]}", "refresh": {dp["trend"]["refresh"]}, "left": {6}, "memalloc": {dp["memalloc"]}, "datatype": "{dp["datatype"]}", "old_value": "{dp["value"]}" }},'

    src_code = src_code.replace('        #<TRENDS_INIT>',          inject_code_def) #Init Trends

    return src_code  


#***** SORT BLOCKS *****
def sort_blocks(blocks):
    getter_list    = []
    setter_list    = []
    constant_list  = []
    block_list     = []
    bind_list      = [] #{f_id, io, mem=0}
    ordered_blocks = []
    import_list    = []

    #sort blocks by type
    for blk in blocks:
        match blk['type']:
            case 'datapoint-set':
                setter_list.append(blk)
            case 'datapoint-get':
                getter_list.append(blk)
            case 'constant':
                constant_list.append(blk)
            case _:
                block_list.append(blk)


    #Scanning for Binds, starting from 'behind' (sets and blocks without outputs)
    for setr in setter_list:
        for io_rec in setr["io"]:
            if io_rec['bind'] != {}:
                bind_list = add_bind(bind_list, io_rec)

#Import List
    for blk in block_list:
        if blk['libimport'] not in import_list:
            import_list.append(blk['libimport'])

#no binds
    antiloop = len(block_list) #antiloop is used to avoid the cases when block can not be filtered, when something is not binded to input 
    while len(block_list) > 0 and antiloop > -1:
        antiloop -= 1
        for blk in block_list:
            quit_loop = False
            out_status = 1 #if 0 - not everything binded
            for io_indx, io_rec in enumerate(blk["io"]):
                if io_rec['type'] == 'output':
                    if f"bind_{blk['id']}_{io_indx}" in bind_list:
                        out_status *= 0 #found not binded element

            if out_status == 1: #All outs are binded, add element to the end of ordered list
                ordered_blocks.append(blk)
                quit_loop = True
                for io_rec in blk["io"]:
                    if io_rec['bind'] != {}:
                        bind_list = add_bind(bind_list, io_rec)                 


            if quit_loop: #quit after founding fully binded element 
                block_list.pop(block_list.index(blk))
                break
    
    #add unsorted at the end
    ordered_blocks.extend(block_list)

    print(f"App Statistics: gets={len(getter_list)}, sets={len(setter_list)}, const={len(constant_list)}, binds={len(bind_list)} ")
    print(f"Block Sorting: sorted={len(ordered_blocks)}, unsorted={len(block_list) - 1}" )

    return import_list, getter_list, setter_list, constant_list, ordered_blocks, bind_list


def add_bind(bind_list, io_rec):
    new_rec = { 
        "name": f"bind_{io_rec['bind']['bind_id']}_{io_rec['bind']['bind_io_index']}",
        "f_id": io_rec['bind']['bind_id'], 
        "io": io_rec['bind']['bind_io_index'], 
        "mem": 0 
    } 
    for rec in bind_list: #check for repeats
        if f'{rec['name']}' == f'{new_rec['name']}':
            return bind_list

    bind_list.append( new_rec ) #blk                        
        
    return bind_list


#***** Manage APP *****
async def run_app(app):
    global PYTHON_SYS

    print(f'>>>> Launching {app} <<<<')

    if PYTHON_SYS == "":
        init_settings()
    
    APP_EXE  = f'{APPS_FOLDER}/{app}/app_main.py'
    if (not os.path.isfile(APP_EXE)):
        error_text = f"{app} Error: App was not build yet"
        await print_app_event(error_text)
        return { 'result': 'error', "error_text": error_text} 


    sub_proc = None
    if __debug__:
        sub_proc = await asyncio.create_subprocess_exec(  
            PYTHON_SYS, APP_EXE,             
            stdout = None, stderr = None #,   #None for std note when none it outputs in console may be useful
        ) 
    else:
        sub_proc = await asyncio.create_subprocess_exec(  
            PYTHON_SYS, '-O', APP_EXE,             
            stdout = None, stderr = None, #start_new_session=True
        ) 

    await print_app_event(f'{app} Started: {sub_proc}' )

    await asyncio.sleep(1)


    #Register DP Mapping in drivers
    dp = load_datapoints(app)

    #loraWAN
    bind_count = add_app_loraWAN_sync(app, dp)
    print(f'LoRaWAN Data Binded: {bind_count}')

    #BACnet
    bind_count = await add_app_BACnet_sync(app, dp)
    print(f'BACnet Data Binded: {bind_count}')

    print(f'>>>> {app} Ready <<<<')

    return { 'result': 'ok', }
    

async def get_app_status(app): # try: i do not know why, but try catch should be done outside this function, otherwise it does not work... WTF?
    #shm = SharedMemory(name=f'{app}_sharedmem', create=False)
    shared_mem_list = ShareableList(name=f'{app}_sharedmem') 
    status  = shared_mem_list[0]     #status
    loop    = shared_mem_list[1]     #loop
    shared_mem_list.shm.close()
    
    return status, loop


async def stop_app(app):
    print(f'>>>> Terminating {app} <<<< ')

    bind_count = free_app_loraWAN_sync(app)
    print(f'LoRaWAN Bindings Cleared: {bind_count}')

    bind_count = free_app_BACnet_sync(app)
    print(f'BACnet Bindings Cleared: {bind_count}')

    mem_name = f'{app}_sharedmem'
    shared_mem_list    = ShareableList(name=mem_name)
    shared_mem_list[0] = False #App Status Flag
    shared_mem_list.shm.close()
    
    await print_app_event(f'>>>> {app} Stopped <<<<')


async def get_app_mem(app): # try: i do not know why, but try catch should be done outside this function, otherwise it does not work... WTF?
    return await get_mem(app)


async def set_app_mem_value(app, memalloc, datatype, value): #it sets value one by one, fix it for raw
    await set_mem_value(app, memalloc, datatype, value)


async def get_binds_mem(app): # try: i do not know why, but try catch should be done outside this function, otherwise it does not work... WTF?
    return await get_binds(app)
