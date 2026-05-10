import ujson
import os

from shutil import rmtree, copytree, copyfile
from glob import glob

#settings
from system.globals     import WORKSPACE, ROOT_FOLDER

from database_sql.workspace_model import workspace_db, logic_palette_rec
from content.users                import check_permissions


def sort_by_order(rec):
    return rec["order"]

    
async def rebuild_logic_db(content):   
    try:
        file_list = glob('./assets/lib_embed/*.py') 
        print("File List: " + str(file_list))
        
        block_db = []

        for file in file_list: 
            print('\nScanning: ' + file)

            imortloc = str(file).replace('./assets/', '').replace('.py', '').replace('/', '.')
            filename = str(imortloc).split(".")[-1]
            
            print("Import Location: " + imortloc)
            
            group = {}
            with open(str(file)) as f:
                for line in f.readlines():
                    if '#GROUP=' in line:
                        group = ujson.loads(line.replace('#GROUP=', '').strip())
                        group['blocks'] = []
                    if '#BLOCK=' in line:
                        group['blocks'].append( ujson.loads(line.replace('#BLOCK=', '').strip()) )
                        group['blocks'][-1]['io'] = []
                    if '#IO=' in line:
                        group['blocks'][-1]['io'].append( ujson.loads(line.replace('#IO=', '').strip()) )    
                    if ('def ' + filename + '_') in line:
                        group['blocks'][-1]['function'] = line.replace('def ', '').replace(':', '').strip()
                        func_name                       = group['blocks'][-1]['function'].split('(')[0]
                        group['blocks'][-1]['import']   = "".join([ 'from ' , imortloc , ' import ' , func_name ])
                        group['blocks'][-1]['id']       = func_name
                
            block_db.append(group)


        #Sort By group order
        block_db.sort(key=sort_by_order)
            
        await workspace_db.delete_all_records(logic_palette_rec) #clear table for rebuild        

        print('\n\n')
    
        logic_list = []
        for group in block_db:
            grp_name = group['name']
            print(str(group['name']))

            for block in group['blocks']:
                logic_list.append(logic_palette_rec(
                    id          = block['id'], 
                    name        = block['name'], 
                    description = block['description'], 
                    group       = grp_name,
                    libimport   = block['import'],
                    type        = block['type'],
                    function    = block['function'],
                    io          = block['io'],
                ))

        await workspace_db.add_records(logic_list)


        #Copy Files To Workfolder
        src_folder = ROOT_FOLDER + '/assets/lib_embed'
        dst_folder = WORKSPACE   + '/lib_embed'

        if os.path.exists(dst_folder):
            rmtree(dst_folder)
        
        copytree(src_folder, dst_folder)

        #Copy app_lib
        src_folder = ROOT_FOLDER + '/assets/app_lib.py'
        dst_folder = WORKSPACE   + '/app_lib.py' 
        copyfile(src_folder, dst_folder)
        
        #Copy Dataconversion
        src_folder = ROOT_FOLDER + '/assets/dataconversion.py'
        dst_folder = WORKSPACE   + '/dataconversion.py' 
        copyfile(src_folder, dst_folder)      

        #Copy Terminal
        src_folder = ROOT_FOLDER + '/assets/terminal.py'
        dst_folder = WORKSPACE   + '/terminal.py' 
        copyfile(src_folder, dst_folder)              

        return await update_logic(content)
    except Exception as ex:
        print("Failed To Rebuild: " + str(ex))
        return  {"result": "error", "error_text": "Failed To Rebuild Logic DB"}


async def update_logic(content):
    try:
        return await workspace_db.get_all_records(logic_palette_rec, to_json=True)
    except  Exception as ex:
        print(str(ex))
        return  {"result": "error", "error_text": f"Failed ro get logic palette... ({ex})"}


async def update_logic_grouped(content):
    list = await update_logic(content)#.sort(key=sort_by_order)
    
    new_grp = ''
    groups = []

    for blk in list:
        if blk['group'] != new_grp:
            new_grp = blk['group']
            groups.append({ "name": new_grp, "list": []})
        
        groups[-1]['list'].append(blk)

    return groups


async def get_block(content):
    try:
        return await workspace_db.get_record(logic_palette_rec, logic_palette_rec.id, content['id'])        
    except Exception as ex:
        print("Failed To Find Block In Palette: " + str(ex))
        return None


COMMANDS_DICT = {
    'update_logic'             : update_logic               , 'perm_update_logic'              : 'developer, ',
    'rebuild_logic_db'         : rebuild_logic_db           , 'perm_rebuild_logic_db'          : 'developer, ',
    'update_logic_grouped'     : update_logic_grouped       , 'perm_update_logic_grouped'      : 'developer, ',
    'get_block'                : get_block                  , 'perm_get_block'      : 'developer, ',
}


#DEFAULT
async def default_msg(content):
    print('Request Error system_tools: ' + str(content))
    return {"result": "error", "error_text": "system_tools command not found"}


async def system_tools_mng(auth, cmd, content):
    content_json = ujson.loads( content )

    if check_permissions(auth, COMMANDS_DICT['perm_' + cmd]):
        return await COMMANDS_DICT.get(cmd, default_msg)(content_json)
    else:
        return { "result": "error", "error_text": f"Permission denied for user '{auth['user']}' accessing '{cmd}'" }