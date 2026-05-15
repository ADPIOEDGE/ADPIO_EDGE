import ujson

from datetime import datetime
 
#GET DB
from content.app_ide            import update_list 
from content.app_ide_datapoints import load_datapoints

#DB
from lib.database_sql.application_model  import find_application_db, trend_rec, datapoints_rec
from sqlmodel import col
from sqlalchemy.sql import text

from lib.dataconversion import  str_to_dp

from content.users import check_permissions


def to_json(rec, utc_off = 0):
    return {   #https://www.w3schools.com/python/python_datetime.asp
        #"time_table"     : rec.time.strftime("%c"),
        "time"           : rec.time.strftime("%H:%M:%S"),
        "date"           : rec.time.strftime("%a %m.%d.%Y"),        
        
        "epoch"          : int( round( datetime.timestamp( rec.time ) + utc_off )), #rounded

        "value"          : str_to_dp( rec.value, rec.datatype ),      
        #"datatype"      : rec.datatype
    }


async def get_trend_list(application_db, content):
    trend_list = []    
    app_list = await update_list({})

    for app in app_list:
        data_p_list: list[datapoints_rec] = await load_datapoints(app['name'])        
        new_sheme = {"name": app['name'], "value": app['name'], "trends": [] }
        
        for dp in data_p_list:
            if dp.trend['enable']:
                new_sheme["trends"].append({"name": dp.name, "value": dp.name})
                
        trend_list.append(new_sheme)
    
    return trend_list 


async def load_trend(application_db, content):
    utc_off = datetime.now().astimezone().utcoffset().total_seconds()

    try:
        trend_recs: list[trend_rec] = await application_db.get_all_records(trend_rec, order_by_desc=trend_rec.time, limit=1200)
        return [ to_json(rec, utc_off) for rec in trend_recs ]
    except Exception as ex:
        return  {"result": "error", "error_text": f"Failed To Load Last Trend {ex}"}    


async def load_date_range_trend(application_db, content):
    utc_off = datetime.now().astimezone().utcoffset().total_seconds()

    start_date = datetime.fromisoformat(content['start'] + " 00:00:00.000000")#.replace("08:00:00", "00:00:00")
    end_date   = datetime.fromisoformat(content['end']   + " 23:59:59.999999")#.replace("08:00:00", "23:59:59")

    try:
        trend_recs: list[trend_rec] = await application_db.get_records_range(
            trend_rec, trend_rec.time,
            start_date, end_date, 
            order_by_desc=trend_rec.time, 
            limit=1200
        )
        return [ to_json(rec, utc_off) for rec in trend_recs ]   
    except Exception as ex:
        return  {"result": "error", "error_text": f"Failed To Load Date Range Trend {ex}"}    
    

COMMANDS_DICT = { #Command, Profile Permission
    'get_trend_list'        : get_trend_list,             'perm_get_trend_list'           : 'any, ',
    'load_last_trend'       : load_trend,                 'perm_load_last_trend'          : 'any, ',
    'load_date_range_trend' : load_date_range_trend,      'perm_load_date_range_trend'    : 'any, ',
    #'get_app_edit_tree' : get_app_edit_tree,    'perm_get_app_edit_tree' : 'any',
}

#DEFAULT
async def default_msg(content):
    print('Request Error user_mng: ' + str(content))
    return {"result": "error", "error_text": "user_mng command not found"}


async def trends_tools_mng(auth, cmd, content):
    app_db = None
    content_json = ujson.loads( content )
    
    if 'app' in content_json:
        app_db = find_application_db(content_json["app"])


    if check_permissions(auth, COMMANDS_DICT['perm_' + cmd]):
        return await COMMANDS_DICT.get(cmd, default_msg)(app_db, content_json)
    else:
        return { "result": "error", "error_text": f"Permission denied for user '{auth['user']}' accessing '{cmd}'" }
