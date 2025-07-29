




from pre_process_module.util_process.util import remove_extra_params,is_number   
    
def invalid_string_number(value):
    return isinstance(value,str) and not is_number(value) or (not isinstance(value,str) and not isinstance(value,int))

def check_dims_simple(dims,start_error_messege:str="",tensor_id=None):
    
    

    if not isinstance(dims,list):
        error_messege=f"{start_error_messege} The \"dims\" param is not a list"
        
        return error_messege
    
    len_dims = len(dims)
    for idx,dim in enumerate(dims):
        if invalid_string_number(dim):
            error_messege=f"{start_error_messege} The dim at pos {idx} of \"dims\" param is not a number"
            return error_messege
        dims[idx]= {"dimValue":int(dim),"index":idx+1,"last_index":"","next_index":idx+2}
        if tensor_id!=None and isinstance(tensor_id,str):
            dims[idx]["tensor_id"]=tensor_id

    return None


def check_complex_dim(dim,start_error_messege):
   

    if not isinstance(dim,dict):
        error_messege=f"{start_error_messege} not a dict"
        return error_messege
    
    if "dimParam" in dim and "dimValue" in dim:
        error_messege=f"{start_error_messege} has both dimParam and dimValue, only one"
        return error_messege

    if "dimParam" in dim and not isinstance(dim["dimParam"],str):
        error_messege=f"{start_error_messege} dimParam only accepts string values"
        return error_messege

    if "dimValue" in dim and invalid_string_number(dim["dimValue"]):
        error_messege=f"{start_error_messege} dimValue is not a valid number"
        return error_messege
    if "dimValue" in dim and isinstance(dim["dimValue"],str):
        dim["dimValue"]=int(dim["dimValue"])

    
    remove_extra_params(dim,keep_params=["dimParam","dimValue"],start_error_messege=start_error_messege)
    return None


def check_complex_dims(shape,start_error_messege:str="",tensor_id=None):
    
    if start_error_messege==None:
        start_error_messege:str=""
    
    if not isinstance(shape,dict):
        error_messege=f"{start_error_messege} The \"shape\" param is not a dict"
        return error_messege,False
    if "dim" not in shape:
        error_messege=f"{start_error_messege} The \"dim\" param is not in the \"shape\" param"
        #shape can be empty
        return None,False
    if not isinstance(shape["dim"],list):
        error_messege=f"{start_error_messege} The \"dim\" param in \"shape\" param is not a list"
        return error_messege,False
    
    remove_extra_params(shape,keep_params=["dim"],start_error_messege=start_error_messege)
    
    len_dims = len(shape["dim"])
    for idx,dim in enumerate(shape["dim"]):
        
        error_messege = check_complex_dim(dim,f"{start_error_messege} The dim at pos {idx} of \"dims\" param in \"shape\" param")
        if error_messege!=None:
            return error_messege,False

        shape["dim"][idx]["index"]= idx+1
        shape["dim"][idx]["last_index"]= ""
        shape["dim"][idx]["next_index"]= idx+2
        if tensor_id!=None and isinstance(tensor_id,str):
            shape["dim"][idx]["tensor_id"]=tensor_id

    return None,True
    



