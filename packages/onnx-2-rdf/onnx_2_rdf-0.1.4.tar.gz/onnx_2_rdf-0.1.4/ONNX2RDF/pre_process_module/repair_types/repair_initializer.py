from repair_tensor import check_tensor_complex,check_sparse_complex
from warnings_thread_safe import warnings 
from pre_process_module.util_process.util import LINE_WITH_TAB





def repair_initializers(graph,start_error_messege="\n"):
    names=[]
    
    for idx,tensor in enumerate(graph["initializer"]):
        
        
        if "name" in tensor and tensor["name"] not in names:
            name=tensor["name"]
            names.append(name)
            check = check_tensor_complex(tensor,start_error_messege=f"{start_error_messege}Initializer ({name}) at pos {idx} has a wrong format {LINE_WITH_TAB}",tensor_id=f"Graph-{graph["name"]}-Initializer-{name}")
        elif "name" in tensor:
            warnings.warn(f"{start_error_messege}Initializer ({name}) at pos {idx}  Has not unique name -> Initializer Being deleted")
            del graph["initializer"][idx]
            continue
        else:
            warnings.warn(f"{start_error_messege}Initializer at pos {idx}  Has no name -> Initializer Being deleted")
            del graph["initializer"][idx]
            continue
        
        if not check:
            if name:
                warnings.warn(f"{start_error_messege}Initializer ({name}) at pos {idx} -> Initializer  Being deleted")
            else:
                warnings.warn(f"{start_error_messege}Initializer at pos {idx} -> Initializer Being deleted")
            del graph["initializer"][idx]
    
    names=[]
    for idx,tensor in enumerate(graph["sparseInitializer"]):
        
        tmp_name=""
        try:
            tmp_name = tensor["values"]["name"]
        except Exception:
            pass
            
        check = check_sparse_complex(tensor,start_error_messege=f"Sparse Initializer ({tmp_name})  at pos {idx} has a wrong format {LINE_WITH_TAB}",tensor_id=f"Graph-{graph["name"]}-SparseInitializer-{tmp_name}")
        if not check:
            if tmp_name:
                warnings.warn(f"{start_error_messege}Sparse Initializer ({tmp_name}) at pos {idx} -> InitializerBeing deleted")
            else:
                warnings.warn(f"{start_error_messege}Sparse Initializer at pos {idx} -> InitializerBeing deleted")
            del graph["sparseInitializer"][idx]

        if check and tmp_name in names:
            warnings.warn(f"{start_error_messege}Sparse Initializer ({tmp_name}) at pos {idx}  Has not unique name -> Sparse Initializer Being deleted")
            del graph["sparseInitializer"][idx]
        elif check:
            names.append(tmp_name)     
            
        
        
    