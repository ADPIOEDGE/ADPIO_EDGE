#Tool for objects and it's proprties mapping
#Command 
#cd ./ADPIO_EDGE/ADPIO_EDGE
#python ./drivers/bacnet_objects_map.py

import sys, inspect, importlib
import os
sys.path.append(f'{os.getcwd()}/ext_lib/') #External Libraries

import ujson
import shutil
import asyncio
import glob



import bacpypes3.object as _client_object

def main():
    jsn_output = [] 

    cls_filtered = []
    cls_exluded  = ['_Any', 'partial', 'Object', 'ObjectMetaclass']###'NotificationForwarderObject']


    cls_all = inspect.getmembers(_client_object, inspect.isclass)
    for cls in cls_all:
        if cls[0] not in cls_exluded and 'bacpypes3.object.' in str(cls[1]) :
            print(f"{cls}")
            cls_filtered.append(cls)
        else:
            print(f"****** Exluded: {cls}")

    print()

    props_all = ['objectName', 'description'] #Common Fields for all
    props_order_mask = [    #Order mask - this fields displayed on top
        'objectName', 
        'description',
        
        'presentValue',
        'relinquishDefault',
        'units',
        
        'priorityArray',

        'statusFlags',
        'outOfService',
        
        'minPresValue',
        'maxPresValue',        
    ]

    print(f'Objects Found: {len(cls_filtered)}')

    print("\n")
    #test_indx = 9

    for cls in cls_filtered:
        obj_indx = cls_filtered.index(cls)
        

        obj_name = str(cls_filtered[obj_indx][1].objectType)
        obj_cls  = cls_filtered[obj_indx][1]
        #print("\n")
        #print(f"{obj_name} Props: {len(obj_cls.__annotations__)}")

        props_built = []
        for prp in props_all:
            props_built.append({'id': f'{prp}'})

        for anno in obj_cls.__annotations__:
            props_built.append({'id': f'{anno}'})

        for prp_filt in props_order_mask[::-1]:
            for prp_blt in props_built:
                if prp_blt['id'] == prp_filt:
                    props_built.insert(0, props_built.pop(props_built.index(prp_blt)))

        print(f'Building props for: {obj_name} - props len: {len(props_built)}')

        jsn_output.append( {"id": obj_name, "props": props_built} )


    #{object-name: [prop list]}
    with open("bacnet_lists.ts", "w") as f:
        f.write(
"""
//Priority array
export const PRIORITY_ARRAY_LIST: any = [
    { value: 1 ,           name: "1 - Manual LifeSafety"        },
    { value: 2 ,           name: "2 - Automatic LifeSafety"        },
    { value: 3 ,           name: "3"        },
    { value: 4 ,           name: "4"        },

    { value: 5 ,           name: "5 - Critical EquipmentControls"        },
    { value: 6 ,           name: "6 - Minimum OnOff"        },
    { value: 7 ,           name: "7"        },
    { value: 8 ,           name: "8 - Manual Operator"        },

    { value: 9 ,           name: "9"         },
    { value: 10 ,          name: "10"        },
    { value: 11 ,          name: "11"        },
    { value: 12 ,          name: "12"        },

    { value: 13 ,          name: "13"        },
    { value: 14 ,          name: "14"        },
    { value: 15 ,          name: "15"        },
    { value: 16 ,          name: "16"        },
]
"""
        )

        f.write('\n\n')

        f.write('//Object properties list\n')
        f.write('export const OBJECT_PROPERTIES: any = {\n')
        for cls in jsn_output:
            f.write(f'  "{cls['id']}": [\n')

            for prop in cls["props"]:
                f.write(f'      "{prop['id']}", \n')

            f.write(f'  ], \n\n')

        f.write('}')



    #print(ujson.dumps(jsn_output,  indent=4))

    

    #Make proprietary with required fields "objectIdentifier", "objectName", "objectType", "propertyList"


if __name__ == "__main__":
    print("Generate BACnet Objects Map\n\n\n")
    main()
    print("\n\n\nBACnet Objects Map Is Done")
 