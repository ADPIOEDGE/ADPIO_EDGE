#GROUP={ "order": 1, "name": "Logic Gates" }


#BLOCK={"name": "AND", "description": "", "type": "block"}
#IO={ "id": "input_1", "bind": {}, "type": "input",  "name": "Value 1", "datatype": "bool", "value": ""}
#IO={ "id": "input_2", "bind": {}, "type": "input",  "name": "Value 2", "datatype": "bool", "value": ""}
#IO={ "id": "result" , "bind": {}, "type": "output", "name": "Result" , "datatype": "bool", "value": ""}
def logic_gates_and(input_1, input_2):
    if input_1 == True and input_2 == True:
        return True
    else: 
        return False


#BLOCK={"name": "OR", "description": "", "type": "block"}
#IO={ "id": "input_1", "bind": {}, "type": "input",  "name": "Value 1", "datatype": "bool", "value": ""}
#IO={ "id": "input_2", "bind": {}, "type": "input",  "name": "Value 2", "datatype": "bool", "value": ""}
#IO={ "id": "result" , "bind": {}, "type": "output", "name": "Result",  "datatype": "bool", "value": ""}
def logic_gates_or(input_1, input_2):
    if input_1 == True or input_2 == True:
        return True    
    return False


#BLOCK={"name": "NOR", "description": "", "type": "block"}
#IO={ "id": "input_1", "bind": {}, "type": "input",  "name": "Value 1", "datatype": "bool", "value": ""}
#IO={ "id": "input_2", "bind": {}, "type": "input",  "name": "Value 2", "datatype": "bool", "value": ""}
#IO={ "id": "result" , "bind": {}, "type": "output", "name": "Result",  "datatype": "bool", "value": ""}
def logic_gates_nor(input_1, input_2):
    if input_1 == True and input_2 == True:
        return True    
    return False


#BLOCK={"name": "XOR", "description": "", "type": "block"}
#IO={ "id": "input_1", "bind": {}, "type": "input",  "name": "Value 1", "datatype": "bool", "value": ""}
#IO={ "id": "input_2", "bind": {}, "type": "input",  "name": "Value 2", "datatype": "bool", "value": ""}
#IO={ "id": "result" , "bind": {}, "type": "output", "name": "Result",  "datatype": "bool", "value": ""}
def logic_gates_xor(input_1, input_2):
    #bool(a) != bool(b)  
    return input_1 ^ input_2


#BLOCK={"name": "Negation", "description": "", "type": "block"}
#IO={ "id": "input" , "bind": {}, "type": "input",  "name": "Input",  "datatype": "bool", "value": ""}
#IO={ "id": "result", "bind": {}, "type": "output", "name": "Result", "datatype": "bool", "value": ""}
def logic_gates_negation(input):
    if input == False:
        return True 
    else:
        return False