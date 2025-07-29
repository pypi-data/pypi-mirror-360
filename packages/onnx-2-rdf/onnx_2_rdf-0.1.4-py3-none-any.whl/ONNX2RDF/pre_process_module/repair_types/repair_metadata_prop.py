from warnings_thread_safe import warnings 
from pre_process_module.util_process.util import remove_extra_params,LINE_WITH_TAB

def check_metadata_entry(entry,keys:list[str],start_error_messege:str=""):
    
    params= ["key","value"]
    
    if not isinstance(entry,dict):
        warnings.warn( f"{start_error_messege} is not a dict")
        return False
    
    if not isinstance(entry,dict):
        warnings.warn( f"{start_error_messege} is not a dict")
        return False
    
    if "key" not in entry and "value" not in entry:
        warnings.warn( f"{start_error_messege} entry has not key or value -> Deleting entry")
        return False
        
    
    if "key" in entry and entry["key"] in keys:
        warnings.warn( f"{start_error_messege} key (\"{entry["key"]}\") is already in use, keys should be distinct -> Deleting Duplicate Key Entry")
        return False
    
    if "key" in entry and "value" not in entry:
        entry["value"]=""
        
    if "key" not in entry and "value" in entry and "" not in keys:
        entry["key"]=""
    elif "key" not in entry and "value" in entry:
        warnings.warn( f"{start_error_messege} its key is missing and the value is filled, but the key (\"\") is already in use")
        return False
    
    if "key" in entry and "value" in entry and not isinstance(entry["key"],str):
        warnings.warn( f"{start_error_messege} its key is not a string")
        return False
        
    if "key" in entry and "value" in entry and not isinstance(entry["value"],str):
        warnings.warn( f"{start_error_messege} its value is not a string")
        return False
    
    
    remove_extra_params(entry,params,start_error_messege)
    return True


def check_metadata_entries(entries,keys:list[str]=None,start_error_messege:str="",element_id="",uri_id="metadata"):
    if start_error_messege==None:
        start_error_messege:str=""
    if keys==None:
        keys=[]
    all_correct=True
    if not isinstance(entries,list):
        warnings.warn(f"{start_error_messege} metadata entries are not a list")
        return False,False
    for idx,entry in enumerate(entries):
        check =check_metadata_entry(entry,keys=keys,start_error_messege=f"{start_error_messege} the entry at pos {idx} has a wrong format {LINE_WITH_TAB}")
        if not check:
            entries.remove(entry)
            all_correct=False
        else:
            keys.append(entry["key"])
            if element_id!="":
                entries[idx]["element_id"]=f"{element_id}-{uri_id}-{entry["key"]}"
            else:
                entries[idx]["element_id"]=f"{uri_id}-{entry["key"]}"
    return len(entries)>0,all_correct
    

       