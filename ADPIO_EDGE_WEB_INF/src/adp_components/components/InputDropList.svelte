<script  lang="ts">
import { 
  random_id
} from "../../stores"


export let label: string = ""
export let item_list:any = [
    {name: "Item 1", value: "Value1"},
]

export let readonly:boolean = false

export let value:any
export let minlength: number  = 0
export let maxlength: number  = 24 

export let width:number = 240

export let onchange = function(e: any){}
export let onfocus  = function(e: any){}

const r_id:string = random_id()

</script>


<div style="width: {width}px;">
    <span class="input-container {readonly? 'input-container-readonly' : ''}">
        {#if readonly}
            {#each item_list as item}
                {#if value === item.value}
                    <span>{item.name} </span> 
                {/if}
            {/each}
        {:else}
            <input id="dropdown_{r_id}" list="dropdown_{r_id}_list" name="dropdown_{r_id}"  required
                bind:value="{value}" 

                minlength  = {minlength}
                maxlength  = {maxlength}

                onfocus = {(e:any) => { 
                    onfocus(e) 
                }}
                    
                onblur  = {(e:any) => {  }}
                oninput = {(e:any) => { onchange(e) }}
            />

            

            <datalist id="dropdown_{r_id}_list" 
                onselect={(e:any) => { 
                    onchange(e) 
                }}
            >
                {#each item_list as item}
                    <option  value="{item.value}" 
                    >
                        {item.name}
                    </option>
                {/each}
            </datalist>   
        {/if}

        <label for="input-text-{r_id}" class="input-label">{label}</label>
        <span  class="input-underline"></span>
    </span>
</div>

<style>

</style>