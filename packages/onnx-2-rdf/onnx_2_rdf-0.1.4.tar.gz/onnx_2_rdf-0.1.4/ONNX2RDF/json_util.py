import os
import json


def get_log_paths(log_dirs,log_file_name,work_dir):
    log_paths=[]
    if not isinstance(log_dirs,list):
        log_dirs=[log_dirs]
        
    for log_dir in log_dirs:
        
        if os.path.isabs(log_dir):
            log_path = os.path.join(log_dir,log_file_name)
        else:
            log_path = os.path.join(work_dir,log_dir,log_file_name)
        log_paths.append(log_path)
    return log_paths

def save_json(json_file,path):

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path,"w") as report:
        json.dump(json_file,report,indent=4,default=str)
    
def load_json(path):
    if os.path.exists(path):
        with open(path,"r") as report:
         return json.load(report)
    raise ValueError(f"Path {path} doesnt exit")
    
def remove_files(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
