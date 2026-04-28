<script lang="ts">
    import { onMount, onDestroy }      from 'svelte'

    import { 
        async_post,
    } from "../../stores"

    import { PRIORITY_ARRAY_LIST } from "../../../public/bacnet_lists"

    import DataTable        from "../../adp_components/components/DataTable.svelte"
    import Modal            from "../../adp_components/components/Modal.svelte"
    import ControlPanel     from "../../adp_components/components/ControlPanel.svelte"
    import ButtonR          from '../../adp_components/components/ButtonR.svelte'
    import InputSelector    from '../../adp_components/components/InputSelector.svelte'
    import InputLabel       from '../../adp_components/components/InputLabel.svelte'

    import {
        Edit,
        FolderParent,
        ConnectionSignal,
        DataQualityDefinition, 
        Run,
        Add,
        TrashCan,
        Folder,
        BuildImage,
        PlayOutline,
        StopOutline,
        Restart,
        Play,
        Stop,
        Save,
        ArrowsVertical,
        ArrowUp,
        ArrowDown,
        
        DataError,
        DataView,
        DataBackup,
        SearchLocateMirror,
    } from "carbon-icons-svelte"
    

    let datatable           : any = undefined

    let selected_device     : any = undefined
    let selected_object     : any = undefined
    let selected_property   : any = undefined
    
    let view_objects_modal    : any = undefined
    let view_properties_modal : any = undefined

    let write_property_modal  : any = undefined
    let writable_value        : any = { priority: 8, value: 'none' }
    
    let interval_update: number

    let data: any = {
        header: "",
        colums: [
            {name: "",                key: "panel",         row_style: "width: 86px;"}, 
            //{name: "ID",              key: "id",            row_style: "", }, 
            {name: "DEVICE ID",       key: "device_id",     row_style: "", },    
            {name: "NETWORK",         key: "net",           row_style: "", }, 
            {name: "NAME",            key: "name",          row_style: "", }, 
            {name: "DESCRIPTION",     key: "description",   row_style: "", }, 
            {name: "LOCATION",        key: "location",      row_style: "", }, 

            //{name: "TX",        key: "segment_tx",      row_style: "", }, 
            //{name: "RX",        key: "segment_rx",      row_style: "", }, 
        ],       
        data: [],
    }

    let dev_data: any = {
        header: "",
        colums: [       
            /*{name: "",              key: "panel",        row_style: "width: 52px;"},      */
            {name: "OBJECT",    key: "object",  row_style: "width: 240px;", }, 
            {name: "NAME",      key: "name",    row_style: "width: 320px;", }, 
            {name: "VALUE",     key: "value",   row_style: "", }, 
        ],       
        data: [],
    }

    let obj_data: any = {
        header: "",
        colums: [       
            {name: "",          key: "panel",     row_style: "width: 52px;"},      
            {name: "PROPERTY",  key: "property",  row_style: "width: 240px;", }, 
            {name: "VALUE",     key: "value",     row_style: "", }, 
        ],       
        data: [],
    }    

    let buttons:any = []
    let device_buttons:any = []
    let object_buttons:any = []

    function update_buttons(){
        buttons = [
            {
                text                : 'View Device Objects',
                color               : 'normal',
                icon                : FolderParent,
                disabled            : selected_device === undefined,

                onclick             : async (e: any) => { await show_objects_modal() }
            },

            {
                text                : 'Read Object List',
                color               : 'normal',
                icon                : DataBackup,
                disabled            : selected_device === undefined,

                onclick             : async (e: any) => {  await read_object_list(selected_device) }
            },

            {
                text                : 'Who Is? Lookup',
                color               : 'green',
                icon                : SearchLocateMirror ,
                disabled            : false,

                onclick             : async (e: any) => { await bacnet_command([{ 'cmd': 'who_is', 'params': {} }]) }
            },

            {
                text                : 'Clear All Devices',
                color               : 'red',
                icon                : TrashCan,
                disabled            : false,

                onclick             : async (e: any) => { await bacnet_command([{ 'cmd': 'clear_db', 'params': {} }])  }
            },
        ]

        device_buttons = [
            {
                text                : "View Object's Properties",
                color               : 'normal',
                icon                : FolderParent,
                disabled            : selected_object === undefined,

                onclick             : async (e: any) => { await show_properties_modal() }
            },

            {
                text                : 'Full Read',
                color               : 'normal',
                icon                : DataBackup,
                disabled            : selected_device === undefined,

                onclick             : async (e: any) => {  await read_object_short_info(selected_device, selected_object, true) }
            }
        ]

        object_buttons = [
            {
                text                : 'Read All Properties',
                color               : 'normal',
                icon                : DataBackup,
                disabled            : false,

                onclick             : async (e: any) => {  await read_object_properties(selected_device, selected_object, [ 'all' ]) }
            }
        ]
    }

    async function read_object_list(device: any){
        let request:any = []

        if (device.segment_tx){
            request.push({ 
                'cmd': 'read_device_list', 
                'params': {
                    'id'        : device.id,
                    'net'       : device.net, 
                    'object'    : `device, ${device.device_id}`, 
                    'property'  : 'object-list', 
                }
            })
        } else {
            for (let i = 1; i <= device.list_size; i++){ 
                request.push({ 
                    'cmd': 'read_device_list', 
                    'params': {
                        'id'        : device.id,
                        'net'       : device.net, 
                        'object'    : `device, ${device.device_id}`, 
                        'property'  : 'object-list', 
                        'index'     : i 
                    }
                })
            } 
        }

        await bacnet_command(request)        
    }

    async function read_object_short_info(device: any, object: any, read_all_obj: boolean = false){
        let request:any   = []
        const min_refresh = [ 'present-value' ]
        const max_refresh = [ 'object-name', 'present-value' ]

        if (read_all_obj){
            device.objects.forEach((object: any) => {
                let properties: any = min_refresh
                if (object.name === '') properties = max_refresh
                request.push({ 
                    'cmd': 'read_property_multi_db', 
                    'params': { 
                        'id'        : device.id, 
                        'net'       : device.net,  
                        'requests'  : [ object.object, properties ]          
                    } 
                }) 
            })
        } else {
            let properties: any = min_refresh
            if (object.name === '') properties = max_refresh

            request.push({ 
                'cmd': 'read_property_multi_db', 
                'params': { 
                    'id'        : device.id, 
                    'net'       : device.net,  
                    'requests'  : [ object.object, properties ]          
                } 
            })        
        }      
        
        await bacnet_command(request)
    }

    async function read_object_properties(device: any, object: any, properties: any){
        let request:any   = []
        request.push({ 
            'cmd': 'read_property_multi_db', 
            'params': { 
                'id'        : device.id, 
                'net'       : device.net,  
                'requests'  : [ object.object, properties ]          
            } 
        }) 
        await bacnet_command(request)
    }

    async function write_property(device: any, object: any, property: any, write_struct: any){
        let request:any   = []
        request.push({ 
            'cmd': 'write_property', 
            'params': { 
                'id'        : device.id, 
                'net'       : device.net,  
                'object'    : object.object,
                'property'  : property.property,
                'value'     : write_struct.value,
                'priority'  : write_struct.priority
            } 
        }) 

        await bacnet_command(request)

        //Temp solution, reread result
        write_property_modal.close()

        await read_object_properties(device, object, [ property.property ])
    }

    async function bacnet_command(cmd: any){
        const read = await async_post( '/network_tools', 'bacnet_tools_read_properties', cmd )
        //console.log(read)
    }

    async function show_objects_modal(){
        if (selected_device.objects.length === 0)
            await read_object_list(selected_device)
        
        view_objects_modal.open(80, 80) 
        await update()
    }   
    
    async function show_properties_modal(){        
        await read_object_properties(selected_device, selected_object, [ 'all' ])
        view_properties_modal.open(120, 120) 
        await update()
    }

    async function show_write_property_dialog() {
        writable_value.value = selected_property.value
        write_property_modal.open(160, 160) 
    }
    

    async function update(){
        data.data = await async_post( '/network_tools', 'bacnet_tools_update' )
        //console.log(data.data)

        data.data.forEach((el: any) => {
            el.panel = []
            
            if (el.objects.length === 0)                 { el.panel.push({ icon: DataError,  color: "grey",   text: `Object List Not Read. Size: ${el.list_size}`}    ) } 
            else if (el.list_size === el.objects.length) { el.panel.push({ icon: DataView,   color: "green",  text: `Object List Read. Size: ${el.objects.length}`}   ) }
            else                                         { el.panel.push({ icon: DataBackup, color: "orange", text: `Progress: ${el.objects.length}/${el.list_size}`} ) } 

            if ((el.segment_rx) && (el.segment_tx)) { el.panel.push({ icon: ArrowsVertical,  color: "green", text: 'Segmentation TX and RX'}) } 
            else if (el.segment_tx)                 { el.panel.push({ icon: ArrowUp,         color: "green", text: 'Segmentation TX'}) } 
            else if (el.segment_rx)                 { el.panel.push({ icon: ArrowDown,       color: "green", text: 'Segmentation RX'}) } 
            else                                    { el.panel.push({ icon: ArrowsVertical,  color: "grey",  text: 'No Segmentation'}) }
        
            if ((selected_device !== undefined) && (selected_device.net === el.net)) {
                dev_data.data = el.objects //Update Selected Device
                selected_device = el

                if (selected_object !== undefined) {
                    dev_data.data.forEach((obj: any) => {
                        if (obj.object === selected_object.object){
                            obj_data.data   = obj.properties
                            selected_object = obj
                        }
                    }) 
                }
            }           
        }) 


        if (selected_object !== undefined){
            selected_object.properties.forEach((prp: any) => {
                prp.panel = []
                if (prp.online) 
                    prp.panel = [{ icon: ConnectionSignal, color: "green", text: 'Online '}]
                else
                    prp.panel = [{ icon: ConnectionSignal, color: "off"  , text: 'Offline'}]

                if ((prp.binds.length > 0) && (prp.online === false) )
                    prp.panel.push({ icon: DataQualityDefinition, color: "red",   text: `Failed To Bind: ${JSON.stringify(prp.binds)}` })
                else if (prp.binds.length > 0) 
                    prp.panel.push({ icon: DataQualityDefinition, color: "green", text: `Binded: ${JSON.stringify(prp.binds)}`})                    
                else
                    prp.panel.push({ icon: DataQualityDefinition, color: "off"  , text: 'No binds'})     
            })
        }
        
    }

    onMount(async () => { 
        update_buttons()
        await update()
        interval_update = setInterval(async () => { await update() }, 2000)
    })

    onDestroy(async () => {
        clearInterval(interval_update)
    }) 

</script>


<div class="content-panel">
    <ControlPanel buttons={buttons} />
</div>

<div class="content-panel"> <!--group="group" -->
    <DataTable bind:this={datatable} data={data}  context_btns={buttons} bind:selected_row={selected_device}  selectable_rows={true}
        onselect={(e: any) => {
            update_buttons()         
        }}
        
        ondblclick={async (e: any) => {
            await show_objects_modal()
        }}
    />
</div>


{#if (selected_device !== undefined)}
    <Modal bind:this={view_objects_modal} title="{selected_device.device_id} [{selected_device.net}]: {selected_device.name}" >
        <div class="modal_panel">
            <ControlPanel buttons={device_buttons} />
        </div>         
        
        <div id="fields">
            <DataTable data={dev_data} selectable_rows={true} bind:selected_row={selected_object} fill_height={false} 
                onselect={async (e: any) => {
                    update_buttons()  
                    await read_object_short_info(selected_device, selected_object)
                }}

                ondblclick={(e: any) => {
                    show_properties_modal()
                }}
            />
        </div>
    </Modal>
{/if}


{#if (selected_object !== undefined)}
    <Modal bind:this={view_properties_modal} title="{selected_object.object} - {selected_object.name}" >
        <div class="modal_panel">
            <ControlPanel buttons={object_buttons} />
        </div>         
        
        <div id="fields">
            <DataTable data={obj_data} selectable_rows={true} bind:selected_row={selected_property} fill_height={false} 
                onselect={async (e: any) => {
                    await read_object_properties(selected_device, selected_object, [ selected_property['property'] ])
                }}

                ondblclick={async (e: any) => {
                    await show_write_property_dialog()
                }}
            />
        </div>
    </Modal>
{/if}


{#if (selected_property !== undefined)}
    <Modal bind:this={write_property_modal} title="{selected_object.object} - {selected_object.name}, {selected_property.property}" >
        <div class="w_fields">
            <InputSelector label="Priority Array"  bind:value={ writable_value.priority } item_list={ PRIORITY_ARRAY_LIST } 
                onchange={()=>{  }}
            />
        </div>

        <div class="w_fields">
            <InputLabel label="Value"  bind:value={ writable_value.value } minlength={0} maxlength={256} 
                oninput={()=>{  }}  
            />
        </div>

        <ButtonR text="Write Value" icon={Edit} color="green" onclick={async (e:any, ) =>  {
            await write_property(selected_device, selected_object, selected_property, writable_value)
        }} />          
    </Modal>
{/if}



<style>

    #fields {
        width: 720px; 
        max-height: 420px;
        display: flex;
    }

    .modal_panel{
        padding: 5px;
    }

    .w_fields{
        padding: 12px 12px;
    }
    
</style>

