from pony.orm import *
import ujson

#DB
from database.app_db        import find_app_db

from content.users          import check_permissions
from content.system_tools   import get_block



def to_json(rec):
    return { 
        'id'        : rec.id, 
        'type'      : rec.type,
        'name'      : rec.name, 
        'function'  : rec.function,
        'libimport' : rec.libimport,
        'x'         : rec.x, 
        'y'         : rec.y, 
        'io'        : rec.io,
    }


async def move_elements(db, content):
    try:
        with db_session:
            for rec in content["elements"]:
                el       = db.logic[rec['id']]
                el.x     = rec['x']
                el.y     = rec['y']
  
        return  {"result": "ok"}

    except Exception as ex:
        print(f"Failed to move logical elements {str(ex)}")
        return  {"result": "error", "error_text": f"Failed to move logical elements {str(ex)}"}     

async def save_elements(db, content):
    try:
        with db_session:
            for rec in content["elements"]:
                el       = db.logic[rec['id']]                
                
                el.name            = rec['name']
                el.type            = rec['type']
                el.function        = rec['function'] 
                el.libimport       = rec['libimport']
                el.x               = rec['x'] 
                el.y               = rec['y']
                el.io              = rec['io']           

        return  {"result": "ok"}

    except Exception as ex:
        print(f"Failed to move logical elements {str(ex)}")
        return  {"result": "error", "error_text": f"Failed to move logical elements {str(ex)}"}     


async def datapointsetget(db, content):
    try:
        with db_session:
            up_list = await update(db, content)

        for db_rec in up_list:
            for io_indx, io_rec in enumerate(db_rec['io']):
                if (io_rec["bind"] != {}):
                    if (io_rec["bind"]["bind_id"] == content["element"]["id"]):
                        with db_session:
                            el_to_clean  = db.logic[db_rec["id"]]
                            el_to_clean.io[io_indx]['bind'] = {}


        with db_session:
            el       = db.logic[content["element"]['id']]

            if (el.type == 'datapoint-get'): #Setter
                el.type            = 'datapoint-set'
                el.io[0]['type']   = 'input'
                el.io[0]['bind']   = {}
    #            el.io              = [{ "id": "value", "bind": {}, "type": "input", "name": "Value", "datatype": "", "value": ""}],
            else:                            #Getter
                el.type            = 'datapoint-get'
                el.io[0]['type']   = 'output'
                el.io[0]['bind']   = {}
                #el.io              = [{ "id": "value", "bind": {}, "type": "output", "name": "Value", "datatype": "", "value": ""}],

        return await update(db, content)

    except Exception as ex:
        print( f"Failed to flip datapoint set get {str(ex)}")
        return  {"result": "error", "error_text": f"Failed to flip datapoint set get {str(ex)}"}    

async def add_element(db, content):
    try:
        if content['element']['type'] == 'block' or content['element']['type'] == 'constant':
            blk = await get_block(content['element'])  
            if blk == None:
                return  {"result": "error", "error_text": f"Failed to find element in palette {content['element']['name']}"}
            
            with db_session: 
                db.logic(
                    name            = blk.name, 
                    type            = blk.type,
                    function        = blk.function, 
                    libimport       = blk.libimport, 
                    x               = content['element']['x'], 
                    y               = content['element']['y'],
                    io              = blk.io, 
                )
        elif content['element']['type'] == 'datapoint':
            with db_session: 
                db.logic(
                    name            = f"{content['element']['group']}:{content['element']['name']}",
                    type            = 'datapoint-get',
                    function        = '',
                    libimport       = '',
                    x               = content['element']['x'], 
                    y               = content['element']['y'],
                    io              = [{ "id": "value", "bind": {}, "type": "output", "name": "Value", "datatype": "", "value": ""}],
                )
        else:
            return  {"result": "error", "error_text": f"Unknown Type {content['element']['name']}"}

        return await update(db, content)
                
    except Exception as ex:
        print( f"Failed to add logic element {str(ex)}")
        return  {"result": "error", "error_text": f"Failed to add logic element {str(ex)}"}
    

async def delete_elements(db, content):
    try:
        with db_session:
            up_list = await update(db, content)

        for db_rec in up_list:
            for io_indx, io_rec in enumerate(db_rec['io']):
                if (io_rec["bind"] != {}):
                    for rec in content["elements"]:
                        if (io_rec["bind"]["bind_id"] == rec["id"]):
                            with db_session:
                                el_to_clean  = db.logic[db_rec["id"]]
                                el_to_clean.io[io_indx]['bind'] = {}

        for rec in content["elements"]:
            with db_session:
                db.logic[rec['id']].delete()

        return await update(db, content)
                
    except Exception as ex:
        print(f"Failed to delete logic element {str(ex)}")
        return  {"result": "error", "error_text": f"Failed to delete logic element {str(ex)}"}            


async def delete_binds(db, content):
    try:
        with db_session:
            for rec in content["elements"]: 
                blk     = db.logic[rec['target_id']]
                blk.io[rec['target_io_index']]['bind']  = {}

        return await update(db, content)
                
    except Exception as ex:
        print(f"Failed to delete logic element {str(ex)}")
        return  {"result": "error", "error_text": f"Failed to delete logic element {str(ex)}"}            


async def bind_elements(db, content):
    try:
        with db_session:
            targ_el =  db.logic[content['elements']['target_blk']]

            for rec in targ_el.io:
                if (rec['id'] == content['elements']['target_io']):
                    rec['bind'] = {"bind_id": content['elements']['bind_blk'], "bind_io": content['elements']['bind_io'], "bind_io_index": content['elements']['bind_io_indx']}
                    break

        return await update(db, content)
                
    except Exception as ex:
        print( f"Failed to bind logic elements {str(ex)}")
        return  {"result": "error", "error_text": f"Failed to bind logic elements {str(ex)}"}

async def update(db, content):
    with db_session: #, content["app_status"]
        return [ to_json(rec) for rec in db.logic.select() ]
    
    return []

def load_blocks(app_name):    
    db = find_app_db(app_name)

    with db_session:
        return [ to_json(rec) for rec in db.logic.select() ]


def save_bind_alloc(app_name, f_id, io_index, mem):    
    db = find_app_db(app_name)

    with db_session:
        el       = db.logic[f_id]
        io       = el.io[io_index]
        io['mem'] = mem

    


COMMANDS_DICT = {
    'update'             : update               , 'perm_update'              : 'developer, ',
    'add_element'        : add_element          , 'perm_add_element'         : 'developer, ',
    'move_elements'      : move_elements        , 'perm_move_elements'       : 'developer, ',
    'save_elements'      : save_elements        , 'perm_save_elements'       : 'developer, ',
    'delete_elements'    : delete_elements      , 'perm_delete_elements'     : 'developer, ',
    'delete_binds'       : delete_binds         , 'perm_delete_binds'        : 'developer, ',
    'bind_elements'      : bind_elements        , 'perm_bind_elements'       : 'developer, ',
    'datapointsetget'    : datapointsetget      , 'perm_datapointsetget'     : 'developer, ',
}

#DEFAULT
async def default_msg(content):
    print('Request Error app_ide_logic_mng: ' + str(content))
    return {"result": "error", "error_text": "app_ide_logic_mng command not found"}


async def app_ide_logic_mng(auth, cmd, content):
    content_json = ujson.loads( content )
    app_db = find_app_db(content_json["name"])

    if check_permissions(auth, COMMANDS_DICT['perm_' + cmd]):
        return await COMMANDS_DICT.get(cmd, default_msg)(app_db, content_json)
    else:
        return { "result": "error", "error_text": f"Permission denied for user '{auth['user']}' accessing '{cmd}'" }
