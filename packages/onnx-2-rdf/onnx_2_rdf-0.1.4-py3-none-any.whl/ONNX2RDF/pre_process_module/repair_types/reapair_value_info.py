
from warnings_thread_safe import warnings 
from repair_metadata_prop import check_metadata_entries
from repair_type_proto import check_type_proto
from pre_process_module.util_process.util import remove_extra_params,LINE_WITH_TAB

def check_value_infos(value_infos,start_error_messege:str="",force_type=False,element_id=""):
    
    
    if not isinstance(value_infos,list):
        warnings.warn(f"\n{start_error_messege} valueInfo is not a list -> valueInfo being deleted")
        return False
    correct=True
    names=[]
    for idx,entry in enumerate(value_infos):
        correct = check_value_info_entry(entry,names,start_error_messege=f"{start_error_messege} valueInfo entry at pos {idx}{LINE_WITH_TAB}",force_type=force_type,element_id=element_id)
        if not correct:
            del value_infos[idx]
            
    return len(value_infos)>0

def check_value_info_entry(value_info,names,start_error_messege:str="",force_type=False,element_id=""):
    if "name" not in value_info:
        warnings.warn(f"\n{start_error_messege} has no param name -> valueInfo entry being deleted")
        return False
    if value_info["name"] in names:
        warnings.warn(f"\n{start_error_messege} its param name is not unique (Duplicate names not allowed) -> duplicate valueInfo entry being deleted")
        return False
    if "docString" in value_info and not isinstance(value_info["docString"],str):
        warnings.warn(f"\n{start_error_messege} The \"docString\" is not a string -> Removing \"docString\"")
        value_info["docString"]=""
    if "metadataProps" in value_info:
        keys=[]
        correct,_ = check_metadata_entries(value_info["metadataProps"],keys,element_id=element_id,start_error_messege=f"{start_error_messege} metadataProps param has a wrong format")
        
        if not correct:
            value_info["metadataProps"]=[]
        
    if "type" in value_info:
        correct= check_type_proto(value_info["type"],start_error_messege=f"{start_error_messege} type param has a wrong format -> valueInfo entry being deleted{LINE_WITH_TAB}",
                                  element_id=f"{element_id}-{value_info["name"]}")
        if not correct:
            return False
    elif force_type:
        warnings.warn(f"\n{start_error_messege} type param is missing -> valueInfo entry being deleted")
        return False
    remove_extra_params(value_info,["name","docString","metadataProps","type","is_input","is_output","is_value"],start_error_messege)
    value_info["element_id"]=f"{element_id}-{value_info["name"]}"
    return True



def revise_value_infos_graph(graph,element_id="",start_error_messege=""):
    if element_id!="":
        element_id=f"{element_id}-"
    
    if "valueInfo" in graph:
        for item in graph["valueInfo"]:
            item["is_value"]=""
        _ = check_value_infos(graph["valueInfo"],start_error_messege=f"{start_error_messege} The valueInfo param defined at the graph has a wrong format{LINE_WITH_TAB}",element_id=f"{element_id}Graph-{graph["name"]}-valuesInfo")
    
    if "input" in graph:
        for item in graph["input"]:
            item["is_input"]=""
        _ = check_value_infos(graph["input"],start_error_messege=f"{start_error_messege} The input param defined at the graph has a wrong format{LINE_WITH_TAB}",force_type=True,element_id=f"{element_id}Graph-{graph["name"]}-inputs")
        
    if "output" in graph:
        for item in graph["output"]:
            item["is_output"]=""
        _ = check_value_infos(graph["output"],start_error_messege=f"{start_error_messege} The output param defined at the graph has a wrong format{LINE_WITH_TAB}",force_type=True,element_id=f"{element_id}Graph-{graph["name"]}-outputs")