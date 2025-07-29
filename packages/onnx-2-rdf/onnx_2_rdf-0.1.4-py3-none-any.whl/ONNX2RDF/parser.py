


import argparse
import inspect
import os
import sys
import re



import traceback
from typing import Union
from enum import Enum
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


from warnings_thread_safe import warnings 

from clean_model import process_model as execute_clean_model
from pre_process_module.pre_process import __pre_process__ as execute_pre_process
  
from ruamel.yaml import YAML
from datetime import datetime
import time
import logging

import functools
from pathvalidate import ValidationError,validate_filepath

from json_util import save_json,get_log_paths,remove_files


import threading

LOADED_CACHE = "loaded_model.json"


VALID_CACHE_PARTS=["load-model","pre-process","yamml2rml","mapping","all","None"]
DEFAULT_RESOURCE_BASE_URL="http://base.onnx.model.com/resource/"

DEFAULT_ONNX2RDF_URI="http://base.onnx.model.com#"
DEFAULT_ONNX2RDF_RESOURCE="http://base.onnx.model.com/resource/"


import urllib.request
from pathlib import Path

MAPPER_NAME = "rmlmapper.jar"

JAR_URL = "https://github.com/RMLio/rmlmapper-java/releases/download/v7.3.3/rmlmapper-7.3.3-r374-all.jar"
JAR_PATH = Path(__file__).parent / MAPPER_NAME

def download_rmlmapper_jar(logger):
    if not JAR_PATH.exists():
        logger.info(f"Downloading RMLMapper JAR from {JAR_URL}...")
        JAR_PATH.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(JAR_URL, JAR_PATH)
        logger.info(f"Downloaded to {JAR_PATH}")
    else:
        logger.info(f"RMLMapper JAR already exists at {JAR_PATH}")
    return JAR_PATH



class ErrorsONNX2RDF(Enum):
    NONE_ERROR=0
    LOADING_MODEL = 1
    PREPROCESING_MODEL=2
    YAMML2RML_COPY=3
    YAMML2RML=4
    MAPPING = 5
    WARNING_ON_PREPROCESS = 6
    FILE_NOT_PRESENT=7
    CACHE_FILE_NOT_PRESENT = 8



def setup_logging(log_files=[], to_console=True,error_file=None,id_process="",log_id=""):
    
    handlers = []
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s") 
    console_handler = logging.StreamHandler(sys.stdout)
   
    if not isinstance(log_files,list):
        log_files=[log_files]
    for log_path in log_files:
        
        os.makedirs(os.path.dirname(log_path),exist_ok=True)
        if log_path is not None:
            handlers.append(logging.FileHandler(log_path, mode='w'))   
    if error_file is not None:
            handlers.append(logging.FileHandler(error_file, mode='w'))    
    if to_console:
            handlers.append(console_handler)
    log_code = "onnx_logger"
    if id_process!="":
        log_code=f"onnx_logger_{id_process}"
    if log_id!="":
        log_code=log_id
    logger = logging.getLogger(log_code)
    
    
    level = logging.DEBUG
    set_handlers_format(handlers,formatter)
    
    logger.setLevel(level)
    
    for handler in handlers:
        logger.addHandler(handler)
    
    return logger
      
def set_handlers_format(handlers,formater):
    for handler in handlers:
        handler.setFormatter(formater) 
def cleanup_handlers(logger):
    if logger==None:
        return None
    
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)        
 


def combine_work_folder(work_folder,path,file_name=""):
    if not os.path.isabs(path):
        path = os.path.join(work_folder,path)
        
    if file_name!="":
        path = os.path.join(path,file_name)
    return path

def setup_error_file(error_folder,work_dir,model_name_path):

    error_folder = combine_work_folder(work_dir,error_folder)
    folder_model = model_name_path
    specific_error = os.path.join(error_folder,folder_model)
    os.makedirs(specific_error,exist_ok=True)
 
    log_file_name = "logs.log"  
    error_log_file = os.path.join(specific_error,log_file_name)
    
    return specific_error,error_log_file

import os
def remove_empty_dirs(base_path, target_dir):
    base_path = os.path.abspath(base_path)
    target_path = os.path.abspath(os.path.join(base_path, target_dir)) if not os.path.isabs(target_dir) else os.path.abspath(target_dir)
  
    if os.path.commonpath([base_path, target_path]) != base_path:
        raise ValueError(f"Target path '{target_path}' is not within base path '{base_path}'")

    current = target_path
    while current != base_path and os.path.isdir(current) and not os.listdir(current):
        try:
            os.rmdir(current)
        except OSError:
            break  
        current = os.path.dirname(current)

def remove_folder_rec(folder,work_dir,model_name_path):
    folder = combine_work_folder(work_dir,folder)
    specific_model_folder = os.path.join(folder,model_name_path)
    remove_empty_dirs(folder, specific_model_folder)


def copy_edit_mappings(yarrml_mapping,work_dir,new_path,model_full_uri,id_process="",log_dirs="logs",tmp_dir="tmp/mappings",cache=False):
    
    file_name = "modified_mapping"
    
    if id_process!="":    
        mapping_name = file_name+"_"+str(id_process)
    else:
        mapping_name = file_name
    if not isinstance(log_dirs,list):
        log_dirs=[log_dirs]
    log_file_name=  f"{file_name}.yaml"  
    log_paths=get_log_paths(log_dirs,log_file_name,work_dir)

        
    output_yaml_path = os.path.join(work_dir,tmp_dir,mapping_name+".yaml")
    cache_activated=False
    exists_path=os.path.exists(output_yaml_path)
    if cache and exists_path:
        cache_activated=True
    
    
    if not cache or not exists_path:
    
        yaml_dumper=YAML() 
        yaml_dumper.allow_duplicate_keys = True
        
        with open(yarrml_mapping,'r') as f:
            
            yaml_dumper.preserve_quotes = True
            yaml_f = yaml_dumper.load(f)
            
        for source in yaml_f["sources"].values():
            source["access"]=new_path
        
        yaml_f["prefixes"]["modelR"]=model_full_uri
        
        yaml_f["prefixes"]["base"]=DEFAULT_ONNX2RDF_URI
        
        yaml_f["prefixes"]["baseR"]=DEFAULT_ONNX2RDF_RESOURCE
        
        
            
        os.makedirs(os.path.dirname(output_yaml_path), exist_ok=True)

        with open(output_yaml_path, 'w',) as f :
            yaml_dumper.dump(yaml_f,stream=f)
        
        for log_path in log_paths:
            save_json(yaml_f,log_path)
           
    return output_yaml_path,cache_activated


class RDF_formats(Enum):
    NQUADS = 'nquads'
    TURTLE = 'turtle'
    TRIG = 'trig'
    TRIX = 'trix'
    JSONLD = 'jsonld'
    HDT = 'hdt'



FORMATS_EXTENSIONS = {
        'nquads': '.nq',
        'turtle': '.ttl',  
        'trig': '.trig',
        'trix': '.trix',
        'jsonld': '.jsonld',
        'hdt': '.hdt'
    }
def get_extension(output_format:Union[RDF_formats, str]):
   
    if isinstance(output_format,RDF_formats):
        str_format=output_format.value
    else:
        str_format=output_format
        
    return FORMATS_EXTENSIONS.get(str_format, None)


import subprocess


def parse_args():

    parser = argparse.ArgumentParser(description="Process a ONNX file or folder with ONNX files to RDF files.")
    parser.add_argument("model_path", help="Path to the onnx file to process or folder with multiple files. Path can be absolute or relative.")
    parser.add_argument("--target_path", default="rdfs", help="Directory where rdf files will be stored (default: 'rdfs'). Path can be absolute and in case relative path actual folder or --work_folder will be used")
    parser.add_argument("--rdf_format", default="nquads", help="Available rdf formats (nquads (default), turtle, trig, trix, jsonld, hdt).")
    parser.add_argument("--log_persistant", action=argparse.BooleanOptionalAction, help="(default: Off) If set instead of the logs being dump on the last_execution folder, a new folder with timestamps is created. \nIf --log_extra is executed only the folder with time_stamps gets the extra files")
    parser.add_argument("--log_extra", action=argparse.BooleanOptionalAction, help=" (default: Off) If set, temporary files created during the pipeline will be store within the logs in the folder --log_folder\n If If --log_persistant is executed only the folder with time_stamps gets the extra files.")
    parser.add_argument("--log_folder", default="logs", help="Folder for logs (default: 'logs') Path can be absolute or relative.")
    parser.add_argument('--cache',nargs='*',metavar='PART',help=("Enable caching. Temporary files created --tmp_folder will not be removed and used as cache . "
            "If followed by parts, only caches files created at those processes (default part: 'all') (default : 'None'). Valid parts: "
            + ", ".join(VALID_CACHE_PARTS))
    )
    parser.add_argument("--error_folder", default="errors", help="Temporary folder where files/info used to recreate error.")
    
    
    parser.add_argument("--debug", action=argparse.BooleanOptionalAction, help="If set, instead of temporary files being delted if not otherwise request by cache those files would be stored .")

    parser.add_argument("--tmp_folder", default="tmp", help="Temporary folder where files are created for pipeline execution. Path can be absolute or relative.")
    parser.add_argument("--id_process", default="", help="If set, this id will be added to files created for parallel processing, just for rml mapping.")
    parser.add_argument("--work_folder", default="", help="Change the relative folder for searching models, creating logs folder or rdf folders.")
    parser.add_argument("--stop-parsing",action=argparse.BooleanOptionalAction, help="If set only preprocessing.")
    parser.add_argument("--model_name_path",default=None, help="Model Name use for the URI of the model (\"{base_url}{model_name_path}\"), (default: 'model_path: filename').")
    parser.add_argument("--base_url", default=None, help="Base url of the resources of the model folowing. The URI of the resources will be (\"{base_url}{model_name_path}\"), (default: 'http://base.onnx.model.com/resource/{model_name_path}').")
    parser.add_argument('-v', '--verbose', action=argparse.BooleanOptionalAction,help="The rml mapping will output in verbose mode ")
                        
    parser.add_argument('--extra', nargs='*',metavar='PART',help="Add paths to extra yarrrml or rml files to be executed within the parser. Use it at you own risk. Usfull for adding custom triples to the graph. ")
    parser.add_argument('--to_console',action="store_false",help=" False to desactivate logging on cmd (stdout) (default: true) ")
    return parser.parse_args()


def is_cache_activated(cache,process):
    return cache and isinstance(cache,list) and (process in cache or "all" in cache)



            
def separate_extra_paths(extra_paths,work_dir):
    yarrml_paths=[]
    rml_paths=[]
    for path in extra_paths:
        extension=None
        
        path = combine_work_folder(work_dir,path)
        
        if os.path.isfile(path):
            extension = os.path.splitext(path)[1]
            
            
        if extension ==".yaml":
            yarrml_paths.append(path)
        if extension ==".ttl":
            rml_paths.append(path)
    return yarrml_paths,rml_paths

def is_onnx_file(path):
    return os.path.isfile(path) and path.lower().endswith('.onnx')

from pathlib import Path

FILE_CACHE_SEPARATOR="-.-"

def rebuild_onnx_path(files,cache_path,input_file_path):
    new_files =[]
    for file in files:
        cache_folder = os.path.join(*os.path.dirname(os.path.relpath(file, start=cache_path)).split(FILE_CACHE_SEPARATOR))
        model_name = os.path.basename(cache_folder)
        onnx_original_path = os.path.join(input_file_path,os.path.dirname(cache_folder),f"{model_name}.onnx").replace("\\","/")
        new_files.append(Path(onnx_original_path).resolve())
    return new_files


def get_onnx_file(directory, recursive=False,name_model=None,cache_activated=False,cache_path=""):
    base = Path(directory).resolve()
    base_cache = Path(cache_path).resolve()
    regex_cache =LOADED_CACHE 

    
    regex_onnx ="*.onnx"
    regex=".onnx"
    
    results=[]
    paths=[]
    
    if name_model ==None:
        name_model=os.path.basename(directory)

    if recursive:
        paths = list(base.rglob(regex_onnx))
    else:
        paths = [f for f in base.iterdir() if f.is_file() and f.suffix.lower() == regex]
        
    if cache_activated and recursive:
        paths_c = list(base_cache.rglob(regex_cache))
        paths_c = rebuild_onnx_path(paths_c,cache_path,directory)
        paths = set(paths) | set(paths_c)
    elif cache_activated:
        paths_c = [f for f in base_cache.iterdir() if f.is_file() and f.suffix.lower() == regex_cache]
        paths_c = rebuild_onnx_path(paths_c,cache_path,directory)
        paths = set(paths) | set(paths_c)
        
    for file in paths:
        relative_folder = file.parent.relative_to(base)
        
        file_stem = file.stem  
        if relative_folder.parts:
            identifier = f"{str(relative_folder).replace(os.sep, FILE_CACHE_SEPARATOR)}{FILE_CACHE_SEPARATOR}{file_stem}"
        else:
            identifier = f"{file_stem}"
        
        results.append((f"{name_model}/{identifier}", file.resolve().as_posix()))


    return results



def validate_path_arg(arg_name):
    '''The `validate_path_arg` function is a decorator in Python that validates a function argument
    representing a file path.
    
    Parameters
    ----------
    arg_name
        The `arg_name` parameter in the `validate_path_arg` function is used to specify the name of the
    argument that should be validated as a path. The decorator created by this function will then check
    if the value passed to the specified argument is a non-empty string and a valid file path.
    
    Returns
    -------
        The `validate_path_arg` function returns a decorator function that can be used to validate a
    specific argument in another function. The decorator function performs checks on the specified
    argument to ensure it is a non-empty string and a valid file path. If the argument fails the
    validation checks, a `ValueError` is raised with an appropriate error message.
    
    '''
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            from inspect import signature
            bound_args = signature(func).bind(*args, **kwargs)
            bound_args.apply_defaults()

            path = bound_args.arguments.get(arg_name)
            if not isinstance(path, str) or not path.strip():
                raise ValueError(f"Argument '{arg_name}' must be a non-empty string.")

            try:
                validate_filepath(path)
            except ValidationError as e:
                raise ValueError(f"Invalid path in argument '{arg_name}': {e}")

            return func(*args, **kwargs)
        return wrapper
    return decorator
import signal
import platform
if platform.system().lower() == "windows":
    signals_to_catch = [signal.SIGINT, signal.SIGTERM, signal.SIGBREAK,signal.SIGABRT]
    dump_redirect = "> nul 2>&1"
else:
    signals_to_catch = [
            signal.SIGINT,     # Ctrl+C
            signal.SIGTERM,    # kill <pid> or default docker stop
            signal.SIGQUIT,    # Ctrl+\
            signal.SIGHUP,     # Terminal closed / systemd reload
            signal.SIGABRT,    # abort()
            signal.SIGPIPE     # Broken pipe
        ]
    dump_redirect = "> /dev/null 2>&1"



class ONNX2RDFParser():
    def cleanup(self):
        if hasattr(self,"__console__"):
            cleanup_handlers(self.__console__)
        if hasattr(self,"logger"):
            cleanup_handlers(self.logger)
    def __del__(self):
        self.cleanup()
        
        
    def __init__(self):
        self.target_path="rdfs"
        self.rdf_format:RDF_formats=RDF_formats.NQUADS
        self.log_folder="logs"
        self.log_extra=False
        self.log_persistant=False
        self.error_folder="errors"
        self.cache=[]
        self.debug=False
        self.tmp_folder="tmp"
        self.work_folder=os.getcwd()
        self.stop_parsing=False
        self.verbose=False
        self.to_console=True
        self.__console__ = setup_logging([],to_console=True,log_id="console")
        self._stop=False
        self._original_handler={}
        self._max_ram="2048m"
        
        download_rmlmapper_jar(self.__console__)
        
        
    


    def __signal_handler__(self,signum, frame):
        self.stop()
    def __signal_handler_stop__(self,signum, frame):
        self.stop()
        raise RuntimeError("Stop Program")
    
    def stop(self):
        
        self._stop=True
        
    def __check_is_stoped__(self):
        if self._stop:
            raise RuntimeError("User Stopped Parsing")
        
    def get_parser_heap(self):
        return self._max_ram
    
    def set_parser_heap(self,heap_size:str):
        self._max_ram=heap_size
    
    def set_rdf_format(self,format:Union[RDF_formats, str]):
        
        extension = get_extension(format)
        if extension==None:
            raise ValueError(f"invalid \"rdf_format\" ({format}) only {FORMATS_EXTENSIONS.keys()} are valid")
        if isinstance(format,str):
            self.rdf_format = RDF_formats._value2member_map_[format]
        else:
            self.rdf_format=format
    
    
    def get_rdf_format(self):
        return self.rdf_format
    
    @validate_path_arg('path')
    def set_log_folder(self,path:str):
        self.log_folder=path
    
    def get_log_folder(self):
        return combine_work_folder(self.work_folder,self.log_folder)
    @validate_path_arg('path')
    def set_tmp_folder(self,path:str):
        self.tmp_folder=path
        
    def get_tmp_folder(self):
        return combine_work_folder(self.work_folder,self.tmp_folder)
    @validate_path_arg('path')
    def set_target_path(self,path:str):
        self.target_path=path
    def get_target_path(self):
        return combine_work_folder(self.work_folder,self.target_path)
    @validate_path_arg('path')
    def set_work_folder(self,path:str):
        path = combine_work_folder(os.getcwd(),path)
        self.work_folder=path
        os.makedirs(path,exist_ok=True)
        
    def get_work_folder(self):
        return self.work_folder
    @validate_path_arg('path')
    def set_error_folder(self,path:str):
        self.error_folder=path
        
    def get_error_folder(self):
        return combine_work_folder(self.work_folder,self.error_folder)
    
    def set_log_extra_files(self,option:bool):
        self.log_extra=option
    def set_log_persistant(self,option:bool):
        self.log_persistant=option
    def set_cache_options(self,parts:list[str]):
        
        if isinstance(parts,str):
            parts=[parts]
        
        self.check_cache_param(parts)
        
        self.cache=parts
    def set_debug(self,option:bool):
        self.debug=option
    def set_stop_parsing(self,option:bool):
        self.stop_parsing=option
    def set_verbose(self,option:bool):
        self.verbose=option
    def set_to_console(self,option:bool):
        self.to_console=option
        
    def get_log_extra_files(self):
        return self.log_extra
    def get_log_persistant(self):
        return self.log_persistant
    def get_cache_options(self):
        return self.cache
    def get_debug(self):
        return self.debug
    def get_stop_parsing(self):
        return self.stop_parsing
    def get_verbose(self):
        return self.verbose
    def get_to_console(self):
        return self.to_console
    
    
    
    def check_cache_param(self,cache = None):
        if cache == None or not isinstance(cache,list):
            return False
        
            
        if cache and len(cache) == 0:
            cache_parts = ['all']
        else:
            invalid = [p for p in cache if p not in VALID_CACHE_PARTS]
            if invalid: 
                self.__console__.warning(f"Invalid cache part(s): [{', '.join(invalid)}] Ignoring Value \n Valid Values:{VALID_CACHE_PARTS}")
            cache_parts = [p for p in cache if p in VALID_CACHE_PARTS]    
        if len(cache_parts)<=0:
            cache=False  
        else:
            cache = cache_parts
        return cache    
    
    
    def run_command(self,command):
        proc = subprocess.Popen(command,shell=True)
        try:
            while proc.poll() is None:
                time.sleep(0.5)  
                self.__check_is_stoped__()
        except Exception:
            proc.terminate()
            raise
        
        out, err = proc.communicate()

        if proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode, command, output=out, stderr=err)
        
    def __set_with_args__(self,args):
        self.set_target_path(args.target_path)
        self.set_rdf_format(args.rdf_format)
        self.set_log_persistant(args.log_persistant)
        self.set_log_extra_files(args.log_extra)
        if args.cache==None:
            cache=[]
        else:
            cache=args.cache
        self.set_cache_options(cache)
        self.set_log_folder(args.log_folder)
        self.set_error_folder(args.error_folder)
        self.set_debug(args.debug)
        self.set_tmp_folder(args.tmp_folder)
        self.set_verbose(args.verbose)
        self.set_stop_parsing(args.stop_parsing)
        if args.work_folder and args.work_folder != "":
            self.set_work_folder(args.work_folder)
        self.set_to_console(args.to_console)
        
    @staticmethod
    def __build_setting_report__(run_info):
        #TODO: print variables chosen for parse (example logging.info(cache setting))
        pass 
    @staticmethod    
    def __build_result_report__(errors_found,warnings_caught,run_info:dict,error_type:ErrorsONNX2RDF=ErrorsONNX2RDF.NONE_ERROR):
        run_info_c=run_info.copy()
        run_info_c["global_elapsed_time"]=time.time()-run_info_c["start_time"]
        
        result={"errors_found":errors_found,"warnings_caught":warnings_caught,"run_info":run_info_c,"error_type":error_type}

        return result
    @staticmethod
    def __acumulate_times_report__(key,report:dict,variable):
        acum_variable=variable
        if key in report.keys():
            acum_variable = acum_variable + report[key]
        else:
            acum_variable=-1
        return acum_variable 
    @staticmethod   
    def __build_global_results_report(result_entries,stoped,uris=[]):
        result={"result_entries":result_entries}
        global_found_erros =False
        global_found_warnings=False

        
        load_elapsed_time=0
        preprocess_elapsed_time=0
        yarrr2rml_elapsed_time=0
        rml_parsing_elapsed_time=0
        global_elapsed_time=0
        errors=[] 
        for result_entry in result_entries:
            if "errors_found" in result_entry and result_entry["errors_found"]:
                global_found_erros=True
            if "warnings_caught" in result_entry and result_entry["warnings_caught"]:
                global_found_warnings=True
            load_elapsed_time = ONNX2RDFParser.__acumulate_times_report__("load_elapsed_time",result_entry["run_info"],load_elapsed_time)
            preprocess_elapsed_time = ONNX2RDFParser.__acumulate_times_report__("preprocess_elapsed_time",result_entry["run_info"],preprocess_elapsed_time)
            yarrr2rml_elapsed_time = ONNX2RDFParser.__acumulate_times_report__("yarrr2rml_elapsed_time",result_entry["run_info"],yarrr2rml_elapsed_time) 
            rml_parsing_elapsed_time = ONNX2RDFParser.__acumulate_times_report__("rml_parsing_elapsed_time",result_entry["run_info"],rml_parsing_elapsed_time) 
            global_elapsed_time = ONNX2RDFParser.__acumulate_times_report__("global_elapsed_time",result_entry["run_info"],global_elapsed_time)     
            errors.append(result_entry["error_type"])
        
        result["error_types"]=errors
        result["number_models"]=len(result_entries)
        
        result["load_elapsed_time"]=load_elapsed_time
        result["preprocess_elapsed_time"]=preprocess_elapsed_time 
        result["yarrr2rml_elapsed_time"]=yarrr2rml_elapsed_time
        result["rml_parsing_elapsed_time"]=rml_parsing_elapsed_time
        result["global_elapsed_time"]=global_elapsed_time
               
        result["errors_found"]=global_found_erros
        result["warnings_caught"]=global_found_warnings
        result["stopped"]=stoped
        result["model_uris"]=uris
        return result
    
    def transform_yarrrml_rml(self,mapping_path,extra_mappings,cache=False):
        #TODO add rml file to logging folder if log extra
        
        mapping_dir = os.path.dirname(mapping_path)
        mapping_name = os.path.splitext(os.path.basename(mapping_path))[0]
        ttl_mapping_path = os.path.join(mapping_dir,mapping_name+".ttl")
        cache_activated=False
        exists_file = os.path.exists(ttl_mapping_path)
        if cache and exists_file:
            cache_activated=True
        extra_mapping_str=""
        if len(extra_mappings)>0:
            extra_mapping_str = f"-i {' -i '.join(extra_mappings)}"
        
        if not cache or not exists_file:
            comando = f"yarrrml-parser -i {mapping_path} {extra_mapping_str} -o {ttl_mapping_path} {dump_redirect} "
            self.run_command(comando)
        
        return ttl_mapping_path,cache_activated
    
    
    
    def yarrml2_rdf_pipeline(self,yarrml_path,file_name="result",output_folder="result_extra"):
      
     
        script_path = os.path.dirname(os.path.abspath(__file__))
        rml_parser = os.path.join(script_path,MAPPER_NAME)
        extension = get_extension(self.get_rdf_format())    
        rdf_file_name = file_name+extension
        ttl_file_name = f"{os.path.splitext(os.path.basename(yarrml_path))[0]}.ttl"
        ttl_mapping_path = combine_work_folder(self.work_folder,os.path.dirname(yarrml_path),ttl_file_name)
        output_path = combine_work_folder(self.work_folder,output_folder,rdf_file_name)
        max_ram = self._max_ram

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        os.makedirs(os.path.dirname(ttl_mapping_path), exist_ok=True)
        
        
        
        
        comando = f"yarrrml-parser -i {yarrml_path} -o {ttl_mapping_path} {dump_redirect} "
        self.run_command(comando)
      
        comando = f"java -Xmx{max_ram} -jar {rml_parser} -m {ttl_mapping_path} -o {output_path} -s {self.get_rdf_format().value}"
        self.run_command(comando)
        return output_path
        
    def rml_parsing(self,rml_parser,work_dir,mapping_path,extra_mappings,output_folder="rdf",model_name_path="model",output_format:RDF_formats=RDF_formats.NQUADS,verbose=False):

        
        extension = get_extension(output_format)
        
        
        rdf_file_name = model_name_path+extension
        
        extra_mapping_str=""
        if len(extra_mappings)>0:
            extra_mapping_str = f"-m  {' -m '.join(extra_mappings)}"
        
        
        output_path = combine_work_folder(work_dir,output_folder,rdf_file_name)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        
        max_ram = self._max_ram
        
        comando = f"java -Xmx{max_ram} -jar {rml_parser} -m {mapping_path} {extra_mapping_str} -o {output_path} -s {output_format.value}"
        if verbose:
            comando = comando +" -v"
        self.run_command(comando)
        return output_path
    
    
    
        
    def __pipeline_run__(self,input_file_path,model_name_path=None,base_resource_url=None,id_process="",extra_files=[]):
        
        
        time_stamp = datetime.now()
        start_time= time.time()
        script_path = os.path.dirname(os.path.abspath(__file__))
        rml_parser = os.path.join(script_path,MAPPER_NAME)
        
        to_console=self.to_console
        
        if base_resource_url==None:
            base_resource_url=DEFAULT_RESOURCE_BASE_URL

        
        warning_caught =False
        
        work_folder=self.work_folder
        tmp_folder=self.tmp_folder
        rdf_format = self.rdf_format
        target_path = self.target_path
        log_folder = self.log_folder
        log_extra = self.log_extra
        log_persistant = self.log_persistant
        error_folder = self.error_folder
        cache = self.cache
        debug=self.debug
        verbose=self.verbose
        stop_parsing=self.stop_parsing
        
        
        run_info=dict()
        
        run_info["input_file_path"]=input_file_path
        run_info["work_folder"]=work_folder
        run_info["log_folder"]=log_folder
        run_info["error_folder"]=error_folder
        run_info["tmp_folder"]=tmp_folder
        run_info["datetime"]=time_stamp
        run_info["start_time"]=start_time
        run_info["target_path"]=target_path
        run_info["rdf_format"]=str(rdf_format)
        run_info["id_process"]=id_process
        run_info["verbose"]=verbose!=None
        run_info["cache"]=cache
        run_info["log_extra"]=log_extra
        run_info["extra_paths"]=extra_files
        run_info["model_name_path"]=model_name_path
        
        if extra_files==None:
            extra_files=[] 
        extra_yarrml_paths,extra_rml_paths=  separate_extra_paths(extra_files,work_folder)
        
        
        error_folder_specific, error_log_file = setup_error_file(error_folder,work_folder,model_name_path)
        
        
        if id_process!="":
            log_file_name = f"logs_{id_process}.log"    
            default_log_folder = "last_execution"+"_"+str(id_process)
        else:
            default_log_folder = "last_execution"
            log_file_name = "logs.log"
        
        default_execution_folder = os.path.join(log_folder,default_log_folder) 
        log_dirs=[default_execution_folder]
        if os.path.exists(default_execution_folder):
            remove_files(default_execution_folder)
        
        log_paths=[]
        if log_persistant:
            time_str = time_stamp.strftime(model_name_path+"_%d_%m_%Y_%Hh_%Mmin")
            time_folder = os.path.join(log_folder,time_str)
            log_dirs.append(time_folder)
        log_paths = get_log_paths(log_dirs,log_file_name,work_folder)
          
        self.logger =setup_logging(log_paths,to_console=to_console,error_file=error_log_file,id_process=id_process)
        logger=self.logger
        if not log_extra:   
            log_dirs=[] 
        if log_persistant and log_extra:
            log_dirs=time_folder
        
            
        
            
        
            
        cache = self.check_cache_param(cache)
        if cache or isinstance(cache,list) and len(cache)>0:
            logger.info(f"Cache settings: {cache}")
        else:
            logger.info("Cache settings: Disable")
            cache=[]
            
            
        onnx_tmp_path = os.path.join(work_folder,os.path.join(tmp_folder,model_name_path),LOADED_CACHE)
            
        if not os.path.exists(input_file_path) and not is_cache_activated(cache,"load-model"):
            logger.error(f"Error: The model at path {input_file_path} does not exist and cache is not activated.")
            process_errors(ErrorsONNX2RDF.LOADING_MODEL,specific_error_folder=error_folder_specific,run_info=run_info,logger=logger,stopped=self._stop)
            cleanup_handlers(self.logger)
            
            return self.__build_result_report__(True,warning_caught,run_info,error_type=ErrorsONNX2RDF.FILE_NOT_PRESENT)
        elif not os.path.exists(input_file_path) and not os.path.exists(onnx_tmp_path):
            logger.error(f"Error: The model at path {input_file_path} does not exist neither its cache file.")
            process_errors(ErrorsONNX2RDF.LOADING_MODEL,specific_error_folder=error_folder_specific,run_info=run_info,logger=logger,stopped=self._stop)
            cleanup_handlers(self.logger)
            return self.__build_result_report__(True,warning_caught,run_info,error_type=ErrorsONNX2RDF.CACHE_FILE_NOT_PRESENT)

        cache_execute_load=False

        logger.info(f"ONNX loading/cleaning started | Model:({model_name_path})")
        

        
        start_load=time.time()
        
        
        try:
            self.__check_is_stoped__()
            json_data,cache_execute_load= execute_clean_model(input_file_path,
                                    tmp_path=onnx_tmp_path,
                                    relative_dir=work_folder,
                                    log_dirs=log_dirs,
                                    cache=is_cache_activated(cache,"load-model"))
        except Exception:
            if not self._stop:
                logger.error(f"Loading file of Model:({model_name_path}) got unexcpeted error\n {traceback.format_exc()}")
            process_errors(ErrorsONNX2RDF.LOADING_MODEL,specific_error_folder=error_folder_specific,run_info=run_info,logger=logger,stopped=self._stop)
            cleanup_handlers(logger)   
            return self.__build_result_report__(True,warning_caught,run_info,ErrorsONNX2RDF.LOADING_MODEL)
        run_info["load_elapsed_time"]=time.time()-start_load
        
        
        
        if cache_execute_load:
            logger.info(f"Cache for [load-model] was activated: File '{onnx_tmp_path}' was used")
        
        run_info["onnx_tmp_path"] = onnx_tmp_path
        start_preprocess_time=time.time()
            
        cache_execute_preprocess=False
        
        logger.info(f"ONNX preprocess started | Model:({model_name_path})")
        
        with warnings.catch_warnings(record=True) as w:
            error_found=False
            error_messege=None
            try:
                self.__check_is_stoped__()
                
                self.set_multiple_singal(signals_to_catch,self.__signal_handler_stop__)
                pre_tmp_path,cache_execute_preprocess = execute_pre_process(json_data,
                                        relative_dir=work_folder,
                                        log_dirs=log_dirs,
                                        tmp_dir=os.path.join(tmp_folder,model_name_path),
                                        cache=is_cache_activated(cache,"pre-process"))
                
                self.set_multiple_singal(signals_to_catch,self.__signal_handler__)
            except Exception:
                error_found=True
                error_messege=traceback.format_exc()
            except (BaseException):
                #Keyboard Interrupt or similars
                self._stop=True
            
            
                
            if w and not self._stop:
                
                w_filtered = []
                current_thread = threading.current_thread().name
                
                for warning in w:
                    
                    message_str = str(warning.message)
                    match = re.match(r"^\[([^\]]+)\]\s*(.*)", message_str)
                    thread_name=None
                    if match:
                        thread_name = match.group(1)
                        message = match.group(2)
                    else:
                        message=message_str
                    
                    if thread_name and thread_name ==current_thread:
                        w_filtered.append(message)
                            
                logger.warning(f"ONNX preprocess finish - {len(w_filtered)} warning(s) caught | Model:({model_name_path})")
                warning_caught=True
                
                for warning_messege in w_filtered:

                    logger.warning(f" Preproces Warning | Model:({model_name_path}) {warning_messege}")
            elif not self._stop:
                logger.info(f"ONNX preprocess finish - No warnings were raised | Model:({model_name_path}).")
            if error_found:
                if not self._stop:
                    logger.error(f"Preprocesing file of Model:({model_name_path}) got unexcpeted error\n {error_messege}")
                process_errors(ErrorsONNX2RDF.PREPROCESING_MODEL,specific_error_folder=error_folder_specific,run_info=run_info,logger=logger,stopped=self._stop)
                cleanup_handlers(logger)
                return self.__build_result_report__(True,warning_caught,run_info)
            
        run_info["process_tmp_path"]=pre_tmp_path  
        run_info["preprocess_elapsed_time"]=time.time()-start_preprocess_time   
            
        if cache_execute_preprocess:
            logger.info(f"Cache for [pre-process] was activated: File '{pre_tmp_path}' was used ")
        
        
        cache_activated_copy_edit=False
        
        yarrml_mapping = os.path.join(script_path,"mappings/mapper_yarr.yaml")
        run_info["yarrml_mapping"]=yarrml_mapping
        start_yarrr2rml_time=time.time()
        
        # YARRM_RML PROCESS
        logger.info(f"YARR2_RML started | Model:({model_name_path})")
        
        try:
            self.__check_is_stoped__()
            uri_name = model_name_path.replace(FILE_CACHE_SEPARATOR,".")
            model_uri = f"{base_resource_url}{uri_name}/"
            
            mapping_path,cache_activated_copy_edit = copy_edit_mappings(yarrml_mapping,work_folder,pre_tmp_path,id_process=id_process,
                                                                        log_dirs=log_dirs,
                                                                        cache=is_cache_activated(cache,"yamml2rml"),
                                                                        model_full_uri=model_uri,
                                                                        tmp_dir=os.path.join(tmp_folder,"mappings"))

        except Exception:
            if not self._stop:
                logger.error(f"Modifying the yarrml before transforming of Model:({model_name_path}) got unexcpeted error\n {traceback.format_exc()}")
            process_errors(ErrorsONNX2RDF.YAMML2RML_COPY,specific_error_folder=error_folder_specific,run_info=run_info,logger=logger,stopped=self._stop)
            cleanup_handlers(logger)
            return self.__build_result_report__(True,warning_caught,run_info)
        
        run_info["mapping_path"]=mapping_path 
        cache_activated_yarr2rml=False
        try:
            mapping_rml_path,cache_activated_yarr2rml = self.transform_yarrrml_rml(mapping_path,extra_yarrml_paths,cache=is_cache_activated(cache,"yamml2rml"))
        except Exception:
            
            logger.error(f"Transforming yarrml to rml of Model:({model_name_path}) got unexcpeted error\n {traceback.format_exc()}")
            process_errors(ErrorsONNX2RDF.YAMML2RML,specific_error_folder=error_folder_specific,run_info=run_info,logger=logger,stopped=self._stop)
            cleanup_handlers(logger)
            return self.__build_result_report__(True,warning_caught,run_info)
        run_info["mapping_rml_path"]=mapping_rml_path 
        
        run_info["yarrr2rml_elapsed_time"]=time.time()-start_yarrr2rml_time    
         
            
        files_cache_yaml2rml=[]    
        if cache_activated_copy_edit:
            files_cache_yaml2rml=[mapping_path]
        if cache_activated_yarr2rml:
            files_cache_yaml2rml.append(mapping_rml_path) 
        if len(files_cache_yaml2rml)==1:
            logger.info(f"Cache for [yamml2rml] was activated: File '{files_cache_yaml2rml[0]}' was used ")
        if len(files_cache_yaml2rml)>1:
            logger.info(f"Cache for [yamml2rml] was activated: Files {files_cache_yaml2rml} were used ") 
        
        
        
        start_rml_parsing_time=time.time()
        # MAPPING PROCESS
        if not stop_parsing:
            logger.info(f"RML Parsing started | Model:({model_name_path})")
            try:
                self.__check_is_stoped__()
                output_path = self.rml_parsing(rml_parser,work_folder,mapping_rml_path,extra_rml_paths,target_path,model_name_path,rdf_format,verbose)
                run_info["output_path_rdf"]=output_path
            except Exception:
                if not self._stop:
                    logger.error(f"Mapping rml process of Model:({model_name_path}) got unexcpeted error\n {traceback.format_exc()}")
                process_errors(ErrorsONNX2RDF.MAPPING,specific_error_folder=error_folder_specific,run_info=run_info,logger=logger,stopped=self._stop)
                cleanup_handlers(logger)
                return self.__build_result_report__(True,warning_caught,run_info)
            logger.info(f"Parsing Finished | Model:({model_name_path})")
        else:
            logger.info(f"RML Parsing Skipped --stop-parsing | Model:({model_name_path})")
        run_info["rml_parsing_elapsed_time"]=time.time()-start_rml_parsing_time   

        # Remove temporary files

        
        if not warning_caught and not debug and not is_cache_activated(cache,"pre-process") and os.path.exists(pre_tmp_path):
            try:
                os.remove(pre_tmp_path)
            except Exception:
                pass
     
        if not warning_caught and not debug and not is_cache_activated(cache,"load-model") and os.path.exists(onnx_tmp_path):
            try:    
                os.remove(onnx_tmp_path)
            except Exception:
                pass
        remove_folder_rec(tmp_folder,work_folder,model_name_path)
                
        if not warning_caught and not debug and not is_cache_activated(cache,"yamml2rml"):
            if os.path.exists(mapping_path):
                try:
                    os.remove(mapping_path)
                except Exception:
                    pass
            if os.path.exists(mapping_rml_path):
                try:
                    os.remove(mapping_rml_path)
                except Exception:
                    pass
            mapping_folder = os.path.dirname(mapping_path)
            if os.path.exists(mapping_folder) and is_folder_empty(mapping_folder):
                try:
                    os.rmdir(mapping_folder)
                except Exception:
                    pass
        cleanup_handlers(logger)        
        if not warning_caught and os.path.exists(error_folder_specific):
            remove_files(error_folder_specific)
            remove_folder_rec(error_folder,work_folder,model_name_path)
        
        if warning_caught:
            process_errors(ErrorsONNX2RDF.WARNING_ON_PREPROCESS,specific_error_folder=error_folder_specific,run_info=run_info,logger=logger,stopped=self._stop)
                
        
        return self.__build_result_report__(False,warning_caught,run_info)
    
    def set_multiple_singal(self,signal_types:list[signal.Signals],handle):
        if threading.current_thread() == threading.main_thread():
            for signal_type in signal_types:
                if ONNX2RDFParser.is_signal_editable(signal_type):
                    signal.signal(signal_type,handle)
    def store_original_handlers(self,signal_types:list[signal.Signals]):
        for signal_type in signal_types:
            self._original_handler[signal_type]=signal.getsignal(signal_type)
    @staticmethod       
    def is_signal_editable(signal_type):
        value = None
        if isinstance(signal_type,signal.Signals):
            value = signal_type.value
        if isinstance(signal_type,int):
            value = signal_type
        return value and value!=9 and value!=19
        
    def restore_multiple_singal(self,signal_types:list[signal.Signals]):
        if threading.current_thread() == threading.main_thread():
            for signal_type in signal_types:
                if ONNX2RDFParser.is_signal_editable(signal_type):
                    signal.signal(signal_type,self._original_handler[signal_type]) 


    def parse_file(self,model_path,model_name=None,base_resource_url=None,id_process="",extra_files=[]):
        result_entries=[]
        try:
            
            error_if_no_java()
            
            self.store_original_handlers(signals_to_catch)
            self.set_multiple_singal(signals_to_catch,self.__signal_handler__)
            
            cache = self.check_cache_param(self.cache)
            
            
            work_folder=self.work_folder
            input_file_path = combine_work_folder(work_folder,model_path)
                
            if os.path.isdir(input_file_path):
                if model_name==None:
                    cache_path = os.path.join(work_folder,self.tmp_folder,os.path.basename(input_file_path))
                else:
                    cache_path = os.path.join(work_folder,self.tmp_folder,model_name)
                onnx_files = get_onnx_file(input_file_path,recursive=True,name_model=model_name,cache_activated=is_cache_activated(cache,"load-model"),cache_path=cache_path)
                
                if len(onnx_files)==0 and not is_cache_activated(cache,"load-model"):
                    raise ValueError(f"No .onnx files found at {input_file_path}")
                elif len(onnx_files)==0:
                    raise ValueError(f"No loaded_model.json cache file or .onnx files found at tmp folder at folder or input_folder {cache_path}")
            else:
                
                file_name = os.path.splitext(os.path.basename(input_file_path))[0]
                
                
                if model_name==None:
                    cache_path = os.path.join(work_folder,self.tmp_folder,file_name,LOADED_CACHE)
                else:
                    cache_path = os.path.join(work_folder,self.tmp_folder,model_name,file_name,LOADED_CACHE)
                
                is_onnx =not is_onnx_file(input_file_path)
                if is_onnx and not is_cache_activated(cache,"load-model"):
                    raise ValueError(f" model_path ({input_file_path}) is not a .onnx file")
                elif is_onnx and not os.path.exists(cache_path):
                    raise ValueError(f" model_path ({input_file_path}) is not a .onnx file and there is not cache file")
                
                
                if model_name==None:
                    model_name_path=os.path.join(file_name)
                else:
                    model_name_path=os.path.join(model_name)
                model_name_path = model_name_path.replace("\\","/")  
                onnx_files = [(model_name_path,input_file_path)]

            
            if base_resource_url==None:
                base_resource_url=DEFAULT_RESOURCE_BASE_URL
            result_entries = []    
                
            try:
                for onnx_file in onnx_files:
                    result_entry = self.__pipeline_run__(input_file_path=onnx_file[1],
                                        model_name_path=onnx_file[0],
                                        id_process=id_process,
                                        base_resource_url=base_resource_url,
                                        extra_files=extra_files)
                    
                    result_entries.append(result_entry)
                    if self._stop:
                        self.logger.error("ONXX2RDF Parser Stopped Cleanly (It can return None)")
                        break
            except Exception:
                if hasattr(self,"logger"):
                    cleanup_handlers(self.logger)
                raise
            uris = __get_all_uri_models__(onnx_files)    
                
            cleanup_handlers(self.logger)
            
            if result_entries==[]:
                return {"stopped":True}
            return self.__build_global_results_report(result_entries,self._stop,uris)
        except (BaseException):
            
            
            self.restore_multiple_singal(signals_to_catch)
            if self._stop:
                self.__console__.error("ONXX2RDF Parser Stopped Abruptly")
            else:
                self.__console__.error(f"ONXX2RDF Parser got unexcpeted error\n {traceback.format_exc()}")
            if hasattr(self,"logger"):
                cleanup_handlers(self.logger)
            if not result_entries:
                return {"stopped":True}
            
            return self.__build_global_results_report(result_entries,True)
            
            
            
def __get_all_uri_models__(onnx_files):
    uris=[]
    for onnx_file in onnx_files:
        path = onnx_file[0].replace(FILE_CACHE_SEPARATOR,".")
        uris.append(path)   
    return uris
        


def is_folder_empty(path):
    return not any(os.listdir(path))




    
  


import shutil



def process_errors(error_type:ErrorsONNX2RDF,specific_error_folder,run_info=None,logger=None,stopped=False):
    
    try:
        meta_file_path = os.path.join(specific_error_folder,"error_data.json")
        
        meta_data ={"name":run_info["model_name_path"],"error_type":error_type.name,"datetime":run_info["datetime"].strftime("%H_%M_%d_%m_%Y"),"paths":
            {"work_folder":run_info["work_folder"],"log_folder":run_info["log_folder"],"temporary_folder":run_info["tmp_folder"],
            "error_folder":run_info["error_folder"],"rdf_path":run_info["target_path"]},"verbose":run_info["verbose"],"cache":run_info["cache"],
            "extra_paths":run_info["extra_paths"]}
        
        
        meta_data["loading_model"]={"model_path":run_info["input_file_path"]}
        
        
        if error_type.value>1:
            new_path = os.path.join(specific_error_folder,LOADED_CACHE)
            file_info = {"original_path":run_info["onnx_tmp_path"],"report_path":new_path}
            meta_data["loading_model"]["result_loading"] = file_info
            shutil.copy2(run_info["onnx_tmp_path"], new_path)
            meta_data["pre_process"]={"loaded_model_path":file_info}
            
        if error_type.value>2:
            
            new_path = os.path.join(specific_error_folder,"preprocess_model.json")
            file_info = {"original_path":run_info["process_tmp_path"],"report_path":new_path}
            meta_data["pre_process"]["result_preprocess"] = file_info
            shutil.copy2(run_info["process_tmp_path"], new_path)
            
            new_path = os.path.join(specific_error_folder,"mapping.yamml")
            file_info_yamml = {"original_path":run_info["yarrml_mapping"],"report_path":new_path}
            shutil.copy2(run_info["yarrml_mapping"], new_path)
            meta_data["copy_mapping"]={"preproces_model_path":run_info["process_tmp_path"],"id_process":run_info["id_process"],
                                    "yarrml_mapping":file_info_yamml}

            
        if error_type.value>3: 
            
            
            new_path = os.path.join(specific_error_folder,"modified_mapping.yamml")
            file_info = {"original_path":run_info["mapping_path"],"report_path":new_path}
            meta_data["copy_mapping"]["result_edit_mapping"] = file_info
            shutil.copy2(run_info["mapping_path"], new_path)
            
            meta_data["yamml2rml"]={"modified_mapping_path":file_info}

            
        if error_type.value>4:
            new_path = os.path.join(specific_error_folder,"modified_mapping.rml")
            file_info = {"original_path":run_info["mapping_rml_path"],"report_path":new_path}
            meta_data["yamml2rml"]["result_rml"] = file_info
            
            file_info_json = {"original_path":run_info["process_tmp_path"],"report_path":new_path}
            shutil.copy2(run_info["mapping_rml_path"], new_path)
            
            meta_data["rml_mapping"]={"rml_mapping":file_info,"preprocess_data":file_info_json,"rdf_format":run_info["rdf_format"]}
        
        if error_type.value>5:
            file_info = {"original_path":run_info["output_path_rdf"]}
            meta_data["rml_mapping"]["result_mapping"] = file_info
            
        if stopped:
            if logger:
                logger.info("Error by Stopped Program")
            meta_data["stopped"]=True
          
        save_json(meta_data,meta_file_path)
    except Exception:
        logger.error(f"Unexcpected Error trying to document and error ,{traceback.format_exc()}")
        
        



def call_main_with_args():
    # Obtener los argumentos desde la línea de comandos
    args = parse_args()
    
    parser  = ONNX2RDFParser()
    
    parser.__set_with_args__(args)
    
    parser.parse_file(args.model_path,args.model_name_path,args.base_url,args.id_process,args.extra)
    


if __name__ == "__main__":
    
    # Ejecutar la función call_main_with_args solo cuando se ejecuta como script
    call_main_with_args()



def error_if_no_java():
    try:
        subprocess.run(["java", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except Exception:
        raise RuntimeError("⚠️ WARNING: Java (OpenJDK) not found. This package may not work correctly without Java.")