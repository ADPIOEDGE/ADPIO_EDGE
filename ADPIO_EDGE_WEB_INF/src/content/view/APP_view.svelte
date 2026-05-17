<script  lang="ts">
    import '../../graphics.css'
    import { onMount, onDestroy }      from 'svelte'

    
    import { 
        async_post,
    } from "../../stores"

    import {
        Edit,
    } from "carbon-icons-svelte"    

    import Modal            from "../../adp_components/components/Modal.svelte"
    import ButtonR          from "../../adp_components/components/ButtonR.svelte"
    import DataDisplay      from '../../adp_components/components/DataDisplay.svelte'
    import InputSelector    from "../../adp_components/components/InputSelector.svelte" 

    export let uri

    let application         : any = undefined
    let content             : any = undefined
    let datapoints          : any = undefined

    let selected_element    : any = undefined

    let interval_datapoints : number
    let write_dp_modal      : any = undefined


    async function update_mem(){   
        const mem:any = await async_post( '/app_live', 'app_mem_get', { name: application.name } )
        
        if ((mem[0] === "APPNOTRUNNING") || (application.status === 0)) {
            clearInterval(interval_datapoints)
            return //App is stopped, nothing to read anymore
        }

        datapoints.forEach((el: any, indx: number) => { el.value = mem[indx] })

        content.forEach((c_el: any) =>  {      
            c_el.error = true       
            datapoints.forEach((d_el: any) =>  {
                if (c_el.datapoint_bind === d_el.id){
                    c_el.datapoint = d_el
                    c_el.error = false
                }
            })
        })

        content = content
    }


    async function live_data(){
        await update_mem()
        interval_datapoints = setInterval(async () => { await update_mem() }, 2000);   
    }


    async function write_live_value(){
        let write_dps:any = []
        write_dps.push(selected_element.datapoint)

        const mem = await async_post( '/app_live', 'app_mem_set', { 
            name        : application.name, 
            datapoints  : write_dps //Temporary sedn only one value
        } )
    }   
    
    async function update_data(){
        content = await async_post( '/app_ide_graphics', 'update', { 
            name            : application.name, 
            app_status      : application.status,
            view            : application.selected_view,
        } )

        datapoints = await async_post( '/app_ide_datapoints', 'update', { name : application.name, })

        if (application.status)  await live_data()
    }

    onMount(async () => { 
        const uri_seg = uri.split('/')

        application = await async_post( '/app_ide', 'get_app', { name : uri_seg[3], } )
        await update_data()
    })

    onDestroy(async () => { clearInterval(interval_datapoints) })
</script>

{#if application === undefined }
    <div> Loading... </div>
{:else if !application.status}
    <div>App {application.name} is not running.</div>
{:else}

    <div class="content-panel">
        <span id="view_select" ><InputSelector label="Views" item_list={application.view_list}  bind:value={application.selected_view} onchange={async () =>  {
            clearInterval(interval_datapoints)
            await update_data()
        }} /></span>
    </div>  


    <div class="content-panel flex flex-gap-tile" >
        {#each content as el, index}
            <!-- svelte-ignore a11y_no_static_element_interactions -->
            <div class="tile tile-basic flex-item" 
                onpointerdown="{(e: any) => { 
                    selected_element = JSON.parse(JSON.stringify(el))  
                    if ((el.datapoint !== undefined) && (el.datapoint.writable))
                        write_dp_modal.open(120, 120) 
                }}"
            >
                <div class="tile-basic-group">{el.datapoint.group}</div>
                <div class="tile-basic-name">{el.datapoint.name}</div>
                {#if el.error}
                    <div class="tile-basic-value">...</div>
                {:else}
                    <div class="tile-basic-value { el.datapoint.writable ? 'tile-editable': ''}">
                        <DataDisplay readonly={true} label=''  bind:datapoint={el.datapoint}  />
                        {el.datapoint.units}
                    </div>
                {/if}
            </div>
        {/each}
    </div>

    <Modal bind:this={write_dp_modal} title="Write Values" > 
        <div>
            <p><DataDisplay readonly={false} bind:datapoint="{selected_element.datapoint}" /></p>
        </div>

        <ButtonR text="Write Value" icon={Edit} onclick={async (e:any) =>  {
            write_dp_modal.close(e)
            await write_live_value()
        }} />  
    </Modal>

{/if}

 

<style>

</style>