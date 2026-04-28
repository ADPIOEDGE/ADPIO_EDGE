<script  lang="ts">
    export let visible:boolean = false

    export let title      :string = "No Title"
    export let description:string = "No Description"

    export let btn_accept_txt :string = "ACCEPT"
    export let btn_decline_txt:string = "CANCEL"

    export let on_accept  = function(e: any){}

    let modal: any = undefined

    function accept(e:any){
        on_accept(e)
        visible = false
    }

    function onshow(e: any){
        modal.focus()
    }      
</script>

{#if visible}
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div  class="conf-modal"  >
        <div>
            <div class="conf-modal-title" >{title}</div>
            <div class="conf-modal-desc"  >{description}</div>
            
            <div class="conf-modal-button ">
                <button class="conf-modal-cancel" 
                    onclick="{(e: any) => { visible = false }}" 
                >
                    {btn_decline_txt}
                </button>
                
                <button  bind:this={modal} class="conf-modal-apply"  
                    use:onshow                    
                    
                    onclick="{(e: any) => { accept(e) }}" 

                    onkeydown={(e: any) => { 
                        if (e.keyCode === 13) {
                            accept(e)
                            modal.blur()
                        } else if (e.keyCode === 27) {
                            visible = false
                            modal.blur()
                        }
                    }} 
                >
                    {btn_accept_txt}
                </button>
            </div>
        </div>
    </div>    
{/if}


<style>
    .conf-modal {
        background-color: rgb(77, 77, 77, 0.25);
        display: block;
        position: fixed;
     
        overflow-y: hidden;
    
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
        z-index: 99999;
       
        overflow: hidden;
        -webkit-overflow-scrolling: touch;
        outline: 0;
    }

    .conf-modal > div {
        top:  50%;
        left: 50%;

        transform: translate(-50%, -50%);

        width: 80%;
        max-width: 500px;
        min-width: 300px;

        position: fixed;
       
        background-color: #fff;

        border-radius: 8px;
        box-shadow: 8px 8px 5px rgba(0, 0, 0, 0.5);
    }

    .conf-modal-title {
        font-size: 20px;
        font-weight: 700;
        color: #646464;
        padding: 0.5em 0.5em
    }

    .conf-modal-desc {
        font-weight: 100;
        color: rgb(102, 102, 102);

        padding: 0.5em 0.5em
    }

    .conf-modal-button{
        width: 50%;

        min-width: 180px;
        margin: auto;

        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;

        padding: 0.25em 0.5em;
    }

    .conf-modal-button button {
        width: 50%;
        height: 35px;
        border-radius: 10px;
        border: none;
        cursor: pointer;
        font-weight: 600;
    }
    
    .conf-modal-cancel {
        background-color: #ddd;
    }

    .conf-modal-apply {
        background-color: rgb(255, 114, 109);
        color: white;
    }
</style>