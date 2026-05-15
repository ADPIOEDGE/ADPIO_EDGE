import ujson

#Tools
from drivers.loraWAN_conn_sever import get_loraWAN_db
from drivers.loraWAN_conn_sever import find_device as find_device_lora

from drivers.bacnet_server      import get_devices, add_new_tasks, find_device, find_object

from content.users import check_permissions


async def lora_update(content):
    return get_loraWAN_db()


async def lora_tools_list_devices(content):
    result = []
    devices = get_loraWAN_db()

    if devices == None:
        return result
    
    for dev in devices:
        result.append({ 'name': f'{dev['devEUI']} - {dev['deviceName']}',  'value': dev['devEUI'] })

    return  result


async def lora_tools_list_fields(content):
    result = []
    devices = get_loraWAN_db()

    if devices == None:
        return result
    
    device = find_device_lora(devices, content['devEUI'])
    if device == None:
        return result
    
    for dev in device['data']:
        if dev['name'] != 'applicationID' and dev['name']  != 'devEUI':
            result.append({ 'name': dev['name'],  'value': dev['name'] })

    return  result


async def bacnet_update(content):
    return get_devices()


async def bacnet_read_properties(content):
    add_new_tasks( content )
    return  { 'result': 'ok', } 


async def bacnet_list_devices(content):
    result = []
    devices = get_devices()

    for dev in devices:
        result.append({ 
            'name': f'{dev['device_id']}[{dev['net']}] - {dev['name']}',  
            'value': dev['net'] 
        })

    return  result


async def bacnet_list_objects(content):
    result = []
    devices = get_devices()

    dev = find_device(devices, content['device_net'])
    if dev == None:
        return result

    for obj in dev['objects']:
        result.append({ 'name': f'{obj['object']} - {obj['name']}',  'value': obj['object'] })

    return  result        


async def bacnet_list_properties(content):
    result = []
    devices = get_devices()

    dev = find_device(devices, content['device_net'])
    if dev == None:
        return result

    obj = find_object(dev, content['object'])
    if obj == None:
        return result    

    for prop in obj['properties']:
        result.append({ 'name': prop['property'],  'value': prop['property'] })

    return  result  
      

COMMANDS_DICT = {
    'lora_tools_update'           : lora_update,             'perm_lora_tools_update'            : 'developer, ',
    
    'lora_tools_list_devices'     : lora_tools_list_devices, 'perm_lora_tools_list_devices'      : 'developer, ',
    'lora_tools_list_fields'      : lora_tools_list_fields,  'perm_lora_tools_list_fields'       : 'developer, ',

    'bacnet_tools_update'         : bacnet_update,           'perm_bacnet_tools_update'          : 'developer, ',
    'bacnet_tools_read_properties': bacnet_read_properties,  'perm_bacnet_tools_read_properties' : 'developer, ',

    'bacnet_tools_list_devices'   : bacnet_list_devices,     'perm_bacnet_tools_list_devices'    : 'developer, ',    
    'bacnet_tools_list_objects'   : bacnet_list_objects,     'perm_bacnet_tools_list_objects'    : 'developer, ',    
    'bacnet_tools_list_properties': bacnet_list_properties,  'perm_bacnet_tools_list_properties' : 'developer, ',    
}


#DEFAULT
async def default_msg(content):
    print('Request Error log_task_mng: ' + str(content))
    return {"result": "error", "error_text": "network_tools_task_mng command not found"}


async def network_tools_mng(auth, cmd, content):
    content_json = ujson.loads( content )

    if check_permissions(auth, COMMANDS_DICT['perm_' + cmd]):
        return await COMMANDS_DICT.get(cmd, default_msg)(content_json)
    else:
        return { "result": "error", "error_text": f"Permission denied for user '{auth['user']}' accessing '{cmd}'" }
