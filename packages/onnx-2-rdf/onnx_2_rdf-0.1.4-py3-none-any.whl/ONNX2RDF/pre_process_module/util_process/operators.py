
from onnx import defs

import onnxruntime.capi.onnxruntime_pybind11_state as rtpy
from onnx.defs import  OpSchema
from . import ONNX_DOMAIN



OPERATORS: dict[str, OpSchema] = dict()
ONNX_RUNTIME_OP: dict[str, OpSchema] = dict()
DOMAINS = []
ONNX_PREDEFINED_DOMAINS=[defs.ONNX_DOMAIN,defs.ONNX_ML_DOMAIN,defs.AI_ONNX_PREVIEW_TRAINING_DOMAIN]
MICROSOFT_COM_DOMAINS = ["com.microsoft","com.microsoft.experimental","com.microsoft.nchwc"]
ONNX_PREDEFINED_DOMAINS.extend(MICROSOFT_COM_DOMAINS)



DOMAINS_VERSION_ONE=[defs.AI_ONNX_PREVIEW_TRAINING_DOMAIN]
DOMAINS_VERSION_ONE.extend(MICROSOFT_COM_DOMAINS)


DEPRACTED: dict[str, OpSchema] = dict()
from .data import __dynamic_dict_find__



from util_process.util import OperatorStatus,get_operator_status_label



def get_operator_url(domain,name):
  is_runtime = is_onnx_runtime(domain,name)
  
  if is_domain_ONNX(domain) and not is_runtime:
    return f"https://onnx.ai/onnx/operators/onnx_{domain}_{name}.html"
  
  elif is_runtime:
    if domain in MICROSOFT_COM_DOMAINS:
      return f"https://github.com/microsoft/onnxruntime/blob/main/docs/ContribOperators.md#{domain}.{name}"
    return None
  else:
    return None


# is the domain,name,version introduced by runtime
def is_onnx_runtime(domain,name=None,version=None):
  list_op = find_operators(name,domain,version)
  if len(list_op)==0:
    return False
  
  if domain and name==None and is_domain_ONNX(domain):
    return False
  list_run = find_operators(name,domain,version,ONNX_RUNTIME_OP)
  if len(list_run) ==0:
    return False
  # los operadores definidos por runtime solo se añaden si no se han añadido en onnx normal
  return True


def get_key_operator(domain,name,version):
  return f"\"{domain}\".\"{name}\".\"{version}\""


def get_correct_status(label):
  if label=="COMMON" or label=="STABLE":
    new_label="STABLE"
    label_code=1
  else:
    new_label="EXPERIMENTAL"
    label_code=0
  label = get_operator_status_label(OperatorStatus[new_label])
  return{"prefLabel":new_label,"altLabel":label_code,"rdfLabel":label}


for schema in defs.get_all_schemas_with_history():
  key = get_key_operator(schema.domain,schema.name,schema.since_version)
  if key not in OPERATORS.keys():
    if schema.deprecated:
      DEPRACTED[get_key_operator(schema.domain,schema.name,schema.since_version)]=schema
    OPERATORS[get_key_operator(schema.domain,schema.name,schema.since_version)]=schema
  if schema.domain not in DOMAINS:
      DOMAINS.append(schema.domain)
      
for schema in rtpy.get_all_operator_schema():
  key = get_key_operator(schema.domain,schema.name,schema.since_version)
  if key not in OPERATORS.keys():
    if schema.deprecated:
      DEPRACTED[get_key_operator(schema.domain,schema.name,schema.since_version)]=schema
    OPERATORS[get_key_operator(schema.domain,schema.name,schema.since_version)]=schema
    ONNX_RUNTIME_OP[get_key_operator(schema.domain,schema.name,schema.since_version)]=schema
  if schema.domain not in DOMAINS:
      DOMAINS.append(schema.domain)



def is_deprecated(domain,name,version):
    return get_key_operator(domain,name,version) in DEPRACTED.keys()


def is_domain_ONNX(domain:str):
    """
    The function `is_domain_ONNX` checks if a given domain is in the predefined ONNX domains.
    
    Args:
      domain (str): The `is_domain_ONNX` function is checking if a given domain is in the
    `ONNX_PREDEFINED_DOMAINS` list. The function takes a `domain` parameter of type string and returns a
    boolean value indicating whether the domain is in the predefined list of domains for ONNX.
    
    Returns:
      The function `is_domain_ONNX` is checking if the input `domain` is in the list of predefined
    domains `ONNX_PREDEFINED_DOMAINS` and returning a boolean value based on that check.
    """
    return domain in ONNX_PREDEFINED_DOMAINS

def is_register_domain(domain:str):
    """
    The function `is_register_domain` checks if a given domain is in a predefined list of domains.
    
    Args:
      domain (str): The `is_register_domain` function takes a domain name as input and checks if it is
    in the `DOMAINS` list. If the domain is found in the list, the function will return `True`,
    indicating that the domain is a registered domain. If the domain is not in the list,
    
    Returns:
      The function `is_register_domain` is returning a boolean value indicating whether the input domain
    is in the `DOMAINS` list.
    """
    
    return domain in DOMAINS

def get_domain_ONNX_version(domain:str):
    """
    This function returns the ONNX opset version based on the input domain.
    
    Args:
      domain (str): The function `get_domain_ONNX_version` takes a `domain` parameter as input. The
    function checks the value of the `domain` parameter and returns the corresponding ONNX version based
    on the domain provided. The possible values for the `domain` parameter are `defs.ONNX_DOMAIN`, `defs
    
    Returns:
      The function `get_domain_ONNX_version` returns the ONNX opset version based on the input domain
    provided. If the domain is `defs.ONNX_DOMAIN`, it returns the ONNX opset version. If the domain is
    `defs.ONNX_ML_DOMAIN`, it returns the ONNX-ML opset version. If the domain is
    `defs.AI_ONNX_PREVIEW_TRAINING_DOMAIN`, it
    """
    if domain == defs.ONNX_DOMAIN:
       return  defs.onnx_opset_version()
    if domain == defs.ONNX_ML_DOMAIN:
       return  defs.onnx_ml_opset_version()
    if domain in DOMAINS_VERSION_ONE:
       return  1
    
   

def is_opertor_list_func_type(operators:dict[str, OpSchema]=OPERATORS):
    """
    This function checks if a list of operators contains at least one valid operator function.
    
    Args:
      operators (list[OpSchema]): The `operators` parameter in the `is_opertor_list_func_type` function
    is expected to be a list of `OpSchema` objects. The function checks if the list is empty, if it
    contains only one element, or if any of the elements in the list are of type `Op
    
    Returns:
      The function `is_opertor_list_func_type` returns a tuple containing two values:
    1. A boolean value indicating whether there are any valid operators in the input list `operators`.
    2. A list of valid operators that were filtered from the input list.
    """
    if len(operators)==0:
        return False,[]
    if len(operators)==1:
        return is_operator_func(operators[0])
    filter_operators = []
    for operator in operators:
        if is_operator_func(operator):
            filter_operators.append(operator)
            
    return len(filter_operators)>0,filter_operators  
    
# busqueda dinamica en un diccionario con claves compuestas
def find_operators(name:str=None,domain:str=None,version:str=None,operator_list:dict[str, OpSchema]=OPERATORS):
    """
    The function `find_operators` searches for operators based on specified criteria such as name,
    domain, and version in a given list of operator schemas.
    
    Args:
      name (str): The `name` parameter is a string that represents the name of an operator. It is used
    to filter the list of operators based on the specified name. If provided, only operators with a
    matching name will be included in the result.
      domain (str): The `domain` parameter in the `find_operators` function is used to filter operators
    based on their domain. If you provide a value for the `domain` parameter, the function will only
    return operators that belong to that specific domain. If you don't provide a value for `domain`, the
      version (str): The `version` parameter in the `find_operators` function is used to filter the
    operators based on a specific version. If you provide a version value when calling the function, it
    will only return operators that match that version. If you don't provide a version value, it will
    not filter based
      operator_list (list[OpSchema]): The `operator_list` parameter in the `find_operators` function is
    expected to be a dictionary where the keys are strings in the format "domain.name.version" and the
    values are instances of `OpSchema`. The function iterates over this dictionary and filters out the
    operators based on the provided `
    
    Returns:
      The function `find_operators` returns a list of `OpSchema` objects that match the criteria
    specified by the `name`, `domain`, and `version` parameters.
    """
    if name!=None and domain!=None and version!=None:
      key = get_key_operator(domain,name,version)
      if key in operator_list.keys():
        return [operator_list[key]]
      else:
        return []
    return __dynamic_dict_find__(operator_list,3,[domain,name,version])
    


def is_operator_func(operator:OpSchema):
    """
    The function `is_operator_func` checks if an operator has a context-dependent function or a regular
    function.
    
    Args:
      operator (OpSchema): OpSchema - an object representing an operator in a computational graph, with
    attributes like has_context_dependent_function and has_function.
    
    Returns:
      The function `is_operator_func` is returning a boolean value based on the conditions provided. It
    checks if the input `operator` has either a context-dependent function or a regular function, and
    returns `True` if either condition is met, otherwise it returns `False`.
    """
    if not hasattr(operator,"has_context_dependent_function") or not hasattr(operator,"has_function"):
      return False

    return operator.has_context_dependent_function or operator.has_function
  
def is_operator_shape_inference(operator:OpSchema):
  '''The function `is_operator_shape_inference` checks if an operator has a type and shape inference
  function.
  
  Parameters
  ----------
  operator : OpSchema
    The function `is_operator_shape_inference` takes an input parameter `operator` of type `OpSchema`.
  The function checks if the `operator` has a type and shape inference function defined and returns a
  boolean value based on that check.
  
  Returns
  -------
    The function `is_operator_shape_inference` is checking if the input `operator` has a type and shape
  inference function. It returns a boolean value indicating whether the `operator` has a type and
  shape inference function (`True`) or not (`False`).
  
  '''
  return operator.has_type_and_shape_inference_function



# existe algun operator registrado con ese nombre/dominio/version  que su dominio sea ONNX
def is_onnx_operator(name:str=None,domain:str=None,version:str=None,operator_list:dict[str, OpSchema]=OPERATORS):
    """
    This function checks if an ONNX operator exists based on its name, domain, and version.
    
    Args:
      name (str): The `name` parameter in the `is_onnx_operator` function is used to specify the name of
    the ONNX operator you are checking for.
      domain (str): The `domain` parameter in the `is_onnx_operator` function is used to specify the
    domain of the ONNX operator. The ONNX specification organizes operators into different domains based
    on their functionality or area of application. By providing a domain value, you can filter the
    operators based on that specific
      version (str): The `version` parameter in the `is_onnx_operator` function is used to specify the
    version of the ONNX operator. This parameter allows you to filter operators based on their version
    numbers. If a specific version is provided, only operators with a version greater than or equal to
    the specified version will
      operator_list (list[OpSchema]): The `operator_list` parameter in the `is_onnx_operator` function
    is a list of `OpSchema` objects. These objects likely contain information about ONNX operators such
    as their name, domain, version, and other relevant details. The function uses this list to find and
    filter operators based on
    
    Returns:
      The function `is_onnx_operator` returns a tuple containing two elements:
    1. A boolean value indicating whether there are any ONNX operators that match the specified criteria
    (name, domain, version).
    2. A list of ONNX operators that match the specified criteria (if any), filtered based on the
    provided name, domain, and version.
    """
    
    
    
    if domain and (domain not in ONNX_DOMAIN):
        return False,[]
    
    operators = find_operators(name,domain,version,operator_list)
    if len(operators)==0:
        return False,[]
    filter_operators = []
    for operator in operators:
        if operator.domain in ONNX_DOMAIN and (domain==None or domain==operator.domain) and (version==None or version>=operator.since_version):
            filter_operators.append(operator)

    
    return len(filter_operators)>0,filter_operators



#devuelve si existe algun operator registrado con ese nombre/dominio/version y la lista de coincidencias
def is_register_operator(name:str=None,domain:str=None,version:str=None,operator_list:dict[str, OpSchema]=OPERATORS):
    """
    This function checks if a given operator is registered based on its name, domain, and version.
    
    Args:
      name (str): The `name` parameter in the `is_register_operator` function is a string that
    represents the name of the operator you want to check for registration.
      domain (str): The `domain` parameter in the `is_register_operator` function refers to the domain
    of the operator being checked. It is used to filter operators based on their domain.
      version (str): The `version` parameter in the `is_register_operator` function is used to specify
    the version of the operator. It is used to filter the operators based on their version number. If a
    version is provided, only operators with a version greater than or equal to the specified version
    will be considered in the
      operator_list (list[OpSchema]): The `operator_list` parameter in the `is_register_operator`
    function is a list of `OpSchema` objects. These objects likely represent different operators used in
    a system or application. The function is designed to check if a specific operator is registered
    based on the provided `name`, `domain`, and
    
    Returns:
      The function `is_register_operator` is returning a tuple containing two values. The first value is
    a boolean indicating whether there are any filtered operators that match the specified criteria, and
    the second value is a list of those filtered operators.
    """
    
    if domain and not is_register_domain(domain):
      return False,[]
    
    operators = find_operators(name,domain,version,operator_list)
    if len(operators)==0:
      return False,[]
    
    filter_operators = []
    for operator in operators:
        if (domain==None or domain==operator.domain) and (version==None or version>=operator.since_version):
            filter_operators.append(operator)
    
    
    return len(filter_operators)>0,filter_operators





