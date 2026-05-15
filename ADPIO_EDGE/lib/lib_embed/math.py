from math import sqrt

#GROUP={"order": 2, "name": "Math Operations" }

#BLOCK={"name": "Addition", "description": "sum +", "type": "block"}
#IO={ "id": "sum_1" , "bind": {}, "type": "input",  "name": "Sum 1",  "datatype": "int float", "value": ""}
#IO={ "id": "sum_2" , "bind": {}, "type": "input",  "name": "Sum 2",  "datatype": "int float", "value": ""}
#IO={ "id": "result", "bind": {}, "type": "output", "name": "Result", "datatype": "int float", "value": ""}
def math_add_2(sum_1, sum_2):
    return sum_1 + sum_2

#BLOCK={"name": "Subtraction", "description": "minus -", "type": "block"}
#IO={ "id": "minuend"   , "bind": {}, "type": "input",  "name": "Minuend",    "datatype": "int float", "value": ""}
#IO={ "id": "subtrahend", "bind": {}, "type": "input",  "name": "Subtrahend", "datatype": "int float", "value": ""}
#IO={ "id": "result"    , "bind": {}, "type": "output", "name": "Result",     "datatype": "int float", "value": ""}
def math_subtract(minuend, subtrahend):
    return minuend - subtrahend

#BLOCK={"name": "Multiplication", "description": "multi *", "type": "block"}
#IO={ "id": "multi_1", "bind": {}, "type": "input",  "name": "Multi 1", "datatype": "int float", "value": ""}
#IO={ "id": "multi_2", "bind": {}, "type": "input",  "name": "Multi 2", "datatype": "int float", "value": ""}
#IO={ "id": "result" , "bind": {}, "type": "output", "name": "Result",  "datatype": "int float", "value": ""}
def math_multiplication(multi_1, multi_2):
    return multi_1 * multi_2

#BLOCK={"name": "Division", "description": "divide /", "type": "block"}
#IO={ "id": "divident", "bind": {}, "type": "input",  "name": "Divident", "datatype": "int float", "value": ""}
#IO={ "id": "divisor" , "bind": {}, "type": "input",  "name": "Divisor",  "datatype": "int float", "value": ""}
#IO={ "id": "result"  , "bind": {}, "type": "output", "name": "Result",   "datatype": "int float", "value": ""}
def math_division(divident, divisor):
    return divident / divisor

#BLOCK={"name": "Absolute", "description": "absolute abs", "type": "block"}
#IO={ "id": "value"  , "bind": {}, "type": "input",  "name": "Value",  "datatype": "int float", "value": ""}
#IO={ "id": "result" , "bind": {}, "type": "output", "name": "Result", "datatype": "int float", "value": ""}
def math_absolute(value):
    return abs(value)

#BLOCK={"name": "Square Root", "description": "SQRT", "type": "block"}
#IO={ "id": "value"  , "bind": {}, "type": "input",  "name": "Value",  "datatype": "int float", "value": ""}
#IO={ "id": "result" , "bind": {}, "type": "output", "name": "Result", "datatype": "int float", "value": ""}
def math_sqrt(value):
    return sqrt(value)


