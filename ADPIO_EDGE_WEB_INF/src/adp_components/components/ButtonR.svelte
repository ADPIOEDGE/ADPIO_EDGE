<script  lang="ts">
  import Tooltip   from "./Tooltip.svelte"
  import ConfModal from "./ConfModal.svelte";
  
  export let color: string = "normal" //red, blue, orange, green
  export let onclick       = function(e: any){}
  export let icon: any
  export let text: string = ""
  export let with_confirmation: boolean = false

  //For Confirmation Dialog
  export let conf_title      :string = "No Title"
  export let conf_description:string = "No Description"

  export let conf_btn_accept_txt :string = "DELETE"
  export let conf_btn_decline_txt:string = "CANCEL"

  export let disabled: boolean = false
  export let rendered: boolean = true

  let modal_view: boolean = false
  let hover     : boolean = false
  
  export function open_conf(){ modal_view = true }
</script>

{#if rendered }
  <button class="round-btn round-btn-{disabled ? 'disabled': color}" 
    onclick={(e: any) => { 
      if (!disabled){
        if (with_confirmation) {
          modal_view = true
        } else {
          onclick(e)
        }
      }
    }} 

    onmouseenter="{() => {hover = true}}" onmouseleave="{() => {hover = false}}"   
  >
    {#if text !== ""}
      <Tooltip text="{text}" show={hover} x="-15px" y="-50px" />
    {/if}

      <svelte:component style="width: 22px; height:24px; vertical-align: top; " this={icon} /> 
  </button>

  {#if with_confirmation}
    <ConfModal 
      title={conf_title} description={conf_description} 
      btn_accept_txt={conf_btn_accept_txt} btn_decline_txt={conf_btn_decline_txt}
      bind:visible={modal_view} on_accept={(e: any) => { onclick(e)} } 
    />  
  {/if}
{/if}  

<style>
  .round-btn {
      border-radius: 50%;

      display: inline-block;
      height: 38px;
      width:  38px;
      text-align: center;
      text-decoration: none;
      margin-left:  2px;
      margin-right: 2px;

      transition: all 0.25s;    
  }


</style>