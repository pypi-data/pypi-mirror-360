from warnings_thread_safe import warnings 
from pre_process_module.util_process.util import remove_extra_params,LINE_WITH_TAB
from repair_tensor import check_tensor_simple,check_tensor_data_type,DataType,get_label_data_type



def check_type_proto(type,start_error_messege:str="",element_id=""):
    if not isinstance(type,dict):
        warnings.warn(f"\n{start_error_messege} Type is not a dict")
        return False
    
    if "denotation" in type and not isinstance(type["denotation"],str):
        warnings.warn(f"\n{start_error_messege} \"denotation\" param is not a string -> Deleting \"denotation\" param")
        
    
    
    if "tensorType" in type:
        check = check_tensor_simple(type["tensorType"],tensor_id=element_id,
            start_error_messege=f"{start_error_messege} The Tensor Value Info has a wrong format {LINE_WITH_TAB}")
        if check:
            remove_extra_params(type,keep_params=["tensorType","denotation"],start_error_messege=f"{start_error_messege} The Tensor Value Info ")
            type["element_id"]=element_id
            type["type"]="tensor"
            return True
        else:
            return False
    if "sparseTensorType" in type:
        check = check_tensor_simple(type,tensor_id=element_id,
            start_error_messege=f"{start_error_messege} The Sparse Tensor Value Info has a wrong format {LINE_WITH_TAB}")
        
        if check:
            remove_extra_params(type,keep_params=["sparseTensorType","denotation"],start_error_messege=f"{start_error_messege} The Sparse Tensor Value Info ")
            type["element_id"]=element_id
            type["type"]="sparse"
            return True
        else:
            return False
    if "sequenceType" in type:
        check = check_sequence_type(type["sequenceType"],f"{start_error_messege} The Sequence Value Info ")
        if check:
            remove_extra_params(type,keep_params=["sequenceType","denotation"],start_error_messege=f"{start_error_messege} The Sequence Value Info ")
            type["element_id"]=element_id
            type["type"]="seq"
            return True
        else:
            return False
    if "mapType" in type:
        check = check_map_type(type["mapType"],f"{start_error_messege} The Map Value Info ")
        if check:
            remove_extra_params(type,keep_params=["mapType","denotation"],start_error_messege=f"{start_error_messege} The Map Value Info ")
            type["element_id"]=element_id
            type["type"]="map"
            return True
        else:
            return False
    if "optional" in type:
        check = check_optional_type(type["optional"],f"{start_error_messege} The Optional Value Info ")
        if check:
            remove_extra_params(type,keep_params=["optional","denotation"],start_error_messege=f"{start_error_messege} The Optional Value Info ")
            type["element_id"]=element_id
            type["type"]="opt"
            return True
        else:
            return False
    
    
    warnings.warn(f"\n{start_error_messege} Type is not a valid Type (tensorType,sparseTensorType,sequenceType,mapType,optionalType)")
    
    return False


def check_sequence_type(value,start_error_messege:str="",element_id=""):
    if not isinstance(value,dict):
        warnings.warn(f"{start_error_messege} Is not a Dict" )
        return False
    if "elem_type" not in value:
        warnings.warn(f"{start_error_messege} \"elem_type\" param is missing" )
        return False
    else:
        if not check_type_proto(value["elem_type"],f"{start_error_messege} \"elem_type\" param has a wrong format {LINE_WITH_TAB}",element_id=f"{element_id}-Seq"):
            return False
    remove_extra_params(value,keep_params=["elem_type"],start_error_messege=start_error_messege)
    return True

def check_map_type(value,start_error_messege:str="",element_id=""):
    if not isinstance(value,dict):
        warnings.warn(f"{start_error_messege} Is not a Dict" )
        return False
    
    if "key_type" not in value:
        warnings.warn(f"{start_error_messege} \"value_type\" param is missing" )
        return False
    
    
    if "value_type" not in value:
        warnings.warn(f"{start_error_messege} \"value_type\" param is missing" )
        return False   
      
    if not check_type_proto(value["value_type"],f"{start_error_messege} \"value_type\" param has a wrong format {LINE_WITH_TAB}",element_id=f"{element_id}-Map"):
        return False
    
    try:
        int(value["key_type"])
    except Exception:
        warnings.warn(f"{start_error_messege} \"key_type\" must be a int value referencing a Tensor.DataType" )
        return False
    enum = check_tensor_data_type(value["key_type"])
    if enum not in [DataType.INT8,DataType.INT16,DataType.INT32,DataType.INT64,
                    DataType.UINT8,DataType.UINT16,DataType.UINT32,DataType.UINT64,DataType.STRING]:
        warnings.warn(f"{start_error_messege} \"key_type\" can only be of DataType ([U]INT{{8|16|32|64}}) or STRING" )
        return False
    label = get_label_data_type(enum)
    value["key_type"]={"prefLabel":enum.name,"altLabel":enum.value,"rdfLabel":label}
    remove_extra_params(value,keep_params=["key_type","value_type"],start_error_messege=start_error_messege)
    return True

def check_optional_type(value,start_error_messege:str="",element_id=""):
    if not isinstance(value,dict):
        warnings.warn(f"{start_error_messege} Is not a Dict" )
        return False
    if not check_type_proto(value["elem_type"],f"{start_error_messege} \"elem_type\" param has a wrong format {LINE_WITH_TAB}",element_id=f"{element_id}-Opt"):
            return False
    remove_extra_params(value,keep_params=["elem_type"],start_error_messege=start_error_messege)
    return True