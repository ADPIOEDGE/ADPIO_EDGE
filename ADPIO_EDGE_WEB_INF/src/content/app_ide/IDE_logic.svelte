<script  lang="ts">
    import { onMount, onDestroy }      from 'svelte'

    import { 
        async_post,
        user_params,
        set_user_params,
        popup_add,
        update_data_groups,
        datapoint_tree,
    } from "../../stores" 

    import { debug }       from '../../../package.json';


    import ContextMenu        from "../../adp_components/components/ContextMenu.svelte" 
    import Modal              from "../../adp_components/components/Modal.svelte"
    import InputLabel         from "../../adp_components/components/InputLabel.svelte"
    import ButtonR            from "../../adp_components/components/ButtonR.svelte"

    import LENBlock           from "../../adp_components/logic_engine/LENBlock.svelte"
    import LENSelectionBox    from "../../adp_components/logic_engine/LENSelectionBox.svelte"
    import LENBind            from "../../adp_components/logic_engine/LENBind.svelte"
    import LENIO              from "../../adp_components/logic_engine/LENIO.svelte"
    import LENConnPath        from "../../adp_components/logic_engine/LENConnPath.svelte"

    import {
        TrashCan,
        Save,
    } from "carbon-icons-svelte"

    const is_debug   = debug

    export let application: any

    $: user      = $user_params
    let interval_live: number

    let content         : any = []
    let selected        : any = []
    let selected_binds  : any = []
    

    const blk_width  = 160
    const blk_height = 40
    const canvas     = { width: 3200, height: 6400 }

    let box_mode           : any     = undefined
    let drag_event         : boolean = false //drage elements normally
    let drop_element_event : any     = { enabled: false, x: 0, y: 0, buffer: {} } //Drag from left menu
    let path_connect       : any     = { enabled: false, x0: 0, x1: 0, y0: 0, y1: 0, bind0_block: {}, bind1_block: {}, bind0_io: {}, bind1_io: {}, }

    let context_menu:any = []
    let buttons:any = []

    let edit_block_modal: any = undefined
    let edit_block      : any = undefined
    
    function update_buttons(){
        let btns: any = [
            {
                text                : 'Disconnect Bind',
                color               : 'red',
                icon                : TrashCan,
                disabled            : selected_binds.length === 0,

                with_confirmation   : true,
                conf_title          : (selected_binds.length > 0) ? `Are you sure you want to disconnect binds?`: '',  
                conf_description    : '',
                conf_btn_accept_txt : 'DELETE',

                onclick             : async (e: any) => { 
                    let disconn:any = []
                    selected_binds.forEach((el: any) => { disconn.push({ target_id: el.bind.this_blk_id, target_io_index: el.bind.this_io_index }) });

                    content = await async_post( '/app_ide_logic', 'delete_binds', { 
                        name            : application.name, 
                        app_status      : application.status,
                        elements        : disconn
                    } )

                    selected_binds = []
                    await update_data(false)
                }
            }, 

            {
                text                : 'Delete Elements',
                color               : 'red',
                icon                : TrashCan,
                disabled            : selected.length === 0,

                with_confirmation   : true,
                conf_title          : "DELETE ELEMENTS",  
                conf_description    : (selected.length > 0) ? `Are you sure you want to delete selected elements?`: '',  
                conf_btn_accept_txt : 'DELETE',

                onclick             : async (e: any) => { 
                    content = await async_post( '/app_ide_logic', 'delete_elements', { 
                        name            : application.name, 
                        app_status      : application.status,
                        elements        : selected
                    } )
                    selected = []
                    await update_data(false)
                }
            }, 
        ]

        return btns
    }

    async function add_element(element: any, pos_x: number, pos_y: number){
        const new_el = { type: element.type, id: element.el_id, name: element.el_name, group: element.el_group, x: pos_x, y: pos_y }

        content = await async_post( '/app_ide_logic', 'add_element', { 
            name            : application.name, 
            app_status      : application.status,
            element         : new_el
        } )

        await update_data(false)
    }


    function pos_to_grid(x: number, y: number){
        let res = [x, y]

        if (x < 20)                          x = 20      //Check Boundries
        if (y < 20)                          y = 20
        if (x > (canvas.width  - blk_width)) x = canvas.width - blk_width
        if (y > canvas.height)               y = canvas.height - 40

        res[0] = Math.round(x / 20) * 20 //Stick to grid
        res[1] = Math.round(y / 20) * 20

        return res
    }

    async function on_edit_block(block: any){
        if (block.type !== "constant") return
        edit_block = JSON.parse( JSON.stringify(block) )
        edit_block_modal.open(120, 120)
    }

    async function move_event() {
        if (selected.length === 0) return

        selected.forEach((el: any) => { 
            const res = pos_to_grid(el.x, el.y)
            el.x = res[0]
            el.y = res[1]
        })

        const result: any = await async_post( '/app_ide_logic', 'move_elements', { 
            name            : application.name, 
            app_status      : application.status,
            elements        : selected
        } )

        if (result['result'] === 'ok')
            content = content
        else   
            update_data(true)
    }

    async function bind_elements(){
        if (path_connect.bind0_io.type === path_connect.bind1_io.type)
            return

        if (path_connect.bind0_io.type === path_connect.bind1_io.type){
            popup_add("ILLIGAL BIND", "Output Can Be Binded Only With Input")
            return 
        } 
        
        let trg_blk           : number = -1
        let trg_io            : string = ""
        let trg_io_indx       : number = -1
        
        let new_bind_blk      : number = -1
        let new_bind_io       : string = ""       
        let new_bind_io_indx  : number = -1 

        if (path_connect.bind0_io.type === "input") {
            trg_blk            = path_connect.bind0_block.id
            trg_io             = path_connect.bind0_io.id
            trg_io_indx        = path_connect.bind0_io_index
            
            new_bind_blk       = path_connect.bind1_block.id
            new_bind_io        = path_connect.bind1_io.id
            new_bind_io_indx   = path_connect.bind1_io_index
        } else if (path_connect.bind1_io.type === "input") {
            trg_blk            = path_connect.bind1_block.id
            trg_io             = path_connect.bind1_io.id
            trg_io_indx        = path_connect.bind1_io_index

            new_bind_blk       = path_connect.bind0_block.id
            new_bind_io        = path_connect.bind0_io.id
            new_bind_io_indx   = path_connect.bind0_io_index
        } else return //Just In Case, should never happen

        content = await async_post( '/app_ide_logic', 'bind_elements', { 
            name            : application.name, 
            app_status      : application.status,
            elements        : { 
                target_blk: trg_blk      , target_io:  trg_io,   target_io_indx : trg_io_indx,
                bind_blk:   new_bind_blk , bind_io: new_bind_io, bind_io_indx   : new_bind_io_indx,
            }
        } )

        update_data(false)
    }

    async function on_flip_datapoint(block: any){        
        content = await async_post( '/app_ide_logic', 'datapointsetget', { 
            name            : application.name, 
            app_status      : application.status,
            element         : block,
        })

        update_data(false)
    }  

    async function update_data(content_update: boolean){
        if (content_update)
            content = await async_post( '/app_ide_logic', 'update', { 
                name            : application.name, 
                app_status      : application.status,
            } )

        content.forEach((blk:any) => { //Find bind pointers
            blk.io.forEach((io:any, io_index: number) => {
                if (( io.type === 'input' ) && ( io.bind.bind_id !== undefined )){
                    io.bind.pointer_blk_index = content.findIndex((el: any) => el.id === io.bind.bind_id) //Target Blk
                    io.bind.pointer_io_index  = content[io.bind.pointer_blk_index].io.findIndex((el: any) => el.id === io.bind.bind_io)
                    io.bind.this_blk_id       = blk.id    //This Blk
                    io.bind.this_io_index     = io_index
                }
            })
        })
    }

    async function live_data(){
        interval_live = setInterval(async () => { 
            const mem: any = await async_post( '/app_live', 'app_binds_get', { name: application.name } )

            if ((mem[0] === "APPNOTRUNNING") || (application.status === 0)) {
                clearInterval(interval_live)
                await update_data(true) 
                return //App is stopped, nothing to read anymore
            }

            content.forEach((blk:any) => { //Find bind pointers
                blk.io.forEach((io:any, io_index: number) => {
                    if ("mem" in io) {
                        io.debug_value = mem.binds[io.mem]
                    }
                })
            })

            content = content
        }, 2000);   
    }

    onMount(async () => { 
        await update_data(true)
        buttons = update_buttons()

        let new_active_tree : any = []

        let data_points : any = await async_post( '/app_ide_datapoints', 'update', { name: application.name, app_status: application.status } )
        let dp_groups   : any = update_data_groups(data_points, "group")
        new_active_tree = datapoint_tree(data_points, dp_groups)

        let groups: any =  await async_post( '/system_tools', 'update_logic_grouped')//Load Function Blocks
        groups.forEach((el:any) => {        //Add expand capabilities
            let new_grp: any = {id: el.name, name: el.name, visible: true, submenu: []}

            el.list.forEach((el_d:any) => { 
                new_grp.submenu.push( {
                    id: `blocks_${el_d.id}`, name: el_d.name,
                    visible: true, draggable: true,                 
                    type    : el_d.type, el_name : el_d.name, el_group: el_d.group, el_id   : el_d.id       //Datapoint Specific
                } )
            })

            new_active_tree.push(new_grp)
        })

        //Menu Drag and Drop Action
        new_active_tree.forEach((gr_el:any) => {
            gr_el.submenu.forEach((el:any) => {
                el.ondropevent = async (e:any) => { 
                    const res = pos_to_grid(drop_element_event.x, drop_element_event.y)
                    await add_element(drop_element_event.buffer, res[0], res[1])
                    drop_element_event.enabled = false
                }

                el.ondragevent = async (e:any) => {
                    drop_element_event.buffer = {type: el.type, el_name: el.el_name, el_group: el.el_group, el_id: el.el_id}
                    drop_element_event.enabled = true
                }
            })
        })

        user.active_tree = new_active_tree
        set_user_params(user)

        if (application.status === true) live_data()
    })

    onDestroy(async () => { 
        clearInterval(interval_live)
    })
</script>

<ContextMenu buttons={buttons} bind:this={context_menu}   /> 


<!-- svelte-ignore a11y-no-static-element-interactions -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<div  id="editor" class="content-panel"  >
    <svg id="editor_svg" width="{canvas.width}" height="{canvas.height}" xmlns="http://www.w3.org/2000/svg" 
        oncontextmenu="{(e: any) => {
            buttons = update_buttons()
            context_menu.open_context(e.clientX, e.clientY)
            e.preventDefault()
        }}"    

        onpointerdown    = "{(e: any) => {             
            box_mode.on_start_box(e)

            if (!e.ctrlKey) { 
                selected        = []
                selected_binds  = []
            }            
        }}" 

        onpointerup    = "{(e: any) => {
            box_mode.on_stop_box(e)
            content  = content
        }}"

        onpointermove  = "{(e: any) => {
            box_mode.on_move_box(e)
        }}"
    >

<!-- Renderer Block-->   
    {#each content as block}  
        <LENBlock bind:selected={selected} bind:selected_binds={selected_binds}  bind:drag_event={drag_event}
            bind:content={content} block={block} 
            blk_height={blk_height} blk_width={blk_width}  user={user}
            on_flip_datapoint= { async (e:any) => { await on_flip_datapoint(block) } }
            on_dblclick      = { async (e:any) => { await on_edit_block(block)     } }
        />   
    {/each} 


<!--  Connection Path -->    
    {#if (path_connect.enabled) } 
        <LENConnPath bind:path_connect={path_connect} is_debug={is_debug} />  
    {/if}
    
<!-- Binds -->    
    {#each content as block} 
        {#each block.io as io}
            {#if      io.type === "input" && io.bind.bind_id !== undefined }
                <LENBind 
                    bind:selected={selected} bind:selected_binds={selected_binds} content={content} 
                    block={block}  io={io}  
                    blk_height={blk_height} blk_width={blk_width} 
                    debug={application.status}
                />              
            {/if}
        {/each}                                              
    {/each}
    

<!-- IO -->   
    {#each content as block} 
        {#each block.io as io, index}
            <LENIO bind:path_connect={path_connect} 
                block={block} io={io} io_index={index} 
                blk_height={blk_height} blk_width={blk_width} 
                on_bind = { async (e:any) => { await bind_elements() }}
            />
        {/each}                                              
    {/each}

<!-- Box Selector -->
    <LENSelectionBox bind:this={box_mode} content={content} selection={selected} blk_height={blk_height} blk_width={blk_width} />

<!-- Drag Area-->
    {#if drag_event}
        <rect class="drag_area{is_debug ? '_debug': ''}"  style="fill: green;" 
            onpointermove  = "{(e: any) => {
                selected.forEach((el: any) => {
                    el.x = e.layerX + el.dX
                    el.y = e.layerY + el.dY
                });

                content  = content      
                e.stopImmediatePropagation()
            }}"

            onpointerup    = "{async (e: any) => {
                drag_event = false
                await move_event()
                e.stopImmediatePropagation()
            }}"
        />
    {/if}

    {#if drop_element_event.enabled}
        <rect class="drag_area{is_debug ? '_debug': ''}" style="fill: deepskyblue;" 
            ondragover = "{(e: any) => {
                drop_element_event.x = e.layerX
                drop_element_event.y = e.layerY
                e.stopImmediatePropagation()
            }}"
        />    
    {/if}
    
    {#if application.status}
        <rect class="drag_area{is_debug ? '_debug': ''}" style="fill: orange;"  
            onpointerdown = "{(e: any) => { e.stopImmediatePropagation() }}"
            onpointerup   = "{(e: any) => { e.stopImmediatePropagation() }}"
            onpointermove = "{(e: any) => { e.stopImmediatePropagation() }}"
            onclick       = "{(e: any) => { e.stopImmediatePropagation() }}"
        />    
    {/if}    
    </svg>
</div>


<Modal bind:this={edit_block_modal} title="Edit Block" >
    <div class="flex-item">
        <InputLabel label="Constant Value" bind:value={edit_block.io[0].value} />
    </div>
   

    <ButtonR text="Save" icon={Save} color="green" onclick={async (e:any) =>  {
        const result: any = await async_post( '/app_ide_logic', 'save_elements', { 
            name            : application.name, 
            app_status      : application.status,
            elements        : [ edit_block ]
        } )

        //Make raw edit of multiple objects
        edit_block_modal.close(e)
        await update_data(true)
    }} /> 
</Modal>


<style>
    #editor { /*border: 1px solid grey;*/  width: 100%;  height: calc(100vh - 118px);  overflow: auto; }

    #editor_svg{
        position: relative;

        background-image: linear-gradient(#dfdfdf 1px, transparent 1px), linear-gradient(to right, #dfdfdf 1px, transparent 1px);
        background-size: 20px 20px;
        background-color: #ffffff;        
        
        background-position-x: 20px;
        background-position-y: 20px;

        /*
            https://10015.io/tools/css-background-pattern-generator
            fill="{selected_elements.includes(block) ? 'lightblue' : 'white'}"
        */
    }



</style>