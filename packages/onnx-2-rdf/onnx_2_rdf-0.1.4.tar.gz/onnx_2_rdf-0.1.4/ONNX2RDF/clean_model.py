

from onnx import load_model
import os
from google.protobuf.json_format import MessageToJson
import json
from json_util import save_json,load_json,get_log_paths


def clear_weight_params(tensor):
    
    tensor.ClearField("float_data")
    tensor.ClearField("int32_data")
    if tensor.string_data !=[]:
        tensor.raw_data = ""
    tensor.ClearField("int64_data")
    if tensor.raw_data !=[]:
        tensor.raw_data = b""
    tensor.ClearField("double_data")
    tensor.ClearField("uint64_data")

    

def load_graph_onnx(model_path):
    model = load_model(model_path,load_external_data=False)
    
    for tensor in model.graph.initializer:
        clear_weight_params(tensor)
    for sparse_init in model.graph.sparse_initializer:
        clear_weight_params(sparse_init.indices)
        clear_weight_params(sparse_init.values)
    
    return model


def convert_json(onnx_model):
    s = MessageToJson(onnx_model)
    onnx_json = json.loads(s)
    return onnx_json



    
from datetime import datetime
def process_model(model_path,tmp_path,relative_dir="",log_dirs="logs",cache=False):
    file_name="loaded_model.json"
    if not isinstance(log_dirs,list):
        log_dirs=[log_dirs]
    log_paths=get_log_paths(log_dirs,file_name,relative_dir)
  
            
    is_in_cache = os.path.exists(tmp_path)
            
    if not cache or (not is_in_cache):
        if cache and not os.path.exists(model_path):
            raise ValueError("Cache was activated, but neither cache file or model file were present")
       
        onnx_model = load_graph_onnx(model_path)
        onnx_json = convert_json(onnx_model) 
        
        for log_path in log_paths:
            save_json(onnx_json,log_path)
        
        if not (cache and is_in_cache):
            save_json(onnx_json,tmp_path)
        
                
               
    executed_cache=False        
    if cache and is_in_cache:
        onnx_json = load_json(tmp_path)
        executed_cache=True
        
                  
    return onnx_json,executed_cache