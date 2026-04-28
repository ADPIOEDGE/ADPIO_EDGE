import { writable, get } from 'svelte/store'
import Cookies from 'js-cookie'

//export const version = 'Dev Version'

/**** GET POST CSRF ****/
//const csrf_token: string = get_cookie_value('csrftoken')                      //CSRF TOKEN for authentication

let headers = new Headers({                                                   //Header For POST Requests
  'Accept': 'application/json',
  'Content-Type': 'application/json; charset=UTF-8',
  //'X-CSRFToken': csrf_token,
  //'Authorization': 'Basic s'
})

export let browser_params = writable( {
  //browser: '',
  outerWidth:   0,
	innerWidth:   0,
	outerHeight:  0,
	innerHeight:  0,
})

export async function async_post(uri: string, cmd: string, jsn_content?: any){  //Async POST Request CMD
  if ((jsn_content === null) ||  (jsn_content === undefined))
    jsn_content = {empty: ''}
  
  let jsn: any = { cmd: cmd, content: JSON.stringify(jsn_content) }

  const pst = await fetch(uri, {
      method: 'POST',
      headers,
      credentials: 'include',

      body: JSON.stringify(jsn)
  })

  jsn = await pst.json();

  if ( ('result' in jsn) && (jsn.result === 'error') ) {
    popup_add('Error', jsn.error_text)
  }

  return jsn;
}

export async function async_get(uri: string){                                          //Async Get Request CMD
  const pst = await fetch(uri)

  return pst
}

export async function set_auth_header(sessionkey: string){
  set_cookie("sessionkey", sessionkey )
  headers.set('Authorization', sessionkey)
}

export function init_browser_params(){
  let brwsr = get(user_params)

  if     ( navigator.userAgent.indexOf("Chrome")  != -1 )  brwsr.client = "chrome";
  else if( navigator.userAgent.indexOf("Opera")   != -1 )  brwsr.client = "opera";
  else if( navigator.userAgent.indexOf("MSIE")    != -1 )  brwsr.client = "ie";
  else if( navigator.userAgent.indexOf("Firefox") != -1 )  brwsr.client = "firefox";
  else brwsr.client = "unknown";

  user_params.set(brwsr)
}

export function set_browser_resize(outerWidth: number, innerWidth: number, outerHeight:number, innerHeight:number){
  let brwsr = get(browser_params)

  brwsr.outerWidth  = outerWidth
	brwsr.innerWidth  = innerWidth
	brwsr.outerHeight = outerHeight
	brwsr.innerHeight = innerHeight

  browser_params.set(brwsr)
}

/**** USER MANAGMENT ****/

export var user_params = writable({     //user params
  user_name:      'Guest',
  user_auth:      false,
  user_profile:  'view',        //Will it even be 
  client:        'unknown',     //Broser

  gui_edit_mode:    false,      //False - View, True - Edit Mode
  gui_edit_btn_ena: false,      //Enables switch over button on top
  tree_visible:     true,       //Expanded or collapsed tree
  filter:           '',         //filter

  view_header:    '',
  view_content:   '',
  view_tree:      [],
  
  edit_header:    '',
  edit_content:   '',
  edit_tree:      [],

  active_header:  '',
  active_content: '',
  active_tree:    [],

})

export function set_user_params(usr: any){
  user_params.set(usr)
}

export function get_user_params(){
  return get(user_params)
}


export function set_edit_mode(edit_mode: boolean){
  let new_user = get(user_params)

  if (edit_mode) {
    new_user.gui_edit_mode  = true
    new_user.active_header  = new_user.edit_header
    new_user.active_content = new_user.edit_content
    new_user.active_tree    = new_user.edit_tree
  } else {
    new_user.gui_edit_mode = false
    new_user.active_header  = new_user.view_header
    new_user.active_content = new_user.view_content
    new_user.active_tree    = new_user.view_tree
  }

  user_params.set(new_user)
}

export function set_navigation(header: string, addr: string){
  let new_navi = get(user_params)

  new_navi.active_header  = header
  new_navi.active_content = addr

  if (new_navi.gui_edit_mode) {
    new_navi.edit_header  = header
    new_navi.edit_content = addr
  } else {
    new_navi.view_header  = header
    new_navi.view_content = addr
  }

  user_params.set(new_navi)
}

export function set_header(header: string){
  let new_navi = get(user_params)

  new_navi.active_header  = header

  user_params.set(new_navi)
}


export async function initialize_user(user_check:any){
  let user = get(user_params)

  set_auth_header(user_check.sessionkey)
  user.user_name = user_check.user
  user.user_auth = true
  user.user_profile = user_check.profile

  const trees = await async_post("/user", "get_tree", { profile: user.user_profile })

  user.view_tree = trees.view_tree
  user.edit_tree = trees.edit_tree  

  if (user.edit_tree.length === 0){
    user.gui_edit_mode    = false
    user.gui_edit_btn_ena = false
    user.active_tree      = user.view_tree 
  } else {
    user.gui_edit_mode    = true
    user.gui_edit_btn_ena = true
    user.active_tree      = user.edit_tree 
  }

  user_params.set(user)

  set_navigation('APP MANAGER', '/app_ide/mng')    
}

export function logout_user(){
  let user = get(user_params)
  
  user.user_name        = 'Guest'
  user.user_auth        = false
  user.gui_edit_btn_ena = false

  set_edit_mode  (false)
  set_auth_header("undefined")

  user.view_tree    =  []
  user.edit_tree    =  []
  user.active_tree  =  []

  user_params.set(user)
  set_navigation('Login', '/login')
}


export function get_cookie_value(name: string) {                                      //Just A cookie filter 
  return Cookies.get(name)
}


export function set_cookie(param:string, value: any){
  Cookies.set(param, value, {SameSite: 'Strict', secure: false,  path: '/'}); //secure obnly in https???
}

/**** Data ****/
export function find_button(buttons:any, name: string){
  return buttons.find((el:any) =>  el.text === name )
}

export function find_button_index(buttons:any, name: string){
  return buttons.findIndex((el:any) =>  el.text === name )
}

export function random_id(){
  return (Math.floor(Math.random() * 100000)).toString() + '_' + Date.now().toString();
}

export function sleep(ms: number) {  return new Promise(resolve => setTimeout(resolve, ms)) }

/**** Popup Engine ****/
export let popup_list:any = writable([])

export function popup_delete(index: number){
  let popups:any = get(popup_list)
  popups.splice(index, 1)
  popup_list.set(popups)
}

export function popup_add(header_msg: string, description_msg: string){
  let popups: any = get(popup_list)
  if (popups.length < 32){
    popups.push({ header: header_msg, description: description_msg })
    popup_list.set(popups)
  }
}


/**** App Edit Tree ****/
export function datapoint_tree(data_db: any, groups_db: any){
  let new_active_tree: any = []

  groups_db.forEach((el:any) => { //Add expand capabilities
    let new_grp: any = {id: el.name, name: el.name, visible: true, submenu: []}

    data_db.forEach((el_d:any) => { 
      if (el_d.group === el.name)
          new_grp.submenu.push( {
              id: `datapoint_${el_d.id}`, name: el_d.name,
              visible: true, draggable: true, 

              type    : 'datapoint', 
              el_name : el_d.name,
              el_group: el_d.group,
              el_id   : el_d.id //Datapoint Specific
            } )
    })

    new_active_tree.push(new_grp)
  })

  return new_active_tree
}

export function update_data_groups(data: any, group: string){ //Data and group is key
  var lst:any = []
  data.forEach((el:any) => {
    if (!lst.includes(el[group]) && (el[group] !== "")){ lst.push(el[group]) }
  })

  let groups: any = []
  lst.forEach((el:any) => { groups.push( { name: el, value: el, expand: true } ) })

  return groups
}