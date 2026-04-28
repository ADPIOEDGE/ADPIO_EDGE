<script  lang="ts">
    import {
        Terminal,
		Code,
        View,
        Menu,
        Logout,
        Login
    } from "carbon-icons-svelte"

    import {set_user_params, set_navigation, set_edit_mode, logout_user} from "../../stores.js"

    import ConfModal    from "../components/ConfModal.svelte"
    import SysTerminal  from "../components/Terminal.svelte"

    export let user   : any
    let terminal_modal: any
    let logout_conf   : boolean = false

</script>

<SysTerminal bind:this={terminal_modal} />

<div id="toolbar">
    <div>
        <button class="toolbar-menu-btns" onclick={()=>{ 
            user.tree_visible = !user.tree_visible
            set_user_params(user)
        }}>
        <Menu /></button>
        <span class="toolbar-separator"></span>

        <div>{user.active_header}</div>
    </div>
       
    <div>      
        {#if user.gui_edit_btn_ena }  
            {#if user.gui_edit_mode}
                <button class="toolbar-menu-btns" onclick={()=>{ set_edit_mode(false) }} >
                    <Code />
                    <span>Edit Mode</span>
                </button>
            {:else}
                <button  class="toolbar-menu-btns" onclick={()=>{ set_edit_mode(true) }} >
                    <View />
                    <span>View Mode</span>
                </button>
            {/if}

            <button  class="toolbar-menu-btns" onclick={async (e: any)=>{ await terminal_modal.open(e) }} >
                <Terminal />
                <span>Terminal</span>
            </button>              

            <button  class="toolbar-menu-btns" onclick={()=>{ logout_conf = true }}  >
                <Logout />
                <span>Logout, {user.user_name}</span>
            </button>  

            
        {:else}   
            <button  class="toolbar-menu-btns" onclick={()=>{ set_navigation('Login', '/login') }} >
                <Login />
                <span>Login</span>
            </button>                    
        {/if}
       
    </div>
</div>

<ConfModal 
    title="LOGOUT CONFIRMATION" description="Are you sure?"
    btn_accept_txt="LOGOUT?" btn_decline_txt="CANCEL"
    bind:visible={logout_conf} on_accept={(e:any) => { logout_user() } } 
/>  

<style>

</style>