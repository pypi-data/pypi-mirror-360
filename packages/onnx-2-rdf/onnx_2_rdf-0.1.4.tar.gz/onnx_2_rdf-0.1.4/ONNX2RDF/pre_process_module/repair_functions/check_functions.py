
from warnings_thread_safe import warnings 
from pre_process_module.repair_types.repair_metadata_prop import check_metadata_entries
from pre_process_module.repair_types.repair_attributes import check_attributes
from pre_process_module.repair_types.reapair_value_info import check_value_infos

from pre_process_module.util_process.util import LINE_WITH_TAB

# repair params not related to domain_opset (name,domain,version), 
#this includes params the params (inputs,outputs,attribute,attributeProto,value_info,metadata)
def get_func_element_id(function):
    element_id=f"name-{function["name"]}"
    if function["domain"]!="":
        element_id=f"{element_id}-domain-{function["domain"]}"
    if function["overload"]!="":
        element_id=f"{element_id}-overload-{function["overload"]}"
    
    return element_id


def repair_function(function,func_pos):
    
    
    function["element_id"]=f"Func-{get_func_element_id(function)}"
    element_id=function["element_id"]
    
    all_correct=True
    
    all_correct = check_fields_functions(function)
    for idx,input in enumerate(function["input"]):
        if not isinstance(input,str):
            all_correct=False
            warnings.warns(f"The function {function["name"]} defined at pos {func_pos} has a wrong input variable{LINE_WITH_TAB} The input_entry at pos {idx} is not a string {LINE_WITH_TAB} Removing Function")
    for idx,output in enumerate(function["output"]):
        if not isinstance(output,str):
            all_correct=False
            warnings.warns(f"The function {function["name"]} defined at pos {func_pos} has a wrong \"output\" variable {LINE_WITH_TAB} The output_entry at pos {idx} is not a string {LINE_WITH_TAB} Removing Function")
    attribute_list=[]
    new_attr_list=[]
    if "attribute" in function:
        if not isinstance(function["attribute"],list):
            all_correct=False
            warnings.warns(f"The function {function["name"]} defined at pos {func_pos} has a wrong \"attribute\" variable It is not a list {LINE_WITH_TAB} Removing Function")
        else:
            for idx,attr in enumerate(function["attribute"]):
                if not isinstance(attr,str):
                    all_correct=False
                    warnings.warns(f"The function {function["name"]} defined at pos {func_pos} has a wrong \"attribute\" variable {LINE_WITH_TAB} The attribute_entry at pos {idx} is not a string {LINE_WITH_TAB} Removing Function")
                else:
                    attribute_list.append(attr)
                    new_attr_list.append({"name":attr,"element_id":f"{element_id}-Attribute-{attr}"})
        function["attribute"]=new_attr_list
    if "docString" in function and not isinstance(function["docString"],str):
        warnings.warns(f"The function {function["name"]} defined at pos {func_pos} has a wrong format {LINE_WITH_TAB} The \"docString\" param is not a string -> Removing \"docString\"")
        function["docString"]=""
        
    if "metadataProps" in function:
        correct,_ =check_metadata_entries(function["metadataProps"],start_error_messege=f"\nThe function {function["name"]} defined at pos {func_pos} has a wrong metadata_prop param{LINE_WITH_TAB}",keys=[],element_id=element_id)
        
        if not correct:
            function["metadataProps"]=[]
            
    if "attributeProto" in function:
        _,all_correct = check_attributes(function["attributeProto"],start_error_messege=f"\nThe function {function["name"]} defined at pos {func_pos} has a wrong attributeProto variable{LINE_WITH_TAB}",element_id=element_id)
        if all_correct:
            att_names = {item["name"]: item for item in function["attributeProto"]}
            intersect = list(set(att_names) & set(attribute_list))
            if len(intersect)>0:
                all_correct=False
                warnings.warn(f"The function {function["name"]} defined at pos {func_pos} has a wrong format {LINE_WITH_TAB} The \"attributeProto\" param has attributes with the same name with the \"attribute\" param {LINE_WITH_TAB} Removing Function")
    
       
    if "valueInfo" in function:
        correct = check_value_infos(function["valueInfo"],start_error_messege=f"\nThe function {function["name"]} defined at pos {func_pos} has a wrong value_info variable{LINE_WITH_TAB}",element_id=f"{element_id}-valuesInfo")
        if not correct:
            function["valueInfo"]=[]
    else:
        function["valueInfo"]=[]

    connect_input_output(function["valueInfo"],function["input"],function["output"],element_id)
    
    return all_correct


def connect_input_output(values:list,inputs:list,outputs:list,element_id):
    for value in values:
        if value["name"] in inputs:
            value["is_input"]=value["element_id"]
        elif value["name"] in outputs:
            value["is_output"]=value["element_id"]
        else:
            value["is_value"]=value["element_id"]
    for input_name in inputs:
        if input_name not in values:
            new_element_id = f"{element_id}-valuesInfo-{input_name}"
            values.append({"is_input":new_element_id,"name":input_name})   
    for output_name in outputs:
        if output_name not in values:
            new_element_id = f"{element_id}-valuesInfo-{output_name}"
            values.append({"is_output":new_element_id,"name":output_name})

def check_fields_functions(function):
    if "opsetImport" not in function or not isinstance(function["opsetImport"],list):
            function["opsetImport"]=[]
    if "node" not in function or not isinstance(function["node"],list):
            function["node"]=[]
    if "input" not in function or not isinstance(function["input"],list):
            function["input"]=[]
    if "output" not in function or not isinstance(function["output"],list):
            function["output"]=[]

    return True