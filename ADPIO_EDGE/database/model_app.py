from typing import Optional
from datetime import datetime
from pony.orm import *

from assets.app_lib import app_datapoint_rec as app_datapoint_run  #Runtime
from assets.app_lib import app_trend_rec     as app_trend_run      #runtime

#MAIN Datatbase, for regestering an app
def app_rec(db):
    table = 'app_model'

    fields = {
		'_table_': table,

        'name'            : PrimaryKey( str, 16,  default = 'App1'            ),
        'description'     : Optional( str, 128,   default = '',               ),
          
        'group'           : Optional( str, 16,    default = 'No Group',       ),
        'version'         : Optional( str, 12,    default = '0.0.1',          ),
  
        'autostart'       : Optional( bool,       default = False             ),
  
        't_created'       : Optional( datetime,   default = datetime.now      ),
        't_updated'       : Optional( datetime,   default = datetime.now      ),
        't_built'         : Optional( datetime,   default = datetime.now      ),
        
        'view_list'       : Optional( Json,       default = [
            {'name': 'Dashboard', 'value': 'Dashboard'},
            {'name': 'Settings',  'value': 'Settings'},
        ]  ),
    }

    return type(table.capitalize(),(db.Entity,),fields)


#SUB database in app folder
def app_datapoint_rec(db):
    return app_datapoint_run(db)



def app_graph_rec(db):
    table = 'app_graph_model'

    fields = { 
		'_table_': table,

		'id'              : PrimaryKey(int, auto = True                                  ),

        'order'           : Optional ( float,     default = 0                            ),

        #'name'            : Required ( str, 32,   default = 'widget',                    ),
        #'description'     : Optional ( str, 64,   default = 'description'                ),
        
        'view'            : Optional  ( str, 32,   default = 'Dashboard'                 ),

        'datapoint_bind'  : Optional  ( int,       default = -1                          ), #Datapoint name Value To Render

        #'parent'          : Optional ( int,          default = -1                         ),

        #'widget_area'     : Optional ( str, 32,   default = 'widget_area'                ),
        #'properties'      : Optional ( Json, default = []                                ),

        #'datapoint_app'   : Optional ( str, 24,                                         ),
        #'datapoint_name'  : Optional ( str, 24,                                         ),

        #'body'          : Required  ( str, 512,  default = '<div>Palette Element:</div>'  ),        
    }

    return type(table.capitalize(),(db.Entity,),fields)


def app_logic_rec(db):
    table = 'app_logic_model'
    
    fields = {
		'_table_': table,

		'id'              :     PrimaryKey( int, auto = True),

        'name'            :     Required  ( str, 32,      default = 'logic',                ),
        #'description'    : Optional  ( str, 128,     default = '',                         ),
        'type'            :     Optional ( str, 16,   default = 'block'                     ),

        'function'        :     Optional  ( str, 256, default = 'print(\'Empty Call\')'     ),        
        'libimport'       :     Optional  ( str, 128, default = ''                          ),
        
        'x'               :     Required  ( int, default = 0,                               ),
        'y'               :     Required  ( int, default = 0,                               ),

        'io'              :     Optional ( Json, default = []                               ),
    }

    return type(table.capitalize(),(db.Entity,),fields)


def app_trend_rec(db):
    return app_trend_run(db)
