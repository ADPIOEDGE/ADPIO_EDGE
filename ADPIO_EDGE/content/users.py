import ujson
from secrets                import compare_digest
from base64                 import b64encode

from lib.database_sql.workspace_model import workspace_db, user_rec, application_rec

 
async def get_tree(content):
    view_tree = []
    edit_tree = []

    app_list = await workspace_db.get_all_records(application_rec)

    groups = []
    for app in app_list:
        if app.group not in groups:
            groups.append(app.group)
            view_tree.append({'id': f'/view/{app.group}', 'name': app.group, 'visible': True, 'submenu': []})

        view_tree[groups.index(app.group)]["submenu"].append( 
            {'id': f'/view/{app.group}/{app.name}', 'name': app.name, 'type': 'menu', 'visible': True, 'draggable': False} 
        )

    view_tree = get_view_tree(view_tree)
    
    if content['profile'] == 'developer':
        edit_tree = get_edit_tree(edit_tree)
        
    return  {"view_tree": view_tree, "edit_tree": edit_tree}


async def user_list(content):
    try:
        return await workspace_db.get_all_records(user_rec, to_json=True)
    except Exception as ex:
        print(str(ex))
        return  {"result": "error", "error_text": "Failed to obtain user list"}


async def get_user(content):
    try:
        return await workspace_db.get_record(user_rec, user_rec.name,  content['name'] )
    except Exception as ex:
        print(str(ex))
        return  {"result": "error", "error_text": "Failed to obtain user data"}


async def add_user(content):
    try:
        await workspace_db.add_record(user_rec(
            name        = content['name'],
            password    = content['password'],

            homepage    = content['homepage'],
            profile     = content['profile'],
            description = content['description'],
        ))

        return  {"result": "ok"}
    except Exception as ex:
        return  {"result": "error", "error_text": "Failed to add user (already exists?)"}

async def save_user(content):
    try:        
        await workspace_db.update_record(
            user_rec(
                name        = content['name'],
                password    = content['password'],

                homepage    = content['homepage'],
                profile     = content['profile'],
                description = content['description'],
            ), 
            user_rec.name, content['name'] )

        return  {"result": "ok"}
    except Exception as ex:
        print(str(ex))
        return  {"result": "error", "error_text": "Failed to save user..."}


async def delete_user(content):   
    try:
        await workspace_db.delete_record(user_rec, user_rec.name, content['name'])
        return  {"result": "ok"}
    except Exception as ex:
        print(str(ex))
        return  {"result": "error", "error_text": "Failed to delete user "}


async def login(content):
    user_cache = await cached_auth()        
    busr = content['key'].encode('utf8')
    
    for rec in user_cache :
        if compare_digest( rec['key'], busr):
            if __debug__:
                print("Logged In: " + str(busr) + " = " + str(rec['key']))
            return { "result": "ok", "auth": True, "sessionkey": rec['sessionkey'], "user": rec['user'],  "profile": rec['profile']}#"cache": rec } #random sessoin key, should go to cookie 
            
    return { "result": "error", "auth": False, "error_text": "The Username or Password is Incorrect" }

async def sessionkey(content):
    user_cache = await cached_auth() 
    busr = content['key'].encode('utf8')
    for rec in user_cache :
        if compare_digest( rec['key'], busr):
            if __debug__:
                print("Session Check: " + str(busr) + " = " + str(rec['key']))
            return { "result": "ok", "auth": True, "sessionkey": rec['sessionkey'], "user": rec['user'], "profile": rec['profile']}#"cache": rec } #random sessoin key, should go to cookie             
    return  {"result": "error",  "auth": False, "error_text": "User Was Logged Out"}


async def logout(content):
    print("LOGOUT *************")
    return  {"result": "error", "error_text": "Failed to logout (not implemented yet)"}


def get_edit_tree(tree: list):
    tree.append({'id': 'app_ide', 'name': 'IDE', 'visible': True, 'submenu': [
        {'id': '/app_ide/mng',    'name': 'APP MANAGER', 'type': 'menu', 'visible': True, 'draggable': False},
    ]})
    
    tree.append({'id': 'tools', 'name': 'TOOLS', 'visible': True, 'submenu': [
        {'id': '/tools/trendview',      'name': 'TREND VIEW',     'type': 'menu', 'visible': True, 'draggable': False},
        {'id': '/tools/bacnetbrowser',  'name': 'BACNET BROWSER', 'type': 'menu', 'visible': True, 'draggable': False},
        {'id': '/tools/lorabrowser',    'name': 'LORA BROWSER',   'type': 'menu', 'visible': True, 'draggable': False},
    ]})    
    
    tree.append({'id': 'tools', 'name': 'DEVELOPMENT', 'visible': True, 'submenu': [
        {'id': '/development/palettelogic',  'name': 'LOGIC PALETTE',  'type': 'menu', 'visible': True, 'draggable': False},
    ]})

    tree.append({'id': 'system', 'name': 'SYSTEM', 'visible': True, 'submenu': [
        {'id': '/system/user',          'name': 'USER MANAGMENT', 'type': 'menu', 'visible': True, 'draggable': False},
        {'id': '/system/logs',          'name': 'LOGS',           'type': 'menu', 'visible': True, 'draggable': False},
        {'id': '/system/about',         'name': 'ABOUT',          'type': 'menu', 'visible': True, 'draggable': False},
    ]})
    
    return tree

def get_view_tree(tree: list):
    #tree.append({'id': 'app_ide', 'name': 'Development IDE', 'visible': True, 'submenu': [
    #    {'id': '/app_ide/mng',    'name': 'APP EDITOR', 'type': 'menu', 'visible': True, 'draggable': False},
    #]})
    
    tree.append({'id': 'tools', 'name': 'TOOLS', 'visible': True, 'submenu': [
        {'id': '/tools/trendview',     'name': 'TREND VIEW',    'type': 'menu', 'visible': True, 'draggable': False},
    ]})
    

    tree.append({'id': 'system', 'name': 'SYSTEM', 'visible': True, 'submenu': [
        #{'id': '/system/user',  'name': 'USER MANAGMENT', 'type': 'menu', 'visible': True, 'draggable': False},
        {'id': '/system/logs',  'name': 'LOGS',           'type': 'menu', 'visible': True, 'draggable': False},
        {'id': '/system/about', 'name': 'ABOUT',          'type': 'menu', 'visible': True, 'draggable': False},
    ]})
    
    return tree    


async def auth_no_users_fix():    
    users = await workspace_db.get_all_records(user_rec)

    if __debug__:
        print("Checking User Existance Count: " + str(len(users)))
        
    if len(users) == 0:
        print("No Users Found, creating admin/admin user")

        await workspace_db.add_record(user_rec(
            name        = 'admin',
            password    = 'admin',
                
            homepage    = '',
            profile     = 'developer',
            description = 'Default Admin User',
        ))


async def cached_auth():
    return [{
        'key'           : b64encode( (usr.name + ":" + usr.password).encode('utf8') ), #convert to byte -> b64 encode
        'user'          : usr.name,
        'profile'       : usr.profile,
        'sessionkey'    : b64encode( (usr.name + ":" + usr.password).encode('utf8') ).decode("utf-8").__str__(), #token_urlsafe(16)   #random sessoin key should be implemented, should go to cookie 
    } for usr in await workspace_db.get_all_records(user_rec)]    


def check_permissions(auth, perm_profiles):
    if perm_profiles == '': #If perm empty, allow not authed req
        return True
    
    if auth['profile'] == '': #If no profile - block access
        return False
    
    if 'any,' in perm_profiles: #Allow All Authed
        return True

    if auth['profile'] + ',' in perm_profiles:
        return True


    return False


COMMANDS_DICT = { #Command, Profile Permission
    'get_tree'          : get_tree,             'perm_get_tree'          : 'any, ',
    #'get_app_edit_tree' : get_app_edit_tree,    'perm_get_app_edit_tree' : 'any',

    'user_list'         : user_list,            'perm_user_list'         : 'developer, ',
    'get_user'          : get_user,             'perm_get_user'          : 'developer, ',
    'add_user'          : add_user,             'perm_add_user'          : 'developer, ',
    'save_user'         : save_user,            'perm_save_user'         : 'developer, ',
    'delete_user'       : delete_user,          'perm_delete_user'       : 'developer, ',
    
    'login'             : login,                'perm_login'             : '',
    'sessionkey'        : sessionkey,           'perm_sessionkey'        : '',
    'logout'            : logout,               'perm_logout'            : '',
}

#DEFAULT
async def default_msg(content):
    print('Request Error user_mng: ' + str(content))
    return {"result": "error", "error_text": "user_mng command not found"}

async def user_mng(auth, cmd, content):
    content_json = ujson.loads( content )
    
    if check_permissions(auth, COMMANDS_DICT['perm_' + cmd]):
        return await COMMANDS_DICT.get(cmd, default_msg)(content_json)
    else:
        return { "result": "error", "error_text": f"Permission denied for user '{auth['user']}' accessing '{cmd}'" }
    

