from pre_process_module.util_process.operators import is_domain_ONNX,get_domain_ONNX_version,is_onnx_operator
from pre_process_module.util_process import ONNX_DOMAIN    
from pre_process_module.util_process.operators import is_opertor_list_func_type,is_register_domain,is_register_operator

from pre_process_module.util_process.data import get_opset_data,function_data_find,opset_data_find,get_functions_data,opset_key,function_key
from warnings_thread_safe import warnings 
from check_functions import repair_function,check_fields_functions
from pre_process_module.util_process.util import remove_extra_params

def repair_opset_and_funcs(data):
    '''The `repair_opset_and_funcs` function in Python is designed to repair and validate opset and
    function data structures by checking for duplicates, missing fields, and conflicting domain
    versions.
    
    Parameters
    ----------
    data
        The `repair_opset_and_funcs` function seems to be a complex function that deals with repairing and
    validating data related to opsets and functions. It performs various checks and repairs on the input
    data to ensure consistency and correctness.
    
    '''
   
    
    
    func_data = __repair_global_opset__(data)
    global_import = get_opset_data(data["opsetImport"])
    add_opset_element_id(data["opsetImport"])
    
    
    for function in data["functions"]:
        __repair_local_opset__(function["opsetImport"],function["name"],func_data,global_import)
        add_opset_element_id(function["opsetImport"])
        
    
def add_opset_element_id(opsets):
    for opset in opsets:
        if opset["domain"]=="":
            opset["element_id"]=f"v{opset["version"]}" 
        else:
            opset["element_id"]=f"domain-{opset["domain"]}-v{opset["version"]}"       
              
        
def __repair_local_opset__(local_import,func_name,func_data,global_import):
    
    domains_opset={}
    
    
    #revisamos opsets locales a funcion buscando duplicados o valores incorrectos
    for idx,opset in enumerate(local_import):
        if __is_non_existance_opset__(opset):
            del local_import[idx]
            continue
        
        __put_onnx_domain__(opset)
        if is_domain_ONNX(opset["domain"]) and "version" not in opset:
            opset["version"]=get_domain_ONNX_version(opset["domain"])
        if not __process_duplicate_opset__(opset,domains_opset):
            del local_import[idx]
            continue
        
        if not __repair_opset__(opset,func_data,func_name=func_name,global_import=global_import):
            del local_import[idx]
            continue
         # no existe ninguna funcion con el dominio -> estamos tratando con un opset que no hace referencia a ningun dominio onnx o funcion
        
        remove_extra_params(opset,keep_params=["domain","version","element_id"],start_error_messege=f"The opset at pos {idx}")   
    __add_base_onnx_opset__(local_import,domains_opset)

def __repair_global_opset__(data):
    
    domains_opset={}
    all_domains=[]
    
    functions_repeat={}
    
    
    # eliminar opsets duplicados con misma version
    # dominio no existente -> dominio ""
    # se guardan los dominios en all_domains
    
    for idx,opset in enumerate(data["opsetImport"]):
        if __is_non_existance_opset__(opset):
            del data["opsetImport"][idx]
            continue
        __put_onnx_domain__(opset)
        
        if is_domain_ONNX(opset["domain"])  and "version" not in opset:
            opset["version"]=get_domain_ONNX_version(opset["domain"])
        elif "version" not in opset:
            opset["version"]="1"
        
        if not __process_duplicate_opset__(opset,domains_opset):
            del data["opsetImport"][idx]
            continue
        if opset["domain"] not in all_domains:
            all_domains.append(opset["domain"])
        remove_extra_params(opset,keep_params=["domain","version","element_id"],start_error_messege=f"The opset at idx {idx}")
        
            
    # onnx domain (base) siempre se incluye si es posible 
    
    __add_base_onnx_opset__(data["opsetImport"],domains_opset)   
            
    
    #revisamos dominios respecto a funciones que tengan las versiones correctas entre si
    # - funciones con nombres de operadores onnx (mas concretamente si son no funcionales (tipo concreto OPERADOR ONNX) ) y el dominio onnx ->invalido
    # - funciones sin nombre -> invalido (añadir un nombre nuevo no seria valido ya que no existirian nodos del grafo que 
    # referencien a esta funcion)
    # - funciones no son un dict ->invalido
    
    # introducimos domian/version de funciones en import opset si no puesto anteriormente (solamente si no son posibles operadores onnx)
    # añadimos dominio nuevo en caso de faltante (solo en el caso que el )

        
            
    #revisamos las funciones
  
    
    
    for idx,function in enumerate(data["functions"]):
        
        if not isinstance(function, dict):
            warnings.warn(f"Function number {idx} has a incorrect format -> function {idx} is being remove",category=SyntaxWarning)
            del data["functions"][idx]
            
            continue
        
        
        if "name" not in function :
            warnings.warn(f"Function number {idx} has no name it cannot be identified -> function {idx} is being remove",category=SyntaxWarning)
            del data["functions"][idx]
            
            continue
        
        
        
        name = function["name"]
        
        domain=None
        
        
        
        if "domain" in function:
            domain = function["domain"]
        
        opsets_filter_domain = opset_data_find(domains_opset,domain)
        
        # Eliminamos
        func_operators=[]
        if "domain" in function and is_register_domain(function["domain"]):
            check=False
            
            check,func_operators = is_function_contradictory(name,domain,domains_opset)
            
            if check:
                warnings.warn(f"\nFunction number {idx} with name {name} and domain {domain} Enters with conflict with predefined operators. \n"+
                              f"(which are not Function type and cannot have function implementation) -> Function number {idx} is being remove")
                del data["functions"][idx]
                
                continue
        
        if "domain" not in function and is_register_operator(name):
            check=False
            
            check,func_operators = is_function_contradictory(name,domains_opset=domains_opset)
            
            if check:
                warnings.warn(f"\nFunction number {idx} with name {name} and no domain Enters with conflict with predefined operators. \n"+ 
                              f"(which are not Function type and cannot have function implementation) ->Function number {idx} is being remove")
                del data["functions"][idx]
                
                continue
                
        # añadimos overload vacio en caso de que no exista
        if 'overload' not in function:
            function['overload'] = ""
            overload = ""
        else:
            overload = function['overload']
        
        if "domain" in function and function_key(domain,name,overload) in functions_repeat.keys():    
            warnings.warn(f"\nGRAVE WARNING: Function number {idx} with name {function["name"]} has same domain/name/overload than other defined function ->the second instance is remove")
            
            del data["functions"][idx]
            continue
        
        
        
        if len(func_operators)>0:
            #TODO: caso raro estamos antes funcion que tiene el mismo nombre que un operador predefinido y puede que tenga una 
            # reimplementacion del metodo pero usando una funcion
            __revised_funcion_onnx_incompatible__(data,function)
            # por ahora simplemente borramos la funcion
            warnings.warn("TODO: operadores funcionales y caso de implementacion con su nombre")
            del data["functions"][idx]
            
            continue
           
            
         
        # Añade el dominio y version en opset_imports ya que faltaba (para funciones)
        
        if "domain" in function and len(func_operators)==0 and len(opsets_filter_domain)==0:
            #Add missing domains at opset import for only custom functions   
            new_entry={"domain":function["domain"],"version":"1"}
            data["opsetImport"].append(new_entry)
            domains_opset[opset_key(domain,1)]=new_entry
            

    
        if "domain" in function and len(func_operators)==0:
            # las funciones no deberian tener la version como parametro no obstante lo vamos a añadir/reescribir para que el mapping sea correcto
            # usaremos los valores del opset existente y en caso que no haya version pondremos la version a 1
            new_version=1
            
            
            opsets:dict = opset_data_find(domains_opset,domain=function["domain"])
            
            
            if len(opsets)==0:
                # domain no in domains_opsets this case should not be possible
                warnings.warn("Unexpected case, when obtaining version for functions")
                del data["functions"][idx]
                
                continue
             
            if len(opsets)==1:
                new_version = opsets[0]["version"]
                
            if len(opsets)>1:
                max_version=None
                idx_opset=None
                for idx,opset in enumerate(opsets):
                    if not max_version:
                        max_version=opset["version"]
                        idx_opset=idx
                    else:
                        max_version=max(opset["version"],max_version)
                        #TODO: verificar del opsets correctly
                        del opsets[idx_opset]
                        warnings.warn("Duplicate opsets with difference versions for user functions are not allowed, as we "+
                                      "we cannont identified specific domain the function relates to we have chose the hightest version delete the others ")
                        idx_opset=idx
            
        
            function['version']=new_version
            
        if "domain" in function and function["domain"] not in all_domains:
            #guardamos el dominio de la funcion en caso que no existiese en all_domains
            #TODO: revisar que no entra en conflicto con el caso raro de func_operators
            all_domains.append(function["domain"])
            
        if  "domain" not in function and len(func_operators)==0:
            #no es un operador pero le falta dominio a la funcion
            # añadimos un nuevo dominio que no exista en la lista de all_domains y añadimos su version a 1
            __new_domain_func__(all_domains,data,function)
            
        if "domain" in function and "overload" in function:    
            functions_repeat[function_key(function["domain"],function["name"],function["overload"])]=function
        
        
        
        if not repair_function(function,idx):
            del data["functions"][idx]
            
            continue
        
        
        opset_id =f"v{function['version']}"
        if function['domain']!="":
            opset_id=f"domain-{function['domain']}-{opset_id}"
        function["opset_id"]=opset_id
            
        remove_extra_params(function,keep_params=["name","domain","overload","version","opsetImport","input","output",
                                                  "attribute","attributeProto","metadataProps","docString","opset_id",
                                                  "valueInfo","node","element_id"],start_error_messege=f"The Function ({function["name"]})")  
    
    func_data = get_functions_data(data)
  
    # reparar el resto de opsets 
    
    return func_data




def __is_non_existance_opset__(opset):
    if "domain" not in opset and "version" not in opset:
        warnings.warn("Opset with no domain or version is being delete")
        return True
    return False

def __add_local_results_operators__(operators_local,operators):
    for operator in operators_local:
            operators.add(operator)

def __revised_funcion_onnx_incompatible__(data,function):
    #TODO: revised if function is valid with same name/domain than ONNX operators
    pass

def is_function_contradictory(name,domain=None,domains_opset=None,ignore_func_operators=False):
    '''The function `is_function_contradictory` checks for contradictions in function names and domains.
    
    Parameters
    ----------
    name
        The `name` parameter represents the name of the function for which you want to check for
    contradictions.
    domain
        The `domain` parameter typically refers to the set of input values for a function. It specifies the
    valid inputs that the function can accept.
    domains_opset
        The `domains_opset` parameter likely refers to a set of domains that the function operates on or is
    defined for. This parameter is used to check for contradictions in the function's domain. If you
    provide the specific domains in the `domains_opset` parameter, the function `is_function_contrad
    
    Returns
    -------
        The function `is_function_contradictory` is returning the result of either
    `__is_function_domain_contradictory__` or `__is_function_name_contradictory__` based on the
    conditions provided.
    
    '''
    if domain!=None and domains_opset:
        return __is_function_domain_contradictory__(name,domain,domains_opset,ignore_func_operators=ignore_func_operators)      
    else:
        return __is_function_name_contradictory__(name,ignore_func_operators=ignore_func_operators)

def __is_function_domain__multiple_version_contradictory__(name,domain,opsets:dict):
    operators=set()
    for opset in opsets:
        version = opset["version"]
        _,operators_local = is_onnx_operator(name,domain,version)
        __add_local_results_operators__(operators_local,operators)
    return len(operators)>0,operators  
 
 
 
def __is_function_domain_contradictory__(name,domain,domains_opset,ignore_func_operators=False):
    
    opsets = opset_data_find(domains_opset,domain)
    check=False
    func_operators=[]
    
    if len(opsets)==1:
        version = opsets[0]["version"]
        check,operators = is_onnx_operator(name,domain,version)
        
    if len(opsets)>1:
        check,operators = __is_function_domain__multiple_version_contradictory__(name,domain,opsets)   
    
    if len(opsets)==0:
        # compruebo respecto a todos los operadores registrados independientemente de la version
        check,operators = is_onnx_operator(name,domain)    
        
    # caso especial que sea un operador 
    
    if not ignore_func_operators:
        return check,operators
    
    if check:
        is_func,func_operators = is_opertor_list_func_type(operators)
        check = not is_func # si el
        
    return check,func_operators

def __is_function_name_contradictory__(name,ignore_func_operators=False):
    check,operators = is_onnx_operator(name)
    if not ignore_func_operators:
        return check,operators
    
    if check:
        is_func,func_operators = is_opertor_list_func_type(operators)
        check = not is_func
    return check,func_operators
    

            
                         
def __repair_opset__(opset,func_data,func_name=None,global_import=None):
    

    if "domain" in opset and "version" not in opset and not is_domain_ONNX(opset["domain"]) and len(function_data_find(func_data,domain=opset["domain"]))==0:
        
        if func_name:
            warnings.warn(f"\nDominio {opset["domain"]}, definido en el opset de la funcion {func_name} le faltaba el atributo version y el dominio no es conflictivo -> la version es 1 ahora")
        else:
            warnings.warn(f"\nDominio {opset["domain"]}, definido en el grafo le faltaba el atributo version y el dominio no es conflictivo -> la version es 1 ahora")
        opset["version"]=1
    
    if "domain" in opset and "version" not in opset and len(function_data_find(func_data,domain=opset["domain"]))>0:
        
            
        # import_meta_global contiene informacion de opsets en el nivel global
        
        possible_list = opset_data_find(global_import,domain=opset["domain"])
        # solo hay una combinacion dominio/version
        if len(possible_list)==0 and func_name:
            warnings.warn(f"\nDominio {opset["domain"]}, definido en el opset de la funcion {func_name} no tenia version. El dominio hace referencia a una funcion que existe en la lista de funciones"+
                                " no obstante el dominio no aparece en la lista de opsets global (no es un dominio de una funcion existente).\n Borrando opset entry conflictiva ")
            return False
            
    
        if len(possible_list)==1 and func_name:
            opset["version"]=possible_list[0]["version"]
        
        
        if len(possible_list)>1 and func_name:
            warnings.warn(f"\nDominio {opset["domain"]}, definido en el opset de la funcion {func_name} no tenia version.El dominio hace referencia a una funcion que existe en la lista de funciones"+
                                " no obstante el dominio aparece mas de una vez con versiones distintas (distintas versiones para la misma funcion).\n Borrando opset entry conflictiva ")
            return False
    return True


# crear dominio que no exista en all_domains y añadirlo en el opset_import            
def __new_domain_func__(all_domains,data,function):
    
    idx=1
    new_domain = f"undefined_domain_{idx}"
    
    while(new_domain in all_domains):
        idx=idx+1
        new_domain = f"undefined_domain_{idx}"
    
   
    function["version"]=1     
    new_entry={"domain":new_domain,"version":1}
    data["opsetImport"].append(new_entry)
    function["domain"]=new_domain
    
    all_domains.append(new_domain)          
            
                    

def __put_onnx_domain__(opset):
    if "version" in opset and "domain" not in opset:
        opset["domain"]=ONNX_DOMAIN
        

def __process_duplicate_opset__(opset,domains_opset):
    

    #intentamos eliminar duplicados en los opsets
    
    
    domain=opset["domain"]
    version=opset["version"]
      
    if domain!=None not in domains_opset.keys():
        
        domains_opset[opset_key(domain,version)]=opset
    else:
        warnings.warn("Opset repetidos con mismo domain/version borrando opset repetido")
        return False
    return True
        
                 

def __add_base_onnx_opset__(opset_field,domains_opset):
    
            
    # onnx domain (base) siempre se incluye si es posible
    
    opsets_list = opset_data_find(domains_opset,"")
    if len(opsets_list)==0:
        new_entry= {"domain":"","version":get_domain_ONNX_version(ONNX_DOMAIN)}
        opset_field.append(new_entry) 
        domains_opset[ONNX_DOMAIN]=new_entry 
     
  
   # repairs and checks for all opsetImports on the onnx json file 
