<script lang="ts">
  import { onMount } from 'svelte'

  import Header       from "./adp_components/layout/Header.svelte"
  import Navigation   from "./adp_components/layout/Navigation.svelte"
  import Popups       from "./adp_components/layout/Popups.svelte"

  import Login        from './content/system/Login.svelte'
  import About        from './content/system/About.svelte'
  import Logger       from './content/system/Logger.svelte'
  import Users        from './content/system/Users.svelte'
  import PaletteLogic from './content/system/PaletteLogic.svelte'
  
  import LoraTools    from './content/system/LoraTools.svelte'
  import BACnetTools  from './content/system/BACnetTools.svelte'

  import IDE_mng      from './content/app_ide/IDE_mng.svelte'
  import IDE_main     from './content/app_ide/IDE_main.svelte'

  import APP_view     from './content/view/APP_view.svelte'
  import Trends_view  from './content/view/Trends_view.svelte'

  import Debug        from './adp_components/Debug.svelte'

  import {
    user_params, 
    browser_params,

    set_user_params, 
    set_edit_mode, 
    async_post,
    set_navigation,
    
    init_browser_params,
    set_browser_resize,

    set_auth_header,
    get_cookie_value,
    initialize_user
  } from "./stores.js"
      
  $: user      = $user_params

  $: outerWidth  = 0
	$: innerWidth  = 0
	$: outerHeight = 0
	$: innerHeight = 0

  let resize_interval:boolean = false

  async function initialize_login(){
    set_navigation('Login', '/login')
    set_edit_mode (false)
  }

  async function on_resize(){
    if (resize_interval) return

    resize_interval = true
    const interval = setInterval(() => {
      set_browser_resize(outerWidth, innerWidth, outerHeight, innerHeight)
      clearInterval(interval)
      resize_interval = false
		}, 250)
  }

  onMount(async () => { 
    //Check Login Cookie
    let ssk = get_cookie_value('sessionkey') 
    let usr_chck: any = undefined

    if (ssk !== undefined && ssk !== "undefined"){
      usr_chck = await async_post("/login", "sessionkey", {'key': ssk})
      user.user_auth = usr_chck.auth
    }

    if (user.user_auth === false)
      await initialize_login()
    else{
      await initialize_user(usr_chck)
    }
      
    //console.log(user)
    //DEBUG PAGES
    //set_navigation('HTML DEBUG COMPONENTS', '/debug')

    //Get Browser Type and window params
    init_browser_params()
    
    await on_resize()
  });
  

</script>

  <svelte:window bind:innerWidth bind:outerWidth bind:innerHeight bind:outerHeight
    onresize="{async () => {
      await on_resize()
    }}" 
  />


	<div class="app-left {user.tree_visible? "app-left-visible":"" }" >
		<Navigation user={user} />
	</div>
	
  <div class="app-right {user.tree_visible? "app-right-visible":"" }">
    <Header user={user}  />    

    <main>

      {#if user.active_content.includes("/view")}
        {#key user.active_content}
          <APP_view uri="{user.active_content}" />
        {/key}
      {:else if user.active_content.includes("/app_ide")}
        {#if      user.active_content.includes("/mng")}    <IDE_mng />
        {:else if user.active_content.includes("/editor")} <IDE_main />
        {/if}
      {:else if user.active_content.includes("/login")}
        <Login />
      {:else if user.active_content.includes("/tools")}  
        {#if      user.active_content.includes("/trendview")}     <Trends_view />   
        {:else if user.active_content.includes("/lorabrowser")}   <LoraTools   />   
        {:else if user.active_content.includes("/bacnetbrowser")} <BACnetTools /> 
        {/if}
      {:else if   user.active_content.includes("/development")}
        {#if      user.active_content.includes("/palettelogic")}  <PaletteLogic />
        {/if}
      {:else if user.active_content.includes("/system")}
        {#if      user.active_content.includes("/user")}  <Users />
        {:else if user.active_content.includes("/logs")}  <Logger />
        {:else if user.active_content.includes("/about")} <About  /> 
        {/if}
      {:else if user.active_content.includes("/debug")}
        <Debug />
      {:else}
        <div>Incorrect Content Request</div>        
        <div>Content Requested: '{user.active_content}'</div>
      {/if}
    
    </main>
	</div>

  <Popups />


<style></style>
