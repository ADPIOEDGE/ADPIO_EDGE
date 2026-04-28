<script lang="ts">
    import { onMount, onDestroy }      from 'svelte'

    import { 
        async_post,
    } from "../../stores"

    import DataTable        from "../../adp_components/components/DataTable.svelte"
    import Modal            from "../../adp_components/components/Modal.svelte"
    import ControlPanel     from "../../adp_components/components/ControlPanel.svelte"
    
    import {
        Edit,
        ConnectionSignal,
        DataQualityDefinition,
        FolderParent
    } from "carbon-icons-svelte"

    let datatable           : any = undefined
    let selected_device     : any = undefined
    let view_data_modal     : any = []
    
    let interval_update: number

    let data: any = {
        header: "",
        colums: [
            {name: "",                key: "panel",          row_style: "width: 28px;"}, 
            {name: "DEVEUI",          key: "devEUI",         row_style: "", }, 
            //{name: "ONLINE",          key: "online",         row_style: "", }, 
            {name: "DEVICE NAME",     key: "deviceName",     row_style: "", },    
            {name: "APP ID",          key: "applicationID",  row_style: "", }, 
        ],       
        data: [],
    }

    let dev_data: any = {
        header: "",
        colums: [       
            {name: "",              key: "panel",        row_style: "width: 52px;"},      
            {name: "NAME",          key: "name",         row_style: "", }, 
            {name: "VALUE",         key: "value",        row_style: "", }, 
        ],       
        data: [],
    }

    let buttons:any = []

    function update_buttons(){
        let btn:any = [
            /*{
                text                : 'Refresh',
                color               : 'normal',
                icon                : Run,
                disabled            : false,

                with_confirmation   : false,

                onclick             : async (e: any) => { await update() }
            },*/ 

            {
                text                : 'Show Device Data',
                color               : 'normal',
                icon                : FolderParent ,
                disabled            : selected_device === undefined,

                onclick             : async (e: any) => { await show_data_modal() }
            }
        ]

        return btn
    }

    async function  update() {
        let buff_data:any = await async_post( '/network_tools', 'lora_tools_update' )

        buff_data.forEach((bf: any) => {
            if (bf.online) 
                bf.panel = [{ icon: ConnectionSignal, color: "green", text: 'Online '}]
            else
                bf.panel = [{ icon: ConnectionSignal, color: "off"  , text: 'Offline'}]

            let new_el = data.data.findIndex((el:any) => el.devEUI === bf.devEUI)

            if (new_el === -1) {
                data.data.push(bf)
                new_el = data.data.length - 1
            } else {
                data.data[new_el].applicationID = bf.applicationID
                data.data[new_el].deviceName    = bf.deviceName
                data.data[new_el].online        = bf.online
                data.data[new_el].data          = bf.data
                data.data[new_el].panel         = bf.panel
            }

            if ((selected_device !== undefined) && (selected_device.devEUI === bf.devEUI)) {
                dev_data.data = selected_device.data
                //console.log(dev_data.data)

                dev_data.data.forEach((dd: any) => {
                    dd.panel = []
                    if (dd.online) 
                        dd.panel.push({ icon: ConnectionSignal, color: "green", text: 'Online '})
                    else
                        dd.panel.push({ icon: ConnectionSignal, color: "off"  , text: 'Offline'})


                    if ((dd.binds.length > 0) && (dd.online === false) )
                        dd.panel.push({ icon: DataQualityDefinition, color: "red",   text: `Failed To Bind: ${JSON.stringify(dd.binds)}` })
                    else if (dd.binds.length > 0) 
                        dd.panel.push({ icon: DataQualityDefinition, color: "green", text: `Binded: ${JSON.stringify(dd.binds)}`})                    
                    else
                        dd.panel.push({ icon: DataQualityDefinition, color: "off"  , text: 'No binds'})                     
                })
            }     
        })
    }

    async function show_data_modal(){
        await update()
        view_data_modal.open(120, 120) 
    }

    onMount(async () => { 
        buttons = update_buttons() 
        
        await update()
        data.data = data.data
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
            buttons = update_buttons()         
        }}
        
        ondblclick={(e: any) => {
            show_data_modal()
        }}
    />
</div>

<Modal bind:this={view_data_modal} title="View Data" >
    <div id="fields">
        <DataTable data={dev_data}  selectable_rows={false} fill_height={false} />
    </div>
</Modal> 

<style>
    #fields {
        width: 612px; 
        max-height: 384px;
        display: flex;
    }
</style>