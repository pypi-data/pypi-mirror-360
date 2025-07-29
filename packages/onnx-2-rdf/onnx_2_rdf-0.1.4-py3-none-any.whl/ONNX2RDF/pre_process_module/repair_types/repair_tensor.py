

from warnings_thread_safe import warnings 
from repair_dims import check_dims_simple,check_complex_dims,invalid_string_number

from repair_metadata_prop import check_metadata_entries
from pre_process_module.util_process.util import remove_extra_params,validate_enum,LINE_WITH_TAB,is_number

from util_process.util import LocationType,get_location_label


data_storage = ["uint64Data","doubleData","int64Data","int32Data","floatData","rawData","stringData"]



def check_sparse_complex(tensor,start_error_messege:str="",check_storage_data=False,tensor_id=None):
    
    
    try:
        tmp_name = tensor["values"]["name"]
        tensor_id = f"{tensor_id}-{tmp_name}"
        
    except Exception:
        pass
    
    
    
    
    check=True
    
    
    if "indices" in tensor:

        check = check_tensor_complex(tensor,start_error_messege=f"{start_error_messege} Sparse Initializer (indices) has a wrong format {LINE_WITH_TAB}",check_storage_data=check_storage_data,tensor_id=f"{tensor_id}-indices",omit_name=True)
        
    if check and "values" in tensor:
        if "name" not in tensor["values"]:
            warnings.warn(f"{start_error_messege} \"values\" param needs to have a tensor with \"name\" param")
            return False,None
        check = check_tensor_complex(tensor,start_error_messege=f"{start_error_messege} Sparse Initializer (values) has a wrong format {LINE_WITH_TAB}",check_storage_data=check_storage_data,tensor_id=f"{tensor_id}-values",omit_name=True)
        
    
    if "dims" not in tensor:
        tensor["dims"]=[]
        warnings.warn(f"\n{start_error_messege} \"dims\" param is missing")
    else:
        tensor["shape"]=[]
        
        if not isinstance(tensor["dims"],list):
            return False,None
        for pos,item in enumerate(tensor["dims"]):
            if invalid_string_number(item):
                warnings.warn(f"\n{start_error_messege} \"dim\" entry at pos {pos} is not a integer")
                return False,None
            shape = {"dimValue":int(item),"index":pos+1,"tensor_id":tensor_id}
            if pos < len(tensor["dims"])-1:
               shape["next_index"]=pos+2
            if pos == len(tensor["dims"])-1:
               shape["last_index"]=""
            tensor["shape"].append(shape)
        del tensor["dims"]
    if "values" not in tensor and "indices" not in tensor:
        warnings.warn(f"\n{start_error_messege} Values and indices are missing")
        return False,None
    
    
    
    
    
    
    remove_extra_params(tensor,["indices","dims","values"],start_error_messege)
    tensor["is_sparse"]=""
    tensor["tensor_id"]=tensor_id
    return True

def check_tensor_complex(tensor,start_error_messege:str="Initializer",check_storage_data=False,tensor_id=None,omit_name=False):
    if not isinstance(tensor,dict):
        
        warnings.warn(f"\n{start_error_messege} Tensor is (it is not a dictionary) -> Tensor its deleted")
        
        return False
    correct=True
    
   
    
    
    
    
    if "dims" in tensor :
         
        if "name" in tensor and not isinstance(tensor["name"],str):
            
            warnings.warn(f"\n{start_error_messege}  Tensor \"name\" param is not a string (sequence of characters)")
            if not omit_name:
                tensor_id = f"{tensor_id}-{tensor["name"]}"
            correct= False
            
        
           
        error = check_dims_simple(tensor["dims"],f"{start_error_messege} Tensor \"dims\" param has a wrong format {LINE_WITH_TAB}",tensor_id=tensor_id)    
        
        if error!=None:
           
            warnings.warn(f"{start_error_messege} error")
            correct= False    
        else:
            dims = tensor["dims"]
            del tensor["dims"]
            tensor["shape"]=dims
            tensor["is_shape"]=""
             
    
        
    if "dataLocation" not in tensor:
        label = get_location_label(LocationType.DEFAULT)
        tensor["dataLocation"] = {"prefLabel":"DEFAULT","altLabel":0,"rdfLabel":label}
        location_type=LocationType.DEFAULT
    else:
        new_entry,location_type = get_correct_data_location(tensor["dataLocation"])
        if new_entry==None:
            warnings.warn(f"\n{start_error_messege} The \"dataLocation\" param is not a valid Location Type")
            correct= False
        else:
           tensor["dataLocation"]=new_entry 
        
    if "dataType" not in tensor:
        
        warnings.warn(f"\n{start_error_messege} Tensor \"dataType\" param is missing")
        
        correct= False
    else:
        enum = check_tensor_data_type(tensor["dataType"])   
        if enum==None:
            warnings.warn(f"\n{start_error_messege} Tensor \"dataType\" param is not a valid DataType")
            correct= False
        else:
            label = get_label_data_type(enum)
            tensor["dataType"]={"prefLabel":enum.name,"altLabel":enum.value,"rdfLabel":label}
            storage_check = validate_data_type_with_storage(enum,tensor,check_storage_data,location_type==LocationType.EXTERNAL,
                                                            f"{start_error_messege} Tensor \"dataType\" param has a incorrect_storage variable {LINE_WITH_TAB}") 
            correct = correct and storage_check
            
      
    if "segment" in tensor:
        check = check_segment(tensor["segment"],start_error_messege=start_error_messege)
        if not check:
            correct=False
        else:
            tensor["segment"]["tensor_id"]=tensor_id
            tensor["is_segment"]=""
        
    
    if "metadataProps" in tensor:
        check,_ = check_metadata_entries(tensor["metadataProps"],start_error_messege=f"{start_error_messege} Tensor \"metadata_prop\" param has a wrong format {LINE_WITH_TAB}",keys=[],element_id=tensor_id)    
        if not check:
            tensor["metadataProps"]=[]
    
    if "externalData" in tensor:
        _,external_correct = check_metadata_entries(tensor["externalData"],start_error_messege=f"{start_error_messege} Tensor \"externalData\" param has a wrong format {LINE_WITH_TAB}",element_id=tensor_id,uri_id="external") 
        correct = correct and external_correct
        
    if "docString" in tensor and not isinstance(tensor["docString"],str):
        
        warnings.warn(f"\n{start_error_messege} The \"docString\" is not a string -> Deleting \"docString\"")

    if correct:
        params = ["externalData","dataLocation","dataType","name","shape","segment","docString","metadataProps","tensor_id","storage_type","value","is_shape","is_segment"]
        params.extend(data_storage)
        
        remove_extra_params(tensor,params,start_error_messege=f"{start_error_messege} The tensor ")
    tensor["is_tensor"]=""   
    tensor["tensor_id"]=tensor_id
    
    
    
     
    return correct



def check_segment(segment,start_error_messege=""):
    correct=True
    if not isinstance(segment,dict):
        warnings.warn(f"{start_error_messege} The \"segment\" param is not a dict")
        return False
    if "begin" not in segment:
        warnings.warn(f"{start_error_messege} The \"segment\" param is missing the \"begin\" param")
        correct=False
    elif invalid_string_number(segment["begin"]):  
        warnings.warn(f"{start_error_messege} The \"segment\" param its \"begin\" param is not a integer")
        correct=False
    elif isinstance(segment["begin"],str):
        segment["begin"]=int(segment["begin"])
        
        
    if "end" not in segment:
        warnings.warn(f"{start_error_messege} The \"segment\" param is missing the \"end\" param")
        correct=False
    elif invalid_string_number(segment["end"]):  
        warnings.warn(f"{start_error_messege} The \"segment\" param its \"end\" param is not a integer")
        correct=False
    elif isinstance(segment["end"],str):
        segment["end"]=int(segment["end"])
    return correct    


def get_correct_data_location(entry):
    label_ext= get_location_label(LocationType.EXTERNAL)
    external = {"prefLabel":"EXTERNAL","altLabel":1,"rdfLabel":label_ext}
    label_def = get_location_label(LocationType.DEFAULT)
    default = {"prefLabel":"DEFAULT","altLabel":0,"rdfLabel":label_def}
    
    
    if isinstance(entry,str) and is_number(entry) or isinstance(entry,int):
        if int(entry)==0:
            return default,LocationType.DEFAULT
        if int(entry)==1:
           return external,LocationType.EXTERNAL 
        return None
    if isinstance(entry,str):
        
        if entry=="DEFAULT":
            return default,LocationType.DEFAULT
        if entry=="EXTERNAL":
            return external,LocationType.EXTERNAL
    
    return None



def check_tensor_simple(tensor,start_error_messege:str="",tensor_id=""):
    
   
    
    if not isinstance(tensor,dict):
        
        warnings.warn(f"\n{start_error_messege} Tensor is not a dict -> Tensor its deleted")
        
        return False
    correct=True
    if "elemType" not in tensor:
        
        warnings.warn(f"\n{start_error_messege} Tensor \"elemType\" param is missing")
        
        correct= False
    else:
        enum = check_tensor_data_type(tensor["elemType"])   
        if enum==None:
            
            warnings.warn(f"\n{start_error_messege} Tensor \"elemType\" param is not a valid DataType")
            
            correct= False
        elif enum==DataType.UNDEFINED:   
            warnings.warn(f"\n{start_error_messege} Tensor \"elemType\" param cannot be \"UNDEFINED\" or \"0\" for a TypeProto entry ")
            correct= False    
        else:
            del tensor["elemType"]
            label = get_label_data_type(enum)
            tensor["dataType"]={"prefLabel":enum.name,"altLabel":enum.value,"rdfLabel":label}
            
    if "shape" in tensor :
        error,dim_present = check_complex_dims(tensor["shape"],f"{start_error_messege} Tensor \"shape\" param has a wrong format {LINE_WITH_TAB}",tensor_id=tensor_id)  
        tensor["is_shape"]=""
        if error!=None:
            warnings.warn("\n"+error)
            correct= False    
        elif dim_present:
            tensor["shape"]=tensor["shape"]["dim"]
        else:
            del tensor["shape"]
    if correct:
        remove_extra_params(tensor,["dataType","shape","is_shape"],start_error_messege=f"{start_error_messege} The tensor ")
    tensor["tensor_id"]=tensor_id    
    return correct
from enum import Enum

class DataType(Enum):
    UNDEFINED = 0
    # Basic types.
    FLOAT = 1        # float
    UINT8 = 2        # uint8_t
    INT8 = 3         # int8_t
    UINT16 = 4       # uint16_t
    INT16 = 5        # int16_t
    INT32 = 6        # int32_t
    INT64 = 7        # int64_t
    STRING = 8       # string
    BOOL = 9         # bool

    # IEEE754 half-precision floating-point format (16 bits wide).
    # This format has 1 sign bit, 5 exponent bits, and 10 mantissa bits.
    FLOAT16 = 10

    DOUBLE = 11
    UINT32 = 12
    UINT64 = 13
    COMPLEX64 = 14   # complex with float32 real and imaginary components
    COMPLEX128 = 15  # complex with float64 real and imaginary components

    # Non-IEEE floating-point format based on IEEE754 single-precision
    # floating-point number truncated to 16 bits.
    # This format has 1 sign bit, 8 exponent bits, and 7 mantissa bits.
    BFLOAT16 = 16

    # Non-IEEE floating-point format based on papers
    # FP8 Formats for Deep Learning, https://arxiv.org/abs/2209.05433,
    # 8-bit Numerical Formats For Deep Neural Networks, https://arxiv.org/pdf/2206.02915.pdf.
    # Operators supported FP8 are Cast, CastLike, QuantizeLinear, DequantizeLinear.
    # The computation usually happens inside a block quantize / dequantize
    # fused by the runtime.
    FLOAT8E4M3FN = 17   # float 8, mostly used for coefficients, supports nan, not inf
    FLOAT8E4M3FNUZ = 18 # float 8, mostly used for coefficients, supports nan, not inf, no negative zero
    FLOAT8E5M2 = 19     # follows IEEE 754, supports nan, inf, mostly used for gradients
    FLOAT8E5M2FNUZ = 20 # follows IEEE 754, supports nan, not inf, mostly used for gradients, no negative zero

    # 4-bit data-types
    UINT4 = 21  # Unsigned integer in range [0, 15]
    INT4 = 22
    FLOAT4E2M1 = 23
    
    
FLOAT_TYPES=[DataType.BFLOAT16,DataType.DOUBLE,DataType.FLOAT,DataType.FLOAT16,DataType.FLOAT8E4M3FN,DataType.FLOAT8E4M3FNUZ,DataType.FLOAT8E5M2FNUZ,DataType.FLOAT8E5M2,DataType.BFLOAT16,DataType.FLOAT4E2M1]
INT_TYPES = [DataType.INT4,DataType.INT8,DataType.INT16,DataType.INT32,DataType.INT64]
UINT_TYPES = [DataType.UINT4,DataType.UINT8,DataType.UINT16,DataType.UINT16,DataType.UINT64]
COMPLEX_TYPES=[DataType.COMPLEX64,DataType.COMPLEX128]


INT_32_TYPES = [DataType.INT32, DataType.INT16, DataType.INT8, DataType.INT4, DataType.UINT16, DataType.UINT8, 
                DataType.UINT4, DataType.BOOL, DataType.FLOAT16, DataType.BFLOAT16, DataType.FLOAT8E4M3FN, 
                DataType.FLOAT8E4M3FNUZ, DataType.FLOAT8E5M2, DataType.FLOAT8E5M2FNUZ,DataType.FLOAT4E2M1]

LABELS_DATA={DataType.FLOAT,DataType.UNDEFINED,DataType.BOOL,DataType.DOUBLE,DataType.STRING}

FLOAT4E2M1_VALUES = {
    0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0,
   -0.0, -0.5, -1.0, -1.5, -2.0, -3.0, -4.0, -6.0
}

ONE_ELEMENT = FLOAT_TYPES.copy()
ONE_ELEMENT.extend(INT_TYPES)
ONE_ELEMENT.extend(UINT_TYPES)
ONE_ELEMENT.extend([DataType.STRING,DataType.BOOL])

def check_tensor_data_type(data_type):
    enum = validate_enum(data_type,DataType)
    return enum



def get_label_data_type(data_type:DataType):
    
    if data_type in UINT_TYPES or data_type==DataType.BFLOAT16:
        return data_type.name[0].upper() +data_type.name[1].upper()+ data_type.name[2:].lower()
    if data_type in LABELS_DATA:
        return "Data" +data_type.name[0].upper()+ data_type.name[1:].lower()
        
    return data_type.name[0].upper() + data_type.name[1:].lower()

def get_storage_value(tensor,start_error_messege:str=""):
    tensor_type=None
   
    for storage_type in data_storage:
        if storage_type in tensor  and tensor_type==None:
            tensor_type=storage_type
        elif storage_type in tensor:
            warnings.warn(f"{start_error_messege} There cannot be two different storage parms at the time ({tensor_type}) and ({storage_type})")
            return None,True
    return tensor_type,False    

def change_upper_by_underscore(storage:str):
    result = []
    
    for i, char in enumerate(storage):
        if char.isupper() and i != 0:
            result.append('_')
            result.append(char.lower())
        else:
            result.append(char)
    
    return ''.join(result)


def validate_data_type_with_storage(data_type:DataType,tensor,check_storage_data=False,is_external=False,start_error_messege:str=""):
    
    correct=True
    storage,repeat = get_storage_value(tensor)
    if repeat:
        return False
    default_error = f"\n{start_error_messege} The storage in tensor is {storage} but the type (\"{data_type.name}\") is not valid for that storage"
    missing_error = f"\n{start_error_messege} The storage in tensor is missing"
    
    if "rawData" == storage and (data_type == DataType.UNDEFINED or data_type==DataType.STRING) :
        warnings.warn(default_error)
        return False 
    
    if "floatData" == storage and data_type not in [DataType.FLOAT,DataType.COMPLEX64]:
        warnings.warn(default_error)
        return False
      
    if "int32Data" == storage and data_type not in INT_32_TYPES:
        warnings.warn(default_error)
        return False    
        
    if "stringData"== storage and data_type != DataType.STRING:
        warnings.warn(default_error)
        return False    
    if "int64Data" == storage and data_type != DataType.INT64:
        warnings.warn(default_error)
        return False    
    if "doubleData"== storage and data_type not in [DataType.COMPLEX128,DataType.DOUBLE]:
        warnings.warn(default_error)
        return False    
    if "uint64Data"== storage and data_type not in [DataType.UINT32,DataType.UINT64]:
        warnings.warn(default_error)
        return False
    
    if storage!=None:
        tensor["storage_type"]=change_upper_by_underscore(storage)
           
    
    if check_storage_data:
        
        if storage==None:
            if "name" in tensor and tensor["name"]=="const_tensor" or is_external:
                return True
            warnings.warn(missing_error)
            return False
       
        correct = validate_data_type_with_storage_with_data(data_type,tensor,storage,start_error_messege)
        tensor["value"]=tensor[storage]
        del tensor[storage]
            
    else:
        tensor["value"]=""
        if storage!=None:
            del tensor[storage]
    return correct




def validate_float(data_type:DataType,values:list,default_error,size_error):
    
    
    for value in enumerate(values):
        if isinstance(value,list):
            validate_float(data_type,value,default_error,size_error)
        try:
            for idx,value in enumerate(values):
                type_value = float(value)
        except Exception:
            warnings.warn(default_error)
            return False
        if not check_float_size(type_value,data_type):
            warnings.warn(size_error)
            return False
    return True

def validate_int(data_type:DataType,values:list,default_error,size_error):
    
    
    for value in enumerate(values):
        if isinstance(value,list):
            validate_int(data_type,value,default_error,size_error)
        try:
            for idx,value in enumerate(values):
                int_value = int(value)
        except Exception:
            warnings.warn(default_error)
            return False
        if data_type in INT_TYPES and not check_int_size(int_value,data_type):
            warnings.warn(size_error)
            return False
        if data_type in UINT_TYPES and not check_uint_size(int_value,data_type):
            warnings.warn(size_error)
            return False
    return True

def validate_generic(data_type:DataType,values:list,func,default_error):
    
    
    for value in enumerate(values):
        if isinstance(value,list):
            validate_generic(data_type,value,func,default_error)
        try:
            correct = func(data_type,value)
        except Exception:
            warnings.warn(default_error)
            return False
        if not correct:
            warnings.warn(default_error)
            return False
    return True
            
        


def validate_data_type_with_storage_with_data(data_type:DataType,tensor,storage:str,start_error_messege:str=""):
    #TODO: check types compatiblity (raw_data,shapes correctly,complex_types)
    default_error =  f"\n{start_error_messege} The type in tensor is {data_type.name} but the value at the storage \"{storage}\" is invalid for the type {data_type.name}"
    list_error =  f"\n{start_error_messege} The type in tensor is {data_type.name} but one of the values at the storage \"{storage}\" is invalid for the type {data_type.name}"
    size_error =  f"\n{start_error_messege} The type in tensor is {data_type.name} but the value at the storage \"{storage}\" has a incorrect size for the type {data_type.name}"
    size_error_list =  f"\n{start_error_messege} The type in tensor is {data_type.name} but one of the values at the storage \"{storage}\" has a incorrect size for the type {data_type.name}"
    
   
    if storage=="rawData":
        #TODO: more complex checking
        return True
   

    if not isinstance(tensor[storage],list):
        values = [tensor[storage]]
        is_list=False
        
    else:
        values = tensor[storage]
        
        is_list=True
        
    if data_type in FLOAT_TYPES:
        if is_list:
            return validate_float(data_type,values,list_error,size_error_list)
        else:
            return validate_float(data_type,values,default_error,size_error)
        
  
    if data_type in INT_TYPES or data_type in UINT_TYPES:
        if is_list:
            return validate_int(data_type,values,list_error,size_error_list)
        else:
            return validate_int(data_type,values,default_error,size_error)
        
    if data_type == DataType.STRING:
        def validate_str(_,value):
            return not isinstance(value,str)
        if is_list:
            return validate_generic(data_type,values,validate_str,list_error)
        else:
            return validate_generic(data_type,values,validate_str,default_error)


    
    if data_type == DataType.BOOL:
        
        warnings.warn(default_error)
        def validate_bool(_,value):
            if isinstance(value,bool) or isinstance(value,int) and (value==0 or value==1) :
                return True
            return False
        if is_list:
            return validate_generic(data_type,values,validate_bool,list_error)
        else:
            return validate_generic(data_type,values,validate_bool,default_error)
   
    if data_type in COMPLEX_TYPES:
        #TODO check complex_types
        return True 
    
    
    raise RuntimeError(f"\n{start_error_messege} The type in tensor is {data_type.name} but is not being processed UNEXPECTED ERROR")
    
import numpy as np

def check_int_size(value:int,type:DataType):
    

    if type == DataType.INT4:
        return -8 <= value <= 7
    if type == DataType.INT8:
        return np.iinfo(np.int8).min <= value <= np.iinfo(np.int8).max
    elif type == DataType.INT16:
        return np.iinfo(np.int16).min <= value <= np.iinfo(np.int16).max
    elif type == DataType.INT32:
        return np.iinfo(np.int32).min <= value <= np.iinfo(np.int32).max
    elif type == DataType.INT64:
        return np.iinfo(np.int64).min <= value <= np.iinfo(np.int64).max
    else:
        return False  
    
def check_uint_size(value: int, type: DataType) -> bool:
    if type == DataType.UINT4:
        return 0 <= value <= 15
    elif type == DataType.UINT8:
        return np.iinfo(np.uint8).min <= value <= np.iinfo(np.uint8).max
    elif type == DataType.UINT16:
        return np.iinfo(np.uint16).min <= value <= np.iinfo(np.uint16).max
    elif type == DataType.UINT32:
        return np.iinfo(np.uint32).min <= value <= np.iinfo(np.uint32).max
    elif type == DataType.UINT64:
        return np.iinfo(np.uint64).min <= value <= np.iinfo(np.uint64).max
    else:
        return False
import math
def is_valid_bfloat16(value):
    try:
        f = float(value)
        return math.isfinite(f) and abs(f) <= 3.38953139e+38
    except (ValueError, TypeError):
        return False

def check_float_size(value: float, type: DataType) -> bool:
    if type == DataType.BFLOAT16:
        return is_valid_bfloat16(value)
    elif type == DataType.DOUBLE:
        return np.finfo(np.float64).min <= value <= np.finfo(np.float64).max
    elif type == DataType.FLOAT:
        return np.finfo(np.float32).min <= value <= np.finfo(np.float32).max
    elif type == DataType.FLOAT16:
        return np.finfo(np.float16).min <= value <= np.finfo(np.float16).max
    elif type == DataType.FLOAT8E4M3FN:
        return -128 <= value <= 127 or np.isnan(value)
    elif type == DataType.FLOAT8E4M3FNUZ:
        if value == -0:
            return False  
        return -128 <= value <= 127 or np.isnan(value)
    elif type == DataType.FLOAT8E5M2:
        return np.finfo(np.float32).min <= value <= np.finfo(np.float32).max or np.isnan(value) or np.isinf(value)
    elif type == DataType.FLOAT8E5M2FNUZ:
        if np.isinf(value):
            return False 
        return np.finfo(np.float32).min <= value <= np.finfo(np.float32).max or np.isnan(value)
    elif type == DataType.FLOAT4E2M1:
        return value in FLOAT4E2M1_VALUES

    return False



def is_valid_float4e2m1(value: float) -> bool:
    return value in FLOAT4E2M1_VALUES
    
    
def check_list_data_type(tensor,type:DataType,storage_param:str,is_list:bool,start_error_messege:str=""):    
    if is_list and not isinstance(tensor[storage_param],list):
        warnings.warn(f"\n{start_error_messege} The storage in tensor is {type.name} but in the storage {storage_param} param the value is not a list ")
        return False
    if not is_list and isinstance(tensor[storage_param],list) and len(is_list)>0:
        warnings.warn(f"\n{start_error_messege} The storage in tensor is {type.name} but in the storage {storage_param} param the value is a list with more than one element ")    
        return False
    return True


   
 