from repair_tensor import check_tensor_complex,check_sparse_complex
from warnings_thread_safe import warnings 
from pre_process_module.util_process.operators import find_operators
from pre_process_module.util_process.data import function_data_find
from repair_type_proto import check_type_proto
from pre_process_module.util_process.util import remove_extra_params,validate_enum,LINE_WITH_TAB
from pre_process_module.repair_nodes.repair_nodes_base import check_subgraph



from enum import Enum
from warnings_thread_safe import warnings 
from onnx.defs import  OpSchema
class AttrType(Enum):
    UNDEFINED = 0
    FLOAT = 1
    INT = 2
    STRING = 3
    TENSOR = 4
    GRAPH = 5
    SPARSE_TENSOR = 11
    TYPE_PROTO = 13

    FLOATS = 6
    INTS = 7
    STRINGS = 8
    TENSORS = 9
    GRAPHS = 10
    SPARSE_TENSORS = 12
    TYPE_PROTOS = 14
    
TYPED_LISTS=[AttrType.FLOATS,AttrType.INTS,AttrType.STRINGS,AttrType.GRAPHS,AttrType.SPARSE_TENSORS,AttrType.TYPE_PROTOS]
INT_TYPES = [AttrType.INT,AttrType.INTS]
STRING_TYPES = [AttrType.STRING,AttrType.STRINGS]
FLOAT_TYPES = [AttrType.FLOAT,AttrType.FLOATS]
TENSOR_TYPES = [AttrType.TENSOR,AttrType.TENSORS]
SPARSE_TYPES = [AttrType.SPARSE_TENSOR,AttrType.SPARSE_TENSORS]
GRAPH_TYPES = [AttrType.GRAPH,AttrType.GRAPHS]
TYPE_PROTO_TYPES = [AttrType.TYPE_PROTO,AttrType.TYPE_PROTOS]

MAPP_ENUM_LABEL={AttrType.FLOAT:"f",AttrType.FLOATS:"floats",
                 AttrType.INT:"i",AttrType.INTS:"ints",
                 AttrType.STRING:"s",AttrType.STRINGS:"strings",
                 AttrType.TENSOR:"t",AttrType.TENSORS:"tensors",
                 AttrType.GRAPH:"g",AttrType.GRAPHS:"graphs",
                 AttrType.SPARSE_TENSOR:"sparse_tensor",AttrType.SPARSE_TENSORS:"sparse_tensors",
                 AttrType.TYPE_PROTO:"tp",AttrType.TYPE_PROTOS:"type_protos"}



def check_att_enum(data_type_value):
   enum = validate_enum(data_type_value,AttrType)
   
   return enum

def check_onnx_op_attributes(enum_type,attribute,op_schema:OpSchema,start_error_messege:str=""):
    attributes_onnx = op_schema.attributes
    if attribute["name"] not in attributes_onnx:
        warnings.warn(f"\n{start_error_messege} the attribute doenst apply for the operator {op_schema.name} {LINE_WITH_TAB} Attribute Could be Removed")
        return False
    onnx_attribute_type =  attributes_onnx[attribute["name"]].type
    if enum_type.name == onnx_attribute_type.name and enum_type.value==onnx_attribute_type.value:
        return True
    else:
        warnings.warn(f"\n{start_error_messege} the attribute type is invalid for the operator {op_schema.name} {LINE_WITH_TAB} Attribute Could be Removed")
        return False
    
def check_func_op_attributes(enum_type,attribute,func_schema,start_error_messege:str=""):
    attributes_func=[]
    attributes_proto_func = dict()
    if "attribute" in func_schema:
        attributes_func.extend(func_schema["attribute"])
    if "attributeProto" in func_schema:
        attributes_proto_func=  {item["name"]: item for item in func_schema["attributeProto"]}    
        attributes_func.extend(attributes_proto_func.keys())
        
        
    if attribute["name"] not in attributes_func:
        warnings.warn(f"\n{start_error_messege} the attribute ({attribute["name"]}) doenst apply for the function {func_schema["name"]} {LINE_WITH_TAB} Attribute Could be Removed")
        return False

    if attribute["name"] in attributes_proto_func.keys():
        #TODO types need to be the same???
       #attribute_data = attributes_proto_func[attribute["name"]]
       #att_type = check_att_enum(attribute_data["type"])
       #same = att_type == enum_type
       pass
   
    return True
    


def check_attribute_type(type,attribute,op_schema=None,func_schema=None,start_error_messege:str=""):
    enum = check_att_enum(type)
    if enum==None:
        warnings.warn(f"\n{start_error_messege} its type is not a valid AttrType {LINE_WITH_TAB} Attribute Could be Removed")
        return None
    
    if op_schema:
       correct = check_onnx_op_attributes(enum,attribute,op_schema,start_error_messege=start_error_messege)
       if correct:
           return enum
       else:
           return None
    if func_schema:
        
        correct = check_func_op_attributes(enum,attribute,func_schema,start_error_messege=start_error_messege)
        if correct:
            return enum
        else:
            return None
    return enum

def check_attribute_fields(attribute,start_error_messege:str=""):
   
    if not isinstance(attribute,dict):
        warnings.warn(f"\n{start_error_messege} its not a dict {LINE_WITH_TAB} Attribute Could be Removed")
        return False

    
    if 'name' not in attribute:
        warnings.warn(f"\n{start_error_messege} name is missing {LINE_WITH_TAB} Attribute Could be Removed")
        return False
    
    if not isinstance(attribute["name"],str):
        warnings.warn(f"\n{start_error_messege} name has a wrong format {LINE_WITH_TAB} Attribute Could be Removed")
        return False
    
    if "type" not in attribute:
        warnings.warn(f"\n{start_error_messege} type is missing {LINE_WITH_TAB} Attribute Could be Removed")
        return False
    
    if not (isinstance(attribute["type"],str) or isinstance(attribute["type"],int)):
        warnings.warn(f"\n{start_error_messege} type has a wrong format {LINE_WITH_TAB} Attribute Could be Removed")
        return False
    
    
    return True




def repair_attribute_data_value(value,enum_type,start_error_messege,is_list,list_pos,element_id="",subgraph_data=None):
    
    if enum_type in INT_TYPES:
        try: 
            if isinstance(value,str) or isinstance(value,float):
                fix_value=int(value)
                return fix_value
        except Exception:
            _=True
            
        if isinstance(value,int):
            return value
            
        if is_list:
            warnings.warn(f"\n{start_error_messege} The attribute of type {enum_type.name} at the pos {list_pos} of the list must be a integer {LINE_WITH_TAB} Attribute Could be Removed"  )
        else:
            warnings.warn(f"\n{start_error_messege} The attribute of type {enum_type.name} must be a integer {LINE_WITH_TAB} Attribute Could be Removed"  )
        return None
    if enum_type in FLOAT_TYPES:
       
        try: 
            if isinstance(value,str):
                fix_value=float(value)
                return fix_value
        except Exception:
            _=True
        
        if isinstance(value,float):
            return value
        elif isinstance(value,int):
            return float(value)
        
        
        if is_list:
            warnings.warn(f"\n{start_error_messege} The attribute of type {enum_type.name} at the pos {list_pos} of the list must be a float(decimal) {LINE_WITH_TAB} Attribute Could be Removed"  )
        else:
            warnings.warn(f"\n{start_error_messege} The attribute of type {enum_type.name} must be a float (decimal) {LINE_WITH_TAB} Attribute Could be Removed"  )
        return None
    if enum_type in STRING_TYPES:
        if isinstance(value,str):
          return value
        else:
            if is_list:
                warnings.warn(f"\n{start_error_messege} The attribute of type {enum_type.name} at the pos {list_pos} of the list must be a string {LINE_WITH_TAB} Attribute Could be Removed"  )
            else:
                warnings.warn(f"\n{start_error_messege} The attribute of type {enum_type.name} must be a string {LINE_WITH_TAB} Attribute Could be Removed")
            return None
    if enum_type in TENSOR_TYPES:
        if is_list:
            check = check_tensor_complex(value,f"{start_error_messege} The attribute of type {enum_type.name} of the list at pos {list_pos} has a wrong format -> Attribute Could be Removed {LINE_WITH_TAB}",check_storage_data=True,tensor_id=f"{element_id}-idx{list_pos}")
        else:
            check = check_tensor_complex(value,f"{start_error_messege} The attribute of type {enum_type.name} has a wrong format -> Attribute Could be Removed {LINE_WITH_TAB}",check_storage_data=True,tensor_id=element_id)
        if check:
            return value
        else:
            
            return None 
    if enum_type in SPARSE_TYPES:
        if is_list:
            check = check_sparse_complex(value,f"{start_error_messege} The attribute of type {enum_type.name} of the list at pos {list_pos} has a wrong format -> Attribute Could be Removed {LINE_WITH_TAB}",check_storage_data=True,tensor_id=f"{element_id}-idx{list_pos}")
        else:
            check = check_sparse_complex(value,f"{start_error_messege} The attribute of type {enum_type.name} has a wrong format -> Attribute Could be Removed {LINE_WITH_TAB}",check_storage_data=True,tensor_id=element_id)
        if check:
            return value
        else:
            return None
    if enum_type in GRAPH_TYPES:
        if is_list:
            check = check_subgraph(value,subgraph_data,start_error_messege=f"{start_error_messege} The attribute of type {enum_type.name} of the list at pos {list_pos} has a wrong format -> Attribute Could be Removed {LINE_WITH_TAB}",element_id=f"{element_id}-idx{list_pos}")
        else:
            check = check_subgraph(value,subgraph_data,start_error_messege=f"{start_error_messege} The attribute of type {enum_type.name} has a wrong format -> Attribute Could be Removed {LINE_WITH_TAB}",element_id=element_id)
        if check:
            return value
        else:
            return None
    if enum_type in TYPE_PROTO_TYPES:
        if is_list:
            check = check_type_proto(value,f"{start_error_messege} The attribute of type {enum_type.name} of the list at the pos {list_pos} has a wrong format -> Attribute Could be Removed {LINE_WITH_TAB}",element_id=f"{element_id}-idx{list_pos}")
        else:
            check = check_type_proto(value,start_error_messege=f"{start_error_messege} The attribute of type  {enum_type.name} has a wrong format -> Attribute Could be Removed {LINE_WITH_TAB}",element_id=element_id)
        if check:
            return value
        else:
            return None
        
    return None
    

def repair_attribute_data(attribute,enum_type:AttrType,start_error_messege,element_id="",subgraph_data=None):

    correct_all=True
    
    field_name = MAPP_ENUM_LABEL[enum_type]
    if "v" in attribute:
        warnings.warn(f"\n{start_error_messege} fields with name \"v\" are deprecated {LINE_WITH_TAB} Attribute Could be Removed")
        return False
   
    if field_name not in attribute:
        warnings.warn(f"\n{start_error_messege} The attribute of type {enum_type.name} must have the field with name {field_name} {LINE_WITH_TAB} Attribute Could be Removed")
        return False 
       
    is_list=True
    
    if enum_type not in TYPED_LISTS:
        values=[attribute[field_name]]
        is_list=False
        
    else:
        values=attribute[field_name]
        attribute["is_list"]=""

    element_id_type=f"{element_id}-{enum_type.name}"
    
    for idx,value in enumerate(values):
        if is_list:
            element_id_value=f"{element_id_type}-idx{idx}"
        else:
            element_id_value=element_id_type
            
            
        value = repair_attribute_data_value(value,enum_type,start_error_messege,is_list,idx,element_id=element_id_value,subgraph_data=subgraph_data)
        if value==None:
            correct_all=False
        if is_list:
            new_value={"value":value}
            new_value["index"]=idx+1
            if idx < len(values)-1:
                new_value["next_index"]=idx+2
            if idx == len(values)-1:
                new_value["last_index"]=""
            new_value["type"]=enum_type.name
            
            new_value["element_id"]=element_id_type
            values[idx]=new_value
        else:
            values[idx]=value
    if not correct_all:
        
        return False    

    if not is_list:
        attribute["value"]=values[0]
        del attribute[field_name]
    elif enum_type==AttrType.TYPE_PROTOS:  
        attribute["no-typed_list"]=values
        del attribute[field_name]
    else:
        attribute["typed_list"]=values
        del attribute[field_name]
    return True





    


def repair_attribute(attribute,op_schema=None,func_schema=None,start_error_messege:str="",element_id="",node_id="",subgraph_data=None):
    
    
    enum_type = check_attribute_type(attribute["type"],attribute,op_schema,func_schema,start_error_messege=start_error_messege)
    if enum_type:   
        
        correct = repair_attribute_data(attribute,enum_type,start_error_messege,element_id=element_id,subgraph_data=subgraph_data)
            
        if "docString" in attribute and not isinstance(attribute["docString"],str):
            warnings.warn(f"\n{start_error_messege} The \"docString\" is not a string. Removing \"docString\"")
            attribute["docString"]=""
        if not correct:

            return False,None
    else:
        
        return False,None
    remove_extra_params(attribute,["name","attrType","value","typed_list","no-typed_list","type","docString","element_id","is_list"],start_error_messege)    
    attribute["element_id"]=element_id
    attribute["node_id"]=node_id
    return True,attribute


def check_missing_onnx_att(att_names,op_schema):
    for att in op_schema.attributes.keys():
        if att not in att_names and op_schema.attributes[att].required :
            return att
    return None

def check_missing_atts_list(att_names,correct_list):
    for att in correct_list:
        if att not in att_names:
            return att
    return None

        
def check_missing_attributes(att_names,op_schema=None,func_schema=None,start_error_messege:str=""):
    
    
    if op_schema:
        att =check_missing_onnx_att(att_names,op_schema) 
        if att:
            warnings.warn(f"\n{start_error_messege} its missing the attribute {att} for the operator {op_schema.name}")
            return False
    if func_schema and "attribute" in func_schema:
        
        att = check_missing_atts_list(att_names,func_schema["attribute"])
        if att:
            warnings.warn(f"\n{start_error_messege} its missing the attribute {att} for the function {func_schema["name"]}")
            return False
    return True
def get_op_schema_func(node,func_data,type_operator_data):
    op_schema=None
    func_schema=None
    if type_operator_data and node and type_operator_data[1]:
        # obtenemos informacion sobre si los atributos son opcionales
        op_schemas = find_operators(node["opType"],node["domain"],node["version"])
        if len(op_schemas)>0:
            op_schema=op_schemas[0]
        else:
            raise RuntimeError(f"Values of domain ({node["domain"]}),name ({node["opType"]}),version ({node["version"]}) are not operators of the model")
         
   
    if type_operator_data and func_data and type_operator_data[0]:
        # get function and get attribute and attribute_proto
        
        funcs = function_data_find(func_data,node["domain"],node["opType"],node["overload"])
        if len(funcs)>0:
            func_schema=funcs[0]
        else:
            raise RuntimeError(f"Values of domain ({node["domain"]}),name ({node["opType"]}),overload ({node["overload"]}) are not functions of the model")
  
    
    return op_schema,func_schema
    
def check_attributes(attributes,node=None,type_operator_data=None,func_data=None,element_id="",start_error_messege:str="",subgraph_data=None):
    
    correct_all=True
    correct=True
    op_schema,func_schema = get_op_schema_func(node,func_data,type_operator_data)  
        
    attribute_names=[]
    incorrect_value_names=[]
    
    if not isinstance(attributes,list):
        warnings.warn(f"\nThe attributes of the node ({node["name"]}) has a wrong format: It is not a list {LINE_WITH_TAB} Attribute Could be Removed")
        return False,False
    
    for idx,attribute in enumerate(attributes):
        att_name=""
        if "name" in attribute:
            att_name = attribute["name"]
        if att_name=="":
            start_error_messege=f"{start_error_messege} The attribute entry at pos {idx} has a wrong format {LINE_WITH_TAB}"
        else:
            start_error_messege=f"{start_error_messege} The attribute entry at pos {idx} and name ({att_name}) has a wrong format {LINE_WITH_TAB}"  
        correct = check_attribute_fields(attribute,start_error_messege)
        
        
        if correct:
            
            
                
            att_element_id = f"{element_id}-Attribute-{att_name}"
            node_id = element_id
            
            correct_att,new_attr = repair_attribute(attribute,op_schema,func_schema,start_error_messege=start_error_messege,element_id=att_element_id,node_id=node_id,subgraph_data=subgraph_data) 
            
            
        if correct and correct_att:
            attributes[idx]=new_attr
            attribute_names.append(attribute["name"])
        else:
            
            if not correct_att and correct:
                
                incorrect_value_names.append(attribute["name"])
            correct_all=False
            del attributes[idx]
            
    
    # Add default values if possible
    if func_schema!=None and "attributeProto" in func_schema:
        for idx,attribute in enumerate(func_schema["attributeProto"]):
            if attribute["name"] not in attribute_names:
                attributes.append(attribute)
        
    
            
    if node:
        
        all_names = attribute_names.copy()
        all_names.extend(incorrect_value_names)
        
        correct = check_missing_attributes(all_names,op_schema,func_schema,f"The node ({node["name"]}) ")
        
    
    return correct,correct_all

      
    #las funciones definen atributos con attributeproto