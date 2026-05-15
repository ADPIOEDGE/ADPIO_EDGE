import ujson

#DB
from lib.database_sql.application_model import datapoints_rec, find_application_db

from content.users import check_permissions


async def update(app_db, content):
    try:
        return await app_db.get_all_records(datapoints_rec, to_json=True)
    except Exception as ex:
        print(str(ex))
        return  {"result": "error", "error_text": f"Failed to obtain update datapoints: {ex}"}

        

#async def get_dataponts(app_db, content):
#    try:
#        with db_session:
#            return [ to_json(rec, False) for rec in db.datapoints.select() ]        
#    except:
#        return  {"result": "error", "error_text": "Failed To Obtain Datapoint"}    


async def add_datapoints(app_db, content):
    try:
        dps = []
        for rec in content["datapoints"]:
            group = rec['group']
            if group == '':
                group = ' '

            dps.append( datapoints_rec(
                name         = rec['name'] ,
                description  = rec['description'],
                datatype     = rec['datatype'],

                value        = str(rec['value']),
                units        = rec['units'],
                writable     = rec['writable'],

                group        = group,

                properties   = rec['properties'], 
                protocol     = rec['protocol'], 
                trend        = rec['trend'],  
            ))

        await app_db.add_records( dps )
        return await app_db.get_all_records(datapoints_rec, to_json=True)
    except Exception as ex:
        print(str(ex))
        return  {"result": "error", "error_text": f"Failed to add new datapoints: {ex}"}
         

async def delete_datapoints(app_db, content):
    try:
        await app_db.delete_records(
            datapoints_rec, datapoints_rec.id, 
            [rec['id'] for rec in content["datapoints"]]
        )

        return await app_db.get_all_records(datapoints_rec, to_json=True)
    except Exception as ex:
        print(str(ex))
        return  {"result": "error", "error_text": f"Failed to delete datapoints: {ex}"}


async def save_datapoints(app_db, content):
    try:
        dps = []
        for rec in content["datapoints"]:
            group = rec['group']
            if group == '':
                group = ' '

            dps.append( datapoints_rec(
                id           = rec['id'],
                name         = rec['name'] ,
                description  = rec['description'],
                datatype     = rec['datatype'],

                value        = str(rec['value']),
                units        = rec['units'],
                writable     = rec['writable'],

                group        = rec['group'],

                properties   = rec['properties'], 
                protocol     = rec['protocol'], 
                trend        = rec['trend'],  
            ))

        await app_db.update_records( dps, datapoints_rec.id )
        return await app_db.get_all_records(datapoints_rec, to_json=True)
    except Exception as ex:
        print(str(ex))
        return  {"result": "error", "error_text": f"Failed to save datapoints: {ex}"}


async def load_datapoints(app_name):    
    application_db = find_application_db(app_name)
    return await application_db.get_all_records(datapoints_rec)


async def save_mem_alloc(app_name, datapoints: list[datapoints_rec]):    
    application_db = find_application_db(app_name)

    mem_alloc = 3 #Starts from 3
    mem_list = []
    for dp in datapoints:
        mem_list.append( {'id': dp.id, 'memalloc': mem_alloc} )
        dp.memalloc = mem_alloc
        mem_alloc += 1

    if (len(mem_list) > 0):
        await application_db.update_multi_fields(datapoints_rec, datapoints_rec.id, 'id', mem_list)

    return datapoints    



COMMANDS_DICT = {
    'update'            : update            ,  'perm_update'            : 'developer, user, view, ',
    #'get_dataponts'    : get_dataponts     ,  'perm_get_dataponts'     : 'developer, user, view, ',
    'add_datapoints'    : add_datapoints    ,  'perm_add_datapoints'    : 'developer, ',
    'delete_datapoints' : delete_datapoints ,  'perm_delete_datapoints' : 'developer, ',
    'save_datapoints'   : save_datapoints   ,  'perm_save_datapoints'   : 'developer, ',
}


#DEFAULT
async def default_msg(content):
    print('Request Error app_ide_datapoints_mng: ' + str(content))
    return {"result": "error", "error_text": "app_ide_datapoints_mng command not found"}


async def app_ide_datapoints_mng(auth, cmd, content):
    content_json = ujson.loads( content )
    application_db = find_application_db(content_json["name"])

    if check_permissions(auth, COMMANDS_DICT['perm_' + cmd]):
        return await COMMANDS_DICT.get(cmd, default_msg)(application_db, content_json)
    else:
        return { "result": "error", "error_text": f"Permission denied for user '{auth['user']}' accessing '{cmd}'" }
