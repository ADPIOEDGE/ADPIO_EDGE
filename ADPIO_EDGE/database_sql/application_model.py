from typing import Any, Dict
from datetime import datetime

from sqlalchemy.orm  import registry
from sqlmodel        import Field, SQLModel, JSON, Column
from database_sql.sqlmodel_driver import engine_db

from system.globals import WORKSPACE, APPS_FOLDER
from assets.dataconversion import  str_to_dp

from database_sql.workspace_model import workspace_db, application_rec

class application_model(SQLModel, registry=registry()): #application model
    pass


class datapoints_rec(application_model, table=True):
    id          : int  =  Field(primary_key = True)

    name        : str  =  Field(max_length = 32,   default = 'Datapoint',  )
    description : str  =  Field(max_length = 128,  default = '',           )
    group       : str  =  Field(max_length = 24,   default = '',           )

    datatype    : str  =  Field(max_length = 8,    default = '',           )
    value       : str  =  Field(max_length = 128,  default = '',           )
    writable    : bool =  Field(default = False,                           )
    units       : str  =  Field(max_length = 24,   default = '',           )

    memalloc    : int  =  Field(default = -1                               )

    properties  : Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    protocol    : Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    trend       : Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    def to_json(self):
        return {
            'id'         : self.id,

            'name'       : self.name,
            'description': self.description,
            'group'      : self.group,

            'datatype'   : self.datatype,
            'value'      : str_to_dp(self.value, self.datatype),
            'writable'   : self.writable,
            'units'      : self.units,

            'memalloc'   : self.memalloc,

            'properties' : self.properties,
            'protocol'   : self.protocol,
            'trend'      : self.trend,
        }


class graphics_rec(application_model, table=True):
    id             : int   = Field(primary_key = True                       )

    order          : float = Field(default = 0                              ) 
    view           : str   = Field(max_length = 32,  default = 'Dashboard'  )
    datapoint_bind : int   = Field(default = -1                             ) #Datapoint name Value To Render

    def to_json(self):
        return {
            'id'             : self.id,
            'order'          : self.order,
            'view'           : self.view,
            'datapoint_bind' : self.datapoint_bind,
            'error'          : True       
        }


class logic_rec(application_model, table=True):
    id         : int  = Field(primary_key = True                                    )

    name       : str  =  Field(max_length = 32,   default = 'logic',                )
    type       : str  =  Field(max_length = 16,   default = 'block'                 )

    function   : str  =  Field(max_length = 256,  default = 'print(\'Empty Call\')' )     
    libimport  : str  =  Field(max_length = 128,  default = ''                      )
        
    x          : int  =  Field(default = 0,                                         )
    y          : int  =  Field(default = 0,                                         )

    io         : Dict[str, Any] = Field(default={}, sa_column=Column(JSON)          )

    def to_json(self):
        return {
            'id'       : self.id,

            'name'     : self.name,
            'type'     : self.type,

            'function' : self.function,
            'libimport': self.libimport,
    
            'x'        : self.x,
            'y'        : self.y,

            'io'       : self.io,
        }


class trend_rec(application_model, table=True):
    time      : datetime = Field(default_factory = datetime.now, primary_key = True)
    name      : str  =  Field(max_length = 32,  default = 'Datapoint',             )

    value     : str  =  Field(max_length = 128, default = '0',                     )
    datatype  : str  =  Field(max_length = 8,   default = '',                      )

    def to_json(self):
        return {
            'time'     :  self.time,
            'name'     :  self.name,
            'value'    :  self.value,
            'datatype' :  str(self.datatype),
        }
    

async def application_db_initialize():
    app_list = await workspace_db.get_all_records(application_rec)

    for rec in app_list:
        create_application(rec.name)

    return app_list


async def application_db_termiante():
    for rec in applciation_db:
        rec.terminate()

    applciation_db.clear()


def find_application_db(app_name):
    for db in applciation_db:
        if db.name == app_name:
            return db

    return None


def create_application(app_name):
    app = find_application_db(app_name)

    if app == None:
        new_app_db = engine_db(f"sqlite:///{APPS_FOLDER}/{app_name}/applicaton.db", application_model, name=app_name)
        new_app_db.initialize()
        applciation_db.append(new_app_db)


def delete_application(app_name):
    app = find_application_db(app_name)

    if app != None:
        app.terminate()
        applciation_db.pop(applciation_db.index(app))


#engine_db(f"sqlite:///{APPS_FOLDER}/{self.app_name}/applicaton.db") 
applciation_db     =  []