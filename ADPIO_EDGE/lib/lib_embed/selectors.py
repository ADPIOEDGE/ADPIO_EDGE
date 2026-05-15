#GROUP={"order": 4, "name": "Selectors" }

import sys

#BLOCK={"name": "Select 1 to 4 ", "description": "selector msv mso msi", "type": "block"}
#IO={ "id": "selector" , "bind": {}, "type": "input",  "name": "Selector 1-4",  "datatype": "int float", "value": ""}
#IO={ "id": "value_1"  , "bind": {}, "type": "input",  "name": "Value 1",  "datatype": "", "value": ""}
#IO={ "id": "value_2"  , "bind": {}, "type": "input",  "name": "Value 2",  "datatype": "", "value": ""}
#IO={ "id": "value_3"  , "bind": {}, "type": "input",  "name": "Value 3",  "datatype": "", "value": ""}
#IO={ "id": "value_4"  , "bind": {}, "type": "input",  "name": "Value 4",  "datatype": "", "value": ""}
#IO={ "id": "result"   , "bind": {}, "type": "output", "name": "Result", "datatype": "", "value": ""}
def selectors_select_1to4(selector, value_1, value_2, value_3, value_4):
    match selector:
        case 1:
            return value_1
        case 2: # Matching multiple values
            return value_2
        case 3:
            return value_3
        case 4:
            return value_4     
        case _: # Default case
            sys.stderr.write(f'Selector error. incorret selector {selector}\n')
            return None
    

#BLOCK={"name": "Select Gate 1", "description": "selector gate", "type": "block"}
#IO={ "id": "selector" , "bind": {}, "type": "input",  "name": "Selector",  "datatype": "bool", "value": ""}
#IO={ "id": "value_1"  , "bind": {}, "type": "input",  "name": "Value 1",  "datatype": "", "value": ""}
#IO={ "id": "value_2"  , "bind": {}, "type": "input",  "name": "Value 2",  "datatype": "", "value": ""}
#IO={ "id": "result"   , "bind": {}, "type": "output", "name": "Result", "datatype": "", "value": ""}
def selectors_select_gate1(selector, value_1, value_2):
    if selector == True:
        return value_2
    else:
        return value_1