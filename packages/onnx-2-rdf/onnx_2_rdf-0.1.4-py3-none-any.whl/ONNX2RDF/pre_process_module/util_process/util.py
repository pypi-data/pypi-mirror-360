from warnings_thread_safe import warnings 

LINE_WITH_TAB="\n\t-> "

DOUBLE_LINE_WITH_TAB="\n\t\t- "

def create_unique_names(already_names,base_name):
    test_name=base_name
    
    idx=1
    while(test_name in already_names):
        test_name=f"{base_name}_{idx}"
        idx=idx+1
    #test_name is new_name, base_name was the first name to try (original name)    
    return test_name

def remove_extra_params(entry:dict,keep_params:list[str],start_error_messege:str=""):
    keys=entry.keys()
    remove_keys=[]
    for key in keys:
        if key not in keep_params:
            remove_keys.append(key)
    accumulate_error = f"{start_error_messege} has extra invalid params {DOUBLE_LINE_WITH_TAB}"
    
    for idx,key in enumerate(remove_keys):
        accumulate_error = f"{accumulate_error} The ({key}) is not a valid parameter. Being removed "
        if idx <len(remove_keys)-1:
            accumulate_error = f"{accumulate_error}{DOUBLE_LINE_WITH_TAB}"
        
        entry.pop(key)
    if remove_keys!=[]:
        warnings.warn(accumulate_error)
        
        
def is_number(s:str):
    try:
        int(s)
        return True
    except ValueError:
        return False
from enum import Enum

def validate_enum(data_type,enum_class:Enum):
    
    if not isinstance(data_type,str) and not isinstance(data_type,int):
        return None

    enum_code = None
    enum_label = None

    if (isinstance(data_type,int) or isinstance(data_type,str) and is_number(data_type)) :
        enum_code=int(data_type)
        
    
    if (isinstance(data_type,str) and enum_code==None) :
        enum_label = data_type
        
        
    if enum_code and int(enum_code) not in enum_class._value2member_map_:
        return None
    elif enum_code:
        return enum_class._value2member_map_[enum_code]

    if enum_label and enum_label not in enum_class._member_names_:
        return None    
    elif enum_label:
        return enum_class[enum_label]
    return None

class LocationType(Enum):
    DEFAULT = 0
    EXTERNAL = 1        
def get_location_label(type:LocationType):
    return "Location"+type.name[0].upper()+type.name[1:].lower()
    
   
class OperatorStatus(Enum):
    EXPERIMENTAL = 0
    STABLE = 1        
    
def get_operator_status_label(type:OperatorStatus):
    return "Status"+type.name[0].upper()+type.name[1:].lower()


def treat_special_chars(input:str):
    treated_result = input.replace("/", "//")
    return treated_result




from warnings_thread_safe import warnings 
import threading

# Custom warning class that includes thread name
class ThreadWarning(UserWarning):
    def __init__(self, message):
        thread_name = threading.current_thread().name
        super().__init__(message)
        self.thread_name = thread_name

# Replacement for warnings.warn
def warn(message, category=None, stacklevel=1, source=None):
    # Wrap the message in ThreadWarning
    if category is None:
        category = ThreadWarning
    # If message is a string, convert to warning object with thread info
    if isinstance(message, str):
        message = ThreadWarning(message)
    warnings.warn(message, category=category, stacklevel=stacklevel+1, source=source)
    