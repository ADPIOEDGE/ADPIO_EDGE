import sys
import os
sys.path.append(f'{os.getcwd()}/ext_lib/') #External Libraries

import uvicorn
import asyncio
from pydantic import BaseModel


### TO BE DEPRICIATED ###
from pony.orm import *
### TO BE DEPRICIATED ###
from sqlmodel import Field, Session, SQLModel, create_engine


#FAST API
from fastapi                 import FastAPI, Request
from fastapi.responses       import HTMLResponse
from fastapi.staticfiles     import StaticFiles
from contextlib              import asynccontextmanager
from fastapi.middleware.gzip import GZipMiddleware


#This more advanced, for future
#from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
#from pydantic import BaseModel


#SYSTEM
from system.globals         import ROOT_FOLDER, WORKSPACE, WEB_INF_index
from system.settings_server import settings_cfg

#DB
### TO BE DEPRICIATED ###
from database.app_db        import apps_db_initialize, apps_db_termiante
### TO BE DEPRICIATED ###

from database_sql.workspace_model import workspace_db

from system.shared_mem      import init_server_mem, clear_server_mem, get_server_mem, STATUS_MEM_ADDR, WORKERS_MEM_ADDR, DB_REBUILD_MEM_ADDR, TERMINAL_MEM_ADDR
from assets.terminal        import terminal_web


#app_ide
from content.app_ide            import app_ide_mng
from content.app_ide_datapoints import app_ide_datapoints_mng
from content.app_ide_graphics   import app_ide_graphics_mng
from content.app_ide_logic      import app_ide_logic_mng
from content.app_live           import app_live_mng

#System Managers
from content.users  import user_mng, cached_auth, auth_no_users_fix
from content.logger import log_task_mng, print_log_system, print_app_event

#Tools 
from content.trends_tools  import trends_tools_mng
from content.system_tools  import system_tools_mng, rebuild_logic_db
from content.network_tools import network_tools_mng

#APPS
from system.app_engine              import stop_app, run_app
from database_sql.application_model import application_db_initialize, application_db_termiante, applciation_db

#Drivers
from drivers.loraWAN_conn_sever import loraWAN_server
from drivers.bacnet_server      import bacnet_server


#from multiprocessing import freeze_support

INDEX       = ""
user_cache  = []
worker      = -1

loraWAN_serv = None
bacnet_serv  = None


class request_jsn(BaseModel): #for standart commands, update, delete record and etc
    cmd:     str = 'command'
    #user:    str = ''
    content: str = ''


async def on_server_startup_drivers(settings):
    global loraWAN_serv, bacnet_serv
    server_mem = get_server_mem()

    #Check If Workspace properly initialized
    if server_mem[DB_REBUILD_MEM_ADDR]:
        print("\n\nFirst DB Initialization, Auto Rebuild Mode On\n\n")
        await rebuild_logic_db({})
        print("\n\nAuto Rebuild Complete!!!\n\n")

    #Initialize drivers
    if settings.lorawan_server['net_autostart']:
        loraWAN_serv = loraWAN_server()
        await loraWAN_serv.init_service( settings.lorawan_server )

    if settings.bacnet_server['net_autostart']:
        bacnet_serv = bacnet_server()
        await bacnet_serv.init_service( settings.bacnet_server )

    server_mem[STATUS_MEM_ADDR] = 1 #Server Status - On


async def on_server_shutdown_drivers():
    global loraWAN_serv, bacnet_serv

    if not loraWAN_serv == None:
        loraWAN_serv.terminate_service()

    if not bacnet_serv == None:
        bacnet_serv.terminate_service()        

    server_mem = get_server_mem()
    server_mem[STATUS_MEM_ADDR] = 2 #Server Status - Off

    
@asynccontextmanager
async def startup_shutdown(app: FastAPI):
    global INDEX, user_cache, worker
    INDEX = WEB_INF_index() #Relink Files in webinf in index.html

    #Init Databases
    workspace_db.initialize()

    server_mem                   = get_server_mem()
    server_mem[WORKERS_MEM_ADDR] += 1 #Workers Count
    worker                       = server_mem[WORKERS_MEM_ADDR]

    if not server_mem[TERMINAL_MEM_ADDR]:
        terminal = terminal_web('system', True) #Terminal For Workers

    print(f'Server Status: {server_mem[STATUS_MEM_ADDR]}, Worker={server_mem[WORKERS_MEM_ADDR]}')

    await auth_no_users_fix() #if there is no user - create admin/admin
    user_cache = await cached_auth()

    #APP database init and autostart
    appliacations = await application_db_initialize()
    print(f"\n\nApplications Count: {len(appliacations)}\n" )
    #if worker == 1:
    #    print(f"APPS Count: {len(appliacations)}\n" )
    #    for app in appliacations:
    #        print(f"{app.name} Autostart: {app.autostart}" )
    #        if app.autostart:
    #            await run_app(app.name)
    #        print()
    
    if worker == 1:
        await print_log_system(f"ADPIO Edge Started! Debug Mode: {__debug__}\n")
    
    yield   #Before This - Startup, After - Shutdown

    #if worker == 1:
    #    for app in appliacations:
    #        try:
    #            await stop_app(app.name)
    #        except Exception as ex:
    #            await print_app_event(f'App {app.name} stopped') 
    
    await application_db_termiante()

    if worker == 1:
        await print_log_system("ADPIO Edge Terminated...")

    if not server_mem[TERMINAL_MEM_ADDR]:
        terminal.terminate()

    workspace_db.terminate()


app = FastAPI( 
    lifespan=startup_shutdown, 

    title="ADPIO_EDGE",
    #version=""
    #debug=True 

    #docs_url    = None, # Disable Swagger UI
    #redoc_url   = None, # Disable ReDoc
    #openapi_url = None  # Disable OpenAPI JSON schema        
) 


app.add_middleware(
    GZipMiddleware,
    minimum_size  = 1024 * 8,
    compresslevel = 6
)

app.mount( "/assets",    StaticFiles(directory = "./WEB-INF/assets"),    name = "assets")    #Svelte Static Resources, ex: bundle, files, pictures    
app.mount( "/favicon",   StaticFiles(directory = "./WEB-INF/favicon"),   name = "favicon")   #Favicon   
app.mount( "/resources", StaticFiles(directory = "./WEB-INF/resources"), name = "resources") #Resources   


def check_auth(sessionid):
    global user_cache

    for usr in user_cache :
        if usr['sessionkey'] == sessionid:
           return usr

    #return {"result": "ok", "auth": True}
    return { "result": "error", "auth": False, "error_text": "The Username or Password is Incorrect" }


@app.get("/",           response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
async def get_index():
    return INDEX

#https://fastapi.tiangolo.com/advanced/security/http-basic-auth/
#async def login(authed: Annotated[str, Depends(get_current_username)], req_json: request_jsn): #, request: Request


@app.post("/login")
async def login(req_json: request_jsn): #, request: Request 
    global user_cache
    user_cache = await cached_auth()
    res = await user_mng({'user': '', 'profile': ''}, req_json.cmd, req_json.content)

    if (res['result'] == 'ok'):
        return  { "result": "ok", "auth": True, "sessionkey": res['sessionkey'], "user": res['user'], "profile": res['profile'] }
    else :
        return { "result": "error", "auth": False, "error_text": "The Username or password are incorrect" }
    

#User and Navigation
@app.post("/app_ide")
async def app_ide(request: Request, req_json: request_jsn ): #, request: Request    
    global user_cache
    user_auth = check_auth(request.headers.get("authorization"))
    return await app_ide_mng(user_auth, req_json.cmd, req_json.content)


@app.post("/app_ide_datapoints")
async def app_ide_datapoints(request: Request, req_json: request_jsn ): #, request: Request 
    global user_cache
    user_auth = check_auth(request.headers.get("authorization"))
    return await app_ide_datapoints_mng(user_auth, req_json.cmd, req_json.content)


@app.post("/app_ide_graphics")
async def app_ide_graphics(request: Request, req_json: request_jsn ): #, request: Request 
    global user_cache
    user_auth = check_auth(request.headers.get("authorization"))
    return await app_ide_graphics_mng(user_auth, req_json.cmd, req_json.content)


@app.post("/app_ide_logic")
async def app_ide_logic(request: Request, req_json: request_jsn ): #, request: Request 
    global user_cache
    user_auth = check_auth(request.headers.get("authorization"))
    return await app_ide_logic_mng(user_auth, req_json.cmd, req_json.content)


@app.post("/app_live")
async def app_live(request: Request, req_json: request_jsn ): #, request: Request
    global user_cache
    user_auth = check_auth(request.headers.get("authorization"))
    return await app_live_mng(user_auth, req_json.cmd, req_json.content)


#User and Navigation
@app.post("/user")
async def user(request: Request, req_json: request_jsn ): #, request: Request
    global user_cache
    user_auth = check_auth(request.headers.get("authorization"))
    return await user_mng(user_auth, req_json.cmd, req_json.content)  


#User and Navigation
@app.post("/logger")
async def logger(request: Request,  req_json: request_jsn ): #, request: Request 
    global user_cache    
    user_auth = check_auth(request.headers.get("authorization"))
    return await log_task_mng(user_auth, req_json.cmd, req_json.content)


#Tools
@app.post("/trends")
async def trends_tools(request: Request, req_json: request_jsn ): #, request: Request
    global user_cache    
    user_auth = check_auth(request.headers.get("authorization"))
    return await trends_tools_mng(user_auth, req_json.cmd, req_json.content)  


@app.post("/network_tools")
async def network_tools(request: Request, req_json: request_jsn ): #, request: Request
    global user_cache    
    user_auth = check_auth(request.headers.get("authorization"))
    return await network_tools_mng(user_auth, req_json.cmd, req_json.content)  


@app.post("/system_tools")
async def system_tools(request: Request, req_json: request_jsn ): #, request: Request
    global user_cache    
    user_auth = check_auth(request.headers.get("authorization"))
    return await system_tools_mng(user_auth, req_json.cmd, req_json.content)  


def main():
    print("Initializing APDIO EDGE...")

    if __debug__: 
        print("DEBUG is ON. Run with -O or -OO to turn off debug")
        print("!!!!! THIS VERSION NOT FOR DISTRIBUTION !!!!!")        
    
    print(f"Global ROOT Folder:      {ROOT_FOLDER}"    )
    print(f"Global WORKSPACE Folder: {WORKSPACE}\n"    )
    
    settings = settings_cfg()
    settings.read_settings()

    auto_reload = False                         # Fix for pyinstaller, if not done you will get infinite loop,
    workers     = settings.uvicorn["workers"]   # Note reload and workers are exluisive    
    log_lvl     = "error"
    
    if __debug__:               # For Dist reload must be false
        auto_reload = True
        workers     = 1
        log_lvl     = "info"   
        print("DEBUG ON !!!")

#Init Workspace DB
    workspace_db.initialize()   

    init_server_mem(
        terminal     = settings.terminal,
        auto_rebuild = settings.auto_rebuild,
        lora_alloc   = settings.lorawan_server['alloc_size'], 
        bacnet_alloc = settings.bacnet_server ['alloc_size'],
    )

    if not settings.terminal:
        print("Custom STDOUT/ERR Initialized... Look In Log Files ")
        terminal = terminal_web('system', True) #Main Terminal

    print("Initializing APDIO EDGE...")
    asyncio.run( on_server_startup_drivers(settings) )
    
    #Init FastAPI
    uvicorn.run(
        "adpio_edge:app",
        host      = settings.uvicorn["host"],
        port      = settings.uvicorn["port"],

        reload    = auto_reload,
        workers   = workers,
        log_level = log_lvl,
    )   

    asyncio.run( on_server_shutdown_drivers() )
    clear_server_mem()

    if not settings.terminal:
        terminal.terminate()

    workspace_db.terminate()


if __name__ == "__main__":
    #freeze_support() #for windows only?
    main()
