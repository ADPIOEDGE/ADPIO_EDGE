from math import sin, cos, tan

#GROUP={"order": 2, "name": "Trigonometry" }


#BLOCK={"name": "Sine", "description": "sine", "type": "block"}
#IO={ "id": "value"  , "bind": {}, "type": "input",  "name": "Value",  "datatype": "int float", "value": ""}
#IO={ "id": "result" , "bind": {}, "type": "output", "name": "Result", "datatype": "int float", "value": ""}
def trigo_sine(value):
    return sin(value)

#BLOCK={"name": "Cosine", "description": "cosine", "type": "block"}
#IO={ "id": "value"  , "bind": {}, "type": "input",  "name": "Value",  "datatype": "int float", "value": ""}
#IO={ "id": "result" , "bind": {}, "type": "output", "name": "Result", "datatype": "int float", "value": ""}
def trigo_cosine(value):
    return cos(value)

#BLOCK={"name": "Tangent", "description": "tangent", "type": "block"}
#IO={ "id": "value"  , "bind": {}, "type": "input",  "name": "Value",  "datatype": "int float", "value": ""}
#IO={ "id": "result" , "bind": {}, "type": "output", "name": "Result", "datatype": "int float", "value": ""}
def trigo_tangent(value):
    return tan(value)


