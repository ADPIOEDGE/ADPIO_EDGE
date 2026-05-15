<script  lang="ts">
    import { onMount } from 'svelte'

    import {
        DATAPOINTS_PROPERTIES,
        DATA_TYPES,
        PROTOCOL_LIST
    } from "../../app_engine"

    import { PRIORITY_ARRAY_LIST } from '../../../public/bacnet_lists'
 
    import { 
        async_post,
    } from "../../stores"

    import InputDropList from "../components/InputDropList.svelte"
    import InputLabel    from "../components/InputLabel.svelte"
    import InputNumber   from "../components/InputNumber.svelte"
    import InputSelector from '../components/InputSelector.svelte'
    import InputSwitch   from "../components/InputSwitch.svelte"
    import DataDisplay   from '../components/DataDisplay.svelte'

    let groups      : string[] = []
    let grp_selected: string   = 'ALL'

    let loraDev_list    : any = []
    let loraFields_list : any = []

    let bacDev_list     : any = []
    let bacObject_list  : any = []    
    let bacProperty_list: any = []    

    export let values: any

    export let widget_list: any = [ //Bind name is a name of the field inside value_ibjec //use bind_sub_name for add on
        { type: 'InputLabel'   , group: "GROUP 1", label: "Test", bind_name: "field", visible: true, args: {
            minlength: 0, maxlength: 24, readonly: false
        }},
        { type: 'InputNumber'  , group: "GROUP 1", label: "Test", bind_name: "field", visible: true, args: {
            type: "int", //Float or Integer
            readonly: false, minvalue: 0, maxvalue: 100, step:1
        }},
        { type: 'InputSelector', group: "GROUP 2", label: "Test", bind_name: "field", visible: true, args: {
            item_list: [ {name: "Item 1", value: "Value1"}, ],
            readonly: false, not_equal: false //Used at multiselection for editing multiple objects
        }},
        { type: 'InputDropList', group: "GROUP 2", label: "Test", bind_name: "field", visible: true, args: {
            item_list: [ {name: "Item 1", value: "Value1"}, ],
            readonly: false,  minlength: 0,  maxlength: 24 
        }},
        { type: 'InputSwitch'  , group: "GROUP 3", label: "Test", bind_name: "field" , visible: true, args: {
            readonly: false
        }}, 

        { type: 'DataDisplayPropEdit'  , group: "GROUP 3", label: "Test", bind_name: "field" , visible: true, args: {
            readonly: false,  show_properties: false, label: ''
        }},

        { type: 'ProtocolEdit'  , group: "GROUP 3", label: "Test", bind_name: "protocol" , visible: true, args: {
            readonly: false, 
        }},

        { type: 'TrendEdit'  , group: "GROUP 3", label: "Test", bind_name: "protocol" , visible: true, args: {
            readonly: false, 
        }},


        { type: 'Label'  , group: "GROUP 3", label: "Test", bind_name: "field" , visible: true, args: {}},        
    ]
	
    function on_value_change(wg: any, sub_filed?: any){
        if (sub_filed === undefined) {
            values.forEach((el:any) => {            
                el[wg.bind_name] = wg.bind
            }) 
        } else {
            values.forEach((el:any) => {      
                el[wg.bind_name][sub_filed]  = wg.bind[sub_filed]
            })             
        }
    }


    function on_datapoint_change(wg: any, field:string){
        values.forEach((el:any) => { 
            el[field] = wg.bind[field]
        })         
    }

    function onpropertychange(wg: any, property: string){
        values.forEach((el:any) => { 
            el.properties[property] = wg.bind.properties[property]
        })  
    }

    function on_datatype_change(wg: any){
        //Detect if type was changed
        let passed = true
        switch (wg.bind.datatype) {
            case "bool":
                wg.bind.value = false
                if (wg.bind.properties.type !== 'bool') wg.bind.properties = DATAPOINTS_PROPERTIES.bool
                break
            case "int":
                wg.bind.value = 0
                if (wg.bind.properties.type !== 'int')  wg.bind.properties = DATAPOINTS_PROPERTIES.int
                break
            case "float":
                wg.bind.value = 0.1
                if (wg.bind.properties.type !== 'float') wg.bind.properties = DATAPOINTS_PROPERTIES.float
                break
            case "str":
                wg.bind.value = "Text"
                if (wg.bind.properties.type !== 'str')   wg.bind.properties = DATAPOINTS_PROPERTIES.str
                break     
            default:
                passed = false
                console.log("Incorrect Data Type: " + wg.bind.datatype)
        }

        if (passed){
            on_datapoint_change(wg, 'datatype')
            on_datapoint_change(wg, 'value')        
            on_datapoint_change(wg, 'properties')
            wg.not_equal_type = false
        }
    }
        

	onMount(() => {
		const interval = setInterval(() => {
            widget_list.forEach((wg: any) => {
                wg['not_equal']      = false
                wg['not_equal_type'] = false

                if (wg.type === 'DataDisplayPropEdit') {
                    wg['bind']  = JSON.parse( JSON.stringify( values[0] ))
                } else if (
                    (wg.type === 'ProtocolEdit') ||
                    (wg.type === 'TrendEdit')
                ){
                    wg['bind']  = JSON.parse( JSON.stringify( values[0][wg.bind_name] ))
                } else wg['bind'] = values[0][wg.bind_name]
            })
            

        //Make Groups
            groups.push('ALL')
            widget_list.forEach((el: any) => {
                if (!groups.includes(el.group)) 
                    groups.push(el.group) //Make group list
            })
            groups = groups

        //Finds all not equal fields 
            if (values.length > 1){ 
                widget_list.forEach((wg: any) => {
                    values.forEach((val: any) => {
                        if (wg.type === 'DataDisplayPropEdit'){
                            if (wg.bind.datatype !== val.datatype) wg.not_equal_type = true 
                            if (wg.bind.value    !== val.value)    {
                                wg.not_equal   = true
                                wg.bind.value  = '≠'
                            } 
                        } else if (wg.type === 'ProtocolEdit'){
                            const keys = Object.keys(wg.bind)

                            keys.forEach((key: any) => {
                              if (wg.bind[key]  !== val[wg.bind_name][key]) wg.bind[key] = '≠'   
                            })
                        } else if (wg.type === 'TrendEdit'){
                            if (wg.bind.enable  !== val[wg.bind_name].enable)  wg.bind.enable  = '≠'
                            if (wg.bind.refresh !== val[wg.bind_name].refresh) wg.bind.refresh = '≠'
                        } else if (('bind_sub_name' in wg) && (wg.bind !== val[wg.bind_name][wg.bind_sub_name])){
                            wg.not_equal = true
                            wg.bind      = '≠'
                        } else if (wg.bind !== val[wg.bind_name]) {
                            wg.not_equal = true  
                            wg.bind      = '≠'   
                        }               
                    })
                })
            }

            widget_list = widget_list

            clearInterval(interval)
		}, 100)
	})

</script>


    {#if groups.length > 2}
        <div class="filter">
            {#each groups as grp}
                <!-- svelte-ignore a11y_no_static_element_interactions -->
                <div class="{(grp_selected === grp)? 'selected_grp' : ''}"
                    onpointerdown={() => {grp_selected = grp}}
                >
                    {grp}
                </div>
            {/each}
        </div>
    {/if}

    <div class="data_edit_flex">
        {#each widget_list as wg}
            {#if ((wg.visible) && ('bind' in wg) && ( (wg.group === grp_selected || grp_selected === 'ALL') ))}
                {#if wg.type      === 'InputLabel'}
                    <div class="data_edit_flex_left">{wg.label}</div>
                    <div class="data_edit_flex_right">
                        <InputLabel    label=""  bind:value={ wg.bind } minlength={wg.args.minlength} maxlength={wg.args.maxlength} readonly={wg.args.readonly}
                            oninput={()=>{ on_value_change( wg ) }}
                        />
                    </div>
                {:else if wg.type === 'InputNumber'}
                    <div class="data_edit_flex_left">{wg.label}</div>
                    <div class="data_edit_flex_right">
                        <InputNumber   label=""  bind:value={ wg.bind } readonly={wg.args.readonly}   minvalue={wg.args.minvalue}  maxvalue={wg.args.maxvalue} step={wg.args.step} 
                            onchange={()=>{  on_value_change( wg )  }}
                        />
                    </div>
                {:else if wg.type === 'InputSelector'}
                    <div class="data_edit_flex_left">{wg.label}</div>
                    <div class="data_edit_flex_right">
                        <InputSelector label=""  bind:value={ wg.bind } item_list={wg.args.item_list} readonly={wg.args.readonly}  
                            onchange={()=>{ on_value_change( wg ) }}
                        />
                    </div>
                {:else if wg.type === 'InputDropList'}
                    <div class="data_edit_flex_left">{wg.label}</div>
                    <div class="data_edit_flex_right">
                        <InputDropList label=""  bind:value={ wg.bind } item_list={wg.args.item_list} readonly={wg.args.readonly}  minlength={wg.args.minlength}  maxlength={wg.args.maxlength} 
                            onchange={()=>{ on_value_change( wg )  }}
                        />
                    </div>
                {:else if wg.type === 'InputSwitch'}
                    <div class="data_edit_flex_left">{wg.label}</div>
                    <div class="data_edit_flex_right">
                        <InputSwitch   label=""  bind:value={ wg.bind } readonly={wg.args.readonly} 
                            onchange={()=>{ on_value_change( wg )  }}
                        />
                    </div>
                {:else if wg.type === 'DataDisplayPropEdit'}
                    <div class="data_edit_flex_left">Data Type</div>
                    <div class="data_edit_flex_right">
                        <InputSelector label=""  bind:value={ wg.bind.datatype } item_list={DATA_TYPES} readonly={false}  
                            onchange={()=>{ on_datatype_change( wg ) }}
                        />
                    </div>

<!-- Present Values-->
                    {#if !wg.not_equal_type} 
                        <div class="data_edit_flex_left">{wg.label}</div>
                        <div class="data_edit_flex_right">
                            <DataDisplay bind:datapoint={ wg.bind } readonly={wg.args.readonly} label={wg.args.label}
                                onchange={()=>{ on_datapoint_change( wg, 'value' ) }}
                            />
                        </div>
                        
                        <!--props--> 
                        {#if ('show_properties' in wg.args) && (wg.args.show_properties)}                    
                            {#if  wg.bind.datatype === 'bool'}
                                <div class="data_edit_flex_left">Disabled Text</div>
                                <div class="data_edit_flex_right"><InputLabel label="" bind:value={wg.bind.properties.text_false}
                                    oninput={()=>{onpropertychange(wg, 'text_false') }}
                                /></div>
                                
                                <div class="data_edit_flex_left">Enabled Text</div>
                                <div class="data_edit_flex_right"><InputLabel label="" bind:value={wg.bind.properties.text_true}
                                    oninput={()=>{onpropertychange(wg, 'text_true') }}
                                /></div>
                                
                            {:else if  wg.bind.datatype === 'int'}
                                <div class="data_edit_flex_left">Minimum Value</div>
                                <div class="data_edit_flex_right"><InputNumber label="" bind:value={wg.bind.properties.min}  step={1} minvalue={-999999999999999} maxvalue={999999999999999}
                                   onchange={()=>{ onpropertychange(wg, 'min') }}
                                /></div>
                                
                                <div class="data_edit_flex_left">Maximum Value</div>
                                <div class="data_edit_flex_right"><InputNumber label="" bind:value={wg.bind.properties.max}  step={1} minvalue={-999999999999999} maxvalue={999999999999999}
                                    onchange={()=>{ onpropertychange(wg, 'max') }}
                                /></div>
                                
                                <div class="data_edit_flex_left">Steps</div> 
                                <div class="data_edit_flex_right"><InputNumber label="" bind:value={wg.bind.properties.step} step={1} minvalue={0}  maxvalue={1000}
                                    onchange={()=>{ onpropertychange(wg, 'step') }}
                                /></div>
                                
                            {:else if  wg.bind.datatype === 'float'}
                                <div class="data_edit_flex_left">Minimum Value</div>
                                <div class="data_edit_flex_right"><InputNumber label="" bind:value={wg.bind.properties.min} minvalue={-999999999999999} maxvalue={999999999999999}
                                    onchange={()=>{ onpropertychange(wg, 'min') }}
                                /></div>    
                                
                                <div class="data_edit_flex_left">Maximum Value</div>
                                <div class="data_edit_flex_right"><InputNumber label="" bind:value={wg.bind.properties.max}  minvalue={-999999999999999} maxvalue={999999999999999}
                                    onchange={()=>{ onpropertychange(wg, 'max') }} 
                                /></div>    
                                
                                <div class="data_edit_flex_left">Decimal Places</div>
                                <div class="data_edit_flex_right"><InputNumber label="" bind:value={wg.bind.properties.decimals} step={1} minvalue={0} maxvalue={64}
                                   onchange={()=>{ onpropertychange(wg, 'decimals') }}
                                /></div>    
                                
                                <div class="data_edit_flex_left">Step</div>
                                <div class="data_edit_flex_right"><InputNumber label="" bind:value={wg.bind.properties.step} type="float"  step={0.1} minvalue={0} maxvalue={1000}
                                    onchange={()=>{ onpropertychange(wg, 'step') }}
                                /></div>                        
                                
                            {:else if  wg.bind.datatype === 'str'}
                                <div class="data_edit_flex_left">Text Max Length</div>
                                <div class="data_edit_flex_right"><InputNumber label="" bind:value="{wg.bind.properties.length}"  minvalue={1} maxvalue={1024}
                                    onchange={()=>{ onpropertychange(wg, 'length') }}
                                /></div>
                            {/if}   
                        {/if}           
                <!--props-->  

                    {:else} 
                        <div class="data_edit_flex_left"></div> 
                        <div class="data_edit_flex_right">Different Data Types</div>
                    {/if}

<!-- Protocols -->
                {:else if wg.type === 'ProtocolEdit'}
                    <div class="data_edit_flex_left">Protocol</div>
                    <div class="data_edit_flex_right">
                        <InputSelector label=""  bind:value={ wg.bind.enable } item_list={PROTOCOL_LIST} readonly={wg.args.readonly}  
                            onchange={()=>{ on_value_change( wg ) }}
                        />
                    </div>
                    
<!-- BACnet -->
                    {#if wg.bind.enable === 'bacnet'}
                        <div class="data_edit_flex_left">Network</div>
                        <div class="data_edit_flex_right">
                            <InputDropList label=""  bind:value={ wg.bind.bac_net } item_list={bacDev_list} readonly={wg.args.readonly}  minlength={1}  maxlength={32} 
                                onchange={()=>{ on_value_change( wg, 'bac_net' )  }}
                                onfocus={async (e:any) => { bacDev_list = await async_post( '/network_tools', 'bacnet_tools_list_devices' )} }
                            />
                        </div>

                        <div class="data_edit_flex_left">Object</div>
                        <div class="data_edit_flex_right">
                            <InputDropList label=""  bind:value={ wg.bind.bac_object } item_list={bacObject_list} readonly={wg.args.readonly}  minlength={1}  maxlength={24} 
                                onchange={()=>{ on_value_change( wg, 'bac_object' )  }}
                                onfocus={async (e:any) => { bacObject_list = await async_post( '/network_tools', 'bacnet_tools_list_objects',  { device_net: wg.bind.bac_net }) }}
                            />
                        </div>

                        <div class="data_edit_flex_left">Property</div>
                        <div class="data_edit_flex_right">
                            <InputDropList label=""  bind:value={ wg.bind.bac_property } item_list={bacProperty_list} readonly={wg.args.readonly}  minlength={1}  maxlength={24} 
                                onchange={()=>{ on_value_change( wg, 'bac_property' )  }}
                                onfocus={async (e:any) => { bacProperty_list = await async_post( '/network_tools', 'bacnet_tools_list_properties', { device_net: wg.bind.bac_net, object: wg.bind.bac_object } ) }}
                            />
                        </div>

                        <div class="data_edit_flex_left">Read Enable</div>
                        <div class="data_edit_flex_right">
                            <InputSwitch   label=""  bind:value={ wg.bind.bac_read_enable } readonly={wg.args.readonly} 
                                onchange={()=>{ on_value_change( wg, 'bac_read_enable' )  }}
                            />
                        </div>
                        {#if wg.bind.bac_read_enable}
                            <div class="data_edit_flex_left">Read Refresh</div>
                            <div class="data_edit_flex_right">
                                <InputNumber label="" bind:value={wg.bind.bac_read_refresh} step={1} minvalue={0}  maxvalue={9999}
                                    onchange={()=>{ on_value_change( wg , 'bac_read_refresh') }}
                                />
                            </div>
                        {/if}

                        <div class="data_edit_flex_left">Write Enable</div>
                        <div class="data_edit_flex_right">
                            <InputSwitch   label=""  bind:value={ wg.bind.bac_write_enable } readonly={wg.args.readonly} 
                                onchange={()=>{ on_value_change( wg, 'bac_write_enable' )  }}
                            />
                        </div>
                        {#if wg.bind.bac_write_enable}
                            <div class="data_edit_flex_left">Write Priority</div>
                            <div class="data_edit_flex_right">
                                <InputSelector label=""  bind:value={ wg.bind.bac_write_prio } item_list={PRIORITY_ARRAY_LIST} readonly={wg.args.readonly}  
                                    onchange={()=>{ on_value_change( wg, 'bac_write_prio' ) }}
                                />
                            </div>
                        {/if}

 <!-- LoRaWAN -->                       
                    {:else if wg.bind.enable === 'lora'}
                        <div class="data_edit_flex_left">Devie EUI</div> 
                        <div class="data_edit_flex_right">
                            <InputDropList label=""  bind:value={ wg.bind.lora_devEUI } item_list={loraDev_list} readonly={wg.args.readonly}  minlength={8}  maxlength={32} 
                                onchange={()=>{ on_value_change( wg, 'lora_devEUI' )  }}
                                onfocus={async (e:any) => {
                                    loraDev_list = await async_post( '/network_tools', 'lora_tools_list_devices' )
                                } }
                            />
                        </div>               

                        <div class="data_edit_flex_left">Property</div>
                        <div class="data_edit_flex_right">
                            <InputDropList label=""  bind:value={ wg.bind.lora_field } item_list={loraFields_list} readonly={wg.args.readonly}  minlength={1}  maxlength={64} 
                                onchange={()=>{ on_value_change( wg, 'lora_field' )  }}
                                onfocus={async (e:any) => {
                                    loraFields_list = await async_post( '/network_tools', 'lora_tools_list_fields', { devEUI: wg.bind.lora_devEUI } )
                                } }
                            />
                        </div> 
                    {/if}

<!-- Trend Edit -->
                {:else if wg.type === 'TrendEdit'}
                    <div class="data_edit_flex_left">Trend Enable</div>
                    <div class="data_edit_flex_right">
                        <InputSwitch   label=""  bind:value={ wg.bind.enable } readonly={wg.args.readonly} 
                            onchange={()=>{ on_value_change( wg, 'enable' )  }}
                        />
                    </div>

                    {#if wg.bind.enable}
                        <div class="data_edit_flex_left">Refresh Rate</div>
                        <div class="data_edit_flex_right">
                            <InputNumber label="" bind:value={wg.bind.refresh} step={1} minvalue={0}  maxvalue={9999}
                                onchange={()=>{ on_value_change( wg , 'refresh') }}
                            />
                        </div>
                    {/if}
                    
                {:else if wg.type === 'Label'}
                    <div class="data_edit_flex_left">{wg.label}</div>
                    <div class="data_edit_flex_right">
                        {wg.bind_name}
                    </div>
                {:else}
                    <div class="data_edit_flex_left">Unknown type: {wg.bind_name}</div>
                    <div class="data_edit_flex_right"></div>
                {/if}    

            {/if}
        {/each}
        
    </div>


<style>
    .filter{
        display: flex; /* or inline-flex */
        flex-wrap: wrap;
        justify-content: flex-start;
    }

    .filter > div {
        margin-right: 16px;
        /*background-color: rgb(158, 255, 179);*/
        padding: 0.4em 1.2em;
        vertical-align: middle;
        text-align: center;

        cursor: pointer;
    }

    .selected_grp{
        /*background-color: rgba(83, 179, 252, 0.8);*/
        border-bottom: 2px solid #ff9800;
    }

    .data_edit_flex { 
        display: flex;   
        flex-wrap: wrap;
        width: 100%;
    }
    
    .data_edit_flex > div {
        padding: 4px 0;
        vertical-align: middle;
    }

    .data_edit_flex_left {
        flex: 1 1 calc(35% - 12px);
        /*background-color: rgb(255, 224, 224);*/
    }

    .data_edit_flex_right {
        flex: 1 1 calc(65% - 12px);
        /*background-color: rgb(236, 255, 209);*/
    }

</style>
