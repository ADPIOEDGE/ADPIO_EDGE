import ujson

from lib.database_sql.workspace_model import workspace_db, logs_rec, workspace_model
from sqlmodel import col
from sqlalchemy.sql import text
from sqlmodel import select, desc, asc

from content.users import check_permissions


async def update(content):
    try:
        return await workspace_db.get_all_records(logs_rec, to_json=True, order_by_desc=logs_rec.date, limit=1200)
    except  Exception as ex:
        print(str(ex))
        return  {"result": "error", "error_text": f"Failed update logs... ({ex})"}


async def clear_all(content):
    try:
        await workspace_db.delete_all_records(logs_rec)
        return { "result": "ok", } 
    except  Exception as ex:
        print(str(ex))
        return  {"result": "error", "error_text": f"Failed to delete all logs... ({ex})"}    


async def print_log_system(txt):
    """global last_records_info

    if txt not in last_records_info:
        last_records_info.insert(0, txt)
        if len( last_records_info ) > __max_back_log:
            last_records_info.pop(__max_back_log)
    """

    txt_trim = txt
    if (len(txt) > 2018):
        txt_trim = txt[:2018] + '...'

    await workspace_db.add_record( logs_rec (type='system', text=txt_trim) )
    
    print( f'System: {txt}' )
    return {'system' : txt}


async def print_log_error(txt):
    txt_trim = txt
    if (len(txt) > 2018):
        txt_trim = txt[:2018] + '...'

    await workspace_db.add_record( logs_rec (type='error', text=txt_trim) )
    
    print( f'Error: {txt}' )
    return {'error' : txt}


async def print_log_lora(txt):
    txt_trim = txt
    if (len(txt) > 2018):
        txt_trim = txt[:2018] + '...'

    await workspace_db.add_record( logs_rec (type='LoRaWAN', text=txt_trim) )
    
    print( f'LoRaWAN: {txt}' )
    return {'LoRaWAN' : txt}


async def print_log_bacnet(txt):    
    txt_trim = txt
    if (len(txt) > 2018):
        txt_trim = txt[:2018] + '...'

    await workspace_db.add_record( logs_rec (type='BACnet', text=txt_trim) )
    
    print( f'BACnet: {txt}' )
    return {'BACnet' : txt}


async def print_app_event(txt):
    txt_trim = txt
    if (len(txt) > 2018):
        txt_trim = txt[:2018] + '...'

    await workspace_db.add_record( logs_rec (type='APPS', text=txt_trim) )
    
    print( f'APPS: {txt}' )
    return {'APPS' : txt}


async def show_logs(content):
    filename = f'/dev/shm/adpio_{content['file']}.log'

    content = []
    max_size = 256
    try:
        with open(filename, 'r') as f:
            #content = f.readlines()
            for line in f:
                content.append( line.replace('\n', '') )

            if len(content) > max_size:
                content = content[(len(content) - max_size):len(content)]

    except FileNotFoundError:
        return { 'content': content }
        
    return { 'content': content }
            

async def clear_logs(content):
    filename = f'/dev/shm/adpio_{content['file']}.log'

    try:
        with open(filename, 'w') as f:
          return {'content': ''}
    except FileNotFoundError:
        print(f"Error: The file 'adpio_{content['file']}.log' was not found.")


COMMANDS_DICT = {
    'update'    : update,    'perm_update'       : 'developer, user, view, ', #Note: This on is DB records, controled by server
    'clear_all' : clear_all, 'perm_clear_all'    : 'developer, ',

    'show_logs' : show_logs,  'perm_show_logs'   : 'developer, ',             #Logs from console, python errors
    'clear_logs': clear_logs, 'perm_clear_logs'  : 'developer, ',
}


#DEFAULT
async def default_msg(content):
    print('Request Error log_task_mng: ' + str(content))
    return {"result": "error", "error_text": "log_task_mng command not found"}


async def log_task_mng(auth, cmd, content):
    content_json = ujson.loads( content )

    if check_permissions(auth, COMMANDS_DICT['perm_' + cmd]):
        return await COMMANDS_DICT.get(cmd, default_msg)(content_json)
    else:
        return { "result": "error", "error_text": f"Permission denied for user '{auth['user']}' accessing '{cmd}'" }
