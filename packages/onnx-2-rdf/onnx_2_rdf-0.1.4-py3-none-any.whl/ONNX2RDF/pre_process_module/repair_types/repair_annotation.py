from warnings_thread_safe import warnings 
from pre_process_module.util_process.util import remove_extra_params,LINE_WITH_TAB

from repair_metadata_prop import check_metadata_entries

def check_annotations(graph,element_id,start_error_messege=""):
    if "quantizationAnnotation" not in graph:
        return True
    
    annotation = graph["quantizationAnnotation"]
    tensor_name="emoty_name"
    
    if "tensorName" in annotation and not isinstance(annotation["tensorName"],str):
        warnings.warn(f" {start_error_messege} The param \"tensorName\" is not a string -> Deleting optional param ")

    elif "tensorName" in annotation:
        tensor_name=annotation["tensorName"]
        graph["quantizationAnnotation"]["connects"]=""
    
    if not isinstance(annotation,dict):
        warnings.warn(f" {start_error_messege} The quantizationAnnotation is not a dict -> quantizationAnnotation being deleted ")
        graph["quantizationAnnotation"]=[]
        return False
    
    if "quantParameterTensorNames" in annotation:
        correct,_ = check_metadata_entries(annotation["quantParameterTensorNames"],keys=[],element_id=element_id,uri_id="quant_parameter",
                               start_error_messege=f"{start_error_messege} The param \"quantParameterTensorNames\" has a wrong format on its entries")
        if not correct:
            warnings.warn(f"{start_error_messege} The param \"quantParameterTensorNames\" has no entry remaining -> quantizationAnnotation being deleted")
            graph["quantizationAnnotation"]=[]
        else:
            graph["quantizationAnnotation"]["element_id"]=f"{element_id}-tensor_annotation-{tensor_name}"
            remove_extra_params(graph["quantizationAnnotation"],keep_params=["tensorName","quantParameterTensorNames","element_id"],start_error_messege=f"{start_error_messege} The quantizationAnnotation ")
        return correct
    else:
        warnings.warn(f"{start_error_messege} The param \"quantParameterTensorNames\" is missing -> quantizationAnnotation being deleted")
        graph["quantizationAnnotation"]=[]