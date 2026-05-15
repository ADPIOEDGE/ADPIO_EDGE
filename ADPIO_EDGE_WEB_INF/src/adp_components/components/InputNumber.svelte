<script  lang="ts">
    import { 
      random_id
    } from "../../stores"

    export let label    :string = ""
    export let value    :number
    export let type     :string = "int" //Float or Integer

    export let readonly :boolean  = false

    export let minvalue :number  = 0
    export let maxvalue :number  = 100
    export let step     :number       = 1
    export let limits   :boolean   = true
    export let decimals :number  = 2

    export let onchange = function(e: any){    }

    export let width: number = 240

    const r_id:string = random_id()
    let focused: boolean = false

    let inpt   : any = undefined

    function check_pattern(e: any){
        var numberRegex: any = /^\d+$/; //Numbers only

        if (e)
            switch (e.keyCode) {
                case 37: //'ArrowLeft':
                case 39: //'ArrowRight':
                case 8 :  //'Backspace':
                case 46: //'Delete':
                case 36: //'Home':
                case 35: //'End':
                    return true

                case 67:  //CTRL C 
                case 86:  //CTRL V
                case 65:  //CTRL A
                    if (e.ctrlKey) return true
            }

    
        if ((type !== "int") && (e.key === '.'))
            return true 

        if ((minvalue < 0) && (e.key === '-'))
            return true

        //Test Key First
        if (numberRegex.test(e.key) !== true)
            e.preventDefault()

        return false
    }

    function check_limits(v: number){
        if (limits) { //Enforse Limits ?
            if (v < minvalue) v = minvalue
            if (v > maxvalue) v = maxvalue
        }   

        if (type === 'float')
            v = parseFloat( v.toFixed(decimals) )

        return Number(v)
    }


</script>

<div style="width: {width}px;">
    <span class="input-container {readonly? 'input-container-readonly' : ''}"  >
        {#if readonly}
            <input inputmode="{type === "int" ? "numeric" : "decimal"}" id="input-text-{r_id}" required
                onkeydown="{(e: any) => { e.preventDefault() }}"
                bind:value={value} 
            >
        {:else}
            <input bind:this={inpt} inputmode="{type === "int" ? "numeric" : "decimal"}" id="input-text-{r_id}" required
                min  = {minvalue}
                max  = {maxvalue}
                step = {step}
                                
                bind:value={value}
                
                onwheel   = {(e:any) => {
                    if (!focused) return
                    e.preventDefault()
                    
                    let val: number = Number(e.target.value)

                    if (e.deltaY < 0)
                        val += step   // Increase
                    else if (e.deltaY > 0) 
                        val -= step   // Decrease

                    value = check_limits(val)
                    onchange(e)
                }}


                onkeydown = {(e:any) => { check_pattern(e) }}
                oninput   = {(e:any) => { onchange(e)    }}

                onfocus = {() => { focused = true  }}
                onblur  = {(e: any) => { 
                    focused = false 
                    onchange(e)
                    value = check_limits(value)
                }}
            >
        {/if}

        <label for="input-text-{r_id}" class="input-label">{label}</label>
        <span  class="input-underline"></span>
    </span>
</div>

<style>

</style>