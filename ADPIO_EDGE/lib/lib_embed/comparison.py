#GROUP={"order": 3, "name": "Comparison" }

#BLOCK={"name": "Greater", "description": ">", "type": "block"}
#IO={ "id": "", "bind": {}, "type": "input",   "name": "First Value",   "datatype": "int float", "value": ""}
#IO={ "id": "", "bind": {}, "type": "input",   "name": "Second Value",  "datatype": "int float", "value": ""}
#IO={ "id": "", "bind": {}, "type": "output",  "name": "Result",        "datatype": "bool",      "value": ""}  
def comparison_more_fl(compare_1, compare_2):
    if compare_1 > compare_2:
        return True
    else:
        return False

#BLOCK={"name": "Greater or Equal", "description": ">=", "type": "block"}
#IO={ "id": "compare_1", "bind": {}, "type": "input",  "name": "First Value",   "datatype": "int float", "value": ""}
#IO={ "id": "compare_2", "bind": {}, "type": "input",  "name": "Second Value",  "datatype": "int float", "value": ""}
#IO={ "id": "result"   , "bind": {}, "type": "output", "name": "Result",        "datatype": "bool",      "value": ""}
def comparison_more_or_eq_fl(compare_1, compare_2):
    if compare_1 >= compare_2:
        return True
    else:
        return False
    
#BLOCK={"name": "Equality", "description": "=", "type": "block"}
#IO={ "id": "compare_1", "bind": {}, "type": "input",  "name": "First Value",   "datatype": "int float", "value": ""}
#IO={ "id": "compare_2", "bind": {}, "type": "input",  "name": "Second Value",  "datatype": "int float", "value": ""}
#IO={ "id": "result"   , "bind": {}, "type": "output", "name": "Result",        "datatype": "bool",      "value": ""}  
def comparison_equality_fl(compare_1, compare_2):
    if compare_1 == compare_2:
        return True
    else:
        return False
    