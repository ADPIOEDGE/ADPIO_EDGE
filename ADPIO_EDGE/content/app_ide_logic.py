import ujson

#DB
from database_sql.application_model import logic_rec, find_application_db

from content.users          import check_permissions
from content.system_tools   import get_block


async def update(app_db, content):
    try:
        return await app_db.get_all_records(logic_rec, to_json=True)
    except Exception as ex:
        print(str(ex))
        return  {"result": "error", "error_text": f"Failed to obtain logic blocks: {ex}"}    


async def load_blocks(app_name):    
    application_db = find_application_db(app_name)
    return await application_db.get_all_records(logic_rec, to_json=True)


async def move_elements(app_db, content):
    try:
        await app_db.update_multi_fields(
            logic_rec, logic_rec.id, 'id',
            [{ 'id': rec['id'], 'x': rec['x'], 'y': rec['y'] } for rec in content["elements"]] 
        )

        return  {"result": "ok"}
    except Exception as ex:
        print(f"Failed to move logical elements {str(ex)}")
        return  {"result": "error", "error_text": f"Failed to move logical elements {str(ex)}"}     


async def save_elements(app_db, content):
    try:
        await app_db.update_records(
            [logic_rec(
                id          = rec['id'],
                name        = rec['name'],
                type        = rec['type'],
                function    = rec['function'],
                libimport   = rec['libimport'],
                x           = rec['x'],
                y           = rec['y'],
                io          = rec['io'],
            ) for rec in content["elements"] ], logic_rec.id
        )

        return  {"result": "ok"}
    except Exception as ex:
        print(f"Failed to move logical elements {str(ex)}")
        return  {"result": "error", "error_text": f"Failed to move logical elements {str(ex)}"}     


async def datapointsetget(app_db, content):
    try:
        up_list = await app_db.get_all_records(logic_rec)

        for db_rec in up_list:
            for io_indx, io_rec in enumerate(db_rec.io):
                if (io_rec["bind"] != {}):
                    if (io_rec["bind"]["bind_id"] == content["element"]["id"]):
                        el_to_clean = await app_db.get_record(logic_rec, logic_rec.id, db_rec.id)
                        el_to_clean.io[io_indx]['bind'] = {}
                        await app_db.update_fields(logic_rec, logic_rec.id, db_rec.id, {"io": el_to_clean.io})

        el = await app_db.get_record(logic_rec, logic_rec.id, content["element"]['id'])
        if (el.type == 'datapoint-get'): #Setter
            el.type            = 'datapoint-set'
            el.io[0]['type']   = 'input'
            el.io[0]['bind']   = {}
            #el.io              = [{ "id": "value", "bind": {}, "type": "input", "name": "Value", "datatype": "", "value": ""}],
        else:                            #Getter
            el.type            = 'datapoint-get'
            el.io[0]['type']   = 'output'
            el.io[0]['bind']   = {}
            #el.io              = [{ "id": "value", "bind": {}, "type": "output", "name": "Value", "datatype": "", "value": ""}],

        await app_db.update_fields(
            logic_rec, logic_rec.id, el.id, 
            {"type": el.type,  "io": el.io}
        ) 

        return await app_db.get_all_records(logic_rec, to_json=True)
    except Exception as ex:
        print( f"Failed to flip datapoint set get {str(ex)}")
        return  {"result": "error", "error_text": f"Failed to flip datapoint set get {str(ex)}"}    


async def add_element(app_db, content):
    try:
        if content['element']['type'] == 'block' or content['element']['type'] == 'constant':
            blk = await get_block(content['element'])  
            if blk == None:
                return  {"result": "error", "error_text": f"Failed to find element in palette {content['element']['name']}"}

            await app_db.add_record( logic_rec(
                name            = blk.name, 
                type            = blk.type,
                function        = blk.function, 
                libimport       = blk.libimport, 
                x               = content['element']['x'], 
                y               = content['element']['y'],
                io              = blk.io, 
            ))
        elif content['element']['type'] == 'datapoint':
            await app_db.add_record( logic_rec(
                name            = f"{content['element']['group']}:{content['element']['name']}",
                type            = 'datapoint-get',
                function        = '',
                libimport       = '',
                x               = content['element']['x'], 
                y               = content['element']['y'],
                io              = [{ "id": "value", "bind": {}, "type": "output", "name": "Value", "datatype": "", "value": ""}],
            ))
        else:
            return  {"result": "error", "error_text": f"Unknown Type {content['element']['name']}"}

        return await app_db.get_all_records(logic_rec, to_json=True)            
    except Exception as ex:
        print( f"Failed to add logic element {str(ex)}")
        return  {"result": "error", "error_text": f"Failed to add logic element {str(ex)}"}


async def delete_elements(app_db, content):
    try:
        up_list = await app_db.get_all_records(logic_rec)

        for db_rec in up_list:
            for io_indx, io_rec in enumerate(db_rec.io):
                if (io_rec["bind"] != {}):
                    for rec in content["elements"]:
                        if (io_rec["bind"]["bind_id"] == rec["id"]):
                            el_to_clean  = await app_db.get_record(logic_rec, logic_rec.id, db_rec.id) 
                            el_to_clean.io[io_indx]['bind'] = {}
                            await app_db.update_fields(logic_rec, logic_rec.id, db_rec.id, {"io": el_to_clean.io})

        await app_db.delete_records(
            logic_rec, logic_rec.id, 
            [rec['id'] for rec in content["elements"]] 
        )
        
        return await app_db.get_all_records(logic_rec, to_json=True)                
    except Exception as ex:
        print(f"Failed to delete logic element {str(ex)}")
        return  {"result": "error", "error_text": f"Failed to delete logic element {str(ex)}"}            


async def bind_elements(app_db, content):
    try:
        block = await app_db.get_record(logic_rec, logic_rec.id, content['elements']['target_blk'])

        for rec in block.io:
            if (rec['id'] == content['elements']['target_io']):
                rec['bind'] = {"bind_id": content['elements']['bind_blk'], "bind_io": content['elements']['bind_io'], "bind_io_index": content['elements']['bind_io_indx']}
                break

        await app_db.update_fields(
            logic_rec, logic_rec.id, block.id, 
            {"io": block.io}
        )

        return await app_db.get_all_records(logic_rec, to_json=True)                
    except Exception as ex:
        print( f"Failed to bind logic elements {str(ex)}")
        return  {"result": "error", "error_text": f"Failed to bind logic elements {str(ex)}"}


async def delete_binds(app_db, content):
    try:
        blocks = []
        for rec in content["elements"]: 
            block     = await app_db.get_record(logic_rec, logic_rec.id, rec['target_id'])
            block.io[rec['target_io_index']]['bind']  = {}
            blocks.append(block)

        await app_db.update_multi_fields(
            logic_rec, logic_rec.id, 'id', 
            [ { "id": block.id, "io": block.io } for block in blocks ]
        )

        return await app_db.get_all_records(logic_rec, to_json=True)
    except Exception as ex:
        print(f"Failed to clean binds {str(ex)}")
        return  {"result": "error", "error_text": f"Failed to clean binds {str(ex)}"}            



async def save_bind_alloc(app_name, f_id, io_index, mem):    
    #application_db = find_application_db(app_name)

    #with db_session:
    #    el       = db.logic[f_id]
    #    io       = el.io[io_index]
    #    io['mem'] = mem

    print('BROKEN save_bind_alloc')

    #await application_db.update_fields(
    #    datapoints_rec, datapoints_rec.id, f_id,
    #    {'memalloc': mem_alloc}, to_json=True
    #)
    


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
    app_db = find_application_db(content_json["name"])

    if check_permissions(auth, COMMANDS_DICT['perm_' + cmd]):
        return await COMMANDS_DICT.get(cmd, default_msg)(app_db, content_json)
    else:
        return { "result": "error", "error_text": f"Permission denied for user '{auth['user']}' accessing '{cmd}'" }
