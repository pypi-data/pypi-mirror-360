


from warnings_thread_safe import warnings 
from onnx.defs import  OpSchema
from pre_process_module.util_process.util import DOUBLE_LINE_WITH_TAB
from pre_process_module.util_process.operators import find_operators

def add_connections_to_namelist(connections:list,name_list:dict,node_id,start_error_messege=""):
    compose_warning=f"{start_error_messege}"
    warning_present=False
    for idx,conn in enumerate(connections):
        if isinstance(conn,str) and conn not in name_list.keys():
            name_list[conn]=f"{node_id}-idx{idx}"
        elif not isinstance(conn,str):
            warning_present=True
            compose_warning= f"{compose_warning} {DOUBLE_LINE_WITH_TAB} Connection at pos {idx} is not a string -> Being Skipped"
    if warning_present:
        warnings.warn(compose_warning)        
            
def get_specific_peripherials(peripherials:list,start_error_messege=""):
    peripherial_name_list=dict()
    compose_warning=f"{start_error_messege}"
    warning_present=False
    for idx,peripherial in enumerate(peripherials):
        if isinstance(peripherial,dict) and "name" in peripherial.keys() and peripherial["name"] not in peripherial_name_list.keys():
            peripherial_name_list[peripherial["name"]]=peripherial["element_id"]
        elif isinstance(peripherial,str):
            peripherial_name_list[peripherial]=""
        else:
            warning_present=True
            compose_warning= f"{compose_warning} Peripherial at pos {idx} is not a valid entry -> Being Skipped"
    if warning_present:
        warnings.warn(compose_warning)
    
    return peripherial_name_list   
     
def get_initializers_names(initializers:list,name_list:dict,start_error_messege="",is_sparse=False):
    compose_warning=f"{start_error_messege}"
    warning_present=False
    for idx,initliazer in enumerate(initializers):
        
        if isinstance(initliazer,dict) and "name" in initliazer.keys() and initliazer["name"] not in name_list.keys():
            name_list[initliazer["name"]]={"id":initliazer["tensor_id"],"is_sparse":is_sparse}
        else:
            warning_present=True
            compose_warning= f"{compose_warning} Initializer at pos {idx} is not a valid entry -> Being Skipped"  
    if warning_present:
        warnings.warn(compose_warning)        
            
            
def get_graph_peripherials(graph,start_error_messege=""):
    inputs=dict()
    outputs=dict()
    if "input" in graph:
        inputs = get_specific_peripherials(graph["input"],
            start_error_messege=f"{start_error_messege} Inputs of graph {graph["name"]} have a wrong format") 
    if "output" in graph:
        outputs = get_specific_peripherials(graph["output"],
            start_error_messege=f"{start_error_messege} Outputs of graph {graph["name"]} have a wrong format")   
 
    return {"inputs":inputs,"outputs":outputs}      
            
def add_connections_to_node_name_lists(node,output_names:dict,input_names:dict,node_id="",start_error_messege=""):
    if "output" in node:
        add_connections_to_namelist(node["output"],output_names,f"{node_id}-Node-{node["name"]}-outputs",
                                    start_error_messege=f"{start_error_messege} Output connections have a wrong format")
    if "input" in node:
        add_connections_to_namelist(node["input"],input_names,f"{node_id}-Node-{node["name"]}-inputs",
                                    start_error_messege=f"{start_error_messege} Input connections have a wrong format")
    

    # lista mas de un elemento
    
def check_for_variadic(peripherial):
    variadic_found=False
    for idx,item in enumerate(peripherial):
        if item.option.name == "Variadic":
            variadic_found=True
        if variadic_found and item.option.name != "Variadic":
            return False,idx,variadic_found
    return True,idx,variadic_found
    
def check_peripherials_onnx(op_schema:OpSchema,is_output=False,connections=[],start_error_messege=""):
    if not op_schema:
        warnings.warn(f"{start_error_messege} Onnx operator metadata is empty")
        return False,False,None
    peripherial =None
    
    if is_output:
        peripherial=op_schema.outputs
    else:
        peripherial=op_schema.inputs
        
    is_variadic_correct,idx,is_variadic = check_for_variadic(peripherial)
    
    
    if not is_variadic_correct:
        warnings.warn(f"{start_error_messege} Onnx operator {op_schema.name} has a variadic variable (dynamic number of inputs/outputs) but it has (Single,Optional) after the variadic input at input pos {idx} ")
        return False,is_variadic,peripherial
    

    
    if not is_variadic and len(peripherial)<len(connections):
        warnings.warn(f"{start_error_messege} Onnx operator {op_schema.name} is not variadic or accepts more than {len(peripherial)} inputs ")
        return False,is_variadic,peripherial
   
    return True,is_variadic,peripherial
      
    
def check_optional_variables(op_schema,peripherial_onnx,idx,start_error_messege=""):

    variable= peripherial_onnx[idx]
    if variable.option.name!="Optional":
        return False,f"{start_error_messege} is empty but \n\t\t\t Onnx operator {op_schema.name} doenst allow the input with pos {idx} to be optional"
    return True,""

def get_new_connection_list(connections,connections_names:dict,node_name,is_output,initializers=[],inputs_graph_names=[],output_graphs_names=[],start_error_messege="",
                            op_schema=None,check_peripherials=False,func_data=None):
    from pre_process_module.repair_functions.check_functions import get_func_element_id
    
    new_connections=[]
    
    compose_warning = f"{start_error_messege}"
    all_correct = True
  
    
    if check_peripherials:
        all_correct,is_variadic,peripherial = check_peripherials_onnx(op_schema,is_output,connections,start_error_messege=start_error_messege)
    if not all_correct:
        warnings.warn(f"{start_error_messege} Connections have a wrong format respecting the operator, check warnings")
    
    
    for idx,connc in enumerate(connections):
        
        if not isinstance(connc,str):
            continue
        
          
        
        if connc!=None and connc in connections_names.keys() or connc in inputs_graph_names.keys() or connc in output_graphs_names.keys() or connc in initializers.keys():
            
            
            
            connection = {"name":connc,"element_id":node_name,"is_empty":False}
            if func_data:
                connection["func_id"] = get_func_element_id(func_data)
            if connc in connections_names.keys(): 
                connection["conc_id"]=connections_names[connc] 
            if connc in inputs_graph_names.keys():
                connection["g_input_id"]=inputs_graph_names[connc]
            if connc in output_graphs_names.keys():
                connection["g_output_id"]=output_graphs_names[connc] 
            if connc in initializers.keys():
                if initializers[connc]["is_sparse"]:
                    connection["sparse_id"]=initializers[connc]["id"]
                else:
                    connection["init_id"]=initializers[connc]["id"] 
                
                
            new_connections.append(connection)
        elif connc!="" and connc!=None:
            
            
            if not is_output:
                compose_warning = f"{compose_warning} {DOUBLE_LINE_WITH_TAB} Node connection ({connc}) of node {node_name} doenst exist "
                all_correct=False
        else:
            correct=True
            if check_peripherials and not is_variadic :
                correct,error = check_optional_variables(op_schema,peripherial,idx,start_error_messege=f"{compose_warning} Node connection ({connc}) of node {node_name}")

            if correct:    
                new_connections.append({"name":"","element_id":node_name,"is_empty":True})
            else:
                all_correct=False
                compose_warning=error       
        
    if not all_correct:
       warnings.warn(compose_warning)    
       
  
    if not all_correct:
        raise SyntaxError(f"{start_error_messege} Connections have a wrong format that cannot be fix, check warnings")
        


    for idx,conn in enumerate(new_connections):
        conn["index"]=idx+1
        if idx < len(new_connections)-1:
            conn["next_index"]=idx+2
        if idx == len(new_connections)-1:
            conn["last_index"]=""
        
    return new_connections       


def check_connections_node(node,conn_data:dict,element_id="",start_error_messege="",is_onnx=False,func_data=None):

    
    op_schema=None
    if is_onnx:
        op_schema = find_operators(node["opType"],node["domain"],node["version"])
        if len(op_schema)>0:
            op_schema=op_schema[0]
        else:
            raise RuntimeError(f"{start_error_messege} Operator {node["opType"]}-{node["domain"]}-{node["version"]} doenst exist")
   
    input_names = dict()
    output_names = dict()
    initializers = dict()
    graph_peripherials = {"inputs":dict(),"outputs":dict()}
    

    for item in conn_data.values():
        input_names = input_names | item["inputs"]
        output_names = output_names | item["outputs"]
        initializers = initializers |item["initializers"]
        graph_peripherials["inputs"]=graph_peripherials["inputs"] | item["inputs"]
        graph_peripherials["outputs"]=graph_peripherials["outputs"] | item["outputs"]
   
    
    node_name= f"{element_id}-Node-{node["name"]}"
        
    if "input" in node:
        inputs=get_new_connection_list(node["input"],output_names,node_name=node_name,is_output=False,initializers=initializers,
                                            inputs_graph_names=graph_peripherials["inputs"],
                                            output_graphs_names=dict(),
                                            start_error_messege=f"{start_error_messege} Inputs have a wrong format",
                                            func_data=func_data,
                                            check_peripherials=is_onnx,op_schema=op_schema)
        del node["input"]
        node["input_node"]=inputs
        
    if "output" in node:
        outputs=get_new_connection_list(node["output"],input_names,node_name=node_name,is_output=True,initializers=initializers,
                                            inputs_graph_names=dict(),
                                            output_graphs_names=graph_peripherials["outputs"],
                                            start_error_messege= f"{start_error_messege} Outputs have a wrong format",
                                            func_data=func_data,
                                            check_peripherials=is_onnx,op_schema=op_schema)
        del node["output"]
        node["output_node"]=outputs
        
    

