
#TO BE DEPRECIATED
from pony.orm import *
from database.model_app    import  app_datapoint_rec, app_graph_rec, app_logic_rec, app_trend_rec
#TO BE DEPRECIATED

from database_sql.workspace_model import workspace_db, application_rec

from system.globals import APPS_FOLDER

class __app_db:
    def __init__(self, app_name):
        self.dbase = None
        self.app_name = app_name
        
        self.graphics        = None
        self.datapoints      = None
        self.logic           = None
        self.trends          = None


    def init_db(self):  #For IDE Editing
        self.dbase = Database()
        #sql_debug(True)
        self.dbase.bind("sqlite", f"{APPS_FOLDER}/{self.app_name}/app_db.sqlite", create_db = True)
        
        self.datapoints     = app_datapoint_rec(self.dbase)
        self.graphics       = app_graph_rec    (self.dbase)
        self.logic          = app_logic_rec    (self.dbase)
        self.trends         = app_trend_rec    (self.dbase)

        self.dbase.generate_mapping(create_tables = True)

        if __debug__:
            print(f"APP {self.app_name} Data Base Initilized!")        
        

    def close_db(self):
        self.dbase.disconnect()
        
        if __debug__:
            print(f"APP {self.app_name} Data Base Terminated...")


async def apps_db_initialize():
    app_list = []
    app_list = await workspace_db.get_all_records(application_rec)

    for rec in app_list:
        create_app_db(rec.name)

    return app_list


async def apps_db_termiante():
    for rec in apps_db:
        rec.close_db()

    apps_db.clear()


def find_app_db(app_name):
    for rec in apps_db:
        if rec.app_name == app_name:
            return rec

    return None


def create_app_db(app_name):
    app = find_app_db(app_name)

    if app == None:
        new_db = __app_db(app_name)
        new_db.init_db()
        apps_db.append(new_db)


def delete_app_db(app_name):
    app = find_app_db(app_name)

    if app != None:
        app.close_db()
        apps_db.pop(apps_db.index(app))


apps_db = []