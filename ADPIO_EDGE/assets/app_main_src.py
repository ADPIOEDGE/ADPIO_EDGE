import asyncio
import sys

#Shared Memory
from multiprocessing.shared_memory    import ShareableList

#<LIBIMPORT/>

#DB
from lib.database_sql.sqlmodel_driver   import engine_db
from lib.database_sql.application_model import application_model, datapoints_rec, trend_rec

from lib.terminal       import terminal_web
from lib.dataconversion import str_to_dp

from lib.globals        import APPS_FOLDER


APP_NAME        = "nonameapp"
application_db  = None


async def startup(shared_mem):
    global application_db

    application_db = engine_db(f'sqlite:///{APPS_FOLDER}/{APP_NAME}/application.db', application_model)
    application_db.initialize()

    datapoints: list[datapoints_rec] = await application_db.get_all_records(datapoints_rec)
    for d_rec in datapoints:
        shared_mem[d_rec.memalloc] = str_to_dp(d_rec.value, d_rec.datatype, fallback = True)
    
    sys.stdout.write(f"{APP_NAME} Loading Datapoint Values (Count {len(datapoints)})...\n")


async def save_current_values(shared_mem):
    global application_db
    
    datapoints: list[datapoints_rec] = await application_db.get_all_records(datapoints_rec)
    mem_list = []
    
    for dp in datapoints:
        mem_list.append({'id': dp.id, 'value': str(shared_mem[dp.memalloc])})

    if (len(mem_list) > 0):
        await application_db.update_multi_fields(datapoints_rec, datapoints_rec.id, 'id', mem_list)
            

async def terminate(shared_mem):
    await save_current_values(shared_mem)
    application_db.terminate()


async def trends_sync(shared_mem, trend_list, sleep):
    global application_db

    for tr in trend_list:
        tr["left"] -= sleep
        
        if tr["left"] <= 0 and tr["old_value"] != shared_mem[tr["memalloc"]]:
            tr["old_value"] = shared_mem[tr["memalloc"]]
            tr["left"] = tr["refresh"]     
            
            await application_db.add_record( trend_rec (
                name     = tr['name'],
                value    = str(shared_mem[tr["memalloc"]]),
                datatype = tr['datatype'],                
            ) )

    return trend_list


async def exec():
    if not __debug__:
        terminal = terminal_web(f'apps_{APP_NAME}', True)

    SLEEP      = 1
    sys.stdout.write(f'APP {APP_NAME} Initializing...\n')

#Shared Mems
    shared_mem = ShareableList( [
            True, 0, #Default Field: Status/Loop Count
            #<DATAPOINTS_LENGTH/>
            
            #<DATAPOINTS_DEF/>
        ], name=f'{APP_NAME}_sharedmem' # track=False, for py 3.13+
    )

#Binds
    bind_mem = ShareableList( [
            #<BINDS_LENGTH/> #Buffer Length
            
            #<BINDS_DEF/>
        ], name=f'{APP_NAME}_bindmem' #track=False, for py 3.13+
    )

#Trends
    trends = [
        #<TRENDS_INIT>
    ]

    sys.stdout.write(f'APP {APP_NAME} Started, Shared Mem Name: {APP_NAME}_sharedmem, Loop Delay: {SLEEP}\n')
  
    await startup(shared_mem)    
    #await write_defaults(shared_mem) #Writed Defaults
    
    while shared_mem[0]:
        try:
            await asyncio.sleep(SLEEP)

    #Gets
            #<GETTERS_CODE/>

    #Code
            #<BLOCK_CODE/>

    #Sets
            #<SETTERS_CODE/>
            
            if __debug__:
                shared_mem[1] += 1
                sys.stdout.write(f'LOOP EXECUTED. Status = {shared_mem[0]} , Loop = {shared_mem[1]}\n')
                if shared_mem[1] == 254:
                    shared_mem[1] = 0
                       
        except Exception as err:
            sys.stderr.write(f'APP {APP_NAME} Runtime Error : {err} \n')
        except:
            sys.stderr.write(f'APP {APP_NAME} Unnamed Error\n')
            shared_mem[0] = False

    #Trends loop
        trends = await trends_sync(shared_mem, trends, SLEEP)
               
    await terminate(shared_mem)
            
    #Clear Shared Memory
    shared_mem.shm.close()
    shared_mem.shm.unlink()
    
    bind_mem.shm.close()
    bind_mem.shm.unlink()

    sys.stdout.write(f'APP {APP_NAME} Terminated.\n')
    if not __debug__:
        terminal.terminate()


if __name__ == "__main__":
    if __debug__: sys.stdout.write("DEBUG For APPS is on. Run with -O to turn off debug\n")
    asyncio.run( exec() )

