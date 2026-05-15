import ujson

#app exec
from system.app_engine import get_app_mem, set_app_mem_value, get_binds_mem

from content.users import check_permissions



async def app_mem_get(content):
    try:
        mem = await get_app_mem(content['name'])

        return mem
    except:
        return  ["APP_STOPED"]  

async def app_binds_get(content):
    try:
        mem_dps  = await get_app_mem  (content['name'])
        mem_bind = await get_binds_mem(content['name'])

        return {
            "datapints" : mem_dps,
            "binds"     : mem_bind
        }
    except:
        return  ["APP_STOPED"]    
     
async def app_mem_set(content):
    try:          
        for rec in content["datapoints"]: 
            await set_app_mem_value( content["name"], rec["memalloc"],  rec["datatype"], rec["value"], )
        
        return {'result': 'ok'}
    except Exception as ex:
        print('app_mem_set error: ' + str(ex))
        return  {"result": "error", "error_text": "Failed to set value: " + str(ex)}


COMMANDS_DICT = {
    'app_mem_get' :   app_mem_get,    'perm_app_mem_get'    : 'developer, user, view, ',
    'app_mem_set' :   app_mem_set,    'perm_app_mem_set'    : 'developer, user, ',
    'app_binds_get' : app_binds_get,  'perm_app_binds_get'  : 'developer, ',
}

#DEFAULT
async def default_msg(content):
    print('Request Error app_live_mng: ' + str(content))
    return {"result": "error", "error_text": "app_live_mng command not found"}

async def app_live_mng(auth, cmd, content):
    content_json = ujson.loads( content )

    if check_permissions(auth, COMMANDS_DICT['perm_' + cmd]):
        return await COMMANDS_DICT.get(cmd, default_msg)(content_json)
    else:
        return { "result": "error", "error_text": f"Permission denied for user '{auth['user']}' accessing '{cmd}'" }
