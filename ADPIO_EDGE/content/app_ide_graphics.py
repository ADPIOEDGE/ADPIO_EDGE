from pony.orm import *
import ujson

#DB
from database.app_db    import find_app_db

from content.users import check_permissions


def to_json(rec, app_status):

    return {
        'id'            : rec.id, 
        #'name'          : rec.name, 
        #'description'   : rec.description, 
        'order'         : rec.order,
        'view'          : rec.view,
        'datapoint_bind': rec.datapoint_bind,           #Datapoint bind #ID
        'error'         : True                          #Fix, checks the datapoint, after load
    }


async def update(db, content):
    with db_session: #content["app_status"]
        return [ to_json(rec, False) for rec in db.graphics.select(view=content["view"]).order_by(lambda r: r.order) ]
       
    return []
        
        
async def add_element(db, content):
    try:
        with db_session:
            db.graphics (
                #name            = content['element']['name'] ,
                #description     = content['element']['description'],
                order           = content['element']['order'],
                view            = content['element']['view'],
                datapoint_bind  = content['element']['datapoint_bind'],
                #datatype       = content['datapoint']['datatype'],
                #value          = content['datapoint']['value'],   
                #writable       = content['datapoint']['writable']                     
            )
                    
            #rec = db.graphics.select(view=app["selected_view"]).order_by(desc(db.graphics.id))
                    
            return await update(db, content) # [ to_json(rec, False) for rec in db.graphics.select(view=content["view"]).order_by(lambda r: r.order) ]
            
    except Exception as ex:
        print(str(ex))
        return  {"result": "error", "error_text": f"Failed to add graphical element: {ex}"} 


async def delete_element(db, content):
    try:
        for rec in content["elements"]: 
            with db_session:
                db.graphics[rec['id']].delete()

        return await update(db, content)
                
    except Exception as ex:
        print(str(ex))
        return  {"result": "error", "error_text": f"Failed to delete graphical element: {ex}"}            


async def clear_view_elements(db, content):
    try:
        with db_session:
            db.graphics.select(lambda p: p.view == content['view']).delete(bulk=True)
        return  {"result": "ok"}
    except Exception as ex:
        print(str(ex))
        return  {"result": "error", "error_text": f"Failed to clear all view graphical elements {ex}"}                  


async def move_element(db, content):
    try:
        for rec in content["elements"]:
            with db_session:
                el       = db.graphics[rec['id']]
                el.order = rec['place'] 
  
        return await update(db, content)

    except Exception as ex:
        return  {"result": "error", "error_text": f"Failed to move graphical element {ex}"}                       



def reorder_graphics(app):
    db = find_app_db(app)
    with db_session:
        data = db.graphics.select().order_by(lambda r: r.order)

    new_order = 0.0
    for el in data:
        
        with db_session:
            el       = db.graphics[el.id]
            el.order = new_order

        new_order += 1.0


COMMANDS_DICT = {
    'update'             : update               , 'perm_update'              : 'developer, user, view, ',
    'add_element'        : add_element          , 'perm_add_element'         : 'developer, ',
    'delete_element'     : delete_element       , 'perm_delete_element'      : 'developer, ',
    'clear_view_elements': clear_view_elements  , 'perm_clear_view_elements' : 'developer, ',
    'move_element'       : move_element         , 'perm_move_element'        : 'developer, ',
}

#DEFAULT
async def default_msg(content):
    print('Request Error app_ide_graphics_mng: ' + str(content))
    return {"result": "error", "error_text": "app_ide_graphics_mng command not found"}

async def app_ide_graphics_mng(auth, cmd, content):
    content_json = ujson.loads( content )
    app_db = find_app_db(content_json["name"])

    if check_permissions(auth, COMMANDS_DICT['perm_' + cmd]):
        return await COMMANDS_DICT.get(cmd, default_msg)(app_db, content_json)
    else:
        return { "result": "error", "error_text": f"Permission denied for user '{auth['user']}' accessing '{cmd}'" }
