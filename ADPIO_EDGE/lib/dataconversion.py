from multiprocessing.shared_memory import ShareableList


def strtobool (val):
    """Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    else:
        raise ValueError("invalid truth value %r" % (val,))
    
def str_to_dp(value, dp_type, fallback = False):
    try:
        if str(value).lower() == "nan":
            if fallback: return __str_to_dp_fallback(dp_type)
            return None
            
        match dp_type:
            case "bool":
                return strtobool(str(value))
            case "int":
                return int(str(value))
            case "float":
                return float(str(value))
            case "str":
                return str(value)
            case _: 
                print('Unknown Data Type  %r' % (str(value)))
                if fallback: return __str_to_dp_fallback(dp_type)
                return None
            
    except: #Fall Back Settings
        print('excetpion converting value {}[{}]'.format(str(value), dp_type))
        if fallback: return __str_to_dp_fallback(dp_type)
        return None
    
def __str_to_dp_fallback(dp_type):
    match dp_type:
        case "bool":
            return False
        case "int":
            return 0
        case "float":
            return 0.0
        case "str":
            return "Fall Back"
        case _: 
            print('Unknown Data Type in app %r' % (str(dp_type),))
            return "None"
        
        
def str_to_dp_trend_safe(value, dp_type):
    try:
        if str(value).lower() == "nan":
            return 0
            
        match dp_type:
            case "bool":
                res = strtobool(str(value))
                if res == True:
                    return 1
                else:
                    return 0
                
            case "int":
                return int(str(value))
            
            case "float":
                return float(str(value))
            
            case "str":
                return 0
            
            case _: 
                print('Unknown Data Type  %r' % (str(value)))
                return 0
    except: #Fall Back Settings
        print('excetpion converting value {}[{}]'.format(str(value), dp_type))
        return 0
            

async def get_mem(app): # try: i do not know why, but try catch should be done outside this function, otherwise it does not work... WTF?
    shared_mem_list = ShareableList(name=f'{app}_sharedmem') 
    mem_length  = shared_mem_list[2] + 3    #dp count
    
    res = []
    for i in range(3, mem_length):
        res.append(shared_mem_list[i])

    #print(str(shared_mem_list))    
    shared_mem_list.shm.close()

    return res

async def get_mem_value(app, memalloc): # try: i do not know why, but try catch should be done outside this function, otherwise it does not work... WTF?
    shared_mem_list = ShareableList(name=f'{app}_sharedmem')     
    value = shared_mem_list[memalloc]
    shared_mem_list.shm.close()

    return value



async def set_mem_value(app, memalloc, datatype, value):
    shared_mem_list = ShareableList(name=f'{app}_sharedmem') 
    #check if value correct
    
    new_value = str_to_dp(str(value), datatype)
    if new_value != None:
        shared_mem_list[memalloc] = new_value
    shared_mem_list.shm.close()


async def get_binds(app):
    shared_mem_list = ShareableList(name=f'{app}_bindmem') 
    mem_length  = shared_mem_list[0] + 1    #bind count
    
    res = []
    for i in range(1, mem_length):
        res.append(shared_mem_list[i])

    #print(str(shared_mem_list))    
    shared_mem_list.shm.close()

    return res  