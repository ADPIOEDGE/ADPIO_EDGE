<script  lang="ts">
    import { elasticInOut } from "svelte/easing";
    import ButtonR    from "./ButtonR.svelte"

    export let buttons:any
    export let binds: any  = [undefined,undefined,undefined,undefined,undefined,undefined,undefined,undefined,undefined,undefined,]
    
    //icon, text, color
    //disabled, rendered
    //onclick
    //with_confirmation, conf_title, conf_description, conf_btn_accept_txt

    export let hotkeys: boolean = false

    async function onkey_down_call(e: any){
        if (!hotkeys) return
        if ( e.keyCode >= 112 && e.keyCode <= 121 ){ //Navigation with F1-F10
            e.preventDefault()

            let index = e.keyCode - 112 
            if (binds[index] === undefined) return

            const btn = buttons[index]
            const bnd = binds  [index]
        
            const rendered = ('rendered' in btn)?  btn.rendered : true
            const disabled = ('disabled' in btn)?  btn.disabled : false

            if (!disabled && rendered === true){
                if (btn.with_confirmation) bnd.open_conf()
                else btn.onclick(e)                
            }
        }
    }

</script>

    <svelte:window on:keydown={async (e:any) => { await onkey_down_call(e) }} />

    {#each buttons as btn, index }
        <ButtonR 
            bind:this           = {binds[index]}
            
            icon                = {btn.icon}   
            text                = {hotkeys?  `${btn.text} [F${index + 1}]` : btn.text}  
            color               = {btn.color} 
                
            disabled            = {('disabled' in btn)?  btn.disabled : false}

            onclick             = {(e: any) => { btn.onclick(e) }}      
                
            with_confirmation   = {btn.with_confirmation}
            conf_title          = {btn.conf_title}
            conf_description    = {btn.conf_description}
            conf_btn_accept_txt = {btn.conf_btn_accept_txt}                
        />
    {/each}

<style>

</style>

