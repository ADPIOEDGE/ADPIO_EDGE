<script  lang="ts">
    import {
        browser_params,
    } from "../../stores.js"

    import {
        CloseOutline,
        Minimize 
    } from "carbon-icons-svelte"

    export let title: string = "No Title"

    let visible    :boolean = false
    let drag_event :any     = {event: false, collapse: false, pos_x: -999, pos_y: -999, layer_x: 0, layer_y: 0}

    export function open(posX: number, posY: number){
        if (visible) close(undefined)
        if (drag_event.pos_x === -999){
            drag_event.pos_x = posX
            drag_event.pos_y = posY
        }
        visible = true
    }

    export let onclose   = (e: any) => {}

    export function close(e: any){
        visible = false
        onclose(e)
    }

    async function move_event(e:any){
        if (drag_event.event){
            drag_event.pos_x = e.clientX - drag_event.layer_x
            drag_event.pos_y = e.clientY - drag_event.layer_y

            const padd_tlb = 20  //padding top left
            const padd_r   = 260 //padding right
            const padd_b   = 80  //padding bottom
            if (drag_event.pos_x < padd_tlb)                              drag_event.pos_x = padd_tlb
            if (drag_event.pos_x > $browser_params.innerWidth - padd_r)   drag_event.pos_x = $browser_params.innerWidth - padd_r
                
            if (drag_event.pos_y < padd_tlb)                              drag_event.pos_y = padd_tlb
            if (drag_event.pos_y > $browser_params.innerHeight - padd_b)  drag_event.pos_y = $browser_params.innerHeight - padd_b
        }
    }

</script>



{#if visible}
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div class="modal" style="transform: translate({drag_event.pos_x}px, {drag_event.pos_y}px)" >

        <div class="modal-header">
            <div 
                onpointerdown  =  "{(e:any) => {
                    drag_event.event = true 
                    drag_event.layer_x = e.layerX
                    drag_event.layer_y = e.layerY
                }}" 

                onpointerup    =  "{(e: any) =>  { drag_event.event = false }}"
            >
                {title}
            </div>

            <div>
                <button onclick="{(e: any) => { 
                    drag_event.collapse = !drag_event.collapse 
                }}" > <Minimize  /> </button>
                <button onclick="{(e: any) => { 
                    visible = false
                    onclose(e)
                }}" > <CloseOutline /> </button>
            </div>
        </div>

        <div class="modal-content {drag_event.collapse? 'modal-content-collapse' : ''}">
            <slot></slot>
        </div>        
    </div>

    {#if drag_event.event }
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div class="modal-drag-area"
            onpointermove  =  "{(e:any) => { move_event(e) }}"
            onpointerup    =  "{(e:any) => { drag_event.event = false }}"
        ></div>
    {/if}    
{/if}



<style>
    .modal {
        background-color: #fcfcfc;
        display: block;
        position: fixed;

        top:  0;
        left: 0;

        /*transform: translate(-50%, -50%);*/

        z-index: 999;
       
        overflow: hidden;
        -webkit-overflow-scrolling: touch;
        outline: 0;

        /*width: 80%;
        max-width: 500px; */
        min-width: 300px;

        border-radius: 6px;
        border: solid 1px #00000056;

        -webkit-box-shadow: 2px 2px 6px #00000056;
        -moz-box-shadow:    2px 2px 6px #00000056;
        box-shadow:         2px 2px 6px #00000056;

        transition: all 20ms;
    }


    .modal-header{
        width: 100%;
        /*padding: 0 5px;*/
        display: inline-flex;
        text-align: left;

        border-bottom: 1px solid orange;

        & > div:first-child{
            cursor: grab;
            width: 100%;

            /*font-size: 1.2em;*/
            font-weight: 600;
            padding: 0.2em 0.5em;
            color: #646464;
        }

        & > div:last-child{
            width: 100px;
            text-align: end;
            margin-right: 4px;
        }        
    }

    .modal-header button{
        padding: 4px 2px 0;

        scale: 1.2;
        color: rgb(255, 123, 123);

        transition: all 0.5s;

        &:hover{
            color: red;
        }        
    }

    .modal-content {
        padding-left:   10px;
        padding-right:  10px;
        padding-top:    2px;
        padding-bottom: 6px;
    }  

    .modal-content-collapse {
        display: none;
    }    


    .modal-drag-area {
        background-color: rgba(255, 255, 255, 0);
        display: block;
        position: fixed;
     
        overflow: hidden;
    
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
        z-index: 99999;
       
        overflow: hidden;
        -webkit-overflow-scrolling: touch;
        outline: 0;
    }
</style>
