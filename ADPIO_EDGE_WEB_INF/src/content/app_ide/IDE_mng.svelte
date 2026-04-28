<script  lang="ts">
    import { 
        async_post,
        set_navigation,
        find_button_index,
        sleep,
        popup_add,
    } from "../../stores"

    import {
        build_app,
        run_app,
        stop_app
    } from "../../app_engine"

    import {
        Add,
        TrashCan,
        Edit,
        Folder,
        BuildImage,
        PlayOutline,
        StopOutline,
        Restart,
        Play,
        Stop,
        Save,
        Key,
    } from "carbon-icons-svelte"

    import { onMount }      from 'svelte'


    import ButtonR          from "../../adp_components/components/ButtonR.svelte"
    import DataTableEdit    from "../../adp_components/components/DataTableEdit.svelte"
    import Modal            from "../../adp_components/components/Modal.svelte"
    import ControlPanel     from "../../adp_components/components/ControlPanel.svelte"
    import FlexDataEdit     from "../../adp_components/layout/FlexDataEdit.svelte"
    
    let app_edit_modal: any
    const new_app_temp = {
        name            : "App1",
        description     : "",
        group           : "No Group",
        version         : "0.0.1",
        state           : 0,
        autostart       : false,
    }

    let new_app_mode:boolean = false
    let edit_app:any    = [ JSON.parse( JSON.stringify( new_app_temp ) ) ]
    let app_table: any  = undefined

    let data = {
        header: "",
        colums: [
            /*{name: "AUTOSTART",    key: "autostart",    row_style: ""}, 
            {name: "STATUS",       key: "status",       row_style: ""}, */
            {name: "",             key: "panel",        row_style: "width: 52px;"}, 
            {name: "NAME",         key: "name",         row_style: ""}, 
            {name: "DESCRIPTION",  key: "description",  row_style: ""},
            //{name: "VER.",         key: "version",      row_style: ""},
        ],
        groups: [
            {name: 'No Group', expand: true}
        ],             
        data: [],
    }
    let apps_selected:  any = []
    let app_modal_flex: any = []

    let buttons:        any = []

    function update_buttons(){ 
        let btns: any = [
            {
                text                : 'OPEN',
                color               : 'normal',
                icon                : Folder,
                disabled            : ((apps_selected.length === 0) || (apps_selected.length > 1)),
            
                onclick             :  (e: any) => { 
                    set_navigation("APP IDE: LOADING...", `/app_ide/editor/${apps_selected[0].name}`)
                }
            }, 
        
            {
                text                : 'BUILD',
                color               : 'normal',
                icon                : BuildImage,
                disabled            : apps_selected.length === 0,

                onclick             : async (e: any) => { 
                    if (apps_selected.length === 0) return 
                    await apps_selected.forEach(async (el: any) =>  {
                        await build_app(el.name) 
                    })
                    await update_data()     
                    popup_add("Command Finished", "App Build Command Finished")
                }
            },   
        ]

        if (apps_selected.length > 0 && !apps_selected[0].status)
            btns.push({
                text                : 'RUN',
                color               : 'green',
                icon                : PlayOutline,
                disabled            : apps_selected.length === 0,
            
                onclick             : async (e: any) => { 
                    popup_add("Executing Run Command", "Wait Command to Complete")
                    if (apps_selected.length === 0) return 
                    await apps_selected.forEach(async (el: any) =>  {
                        await run_app(el.name) 
                    })

                    await sleep(1200);
                    await update_data()
                    popup_add("Command Finished", "App Run Command Finished")
                }
            })  
            
        if ((apps_selected.length === 0) || (apps_selected.length > 0 && apps_selected[0].status))
            btns.push({
                text                : 'STOP',
                color               : 'red',
                icon                : StopOutline,
                disabled            : apps_selected.length === 0,

                onclick             : async (e: any) => { 
                    popup_add("Executing Stop Command", "Wait Command to Complete")
                    if (apps_selected.length === 0) return
                    await apps_selected.forEach(async (el: any) =>  {
                        await stop_app(el.name) 
                    })

                    await sleep(600);
                    await update_data()
                    popup_add("Command Finished", "App Stop Command Finished")
                }
            })           
        
        btns.push({
                text                : 'NEW APP',
                color               : 'normal',
                icon                : Add,

                onclick             : async (e: any) => { 
                    new_app_mode = true
                    edit_app = [ JSON.parse( JSON.stringify( new_app_temp ) ) ]
                    
                    const ctls = update_buttons()
                    buttons        = ctls[0]
                    app_modal_flex = ctls[1] 

                    app_edit_modal.open(e.clientX, e.clientY) 
                }
            }, 
        
            {
                text                : 'PROPERTIES',
                color               : 'normal',
                icon                : Edit,
                disabled            : (apps_selected.length === 0) ,

                onclick             : async (e: any) => { 
                    new_app_mode = false
                    app_edit_modal.open(40, 40)//(e.clientX, e.clientY) 
                
                    //const rec = await async_post( '/app_ide', 'get_app', {name: apps_selected[0].name} )  
                    edit_app = JSON.parse( JSON.stringify( apps_selected ) )
                    
                    const ctls = update_buttons()
                    buttons       = ctls[0]
                    app_modal_flex= ctls[1]
                }
            }, 
        
            {
                text                : 'DELETE',
                color               : 'red',
                icon                : TrashCan,
                disabled            : ((apps_selected.length === 0) || (apps_selected.length > 1)),

                with_confirmation   : true,
                conf_title          : 'DELETE APPLICATION',
                conf_description    : (apps_selected.length > 0) ? `Are you sure you want to delete: ${apps_selected[0].name}?`: '',
                conf_btn_accept_txt : 'DELETE',

                onclick             : async (e: any) => { await delete_app() }
            })
        

        let flx: any = [
            { type: 'InputLabel'   , group: "GR", label: "APP NAME",    bind_name: 'name', visible: true, args: {
                minlength: 4, maxlength: 24, readonly: !new_app_mode
            }},
            { type: 'InputLabel'   , group: "GR", label: "DESCRIPTION", bind_name: 'description', visible: true, args: {
                minlength: 0, maxlength: 256, readonly: false
            }},
            { type: 'InputDropList', group: "GR", label: "GROUP",       bind_name: 'group', visible: true, args: {
                item_list: data.groups,
                readonly: false,  minlength: 0,  maxlength: 24 
            }},  
            { type: 'InputSwitch'  , group: "GR", label: "AUTOSTART",   bind_name: 'autostart', visible: true, args: {
                readonly: false
            }},
        ]

        return [btns, flx]
    }


    async function update_data(){
        data.data = await async_post( '/app_ide', 'update_list' )
        app_table.update_groups()

        data.data.forEach((el: any) => {
            el.panel = []
            
            if (el.status)    el.panel.push({ icon: Play,     color: "green", text: 'APP Running'})
            else              el.panel.push({ icon: Stop,     color: "off"  , text: 'APP Stopped'})    
                
            if (el.autostart) el.panel.push({ icon: Restart,  color: "green", text: 'Autostart Enabled'})
            else              el.panel.push({ icon: Restart,  color: "off"  , text: 'Autostart Disabled'})      
        })

        const ctls = update_buttons()
        buttons        = ctls[0]
        app_modal_flex = ctls[1]

    }

    async function delete_app(){
        if (apps_selected.length === 0) return
        const res = await async_post( '/app_ide', 'delete_app', {name: apps_selected[0].name} )   
    
        apps_selected = []             
        await update_data()
    }


    onMount(async () => { 
        update_data() 
        //buttons = build_buttons()
    })

</script>

<div class="content-panel">
    <ControlPanel buttons={buttons} hotkeys />
</div>

<div class="content-panel" >
   <DataTableEdit bind:this={app_table} data={data} selectable_rows context_btns={buttons} group="group" 
        bind:selected_rows={apps_selected}

        ondblclick= {(e: any) => { 
            buttons[find_button_index(buttons, 'OPEN')].onclick(e) 
        }}

        onselect = {(e:any) => {
            const ctls = update_buttons()
            buttons        = ctls[0]
            app_modal_flex = ctls[1]
        }}
   />
</div>


<Modal bind:this={app_edit_modal} title="{ new_app_mode ? 'Create New Application' : 'Edit Application'} " >
    <div  class="edit_data_mod"><FlexDataEdit bind:values={edit_app} widget_list={app_modal_flex} /></div>
    
    <ButtonR  icon={Save}   text="Create" color="green" 
        onclick={async (e: any) => { 
            if (new_app_mode) 
                await async_post( '/app_ide', 'add_app', edit_app[0] )
            else 
                await async_post( '/app_ide', 'save_app', edit_app )  

            await update_data()    
            app_edit_modal.close(e)
        }}
    />    
</Modal>


<style>

</style>
