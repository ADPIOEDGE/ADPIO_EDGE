#GROUP={ "order": 99, "name": "Debug" }

from datetime import datetime
import sys
import psutil


	
#BLOCK={"name": "Print String To Terminal", "description": "Prints to terminal input_string", "type": "block"}
#IO={ "id": "input_string", "bind": {}, "type": "input",  "name": "Input 1",  "datatype": "any", "value": ""}
def debug_print_to_terminal(app_props, input_string):
    if input_string is None:
        input_string = 'None'
    sys.stderr.write(app_props['name']  + ': ' + str(input_string))
	
#BLOCK={"name": "Sys Stats", "description": "Show CPU RAM HDD", "type": "block"}
#IO={ "id": "cpu"      , "bind": {}, "type": "output",  "name": "CPU Load",  "datatype": "float", "value": ""}
#IO={ "id": "ram_used" , "bind": {}, "type": "output",  "name": "RAM Used",  "datatype": "float", "value": ""}
#IO={ "id": "ram_total", "bind": {}, "type": "output",  "name": "RAM Total", "datatype": "float", "value": ""}
def debug_sys_stats(): #CPU interval is thread blocking
    return psutil.cpu_percent(interval=6, percpu=False), psutil.virtual_memory().used >> 20, psutil.virtual_memory().total >> 20
    
    
