from util_process.operators import is_register_operator,is_domain_ONNX
from warnings_thread_safe import warnings 

from util_process.data import get_opset_data,function_data_find,opset_data_find,function_key,opset_key,get_func_values,get_functions_data
from node_connections import check_connections_node,add_connections_to_node_name_lists,get_initializers_names,get_graph_peripherials

from pre_process_module.util_process.util import remove_extra_params
from pre_process_module.repair_types.reapair_value_info import revise_value_infos_graph
from pre_process_module.util_process.util import LINE_WITH_TAB,create_unique_names
from pre_process_module.repair_types.repair_metadata_prop import check_metadata_entries

from pre_process_module.repair_types.repair_annotation import check_annotations
from repair_types.repair_initializer import repair_initializers

MAX_RECURSIVE=1

def __get_correct_params_func_node__(op_name,func_data,import_data,domain=None,overload=None): 
    from pre_process_module.repair_functions.repair_opsets import is_function_contradictory
    
    possible_funcs_name = function_data_find(func_data,name=op_name)
    if len(possible_funcs_name)==0:
        # no existe ninguna funcion con ese nombre
        return False,None,None,None,None
    # hay dos opciones o el dominio no existe o si existe esta incorrecto
    
    if overload==None:
        overload_check=""
    else:
        overload_check=overload
    if domain==None:
        domain_check=""
    else:
        domain_check=domain
    
    possible_funcs_all = function_data_find(func_data,domain=domain_check,name=op_name,overload=overload_check)
    
    # all attributes match -> all correct
    if len(possible_funcs_all)==1:
        return True,possible_funcs_all[0]["domain"],possible_funcs_all[0]["overload"],possible_funcs_all[0]["version"],[{"version":possible_funcs_all[0]["version"]}]
    
    
    if len(possible_funcs_all)>1:
        # same version,domain and overload
        raise RuntimeError("There cannot be two functions with same domain/name/overload at func_data")

    non_contradictory={}

    for fun in possible_funcs_name:
        if not is_function_contradictory(op_name,fun["domain"],import_data):
            non_contradictory[function_key(fun["domain"],fun["name"],fun["version"])]=fun
    if len(non_contradictory)==0:
        #todas las funciones contradicen con el opset conclusion no es una funcion
        return False,None,None,None,None
    
    
        
    
    values=function_data_find(non_contradictory,name=op_name)
    # caso visto anterior pero con la lista filtrada
    if len(values)==1:
        # Estamos seguros que no es contradictorio y hay una solucion
        return True,values[0]["domain"],values[0]["overload"],values[0]["version"]
    if len(values)==0:
        # esta opcion deberia haberse tratado antes
        return False,None,None,None,None
    
    
    func_domains = function_data_find(non_contradictory,domain=domain_check,name=op_name) 
    
    
    unique_domains=get_func_values(non_contradictory,"domain")
    
    if len(func_domains)==0 and (len(unique_domains)>1 or len(unique_domains)<=0):
        # no hay funciones con ese dominio y no es posible ajustar a un dominio concreto
        return False,None,None,None,None
    
    # el dominio existente es incorrecto
    if len(func_domains)==0 and len(unique_domains)==1:
        check,_=is_function_contradictory(name=op_name,domain=unique_domains[0],domains_opset=import_data)
        
        other_domains = opset_data_find(import_data,domain)
        if len(other_domains)>=1:
            #estamos en el posible caso de que existen dominios importados con el dominio incorrecto no es que este mal puesto -> no es una funcion
            return False,None,None,None,None
        if len(other_domains)==0 and check:
            #no hay dominios con este dominio ("erroneo") y el nuevo dominio tampoco es contradictorio
            domain = unique_domains[0]
             
    if len(func_domains)==1:
        return True,func_domains[0]["domain"],func_domains[0]["overload"],func_domains[0]["version"],[{"version":func_domains[0]["version"]}]
    
    #len de func_domains es mayor que 1, hay mas de un posible overload y como ya hemos comparado que el overload vacio sea "",
    #estamos en el caso que hay mas de un overload valido y el overload usado en en la funcion no es ninguno de ellos y no 
    # podemos arreglarlo
    
    final_list = function_data_find(non_contradictory,domain=domain_check,name=op_name,overload=overload_check)
    
    if len(final_list)==1:
        return True,final_list[0]["domain"],final_list[0]["overload"],final_list[0]["version"],[{"version":final_list[0]["version"]}]
    
    # o len(final_list)==0 o len(final_list) es mayor que 1 que ya es raro de por si
    return False,None,None,None,None
        
from onnx.defs import OpSchema

def __get_max_version__(list,key="version"):
    max_version=None
    for item in list:
        version=None
        if isinstance(item,dict):
            version =item[key]
        if isinstance(item,object) and hasattr(item, key):
            version =getattr(item,key)
            
        if max_version==None and version:
            max_version=version
        elif version:
            max_version =max(int(version),int(max_version))
            
    return max_version

# devuelve since_versions que sean menores iguales que version_maximum, de esta forma podemos comprobar si
# el domain opset incluye el operador
def __get_adequate_version__(list_op:list[OpSchema],version_maximum):
    node_version=None
    opset_versions=[]
    deprecated_found=False
    
    list_op.sort(key=lambda x: x.since_version)
    
    for operator in list_op:
        version = operator.since_version
         
        if int(version) <= int(version_maximum) and  (not node_version or int(version)>= int(node_version)):
            if operator.deprecated:
                # si hay una version mayor justo despues (sorted) pero deprecated el operador no esta disponible
                deprecated_found=True
            else:
                # guardamos la version del operador, 
                # en caso de que la version siguiente este deprecated (podemos usar la ultima version disponible)
                # y en caso de que se vuelva a reintroducir en versiones posteriores deprecated_found permite seguir buscando
                node_version=version
                deprecated_found=False
    
    # esta version puede ser escalada en el opset_final (force=False)
    opset_versions=[{"version":version_maximum,"force":False}]
    
    
           
    if deprecated_found:
        # necesitamos ambas versiones la actual y la vieja
        
        if version_maximum>node_version:
            #necesitamos ambas versiones la del nodo y la del opset actual
            opset_versions=[{"version":node_version,"force":True},opset_versions[0]]
            #TODO: improve warning
            warnings.warn("Depracted Operator, actual version is higher")
        else:
            #necesitamos mantener la version del depracated
            opset_versions=[{"version":node_version,"force":True}]
            #TODO: improve warning
            warnings.warn("Depracted Operator, actual version is equal to last functional_version")
        
    return node_version,opset_versions

def __get_opset_version_onnx__(import_data,domain):
    
    
    actual_opsets = opset_data_find(import_data,domain)
   
    
    actual_version=None
    if len(actual_opsets)==1:
        actual_version=actual_opsets[0]["version"]
    elif len(actual_opsets)>1:
        actual_version=__get_max_version__(actual_opsets,key="version")
        
    return actual_version


def __get_correct_params_onnx_node__(op_name,import_data,domain=None):
    
    
    
    list_op:list[OpSchema]=[]
    check,list_op = is_register_operator(op_name)
    require_opset_versions=[]
    
    
    if not check:
        return False,None,None,None
    if len(list_op)==1 and not list_op[0].deprecated:
        # opset_version es la version actual del opset si existe
        
        opset_version=__get_opset_version_onnx__(import_data,list_op[0].domain)
        if opset_version:
            return True,list_op[0].domain,list_op[0].since_version,[{"version":opset_version,"force":False}]
        # como solo hay una entrada no deberian ser operadores depracted
        
    elif len(list_op)==1:
        domain_new = list_op[0].domain
        if domain==None or domain != domain_new:
            domain=domain_new
    
    
    if domain==None:
        domain_check=""
    else:
        domain_check=domain
    
    
    
    check,list_op = is_register_operator(op_name,domain=domain_check)
    
    if not check:
        return False,None,None,None
    if len(list_op)==1 and  not list_op[0].deprecated:
        # como solo hay una entrada no deberian ser operadores depracted
        
        opset_version=__get_opset_version_onnx__(import_data,list_op[0].domain)
        if opset_version:
            return True,list_op[0].domain,list_op[0].since_version,[{"version":opset_version,"force":False}]
    elif len(list_op)==1:
        warnings.warn(f"\nDeprecated operator {list_op[0].name} since version {list_op[0].since_version}")

    
    # si opset_version es None esto implica que hay que añaldir correct_version
    opset_version=__get_opset_version_onnx__(import_data,domain_check)
    
    
    
    correct_version=None
    if opset_version:
        # hay que encontrar en la lista la mejor version para el nodo y la version del opset que se debe comprobar
        # correct_version es la version del nodo (since_version) y new_opset_version es la version que debe existir en los
        # opsets para que sea valido el operador (considera tambien el caso de operadores depracted en versiones anteriores) 
        # poniendo warning -> o dejarlo arreglado o actualizar operador (deberia ser problema del usuario)
        correct_version,require_opset_versions = __get_adequate_version__(list_op,opset_version)
        
    else:
        #no hay ninguna version en el opset para este dominio usamos la mejor version
        correct_version=__get_max_version__(list_op,key="since_version")
        require_opset_versions=[{"version":correct_version,"force":False}]
        
    
    
    # tenemos multiples versiones para el mismo operador, pero como son operadores del dominio onnx, podemos estar seguros cogiendo la 
    # version mayor
    
    if correct_version==None:
        raise RuntimeError("Repairing a ONNX node, There is no version at the opset, revise opsets for missing versions, or execute repair_opsets")
    
    
    return True,domain_check,correct_version,require_opset_versions
        
    
def __get_correct_params_user_domain_node__(op_name,domain,import_data):
    
    list_opset = opset_data_find(import_data,domain)
    
    
    if len(list_opset)==1:
        return True,domain,list_opset[0]["version"]
    max_version=__get_max_version__(list_opset,key="version")
    if len(list_opset)>=1:
        max_version=__get_max_version__(list_opset,key="version")
        if max_version==None:
            #TODO: improve error messege
            raise RuntimeError("Reparing a node, There is no version at the opset, revise opsets for missing versions, or execute repair_opsets")
        return True,domain,max_version
    
    # tenemos multiples versiones para el mismo operador, pero como son operadores del dominio onnx, podemos estar seguros cogiendo la 
    # version mayor
    return False,None,None 

  
  
  
  



def __get_opsets_to_add__(op_name,domain,require_versions,import_data,node_name,func_name,node_pos):
    configs_to_add=[]
    
    
    for require in require_versions:
        
        opset_list = opset_data_find(import_data=import_data,domain=domain,version=require["version"])
        if len(opset_list)>1:
            raise RuntimeError("Opsets in Opsets_Data have two instances with the same key (domain,version)")
    
        if len(opset_list)==0 and "force" in require and require["force"]:
            warnings.warn(f"\nNode {node_name} applaying operator ({op_name}) defined at the graph at the pos {node_pos}. It applies the operator ({op_name}) which is deprecated method in newest versions. \n"+
                          "The last version containing a avaible version of the operator is not write at the opset_import, this version will be added")
            configs_to_add.append({"domain":domain,"version":require["version"],"force":True})
        elif len(opset_list)==0:
            # no esta en la lista de opsets pero luego cuando se revisen solo la version mas grande debe quedar
            
            #warnings.warn(f"\nNode {node_name} applaying operator ({op_name}) defined at function {func_name} at the pos {node_pos}. It applies the operator ({op_name}) but opset_import has its import missing or with a incorrect version")
            configs_to_add.append({"domain":domain,"version":require["version"],"force":False})
            
      
    return configs_to_add




# usar los valores del nodo para determinar si es un operador ONNX,funcion o operador no ONNX 
# y revisar sus atributos de domain,version o overload
def __get_correct_operator_data__(op_name,node,import_data:dict,func_data:dict,func_name="",node_pos=""):
    
    correct=False
    version_correct=None
    domain_correct=None
    overload_correct=None
    configs_to_add=None
    is_onnx=False
    is_custom=False
  
    
    is_function=False
    domain=None
    
    overload=None
    
    node_name = ""
    if "name" in node:
        node_name=f"({node["name"]})"
    
    
    
    if "domain" in node:
        domain =node["domain"]
    if "overload" in node:
        overload =node["overload"]
    
    
    is_function,domain_correct,overload_correct,version_correct,require_opset_versions = __get_correct_params_func_node__(op_name,func_data,import_data,domain,overload)
    
    
    if is_function and op_name==func_name:
        raise SyntaxError(f"Node {node_name} defined at the function {func_name} at the pos {node_pos}. It calls itself. Recursive calls are not allowed")
    
    
    
    if not is_function and overload:
        del node["overload"]

    
    if not is_function:
        # ahora o es un operador onnx o un operator set, custom que no sea a añadido a la lista de operators del motor onnx con is register
        # y solo aparece en la lista de dominios
        
        
        is_onnx,domain_correct,version_correct,require_opset_versions=__get_correct_params_onnx_node__(op_name,import_data,domain)
        
    
    
    if not is_onnx and not is_function and domain!=None:
        
        is_custom,domain_correct,version_correct = __get_correct_params_user_domain_node__(op_name,domain,import_data)
        
       
        
        


    
    
    if not is_onnx and not is_function and not is_custom:
        if domain==None and func_name!="": 
            raise SyntaxError(f"Node {node_name} defined at the graph at the pos {node_pos}.It applies the operator with name ({op_name}) but the operator has not domain and it is not related to any known operator or defined opset. Fix the Node")
        elif domain==None:
            raise SyntaxError(f"Node {node_name} defined at the function {func_name} at the pos {node_pos}. It applies the operator with name ({op_name}) but the operator is not related to any known operator or defined opset. Fix the Node")
    
    #check_func_node(op_name,node,versions,func_data)
    

        
    if is_onnx or is_function:
        
        configs_to_add=__get_opsets_to_add__(op_name,domain_correct,require_opset_versions,import_data,node_name,func_name,node_pos)  
        
    
    if overload_correct!=None:
        result = {"opType":op_name,"domain":domain_correct,"version":version_correct,"overload":overload_correct} 
    else:       
        result={"opType":op_name,"domain":domain_correct,"version":version_correct}
        
    correct=is_function or is_onnx or is_custom

    return correct,result,configs_to_add,(is_function,is_onnx,is_custom)













def __repair_default_node__(node,correct_data,func_name="",node_pos=""):
    
         
    #No esta domain pero la version es igual a la version onnx (onnx_version)
    node_name = ""
    new_overload=None
    old_domain=None
    old_overload=None
    if "name" in node:
        node_name=f"({node["name"]})"
    
    if "domain" in node:
        old_domain=node["domain"]
    
    if "overload" in node:
        old_overload=node["overload"]  
    if  "overload" in correct_data:
        new_overload=correct_data["overload"]
    new_domain=correct_data["domain"]
    
    
    node["version"]=str(correct_data["version"])
      
      
    if old_domain!=None and new_domain!=old_domain :
        if func_name=="":
            warnings.warn(f"\nNode {node_name} defined at the graph at the pos {node_pos}.Its domain ({old_domain}) was changed for correct domain ({new_domain}) ")
        else:
            warnings.warn(f"\nNode {node_name} defined at the function {func_name} at the pos {node_pos}.Its domain ({old_domain}) was changed for correct domain ({new_domain}) ")
    node["domain"]=new_domain    
     
    if new_overload!=None and old_overload!=None and new_overload!=old_overload:
        if func_name=="":
            warnings.warn(f"\nNode {node_name} defined at the graph at the pos {node_pos}.Its function overload ({old_overload}) was changed for correct domain ({new_overload}) ")
        else:
            warnings.warn(f"\nNode {node_name} defined at the function {func_name} at the pos {node_pos}.Its function overload ({old_overload}) was changed for correct overload ({new_overload}) ")
    if new_overload!=None: 
        node["overload"]=new_overload
    

# prerequisite: using repair_opset_and_funcs with data                


def __combine_config_to_add__(all_configs_add:dict,configs_add_local):
    
    for config in configs_add_local:
        key=opset_key(config["domain"],config["version"])
       
        if key not in all_configs_add.keys() and config["force"] :
            #estos son obligatorios
            all_configs_add[key]=config
        
        configs_domain = opset_data_find(all_configs_add,domain=config["domain"])
        if len(configs_domain)==0:
             all_configs_add[key]=config
        if len(configs_domain)>=1:
            max_version = __get_max_version__(configs_domain,"version")
            if max_version<config["version"]:
                all_configs_add= __delete_config_to_add__(all_configs_add,configs_domain)
                all_configs_add[key]=config
                
def __delete_config_to_add__(all_configs_add:dict,list_config:list[dict]):
    for config in list_config:
        key=opset_key(config["domain"],config["version"])
        if not config["force"]:
            del all_configs_add[key]
    return all_configs_add


  
def __repair_node_name__(node,all_names):
    if "name" in node:
        base_name=node["name"]
    else:
        base_name="unnamed"
    
    new_name =create_unique_names(all_names,base_name)    
    all_names.append(new_name)
    
    return new_name
    
def repair_nodes(data):
    from pre_process_module.repair_functions.repair_opsets import repair_opset_and_funcs

    #main graph
    nodes = data["graph"]["node"]
    
    imports = data["opsetImport"]
    func_data=get_functions_data(data)
    
    
    all_initlizer_names=dict()
    get_initializers_names(data["graph"]["initializer"],all_initlizer_names)
    get_initializers_names(data["graph"]["sparseInitializer"],all_initlizer_names,is_sparse=True)
    
    peripherials = get_graph_peripherials(data["graph"])
    sub_graph_metadata={"global_data":data,"graph_names":[data["graph"]["name"]]}
    correct =__repair_nodes_local__(nodes,imports,func_data,initializers=all_initlizer_names,peripherials=peripherials,graph_name=data["graph"]["name"],sub_graph_metadata=sub_graph_metadata)
    iterations=0
    
    while not correct:
        iterations=iterations+1
        repair_opset_and_funcs(data)
        
        correct =__repair_nodes_local__(nodes,imports,func_data,initializers=all_initlizer_names,peripherials=peripherials,graph_name=data["graph"]["name"],sub_graph_metadata=sub_graph_metadata)
        if not correct and iterations==MAX_RECURSIVE:
            raise RuntimeError("Nodes at Graph cannot be repaired")
    
    for function in data["functions"]:
        nodes = function["node"]
        imports = function["opsetImport"]
        
        peripherials = get_graph_peripherials(function)
        
        
        correct =__repair_nodes_local__(nodes,imports,func_data,func_name=function["name"],initializers=all_initlizer_names,peripherials=peripherials,global_func=function,sub_graph_metadata=sub_graph_metadata)
        iterations=0
        while not correct:
            repair_opset_and_funcs(data)
            correct =__repair_nodes_local__(nodes,imports,func_data,func_name=function["name"],initializers=all_initlizer_names,peripherials=peripherials,iterations=iterations,global_func=function,sub_graph_metadata=sub_graph_metadata)
            if not correct and iterations==MAX_RECURSIVE:
                raise RuntimeError(f"Nodes at Function ({function["name"]}) cannot be repaired")                              
    
def __repair_nodes_local__(nodes,imports,func_data,func_name="",graph_name="",initializers=[],peripherials=None,iterations=0,up_element_id="",sub_graph_metadata=None,global_func="",start_error_messege="\n"):
    from pre_process_module.repair_types.repair_attributes import check_attributes
    from pre_process_module.repair_functions.check_functions import get_func_element_id
    
    imports_data = get_opset_data(imports) 

    
    global_data = None
    

    if sub_graph_metadata and "up_metadata" not in sub_graph_metadata:
        up_metadata=dict()
    else:
        up_metadata = sub_graph_metadata["up_metadata"]
        
    if sub_graph_metadata and "global_data" in sub_graph_metadata:
        global_data = sub_graph_metadata["global_data"]
        
    
    all_config_add=dict()
    types_operator_data=[]
    correct_all=True  

    all_names=[]
    input_names=dict()
    output_names=dict()
    
    
    element_id=""
    if func_name!="":
        element_id=f"Func-{get_func_element_id(global_func)}"
        up_metadata[func_name]={"inputs":input_names,"outputs":output_names,"initializers":initializers,"graph_peripherials":peripherials}
    
    if graph_name!="":
        element_id=f"Graph-{graph_name}"
        up_metadata[graph_name]={"inputs":input_names,"outputs":output_names,"initializers":initializers,"graph_peripherials":peripherials}
        
    if up_element_id!="":
        element_id=f"{up_element_id}-{element_id}"
    
    
    
    for idx,node in enumerate(nodes):
        new_name = __repair_node_name__(node,all_names)
        node["name"]=new_name
        
        if not __check_node_fields__(node):
            if func_name!="":
                warnings.warn(f"{start_error_messege}Node number {idx} of function ({func_name}) doesnt follow correct format: It is not a dict. Deleting node ")
            else:
                warnings.warn(f"{start_error_messege}Node number {idx} of the graph ({graph_name}) doesnt follow correct format: It is not a dict. Deleting node ")
            continue
        
        if iterations==0:
            add_connections_to_node_name_lists(node,output_names,input_names,element_id)
        
        if "opType" in node:
            check,correct_data,configs_to_add,type_op=__get_correct_operator_data__(node["opType"],node,imports_data,func_data,func_name=func_name,node_pos=idx)
            
            if not check:
                correct_all=False
                __clean_node__(node,False,start_error_messege=start_error_messege)
                types_operator_data.append(None)
                continue
            
            
            if configs_to_add:
                # version en opset invalida para el operador usado, guardando datos para reparar
                __combine_config_to_add__(all_config_add,configs_to_add)
                
                     
            
            if "overload" in correct_data.keys():
                repairs = {"opType":node["opType"],"domain":correct_data["domain"],"overload":correct_data["overload"],"version":correct_data["version"]}
                __repair_default_node__(node,repairs,func_name,idx)
                
            else:
                repairs = {"opType":node["opType"],"domain":correct_data["domain"],"version":correct_data["version"]}
                __repair_default_node__(node,repairs,func_name,idx)
            types_operator_data.append(type_op)
        else:
            types_operator_data.append(None)
            
        __clean_node__(node,True,start_error_messege)
                
    
    
    
    if len(all_config_add)>0:
        for config in all_config_add.values():
            imports.append({"domain":config["domain"],"version":config["version"]})            
    if len(all_config_add)>0:
        return False
    
    
    
      
    
    
    
    for idx,node in enumerate(nodes):
        
        node["element_id"]=element_id
        func_data_conn = None
        if global_func!="":
            func_data_conn=global_func
        if "opType" in node:
            check_connections_node(node,conn_data=up_metadata,element_id=element_id,
                                   is_onnx=types_operator_data[idx]!= None and types_operator_data[idx][1],
                                   func_data=func_data_conn,
                                   start_error_messege =f"{start_error_messege}nConnections of node of graph {graph_name} at pos {idx} with name ({node["name"]}) have a wrong format {LINE_WITH_TAB}")
            if types_operator_data[idx] and types_operator_data[idx][0]:
                node["func_id"]=build_applies_func_id(node)
                
                get_func_element_id()
                
            if types_operator_data[idx] and types_operator_data[idx][1] :
                node["operator_id"]=build_applies_operator_id(node)
                
            if types_operator_data[idx] and types_operator_data[idx][2]:
                node["custom_id"]=build_applies_operator_id(node)
            
        attributes=[]
        if "attribute" in node:
            attributes=node["attribute"]
        corret_all_att=True
        
        correct_att,corret_all_att=check_attributes(attributes,node,types_operator_data[idx],func_data,element_id=f"{element_id}-Node-{node["name"]}",
                                   subgraph_data={"global_data":global_data,"up_metadata":up_metadata}
                                   ,start_error_messege=f"{start_error_messege} Attributes of node of graph {graph_name} at pos {idx} with name ({node["name"]}) have a wrong format {LINE_WITH_TAB}")
        
        if "metadataProps" in node:
            correct_meta,_ =check_metadata_entries(node["metadataProps"],start_error_messege=f"{start_error_messege}The nodo of graph {graph_name} at pos {idx} with name ({node["name"]}) has a wrong metadata_prop param {LINE_WITH_TAB}",keys=[],element_id=element_id)

            if not correct_meta:
                node["metadataProps"]=[]
        
        
        
        if not corret_all_att or not correct_att:
            correct_all=False
            
            if func_name!="":
                warnings.warn(f"{start_error_messege}Node number {idx} of function ({func_name}) has invalid attribute param.")
            else:
                 warnings.warn(f"{start_error_messege}Node number {idx} of the graph ({graph_name}) has invalid attribute param.")
    
         
               
    if not correct_all:
        raise SyntaxError("While repairng the nodes some error where find on some of the nodes: Operators are invalid or connections are wrong or attributes are invalid. Revise and fix the model")               
    
    return True

def build_applies_operator_id(node):
    
    domain_str=""
    if node["domain"]!="":
        domain_str=f"-domain-{node["domain"]}"
    
    return f"name-{node["opType"]}{domain_str}-v{node["version"]}"
    
def build_applies_func_id(node):
    overload_str=""
    if node["overload"]!="":
        overload_str=f"-overload-{node["overload"]}"
    
    return f"Func-{node["opType"]}-domain-{node["domain"]}{overload_str}"

def __check_sub_graph_fields__(graph,start_error_messege="",graph_names:list[str]=[]):
    if "node" not in graph or not isinstance(graph["node"],list):
            graph["node"]=[]
    if "initializer" not in graph or not isinstance(graph["initializer"],list):
            graph["initializer"]=[]
            
    if "sparseInitializer" not in graph or not isinstance(graph["sparseInitializer"],list):
            graph["sparseInitializer"]=[]
    
    if "name" in graph :
        base_name =graph["name"]
    else:
        base_name="unnamed_graph"   
        
    graph["name"] =create_unique_names(graph_names,base_name)
        
            
    return True



def check_subgraph(subgraph,subgraph_data,start_error_messege="",element_id=""):
    subgraph["element_id"]=element_id
    subgraph["is_subgraph"]=""
    global_data = subgraph_data["global_data"]
    up_metadata = subgraph_data["up_metadata"]
  
  
    __check_sub_graph_fields__(subgraph,start_error_messege=f"{start_error_messege}",graph_names=up_metadata.keys())

    graph_element_id = f"{element_id}-Graph-{subgraph["name"]}"
    
    repair_initializers(subgraph,start_error_messege=f"{start_error_messege} The subgraph defined as an attribute value has a wrong format {LINE_WITH_TAB}")
    
    revise_value_infos_graph(subgraph,element_id=graph_element_id,start_error_messege=f"{start_error_messege} The subgraph defined as an attribute value has a wrong format {LINE_WITH_TAB}")
    
    
    
    imports = global_data["opsetImport"]
    func_data=get_functions_data(global_data)
    
    all_initlizer_names=dict()
    get_initializers_names(subgraph["initializer"],all_initlizer_names,start_error_messege=start_error_messege)
    get_initializers_names(subgraph["sparseInitializer"],all_initlizer_names,is_sparse=True,start_error_messege=start_error_messege)
    peripherials = get_graph_peripherials(subgraph["node"])
    
    if "metadataProps" in subgraph:
        correct_meta,_ =check_metadata_entries(subgraph["metadataProps"],start_error_messege=f"{start_error_messege}The graph {subgraph["name"]} has a wrong metadata_prop param {LINE_WITH_TAB}",keys=[],element_id=element_id)

        if not correct_meta:
            subgraph["metadataProps"]=[]

    __repair_nodes_local__(subgraph["node"],imports,func_data,graph_name=subgraph["name"],peripherials=peripherials,initializers=all_initlizer_names,up_element_id=element_id,sub_graph_metadata=subgraph_data,
                           start_error_messege=f"{start_error_messege}")
    
    check_annotations(subgraph,element_id,start_error_messege = f"{start_error_messege} The quantizationAnnotation of graph ({subgraph["name"]}) has a wrong format {LINE_WITH_TAB}" )
    
    remove_extra_params(subgraph,["input","output","node","name","initializer","sparseInitializer","valueInfo","element_id","metadataProps","docString","quantizationAnnotation","is_subgraph"],
                        f"The subgraph with name ({subgraph["name"]})")
    return True






def __clean_node__(node,correct,start_error_messege=""):
    keep_dims=["opType","domain","overload","version","name","input","output","attribute","docString","metadataProps","is_custom"]
    keep_dims_wrong=["name","input","output","docString","metadataProps"]
    if correct:
        remove_extra_params(node,keep_dims,start_error_messege=f"The node with name ({node["name"]})")
    else:
        remove_extra_params(node,keep_dims_wrong,start_error_messege=f"The node with name ({node["name"]})")
   
def __check_node_fields__(node):
    if not isinstance(node,dict):
        return False
    
            
    return True