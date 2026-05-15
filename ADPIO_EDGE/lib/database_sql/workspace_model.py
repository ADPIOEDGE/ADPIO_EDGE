from typing import Any, Dict
from datetime import datetime

from sqlalchemy.orm  import registry
from sqlmodel        import Field, SQLModel, JSON, Column
from lib.database_sql.sqlmodel_driver import engine_db

from lib.globals  import WORKSPACE


class workspace_model(SQLModel, registry=registry(), checkfirst=False): #workspace model
    pass


class application_rec(workspace_model, table=True):
    name        : str       =  Field(max_length = 16,   default = 'App1', primary_key = True)
    description : str       =  Field(max_length = 128,  default = '',            )

    group       : str       =  Field(max_length = 16,   default = 'No Group',    )
    version     : str       =  Field(max_length = 12,   default = '0.0.1',       )
  
    autostart   : bool      =  Field(default = False                             )
  
    t_created   : datetime  =  Field(default_factory = datetime.now              )
    t_updated   : datetime  =  Field(default_factory = datetime.now              )
    t_built     : datetime  =  Field(default_factory = datetime.now              )

    view_list   : Dict[str, Any] = Field(
        default=[ {'name': 'Dashboard', 'value': 'Dashboard'}, ], 
        sa_column=Column(JSON) 
    )

    def to_json(self):
        return {
            "name"         : self.name        ,
            "description"  : self.description ,
            "group"        : self.group       ,
            "version"      : self.version     ,
            "autostart"    : self.autostart   ,
            
            "t_created"    : str(self.t_created),
            "t_updated"    : str(self.t_updated),
            "t_built"      : str(self.t_built)  ,

            "view_list"    : self.view_list     ,      
        }    


class user_rec(workspace_model, table=True):
    name        : str       =  Field(max_length = 12,  default = 'User', primary_key = True)
    password    : str       =  Field(max_length = 16,  default = '',               )
    sessionkey  : str       =  Field(max_length = 32,  default = 'No Key',         )
    sessionexp  : datetime  =  Field(default_factory = datetime.now                )
    homepage    : str       =  Field(max_length = 24,  default = '/system/about',  )
    profile     : str       =  Field(max_length = 16,  default = 'admin',          )
    description : str       =  Field(max_length = 64,  default = '',               )

    def to_json(self):
        return {
            'name'          :  self.name        ,
            'password'      :  self.password    ,
            'sessionkey'    :  self.sessionkey  ,
            'sessionexp'    :  str(self.sessionexp).split('.')[0], 
            'homepage'      :  self.homepage    ,
            'profile'       :  self.profile     ,
            'description'   :  self.description ,
        }


class logs_rec(workspace_model, table=True):
    date : datetime  =  Field(default_factory = datetime.now, primary_key = True)
    type : str       =  Field(max_length = 12  , default = 'notype'     ) 
    text : str       =  Field(max_length = 4096, default = 'notext'     ) 

    def to_json(self):
        return {
            "date"  :  str(self.date).split('.')[0], 
            "type"  :  self.type,                    
            "text"  :  self.text,              
        }


class logic_palette_rec(workspace_model, table=True):
    id           : str  =  Field(max_length = 64,   default = 'Funck BLK', primary_key = True)
    name         : str  =  Field(max_length = 32,   default = 'name here'                    )
    description  : str  =  Field(max_length = 64,   default = 'description'                  )
    group        : str  =  Field(max_length = 24,   default = 'New Group'                    )
    libimport    : str  =  Field(max_length = 128,  default = ''                             )
    type         : str  =  Field(max_length = 16,   default = 'block'                        )
    function     : str  =  Field(max_length = 128,  default = 'print(\'Empty Call\')'        )
    io           : Dict[str, Any] = Field(default={}, sa_column=Column(JSON)               )

    def to_json(self):
        return {
            'id'          :  self.id, 
            'name'        :  self.name, 
            'description' :  self.description, 
            'group'       :  self.group,
            'type'        :  self.type,
            'function'    :  self.function,
            'libimport'   :  self.libimport,
            'io'          :  self.io,            
        }


workspace_db  =  engine_db(f"sqlite:///{WORKSPACE}/workspace.db", workspace_model)