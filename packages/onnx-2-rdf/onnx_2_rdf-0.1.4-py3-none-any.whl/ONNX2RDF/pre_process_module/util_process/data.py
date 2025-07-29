from . import ONNX_DOMAIN

def get_opset_data(import_field:dict):
    
    versions={}
    
    
    for item in import_field:
        if "version" in item and "domain" in item:
            versions[opset_key(item["domain"],item["version"])]={"domain":item["domain"],"version":item["version"]}
            
        if "version" in item and "domain" not in item:
            versions[opset_key(ONNX_DOMAIN,item["version"])]={"domain":item["domain"],"version":item["version"]}
            import_field["domain"]=ONNX_DOMAIN 
              
    return versions








def get_functions_data(data):
    functions_data=dict()

    for function in data["functions"]:
        item = function
        functions_data[function_key(function["domain"],function["name"],function["overload"])] = item

    return functions_data

def function_data_find(func_data: dict, domain=None, name=None, overload=None):
    
    return __dynamic_dict_find__(func_data,3,[domain,name,overload])

def opset_data_find(import_data: dict, domain=None, version=None):
    
    
    return __dynamic_dict_find__(import_data,2,[domain,version])

def __dynamic_dict_find__(dict:dict,number_keys,key_values:list[str]):
    
    result = []
    
    
    # Iterar sobre las claves del diccionario
    for key in dict.keys():
        # Descomponer la clave en sus partes (domain, version)
        key_parts = [part.strip('"') for part in key.split('".')]
        
        # Verificar si la clave tiene el formato esperado
        if len(key_parts) != number_keys:
            continue
        
        ignore=False
       
        for idx,key_local in enumerate(key_parts):
            
            if (key_values[idx]!=None) and str(key_values[idx])!=str(key_local):
                ignore=True
        # Comprobar si la clave coincide con los parámetros dados
        
        if ignore:
            continue
        # Si la clave coincide con todos los criterios, agregar el valor al resultado
        result.append(dict[key])
    
    return result


def opset_key(domain,version):
    return __build_dynamic_key__([domain,version])
    
def function_key(domain,name,overload):
    return __build_dynamic_key__([domain,name,overload])


def get_opset_values(opset_data,key):
    return __get_values_dynamic__(opset_data,["domain","name","version"],key)

def get_func_values(func_data,key):
    return __get_values_dynamic__(func_data,["domain","name","overload"],key)


def __get_values_dynamic__(dict,key_names:list,key_name):
    if key_name not in key_names:
        return None
    idx = key_names.index(key_name)
    values=[]
    for key in dict.keys():
        parts=key.split(".")
        if parts[idx] not in values:
            values.append(parts[idx])
    return values

def __build_dynamic_key__(key_values):
    if len(key_values)==0:
        raise RuntimeError("Dynamic key construction receive 0 as number of params")
    key=""
    for idx,key_part in enumerate(key_values):
        if idx < len(key_values)-1:
            key=key+"\""+str(key_part)+"\""+"."
        else:
            key=key+"\""+str(key_part)+"\""
    return key  