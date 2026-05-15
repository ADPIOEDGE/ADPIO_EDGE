import ujson
import os
import shutil
import asyncio 

from lib.globals       import ROOT_FOLDER, WORKSPACE, APPS_FOLDER, ASSET_FOLDER
from system.shared_mem import DB_REBUILD_MEM_ADDR


class settings_cfg:
    def __init__(self):
        self.uvicorn        = None
        self.lorawan_server = None
        self.bacnet_server  = None

        self.python         = ''
        self.terminal       = False
        self.auto_rebuild   = False
        
        self.create_work_folder()        
        
    def create_work_folder(self):
        #make workspace
        if (not os.path.isdir(WORKSPACE)):
            try: 
                os.mkdir(WORKSPACE)
                self.auto_rebuild = True
            except OSError as error:  
                print(error)
                
        #make default setings file
        if (not os.path.isfile(f'{WORKSPACE}/settings.json')):
            try: 
                shutil.copy2( f'{ROOT_FOLDER}/assets/settings.json', f'{WORKSPACE}/settings.json' )
            except OSError as error:  
                print(error)

        #make apps folder
        if (not os.path.isdir(APPS_FOLDER)):
            try: 
                os.mkdir(APPS_FOLDER)
            except OSError as error:  
                print(error)
        
        #make assets folder
        if (not os.path.isdir(ASSET_FOLDER)):
            try: 
                os.mkdir(ASSET_FOLDER)
            except OSError as error:  
                print(error)      

        #LOGS - HDD
        if (not os.path.isdir(WORKSPACE + '/log')):
            try: 
                os.mkdir(WORKSPACE + '/log')
            except OSError as error:  
                print(error)      
                                      
        
    def read_settings(self):
        with open (f'{WORKSPACE}/settings.json' ) as f:
            rd = f.read()
            cls = ujson.loads( rd )
            
            self.python         = cls['python_exe']
            self.terminal       = cls['terminal']
            
            self.uvicorn        = cls['uvicorn']

            self.lorawan_server = cls['lorawan_server']
            self.bacnet_server  = cls['bacnet_server']
            

    """
    def write_settings(self):
        jsn = {
            'uvicorn':         self.uvicorn,
            'app_ids':         self.app_ids,
            'loraWAN':       self.loraWAN,
        }
        with open(WORK_FOLDER + '/settings.json', 'w') as f:
            f.write( ujson.dumps(jsn,  default = lambda o: o.__dict__, indent=4) )
    """