<script  lang="ts">
    import { 
        async_post,
        set_navigation,
        get_user_params,
        set_header, 
        user_params,
        set_user_params,
        popup_add,
        sleep
    } from "../../stores";

    import {
        PreviousOutline,
        BuildImage,
        BuildRun,
        StopOutline,
        ColumnDependency,
        DataVolume,
        Screen,
        Terminal
    } from "carbon-icons-svelte"

    import {
        build_app,
        run_app,
        stop_app
    } from "../../app_engine"
    
    import { onMount }      from 'svelte'

    import ControlPanel     from "../../adp_components/components/ControlPanel.svelte"
    import IDE_datapoints   from "../../content/app_ide/IDE_datapoints.svelte"
    import IDE_logic        from "../../content/app_ide/IDE_logic.svelte"
    import IDE_graphics     from "../../content/app_ide/IDE_graphics.svelte"
    import SysTerminal      from "../../adp_components/components/Terminal.svelte"
    
    $: user      = $user_params

    const VIEW_DATA  = 0
    const VIEW_GRAPH = 1
    const VIEW_PROG  = 2

    let application   : any       = undefined
    let view          : number    = VIEW_DATA  // //0 - datapoints, 1 - graph, 2 - prog
    let terminal_modal: any

    let buttons:any = []

    function update_buttons(){
        let btns: any = [
            {
                text                : 'BACK',
                color               : 'normal',
                icon                : PreviousOutline,
                disabled            : false,

                onclick             : (e: any) => { 
                    user.active_tree = user.edit_tree        
                    set_user_params(user)                
                    set_navigation('APP EDITOR', '/app_ide/mng') 
                }
            },

    /* Navigation */
            {
                text                : 'DATAPOINTS',
                color               : 'normal',
                icon                : DataVolume ,
                disabled            : (view === VIEW_DATA? true : false),

                onclick             : async (e: any) => { 
                    view = VIEW_DATA
                    buttons = update_buttons()
                }
            },  

            {
                text                : 'GRAPHICS IDE',
                color               : 'normal',
                icon                : Screen,
                disabled            : (view === VIEW_GRAPH? true : false),

                onclick             : async (e: any) => { 
                    view = VIEW_GRAPH
                    buttons = update_buttons()
                }
            },    

            {
                text                : 'LOGIC IDE',
                color               : 'normal',
                icon                : ColumnDependency ,
                disabled            : (view === VIEW_PROG? true : false),

                onclick             : async (e: any) => { 
                    view = VIEW_PROG
                    buttons = update_buttons()            
                }
            },
                    
            {
                text                : 'BUILD APP',
                color               : 'normal',
                icon                : BuildImage,
                disabled            : false,

                onclick             : async (e: any) => { 
                    await build_app(application.name) 
                    popup_add("Command Finished", "App Build Command Finished")
                }
            }]

        if ( application.status ) 
            btns.push({
                text                : 'STOP APP',
                color               : 'red',
                icon                : StopOutline,
                disabled            : false,
                rendered            : application.status,

                onclick             : async (e: any) => { 
                    popup_add("Executing Stop Command", "Wait Command to Complete")
                    await stop_app  (application.name) 
                    await sleep(600);
                    application = await update_app(application.name)
                    buttons     = update_buttons()
                    popup_add("Command Finished", "App Stop Command Finished")
                }
            }) 
        else
            btns.push({
                text                : 'RUN APP',
                color               : 'green',
                icon                : BuildRun,
                disabled            : false,
                rendered            : !application.status,

                onclick             : async (e: any) => { 
                    popup_add("Executing Run Command", "Wait Command to Complete")
                    await run_app   (application.name) 
                    await sleep(1200);
                    application = await update_app(application.name)
                    buttons     = update_buttons()
                    popup_add("Command Finished", "App Run Command Finished")
                }
            }) 

        btns.push({
                text                : 'APP TERMINAL',
                color               : 'normal',
                icon                : Terminal,
                disabled            : false,
                rendered            : true,

                onclick             : async (e: any) => { 
                    await terminal_modal.open(e)
                }
        })
        

        return btns
    }


    async function update_app(app_name: string){
        const app = await async_post( '/app_ide', 'get_app', {name: app_name} )  

        return app
    }

    onMount(async () => { 
        //Load Basic App Data
        const app_name = get_user_params().active_content.replaceAll('/app_ide/editor/', '')
        set_header("APP IDE: " + app_name)
        
        //Application
        application = await update_app(app_name)
        buttons     = update_buttons()

    })
</script>

{#if application !== undefined}
    <SysTerminal bind:this={terminal_modal} header={application.name} log_file="apps_{application.name}" />    
{/if}



<div class="content-panel" >
    <ControlPanel buttons={buttons} hotkeys />
</div>

{#if application === undefined}
    <div>LOADING...</div>
{:else}
    {#key application.status} 
        {#if      view === VIEW_DATA}
            <IDE_datapoints application={application} />
        {:else if view === VIEW_GRAPH}
            <IDE_graphics   application={application} />
        {:else if view === VIEW_PROG}
            <IDE_logic      application={application} />
        {:else}
            <div>ERROR: VIEW DOES NOT EXIST ({view})...</div>
        {/if}

    {/key}
{/if}

<style>

</style>