import ujson

#DB
from database_sql.application_model import graphics_rec, find_application_db

from content.users import check_permissions


async def update(app_db, content):
    try:
        return await app_db.get_records(graphics_rec, graphics_rec.view, content['view'], to_json=True, order_by=graphics_rec.order)
    except Exception as ex:
        print(str(ex))
        return  {"result": "error", "error_text": f"Failed to obtain graphics: {ex}"}    


async def add_element(app_db, content):
    try:
        await app_db.add_record( graphics_rec(
            order           = content['element']['order'],
            view            = content['element']['view'],
            datapoint_bind  = content['element']['datapoint_bind'],
        ))                 

        return await app_db.get_records(graphics_rec, graphics_rec.view, content['view'], to_json=True, order_by=graphics_rec.order)     
    except Exception as ex:
        print(str(ex))
        return  {"result": "error", "error_text": f"Failed to add graphical element: {ex}"} 


async def delete_element(app_db, content):
    try:
        await app_db.delete_records(
            graphics_rec, graphics_rec.id, 
            [rec['id'] for rec in content["elements"]]
        )

        return await app_db.get_records(graphics_rec, graphics_rec.view, content['view'], to_json=True, order_by=graphics_rec.order)
    except Exception as ex:
        print(str(ex))
        return  {"result": "error", "error_text": f"Failed to delete graphical element: {ex}"}            


async def clear_view_elements(app_db, content):
    try:
        await app_db.delete_records_recursively(graphics_rec, graphics_rec.view, content['view'])
        return  {"result": "ok"}
    except Exception as ex:
        print(str(ex))
        return  {"result": "error", "error_text": f"Failed to clear all view graphical elements {ex}"}                  


async def move_element(app_db, content):
    try:
        await app_db.update_multi_fields(
            graphics_rec, graphics_rec.id, 'id',
            [ {'id': rec['id'], 'order': rec['place']} for rec in content["elements"] ]
        )

        return await app_db.get_records(graphics_rec, graphics_rec.view, content['view'], to_json=True, order_by=graphics_rec.order)
    except Exception as ex:
        return  {"result": "error", "error_text": f"Failed to move graphical element {ex}"}                       


def reorder_graphics(app):
    print('!!!!!!!!!!!!!!! BROKEN reorder_graphics')
#    db = find_app_db(app)
#    with db_session:
#        data = db.graphics.select().order_by(lambda r: r.order)
#
#    new_order = 0.0
#    for el in data:
#        
#        with db_session:
#            el       = db.graphics[el.id]
#            el.order = new_order
#
#        new_order += 1.0


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
    app_db = find_application_db(content_json["name"])

    if check_permissions(auth, COMMANDS_DICT['perm_' + cmd]):
        return await COMMANDS_DICT.get(cmd, default_msg)(app_db, content_json)
    else:
        return { "result": "error", "error_text": f"Permission denied for user '{auth['user']}' accessing '{cmd}'" }
