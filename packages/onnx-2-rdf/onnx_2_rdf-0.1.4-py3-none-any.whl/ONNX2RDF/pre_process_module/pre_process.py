import os
from json_util import save_json,load_json,get_log_paths
from util_process.util import remove_extra_params

from util_process.operators import find_operators,get_key_operator,is_domain_ONNX,get_correct_status
from util_process.operators import is_operator_func,get_operator_url,is_operator_shape_inference,is_onnx_runtime
from onnx.defs import  OpSchema
from warnings_thread_safe import warnings 
from repair_functions.repair_opsets import repair_opset_and_funcs

from util_process.data import get_opset_data,function_data_find,opset_data_find,get_functions_data,function_key,opset_key,get_opset_values,get_func_values
from repair_nodes.repair_nodes_base import repair_nodes

from repair_types.repair_initializer import repair_initializers
from repair_types.reapair_value_info import revise_value_infos_graph
from repair_types.repair_tensor import DataType,get_label_data_type
from util_process.util import LocationType,OperatorStatus,get_location_label,get_operator_status_label

from repair_types.repair_metadata_prop import check_metadata_entries
from util_process.util import LINE_WITH_TAB,create_unique_names

from repair_types.repair_annotation import check_annotations







def __check_graph_fields__(graph):
    if "node" not in graph or not isinstance(graph["node"],list):
            graph["node"]=[]
            warnings.warn("Graph has nodes missing or are not a list, the result model will have empty nodes. ")
    if "initializer" not in graph or not isinstance(graph["initializer"],list):
            graph["initializer"]=[]      
    if "sparseInitializer" not in graph or not isinstance(graph["sparseInitializer"],list):
            graph["sparseInitializer"]=[]

    if "name" in graph :
        base_name =graph["name"]
    else:
        base_name="unnamed_graph"   
        
    graph["name"] =create_unique_names([],base_name)
    
        
            
    return True
       
                
def __funct_contains_name__(data,name):
    for function in data["functions"]:
        
        if "name" in function and function["name"]==name:
            return True
    return False

def __is_operator_depracted_on_version__(operator,version):
    new_ops:list[OpSchema] = find_operators(operator.name,operator.domain,version)
    if len(new_ops)==0:
        return False
    return new_ops[0].deprecated
 
def __get_version_opset_to_operator__(import_data,domain,operator:OpSchema):
    opsets = opset_data_find(import_data,domain)
    
    best_version=None
    for opset in opsets:
        version=opset["version"]
        if int(version)>=int(operator.since_version) and (best_version==None or int(version)>int(best_version)): 
            if not __is_operator_depracted_on_version__(operator,version):
                best_version=version    
            
    return best_version

                         
def __add_operator_if_onnx__(name,domain,version,dict_ops:dict,import_data):
    key = get_key_operator(domain,name,version)
    
    if key not in dict_ops.keys():
        operator = find_operators(name=name,domain=domain,version=version)
        
        if len(operator)>0:
            dict_ops[key]={"schema":operator[0],"opset_version":__get_version_opset_to_operator__(import_data,domain,operator[0])}
            
            
def add_entry_if_exists(dict_instance,key,entity,new_key=None):
    value=None
    if isinstance(entity,dict) and key in entity.keys():
        value = entity[key]
    if isinstance(entity,object) and hasattr(entity, key):
        value = getattr(entity,key)
    if value!=None and not new_key:
        dict_instance[key]=str(value)
    if value!=None and new_key:
        dict_instance[new_key]=str(value)

def __fill_status_codes(data):
    
    data["operator_types"]=[]
    type_list=data["operator_types"]
    for tensor_type in OperatorStatus:
        label = get_operator_status_label(tensor_type)

        type_list.append({"prefLabel":tensor_type.name,"altLabel":tensor_type.value,"label":label})
    
    data["location_types"]=[]
    type_list=data["location_types"]
    for tensor_type in LocationType:
        label = get_location_label(tensor_type)

        type_list.append({"prefLabel":tensor_type.name,"altLabel":tensor_type.value,"label":label})
    
    
    data["tensor_types"]=[]
    type_list=data["tensor_types"]
    for tensor_type in DataType:
        label = get_label_data_type(tensor_type)

        type_list.append({"prefLabel":tensor_type.name,"altLabel":tensor_type.value,"label":label})
        
    data["map_key_types"]=[]
    type_list=data["map_key_types"]
    
    map_key_types=[DataType.UINT64,DataType.UINT32,DataType.UINT16,DataType.UINT8,
                   DataType.INT64,DataType.INT32,DataType.INT16,DataType.INT8,DataType.STRING]
    
    for tensor_type in map_key_types:
        label = get_label_data_type(tensor_type)

        type_list.append({"prefLabel":tensor_type.name,"altLabel":tensor_type.value,"label":label})
 

 
            
def __fill_operator_metadata__(data):
    
    operators_onnx={}
    import_data=get_opset_data(data["opsetImport"])
    for node in data["graph"]["node"]:
        
        if "opType" in node and "domain" in node and "version" in node :
            __add_operator_if_onnx__(node["opType"],node["domain"],node["version"],operators_onnx,import_data)
        
    for func in data["functions"]:
        import_data=get_opset_data(func["opsetImport"])
        for node in func["node"]:
            if "opType" in node and "domain" in node and "version" in node :
                __add_operator_if_onnx__(node["opType"],node["domain"],node["version"],operators_onnx,import_data)
    data["operators"]=[]
                
    for operator_data in operators_onnx.values():
        operator=operator_data["schema"]
        operator_entry=dict()
        add_entry_if_exists(operator_entry,"name",operator)
        add_entry_if_exists(operator_entry,"domain",operator)
        add_entry_if_exists(operator_entry,"since_version",operator)
        add_entry_if_exists(operator_entry,"doc",operator,new_key="docString")
        
        #operator status
        if hasattr(operator,"support_level"):
            operator_entry["status"]=get_correct_status(operator.support_level.name)

        operator_entry["is_function"]=is_operator_shape_inference(operator)
        operator_entry["is_shape_inference"]=is_operator_func(operator)
        if operator_entry["domain"]!=None and operator_entry["name"] and (is_domain_ONNX(operator_entry["domain"]) or is_onnx_runtime(operator_entry["domain"])):
            
            
            url = get_operator_url(operator_entry["domain"],operator_entry["name"])
            if url:
                operator_entry["url"]=url
        
        
        
        opset_id =f"v{operator_data["opset_version"]}"
        if operator_entry["domain"]!="":
            opset_id=f"domain-{operator_entry["domain"]}-{opset_id}"
        operator_entry["opset_id"]=opset_id
        
        #TODO: get default_attributes
        #TODO: get input/output constrains
        
        
        element_id=f"name-{operator_entry["name"]}"
        if operator_entry["domain"]!="":
            element_id=f"{element_id}-domain-{operator_entry["domain"]}"
        element_id=f"{element_id}-v{operator_entry["since_version"]}"
        operator_entry["element_id"]=element_id
        
        data["operators"].append(operator_entry)
    
                
 
 

 
def check_first_fields(data):
    
    if "graph" not in data or not isinstance(data["graph"],dict):
        warnings.warn("Graph was missing from file or the format was wrong, the new graph will be empty. ")
        data["graph"]=dict()
    
    if "functions" not in data or not isinstance(data["functions"],list):
        data["functions"]=[]
        
    if "opsetImport" not in data or not isinstance(data["opsetImport"],list):
        data["opsetImport"]=[]
    return True
 
 



            

 


        
# Main library function of the pre_process function
# Inputs json dict and outputs repair/modified json_dict for rdf mapping
def pre_process(data:dict):
    
    check_first_fields(data)
    repair_opset_and_funcs(data)
    
    __check_graph_fields__(data["graph"])
    
    repair_initializers(data["graph"])
    revise_value_infos_graph(data["graph"])
    
    repair_nodes(data)
    data["graph"]["element_id"]=""
    
    check_annotations(data["graph"],element_id="",start_error_messege= f"\n The quantizationAnnotation of graph ({data["graph"]["name"]}) has a wrong format {LINE_WITH_TAB}")
            
    remove_extra_params(data["graph"],["input","output","node","name","initializer","sparseInitializer","valueInfo","element_id","metadataProps","docString","quantizationAnnotation"],
                        start_error_messege=f"The Main graph with name ({data["graph"]["name"]})")
    remove_extra_params(data["graph"],["input","output","node","name","initializer","sparseInitializer","valueInfo","element_id","metadataProps","docString","quantizationAnnotation"],
                        start_error_messege="The model")
    check_metadata(data)
    
    
    __fill_operator_metadata__(data)
    __fill_status_codes(data)
    
def check_metadata(data):
    
    if "metadataProps" in data and data["metadataProps"]!=[]:
        
        correct_meta,_ =check_metadata_entries(data["metadataProps"],start_error_messege=f"\nThe file has a wrong metadata_prop param {LINE_WITH_TAB}",keys=[],element_id="")

        if not correct_meta:
            data["metadataProps"]=[] 
          
            
    if "metadataProps" in data["graph"] and data["graph"]["metadataProps"]!=[]:
        correct_meta,_ =check_metadata_entries(data["graph"]["metadataProps"],keys=[],element_id=f"Graph-{data["graph"]["name"]}",
            start_error_messege=f"\nThe graph {data["graph"]["name"]} has a wrong metadata_prop param {LINE_WITH_TAB}"
                                               )

        if not correct_meta:
            data["graph"]["metadataProps"]=[]  
    
    
from datetime import datetime  

# Main cmd function of the pre_process function
# Inputs json dict and uses parms for managing cache files,log dirs, etc
def __pre_process__(data,relative_dir="",tmp_dir="tmp",log_dirs="logs",cache=True):
    
    cache_executed=False
    file_name="preprocess_model.json"
        
    tmp_path = os.path.join(relative_dir,tmp_dir,file_name)
    if not isinstance(log_dirs,list):
        log_dirs=[log_dirs]
    
    log_paths=log_paths=get_log_paths(log_dirs,file_name,relative_dir)
    
        
    is_in_cache = os.path.exists(tmp_path)
    
    
    if cache and is_in_cache:
        cache_executed=True
            
    if not cache or (not is_in_cache):
        
        pre_process(data) 
        for log_path in log_paths:
            save_json(data,log_path)
        
        save_json(data,tmp_path)     
                   
    return tmp_path,cache_executed