import re
import warnings

from collections import defaultdict
from huggingface_hub import hf_hub_download,list_repo_files,get_hf_file_metadata,hf_hub_url,model_info
import huggingface_hub.file_download as file_download
from huggingface_hub.hf_api import ModelInfo
import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))


from pathlib import Path
from huggingface_hub._local_folder import _short_hash
import huggingface_hub


os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

import logging
from logging import Logger
import argparse
from typing import Union


from pathvalidate import ValidationError,validate_filepath
from huggingface_hub import HfApi
import functools
import random
import pandas as pd
from datetime import datetime
import time
import psutil
from ONNX2RDF.parser import ErrorsONNX2RDF
import numpy as np
import traceback

import pickle


import tqdm as tq
import huggingface_hub.file_download as file_download
from contextlib import nullcontext

from utils_hugg import SelectedMethods


import signal
from  requests.exceptions import ConnectionError as conn_err
from HuggingFaceMetadataParser import created_metadata_json,edit_copy_mappings,delete_meta_files
import platform

import concurrent.futures



if platform.system().lower() == "windows":
    signals_to_catch = list(signal.valid_signals())
else:
    signals_to_catch = [
            signal.SIGINT,     # Ctrl+C
            signal.SIGTERM,    # kill <pid> or default docker stop
            signal.SIGQUIT,    # Ctrl+\
            signal.SIGHUP,     # Terminal closed / systemd reload
            signal.SIGABRT,    # abort()
            signal.SIGPIPE     # Broken pipe
        ]


connection_error ="Connection to HuggingFace is down. Stoping program. Try in other moment"



def long_task(x):
    time.sleep(10)  # Simulate long computation
    return x * x





    




    


def is_notebook() -> bool:
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True   # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False      # Probably standard Python interpreter


def patch_hf_progress(shared_bar):
    original = file_download._get_progress_bar_context

    def patched(*args, **kwargs):
        return nullcontext(shared_bar)

    file_download._get_progress_bar_context = patched
    return original

def unpatch_hf_progress(original):
    file_download._get_progress_bar_context = original
    
def str_to_bool(s: str):
    return {"true": True, "false": False}.get(s.strip().lower(), False)


def __load_pickle__(path):
    with open(path, "rb") as f:
        return pickle.load(f)

def __dump_pickle__(path,data):
    with open(path, "wb") as f:
        pickle.dump(data, f)    
    

def __dump_json__(path,data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4,default=str)
            
def __load_json__(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    

def __validate_path_arg__(arg_name):
    '''The `__validate_path_arg__` function is a decorator in Python that validates a function argument
    representing a file path.
    
    Parameters
    ----------
    arg_name
        The `arg_name` parameter in the `__validate_path_arg__` function is used to specify the name of the
    argument that should be validated as a path. The decorator created by this function will then check
    if the value passed to the specified argument is a non-empty string and a valid file path.
    
    Returns
    -------
        The `__validate_path_arg__` function returns a decorator function that can be used to validate a
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
                # This checks for OS-level invalid paths (but not existence)
                validate_filepath(path)
            except ValidationError as e:
                raise ValueError(f"Invalid path in argument '{arg_name}': {e}")

            return func(*args, **kwargs)
        return wrapper
    return decorator
    
def __combine_work_folder__(work_folder,path,file_name=""):
    if not os.path.isabs(path):
        path = os.path.join(work_folder,path)
        
    if file_name!="":
        path = os.path.join(path,file_name)
    return path
 

def calculate_file_size(path):
    file_path = Path(path)
    return file_path.stat().st_size 
    
def calculate_after_size(result): 
       
        after_size=0
        for entry in result["result_entries"]:
            if "output_path_rdf" in entry["run_info"]:
                after_size = after_size + calculate_file_size(entry["run_info"]["output_path_rdf"])
        if after_size==0:
            after_size=pd.NA
        return after_size 

    

def __get_hugg_list__():
    
    api = HfApi()
    models = api.list_models(library="onnx",cardData=True,full=True)
    
    return list(models)





import shutil

def is_folder_empty(path):
    return not any(os.listdir(path))

def __move_onnx_file__(onnx_folder,repo_dir,logger:Logger=None):
    move_paths=[]
    for file_name in os.listdir(onnx_folder):
        if file_name.endswith('.onnx'):
            # Full path to the model file inside the 'onnx' folder
            file_path = os.path.join(onnx_folder, file_name)

            # Construct the new path (one level up, i.e., in the repo directory)
            new_path = os.path.join(repo_dir, file_name)
            new_path=new_path.replace("\\","/")
            file_path=file_path.replace("\\","/")
            # Move the file from the 'onnx' folder to the repo directory
            if logger!=None:
                logger.info(f"Moving {file_path} to {new_path}")
            shutil.move(file_path, new_path)
            move_paths.append((file_path,new_path))
            
    return move_paths  
                
def __remove_cache_dir__(cache_dir,logger:Logger=None):
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
        info = f"Cache directory '{cache_dir}' and all its contents have been removed."
    else:
        info = f"Cache directory does not exist: {cache_dir}"
    if logger!=None:
        logger.info(info)

def __move_models_outside_onnx__(models_folder, repo_id,downloaded_paths,logger=None):
    # Construct the full path to the repository directory
    repo_dir = os.path.join(models_folder, repo_id)

    # Path to the 'onnx' folder inside the repository
    onnx_folder = os.path.join(repo_dir, 'onnx')

    # Check if the 'onnx' folder exists
    if os.path.exists(onnx_folder) and os.path.isdir(onnx_folder):
        # Get all .onnx files in the 'onnx' folder
        paths = __move_onnx_file__(onnx_folder,repo_dir,logger=logger)

        # Optionally, remove the 'onnx' folder if empty
        if not os.listdir(onnx_folder):  # Check if the folder is empty
            os.rmdir(onnx_folder)
        for (old_path,new_path) in paths:
            if old_path in downloaded_paths:
                downloaded_paths.remove(old_path)
            if new_path not in downloaded_paths:
                downloaded_paths.append(new_path)


import threading
from queue import Queue
class ThreadFormatter(logging.Formatter):
    def format(self, record):
        # Attach thread_id if present; fallback to thread name
        
        thread_id = getattr(threading.current_thread(), 'thread_id', threading.current_thread().name)
        record.thread_id = thread_id
        return super().format(record) 
    

from ONNX2RDF.parser import ONNX2RDFParser,RDF_formats
import json
import configparser




def __fix_paths_hub_download__():

    def incomplete_path(self, etag: str) -> Path:
        """Return the path where a file will be temporarily downloaded before being moved to `file_path`."""
        path = self.metadata_path.parent / f"{_short_hash(self.metadata_path.name)}.{etag}.incomplete"
        resolved = path.resolve()
        resolved_str = str(resolved)
        if len(resolved_str) > 255 and not resolved_str.startswith(r"\\?\\"):
            path = Path(r"\\?\{}".format(resolved_str))
        return path
    temporal_fix = incomplete_path
    original = huggingface_hub._local_folder.LocalDownloadFilePaths.incomplete_path
    huggingface_hub._local_folder.LocalDownloadFilePaths.incomplete_path=temporal_fix
    return original

def __restore_original_method__(original):
    huggingface_hub._local_folder.LocalDownloadFilePaths.incomplete_path=original


    

    
class HuggingFaceParser():

    
    def __init__(self):
        self._num_threads = 1
        self._original_handler={}
        
        self._repo_data_queue =Queue()

        
        self._threads=[]
        self._dirty=True
        
        self._rdf_parsers = [ONNX2RDFParser()]

        self._work_folder=os.getcwd()
        self._script_path = os.path.dirname(os.path.abspath(__file__))
        self._lock = threading.RLock()
        self._running=False
        self._hard_stop=False
        

        
        
        self.__setup_config_values__()
        self.__load_metrics_file__()
        
        self._logger = self.__setup_logger__(self._to_console)
        
        
        
        
        self._default_repo_lists = {"repo_id_done":[],"repo_id_error":[],"repo_id_warning":[],"repo_id_try_again":[],"repo_id_banned":[],"repos_stopped":[]}
        self._repo_lists = self._default_repo_lists 
        
    def __set_multiple_singal__(self,signal_types:list[signal.Signals],handle):
        if threading.current_thread() == threading.main_thread():
            for signal_type in signal_types:
                if HuggingFaceParser.__is_signal_editable__(signal_type):
                    signal.signal(signal_type,handle)
                    
    @staticmethod       
    def __is_signal_editable__(signal_type):
        value = None
        if isinstance(signal_type,signal.Signals):
            value = signal_type.value
        if isinstance(signal_type,int):
            value = signal_type
        return value and value!=9 and value!=19                
                    
                    
    def __store_original_handlers__(self,signal_types:list[signal.Signals]):
        for signal_type in signal_types:
            self._original_handler[signal_type]=signal.getsignal(signal_type)
    def __restore_multiple_singal__(self,signal_types:list[signal.Signals]):
        if threading.current_thread() == threading.main_thread():
            for signal_type in signal_types:
                if HuggingFaceParser.__is_signal_editable__(signal_type):
                    signal.signal(signal_type,self._original_handler[signal_type])
    def __delegate_to_process__(self,func,kwargs):
        
        with concurrent.futures.ProcessPoolExecutor() as executor:
            future = executor.submit(func, **kwargs)

            try:
                while not future.done():
                    time.sleep(1)
                    self.__check_is_stoped__()
                result = future.result()
                if result:
                    return result
            except Exception:
                future.cancel()
                raise
        raise RuntimeError(f"Unexpected error when execution func {func}")
                

    def __setup_config_values__(self):
        _config = configparser.ConfigParser()
        default_parser = os.path.join(self._script_path,"default_parser.config")
        custom_parser = os.path.join(self._work_folder,"custom_parser.config")
        os.makedirs(os.path.dirname(custom_parser),exist_ok=True)
        if not os.path.exists(custom_parser):
            shutil.copy2(default_parser,custom_parser)
        
        _config.read([default_parser,custom_parser])
        self._config = _config
        
        
        for parser in self._rdf_parsers:
            parser.set_debug(_config.get("PARSER","debug"))
            parser.set_work_folder(_config.get("PARSER","work_folder"))
            parser.set_cache_options(_config.get("PARSER","cache"))
            parser.set_to_console(str_to_bool(_config.get("PARSER","to_console")))
            parser.set_parser_heap(_config.get("PARSER","max_ram"))
            parser.set_stop_parsing(str_to_bool(_config.get("PARSER","no_parsing")))
        
        self._metrics_file = _config.get("METRICS","file_name")
        self._metadata_folder = _config.get("METADATA","tmp_metadata_folder")
        self._metadata_mapping_folder = _config.get("METADATA","mapping_path")
        self._metadata_mapping_file = _config.get("METADATA","mapping_file")
        self._resource_url = _config.get("URIS","resource_url")
        
        self._cache_file_name =  _config.get("CACHE","progress_file")
        self._full_list_name =  _config.get("CACHE","cache_hugg_list")

        self._models_folder = _config.get("PARSER","models_folder")
        self._log_folder = _config.get("LOGS","logs_folder")
        
        self._to_console = _config.get("LOGS","to_console")
        

    METRICS_COLUMNS = ["repo_id","number_of_files","hugginface_repo_size","rdf_repo_size","repo_coverage","date",
                "downloading_time","load_elapsed_time","preprocess_elapsed_time",
                "yarrr2rml_elapsed_time","rml_parsing_elapsed_time","global_elapsed_time","Error_Found"]
    
    def __load_metrics_file__(self):
        with self._lock:
            path = os.path.join(self._work_folder,self._metrics_file)
            
            if os.path.exists(path):
                # load
                df = pd.read_csv(path)
                
                default_value = ''
                missing_cols = set(HuggingFaceParser.METRICS_COLUMNS) - set(df.columns)
                if len(missing_cols)>0:
                    # Add missing columns using a dict (vectorized)
                    df = df.assign(**{col: default_value for col in missing_cols})
                    self._logger.warning("When loading metrics file some columns where missing")
                keys_in_df = [col for col in HuggingFaceParser.METRICS_COLUMNS if col in df.columns]
                other_cols = [col for col in df.columns if col not in keys_in_df]

                # Reorder
                new_order = keys_in_df + other_cols
                df = df[new_order]
                self._metrics_data=df
            else:
            
                self._metrics_data = pd.DataFrame(columns=HuggingFaceParser.METRICS_COLUMNS)

            
        
        
    def __set_with_args__(self,args):
        
        self.set_number_threads(args.num_threads)
        self.set_rdf_format(args.rdf_format)

        if args.work_folder and args.work_folder != "":
            self.set_work_folder(args.work_folder)
        
    
        
    def __save_metrics__(self,data:pd.DataFrame):
        
        with self._lock:
            path = os.path.join(self._work_folder,self._metrics_file)
            data.to_csv(path, index=False, encoding='utf-8')
    
   
    def __load_progress__(self, path):
        with self._lock:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception as e:
                    raise RuntimeError(f"Failed to load cache progress: {e}")
                for key in self._default_repo_lists.keys():
                    if key not in data or not isinstance(data[key],list):
                        data[key] = []
                self._repo_lists=data 
            else:
                self._repo_lists=self._default_repo_lists    
              
            
   
    
       
        
    @__validate_path_arg__('path')
    def set_work_folder(self,path:str):
        # in case work_folder is relativer to actual work_folder
        old_cache_file = os.path.join(self._work_folder,self._cache_file_name)
        path = __combine_work_folder__(os.getcwd(),path)
        new_cache_file = os.path.join(path,self._cache_file_name)
        with self._lock:
            os.makedirs(path,exist_ok=True)
            if os.path.exists(old_cache_file):
                os.remove(old_cache_file)
            
            __dump_json__(new_cache_file,self._repo_lists)
                
            self._work_folder=path
        
        
    def get_work_folder(self):
        return self._work_folder
        
    def set_rdf_format(self,rdf_format:Union[str,RDF_formats]):
        for parser in self._rdf_parsers:
            parser.set_rdf_format(rdf_format)
        
    def get_rdf_format(self):
        return self._rdf_parsers[0].get_rdf_format()
    
    def set_number_threads(self,num_threads):
        if self._running:
            self._logger.warning("Parser is Running, number of threads cannot be changed")
            return False
        self._num_threads=num_threads
        for parser in self._rdf_parsers:
            parser.cleanup()
        parsers=[]
        for _ in range(num_threads):
            parsers.append(ONNX2RDFParser())
        self.__setup_config_values__()
        self._rdf_parsers=parsers
        return True
        
    def get_number_threads(self):
        return self._num_threads     
     
  
    def __setup_logger__(self,to_console=True,files=[]):
        logger = logging.getLogger("HuggParser")
        
        if (logger.hasHandlers()):
            logger.handlers.clear()
        logger.setLevel(logging.INFO)
        
        console = logging.StreamHandler()
        
        
        for file in files:
            file_handle = logging.FileHandler(file,mode="w")
            if file_handle:
                logger.addHandler(file_handle)
        
        formatter = ThreadFormatter(
            fmt='[%(asctime)s] [Thread-%(thread_id)s] %(levelname)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        console.setFormatter(formatter)
        if to_console:
            logger.addHandler(console)
        logger.propagate = False
        return logger
    
    
    
    def __add_hugg_id__(self, task_list):
        for task in task_list:
            self.tasks.put(task)
            
    def __add_cache__(self, key, item):
        """Add an item to the specified list in a thread-safe way."""
        with self._lock:
            if key not in self._repo_lists:
                raise ValueError(f"Invalid key: {key}")
            if item not in self._repo_lists[key]:
                self._repo_lists[key].append(item)
            path_save = os.path.join(self._work_folder,self._cache_file_name)
            __dump_json__(path_save,self._repo_lists)

                
    def __get_cache__(self,key):
        return self._repo_lists[key]
                
    def __remove_cache__(self, key, item):
        """Remove an item from the specified list (thread-safe)."""
        with self._lock:
            if key not in self._repo_lists:
                raise ValueError(f"Invalid key: {key}")
            try:
                self._repo_lists[key].remove(item)
                path_save = os.path.join(self._work_folder,self._cache_file_name)
                __dump_json__(path_save,self._repo_lists)
            except ValueError:
                pass  # silently ignore if item is not present
     
    def __worker__(self,thread_id,try_again=False):
        """Thread execution."""
        
        
        while not self._repo_data_queue.empty() and not self._hard_stop:
            os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
            try:
                repo_data = self._repo_data_queue.get(block=True)
            except Exception:
                break
            
            
            try:
                
                time_stamp = datetime.now()
                result = self.__process_repo__(repo_data,thread_id,self._logger,try_again)
                
                if self._hard_stop:
                    self.__add_cache__("repos_stopped", repo_data.id)
                else:
            
                    if result["error_found"]:
                        self.__remove_cache__("repo_id_done",repo_data.id)
                        self.__remove_cache__("repos_stopped",repo_data.id)
                
                    if result["error_found"] and result["error_type"]=="Parsing_Warning":
                        self.__add_cache__("repo_id_warning", repo_data.id)
                        self.__add_cache__("repo_id_try_again", repo_data.id)
                        self.__remove_cache__("repo_id_error",repo_data.id)
                        self.__remove_cache__("repos_stopped",repo_data.id)
                    
                    elif result ["error_found"] and result["error_type"]=="Parsing_Error":
                        self.__add_cache__("repo_id_error", repo_data.id)
                        self.__add_cache__("repo_id_try_again", repo_data.id)
                        self.__remove_cache__("repo_id_warning",repo_data.id)
                        self.__remove_cache__("repos_stopped",repo_data.id)
                    
                    elif result["error_found"]:
                        self.__add_cache__("repo_id_error", repo_data.id)
                        self.__remove_cache__("repo_id_warning",repo_data.id)
                        self.__remove_cache__("repos_stopped",repo_data.id)
                                       
                    else:
                        if not self._hard_stop:
                            self.__add_cache__("repo_id_done", repo_data.id)
                            self.__remove_cache__("repo_id_try_again",repo_data.id)
                            self.__remove_cache__("repo_id_error",repo_data.id) 
                            self.__remove_cache__("repo_id_warning",repo_data.id)
                            self.__remove_cache__("repos_stopped",repo_data.id)
                            self.__remove_cache__("repo_id_banned",repo_data.id)
                            
                if not self._hard_stop:  
                    self.__fill_csv_report__(repo_data,result,time_stamp,try_again=try_again)
                else:
                    repo_data["error_name"]="Program Stopped"
                    self.__fill_csv_report__(repo_data,result,time_stamp,try_again=try_again)
                if result ["error_found"]:
                    
                    self._logger.info(f"Finishing Parsing Repo {repo_data.id} with errors (Warnings or Parsing Erros)")
                else:
                    self._logger.info(f"Finishing Parsing Repo {repo_data.id} Correclty")
                    self._n_right = self._n_right +1
            except Exception:
                if not self._hard_stop:
                    
                    self._logger.info(f"Repo {repo_data.id} could not be parsed  \n{traceback.format_exc()}")
                    self.__remove_cache__("repo_id_done", repo_data.id)
                    self.__add_cache__("repo_id_error",repo_data.id)
                else:
                    self._logger.info(f"Repo {repo_data.id} could not be finished as program was terminated")
            finally:
                self._repo_data_queue.task_done()
                
                with self._lock:
                    self._pbar.update(1)
            
            
        if self._hard_stop:
            if hasattr(self,"_threads_stopped_bar"):
                self._threads_stopped_bar.update(1)
            self._logger.error(f"Thread {thread_id} terminated ")
        else:
            self._logger.info(f"Thread {thread_id} finished all work ")
        
     
    
    def __wait_threads__(self):
        one_alive=True
        start_time = time.time()
        while one_alive:
            self.__check_is_stoped__()
            one_alive=False
            for thread in self._threads:
                thread:threading.Thread
                one_alive = one_alive or thread.is_alive()
            
            time.sleep(1)
            # each minute we update info
            if time.time() - start_time >= 60:
                
                start_time = time.time()  # Reset timer if needed
                if self._repo_lists:
                    path_save = os.path.join(self._work_folder,self._cache_file_name)
                    __dump_json__(path_save,self._repo_lists)
                if hasattr(self, "_metrics_data") and self._dirty:
                    self.__save_metrics__(self._metrics_data)
                    self._dirty=True
            
        
        return True
  
          
    
    def __paralalise_executions__(self,try_again=False):
        
        self._logger.info(f"Number of Threads: {self._num_threads}")
        for thread_id in range(self._num_threads):
            
            thread = threading.Thread(target=self.__worker__,kwargs={"thread_id":thread_id,"try_again":try_again},name=f"HuggParser_{thread_id}")
            thread.daemon = True
            thread.start()
            self._threads.append(thread)

        self.__wait_threads__()

        if self._hard_stop:
            self._logger.info("Program is being Stopped. Closing Threads and Resources.")
        
    def __get__onnx_data__(self,repo_id):
        try:
            files = list_repo_files(repo_id=repo_id)
        except Exception as e:
            if isinstance(e,conn_err):
                self._logger.info(connection_error)
                self._hard_stop=True
            raise
        base_pattern = re.compile(r".*\.(onnx_data|onnx\.data)$")  
        return [file for file in files if re.search(base_pattern, file)]
            
    def __get_onnx_paths__(self,repo_id, specified_optimization:int=4,logger:Logger=None):
        
        try:
            files = list_repo_files(repo_id=repo_id)
        except Exception as e:
            if isinstance(e,conn_err):
                self._logger.info(connection_error)
                self._hard_stop=True
            raise   
        optimized_pattern = re.compile(r".*model_O(\d+)\.onnx$")
        base_pattern = re.compile(r".*\.onnx$")

        folder_to_optimized = defaultdict(list)
        folder_to_default = defaultdict(list)

        for file in files:
            folder = os.path.dirname(file)
            if match := optimized_pattern.match(file):
                model_id = int(match.group(1))
                folder_to_optimized[folder].append((file, model_id))
            elif base_pattern.match(file):
                folder_to_default[folder].append(file)

        all_folders = set(folder_to_optimized.keys()) | set(folder_to_default.keys())
        selected_files = []

        for folder in all_folders:
            
            optimized_entries = folder_to_optimized.get(folder, [])
            id_to_files = defaultdict(list)
            for file, model_id in optimized_entries:
                id_to_files[model_id].append(file)

            if specified_optimization is not None and specified_optimization in id_to_files:
                selected = id_to_files[specified_optimization]
                
                info = f"[{folder}] Found model_O{specified_optimization}.onnx: {selected}"
                if logger!=None:
                    logger.info(info)
            elif id_to_files:
                max_id = max(id_to_files)
                selected = id_to_files[max_id]
                info = f"[{folder}] Found model_O{max_id}.onnx: {selected}"
                if logger!=None:
                    logger.info(info)
            else:
                default_files = folder_to_default.get(folder, [])
                if default_files:
                    selected = default_files
                    info = f"[{folder}] Found .onnx file: {default_files}"
                    if logger!=None:
                        logger.info(info)
                else:
                    info = f"[{folder}] No ONNX models found."
                    if logger!=None:
                        logger.info(info)
                    selected = []

            selected_files.extend(selected)

        return selected_files
    
    @staticmethod
    def __exists_cache__(file_path,repo_id,work_folder):
        file_cache_path = os.path.join(str(Path(file_path).with_suffix("")).replace(os.sep,"-.-"),"loaded_model.json")
        repo_cache_name = HuggingFaceParser.__build_model_name__(repo_id)
        
        cache_path = os.path.join(work_folder,"tmp",repo_cache_name,file_cache_path).replace("\\","/")
        
        return os.path.exists(cache_path)
    
    
        
    def __download_models__(self,repo_id, file_paths,local_dir=None,logger:Logger=None,just_paths=False,work_folder_parser=""):
        downloaded_files = []
        
        redownload_paths = []
        
        if just_paths:
            for file in file_paths:
                downloaded_path:str = os.path.join(local_dir,file)
                downloaded_path = downloaded_path.replace("\\","/")
                
                if not self.__exists_cache__(file,repo_id,work_folder_parser):
                    redownload_paths.append(file)
                else:
                    downloaded_files.append(downloaded_path)          
        else:
            redownload_paths=file_paths
        
        
        
        original_get_progress = file_download._get_progress_bar_context
        
        desc=f"Files to Downloaded of Repo {repo_id}"
        
        if len(downloaded_files) > len(redownload_paths):
            desc=f"Files to ReDownloaded of Repo {repo_id}"
        original_download_func=False
        if len(redownload_paths)>0:
            
            if is_notebook():
                outer_progress = tq.tqdm_notebook(total=len(redownload_paths),desc=desc)
                file_progress_bar = tq.tqdm_notebook(total = 0,desc="Error",unit="B",unit_scale=True,initial=0)
            else:
                outer_progress = tq.tqdm(total=len(redownload_paths),desc=desc)
                file_progress_bar = tq.tqdm(total = 0,desc="Error",unit="B",unit_scale=True,initial=0)

            #TODO: temporal fix should do PR to hugginface_hub solving this issue
            original_download_func = __fix_paths_hub_download__()
        
        for file in redownload_paths:
            # Download each model file using hf_hub_download
            self.__check_is_stoped__()
            
            self.__check_is_stoped__()
           
            try:
                
                file_url = hf_hub_url(repo_id=repo_id,filename=file)
                info = get_hf_file_metadata(file_url)
                file_progress_bar.reset(info.size)
                displayed_filename=f"Downloading {os.path.basename(file)}"
                if len(displayed_filename) > 40:
                    displayed_filename = f"Downloading (…){os.path.basename(file)[-40:]}"
                file_progress_bar.set_description(displayed_filename)
                def patched_get_progress_bar_context(*args, **kwargs):
                    return nullcontext(file_progress_bar)  # <== always use our bar
                file_download._get_progress_bar_context = patched_get_progress_bar_context
                local_dir = local_dir.replace("\\","/")
                
                #fix annoying issue with max path
                args = {"repo_id":repo_id, "filename":file,"local_dir":local_dir,"cache_dir":local_dir,"force_download":True,"resume_download":True,"etag_timeout":130}
                
                self.__delegate_to_process__(hf_hub_download,kwargs=args)

                outer_progress.update(1)
                if logger:    
                    logger.info(f"Downloaded {file} to {downloaded_path}")
                
                
                downloaded_path=downloaded_path.replace("\\","/")
                downloaded_files.append(downloaded_path)
                file_download._get_progress_bar_context = original_get_progress
            except (Exception,KeyboardInterrupt) as e:
                
                
                file_download._get_progress_bar_context = original_get_progress
                if original_download_func:
                    __restore_original_method__(original_download_func)
                raise
        if original_download_func:
            __restore_original_method__(original_download_func)
            
            
            
            
                
        
        return downloaded_files + redownload_paths
    
    
    
        
        
    def __selected_list_multiple_methods__(self,filter_list:list[ModelInfo],number_repos,method:SelectedMethods):
        if method==SelectedMethods.RANDOM:
            return random.sample(filter_list, number_repos)
        if method==SelectedMethods.MOST_DOWNLOADS:
            
            sort_list = sorted(filter_list, 
                key=lambda m: m.downloads if m.downloads is not None else 0,
                reverse=True)
            return sort_list[0:number_repos]
        if method==SelectedMethods.LEAST_DOWNLOADS:
            sort_list = sorted(filter_list, 
                key=lambda m: m.downloads if m.downloads is not None else 0,
                reverse=False)
            return sort_list[0:number_repos]
        
        return filter_list[0:number_repos]
    
      
    
    
      
        

    def __build_final_id_list__(self,number_repos,try_again=False,try_error=False,order_method:SelectedMethods=SelectedMethods.RANDOM):
        
        cache_path = os.path.join(self._work_folder,"full_list.pkl")
        found=False
        if os.path.exists(cache_path):
            try:
                set_cache = __load_pickle__(cache_path)
                self.__full_list__:list[ModelInfo]=set_cache
                found=True
            except Exception:
                pass
        
        if not found:
            try:
                self.__full_list__:list[ModelInfo] = __get_hugg_list__()
            except Exception as e:
                if isinstance(e,conn_err):
                    self._logger.info(connection_error)
                    self._hard_stop=True
                raise
            __dump_pickle__(cache_path,self.__full_list__)
            
        
        not_need_ids = set(self._repo_lists["repo_id_done"] + 
                           self._repo_lists["repo_id_warning"] + 
                           self._repo_lists["repo_id_error"] 
                           )
        try_again_set=set([])
        try_error_set=set([])
        
        banned_list = set(self._repo_lists["repo_id_banned"])
        stopped_list = list(set(self._repo_lists["repos_stopped"]))
        
        if try_again:
            try_again_set = set(self._repo_lists["repo_id_try_again"])
        if try_error:
            try_error_set = set(self._repo_lists["repo_id_error"])

        stopped_subset = [repo for repo in self.__full_list__ if repo.id in stopped_list and repo.id not in banned_list]
        combined_try_error = list(try_again_set | try_error_set)

        if try_again or try_error:
            filter_list = [repo for repo in self.__full_list__ if repo.id in combined_try_error and repo.id not in banned_list]
        else:
            filter_list = [repo for repo in self.__full_list__ if repo.id not in not_need_ids and repo.id not in banned_list]
            
        
        
        if len(filter_list)==0:
            if (try_again and try_error):
                self._logger.info("There are no more Repos on the try_again_list and the error_list to fix. Good Job")
                return False
            if (try_error):
                self._logger.info("There are no more Repos on the error_list to fix. Good Job")
                return False
            if (try_again):
                self._logger.info("There are no more Repos on the try_again_list to fix. Good Job")
                return False
            self._logger.info("There are no more Repos on HuggingFace to parse. Very Good Job")
            return False
        
        
        if number_repos==-1:
            selected_list = self.__selected_list_multiple_methods__(filter_list,len(filter_list),order_method)
        else:
            stopped_slice = stopped_subset[:number_repos]
            remaining_repos = number_repos-len(stopped_slice)
            if remaining_repos<=0:
                selected_list = stopped_slice
            else:
                selected_list= stopped_slice + self.__selected_list_multiple_methods__(filter_list,remaining_repos,order_method)
        
        self._n_repos = len(selected_list)
        self._logger.info(f"Number of Repos: {self._n_repos}")
        for item in selected_list:
            self._repo_data_queue.put(item)
            self._logger.info(f"Repo: {item.id}")
        return True
    
    def __change_try_again_cache__(self):
        for parser in self._rdf_parsers:
            options = parser.get_cache_options()
            if "load-model" not in options:
                options.append("load-model")
                parser.set_cache_options(options)
                
    def stop(self):
        self._running=False
        self._hard_stop=True
        
    def __check_is_stoped__(self):
        if self._hard_stop:
            raise RuntimeError("Signal Stop Program") 
        
    def __signal_handler_raise__(self,signum, frame):
        self.stop()
        self._logger.error(f"Program {signal.strsignal(signum)}, closing resources. Wait or signal to stop program again")
        raise RuntimeError("Signal Stop Program")      

    def __signal_handler__(self,signum, frame):
        self.stop()
        
        self._logger.error(f"Program {signal.strsignal(signum)}, closing resources. Wait or signal to stop program again")
        
                   
                
                          
    def run(self,number_repos:int,try_again=False,try_error=False,order_method="random"):
        """Start threads and process the tasks."""
        
        self.__setup_config_values__()
        
        try:
            order_method = SelectedMethods._value2member_map_[order_method]
        except Exception:
            raise ValueError(f"order_method {order_method} is not a valid option. Valid Options are {list(SelectedMethods._value2member_map_.keys())}")

        
        
        
        buffer = 4 * 1024 ** 3 #1GB
        disk_space = psutil.disk_usage("/").free
        if disk_space< buffer:
            raise RuntimeError("Not Enough Recommeded memory (4GB) to run parser")
        
        
        
        
        timestamp = datetime.now()
        
        there_is_work=False
        try:
            self._hard_stop=False
            self._running=True
            if hasattr(self,"_logger"):
                for handle in self._logger.handlers:
                    handle.close()

            log_folder = os.path.join(self._work_folder,self._log_folder)
            log_name = timestamp.strftime("logs_%d_%m_%Y_%Hh_%Mmin.log")
            os.makedirs(log_folder,exist_ok=True)
            self._logger = self.__setup_logger__(to_console=self._to_console,files=[os.path.join(log_folder,log_name)])
            
            
            self._n_right = 0
            
            self.__store_original_handlers__(signals_to_catch)
            self.__set_multiple_singal__(signals_to_catch,self.__signal_handler__)
            
            self.__load_progress__(os.path.join(self._work_folder,self._cache_file_name))
            self.__load_metrics_file__()
            
            
            there_is_work =self.__build_final_id_list__(number_repos,try_again,try_error,order_method)
            
            if not there_is_work:
                return 0
            
            if is_notebook():
                self._pbar = tq.tqdm_notebook(total=self._n_repos, desc="Nº Completed Repos")
            else:
                self._pbar = tq.tqdm(total=self._n_repos, desc="Nº Completed Repos")
            
            if try_again or try_error:
                self.__change_try_again_cache__()
            self.__check_is_stoped__()
            self.__paralalise_executions__(try_again=try_again)
            self._running=False
        except (BaseException):
            if self._hard_stop!=True:
                self._logger.error(f"Error Parsing HuggingFace Repos: got unexcpeted error\n {traceback.format_exc()}")         

        finally:
            self._running=False
            
            if hasattr(self,"_pbar"):
                self._pbar.close()
            
            if self._hard_stop:
                if hasattr(self,"_rdf_parsers"):
                    for parser in self._rdf_parsers:
                        parser.stop()
                      
                if hasattr(self,"_threads"):
                    
                    stopped_threads = [t for t in self._threads if not t.is_alive()]

                    # Create tqdm progress bar
                    with self._lock:
                        if is_notebook():
                            self._threads_stopped_bar = tq.tqdm_notebook(total=len(self._threads), desc="Stopping Threads")
                        else:
                            self._threads_stopped_bar = tq.tqdm(total=len(self._threads), desc="Stopping Threads")
                        self._threads_stopped_bar.update(len(stopped_threads)) 
                    
                    self.__set_multiple_singal__(signals_to_catch,self.__signal_handler_raise__)
                    try:
                        for thread in self._threads:
                            thread.join()
                    except Exception:
                        self._logger.error("Stopping Threads Forcefully. Errors might occur")
                    self.__set_multiple_singal__(signals_to_catch,self.__signal_handler__)
                    self._logger.error("All Threads properly stopped")
                    self._repo_lists
                    
            self.__restore_multiple_singal__(signals_to_catch)        
                    
            if hasattr(self,"_repo_lists") and hasattr(self,"_repo_data_queue"):
                self.__fill_stopped_list__()
                    

            if hasattr(self,"_n_repos"):      
                n_repos = self._n_repos
                n_right = self._n_right
                n_wrong = self._n_repos - self._n_right
                
                if self._hard_stop and n_right>0:
                    self._logger.info(f"Program was Stoped. \n Report: {n_right} of {n_repos} Repos have been parsed correlty before the program closing \n Files are at {self._rdf_parsers[0].get_target_path()}")
                elif self._hard_stop:
                    self._logger.info("Program was Stoped. Closing Threads and Resources. \n Report: No Repos have been parsed correlty before the program closing")
                elif n_right>0:
                    self._logger.info(f"All threads have finished working. \n Report: {n_right} of {n_repos} Repos have been parsed correlty. {n_wrong} Incorrectly \n Files are at {self._rdf_parsers[0].get_target_path()} ")
                else:
                    self._logger.info(f"All threads have finished working. \n Report: No Repos of {n_repos} Repos have been parsed correlty.")
            
            
            self._hard_stop=False
            
            if self._repo_lists:
                path_save = os.path.join(self._work_folder,self._cache_file_name)
                with self._lock:
                    __dump_json__(path_save,self._repo_lists)

            if hasattr(self, "_metrics_data"):
                self.__save_metrics__(self._metrics_data)
            if hasattr(self,"_logger"):
                for handle in self._logger.handlers:
                    handle.close()
                

    def __fill_stopped_list__(self):      
        list_items = self.__get_cache__("repos_stopped")
        queue:Queue = self._repo_data_queue
        while not queue.empty():
            item = queue.get()
            if item.id not in list_items:
                self.__add_cache__("repos_stopped",item.id)
        
        
            
            
    METRICS_COLUMNS = ["repo_id","number_of_files","hugginface_repo_size","rdf_repo_size","repo_coverage","date",
                "downloading_time","metadata_time","load_elapsed_time","preprocess_elapsed_time",
                "yarrr2rml_elapsed_time","rml_parsing_elapsed_time","global_elapsed_time","Error_Found","Error_Type","Error_Name"]
    
    @staticmethod
    def __add_time_report__(row,report_repo,key,new_key):
        if "result" in report_repo and key in report_repo["result"] and report_repo["result"][key]!=-1:
            row[new_key] = report_repo["result"][key]
        else:
            row[new_key] = pd.NA
            
    @staticmethod
    def __add_result_errors__(data,report_repo,row):
        error_list : list[ErrorsONNX2RDF] = report_repo["result"]["error_types"]
        values=dict()
        
        number_erros=0
        
        for error in error_list:
            column_name = f"n_errors_{error.name}"
            if error !=ErrorsONNX2RDF.NONE_ERROR and column_name not in data.columns:
                data[column_name] = 0
            if error !=ErrorsONNX2RDF.NONE_ERROR:
                number_erros=number_erros+1
                values[error.name]=values.get(error.name, 0) + 1
        for key in values.keys():
            row[f"n_errors_{key}"]=values[key]
        n_files=len(error_list)
        coverage = (n_files/(n_files-number_erros))*100
        row["repo_coverage"]=coverage
    
    
    @staticmethod
    
    def __add_error_data__(data,row,report_repo):
        if "error_found" not in report_repo or not report_repo["error_found"]:
            row["Error_Found"] = False
            return   
        row["Error_Found"] = report_repo["error_found"]
        error_type=""
        
        if "error_type" in report_repo:
            error_type=report_repo["error_type"]
            row["Error_Type"]=error_type
        else:
            row["Error_Type"]=pd.NA
        if "error_name" in report_repo:
            row["Error_Name"]=report_repo["error_name"]
        else:
            row["Error_Name"]=pd.NA
        if error_type in ["Parsing_Error","Parsing_Warning"] and "error_name" not in report_repo:
            if "result" in report_repo and "number_models" in report_repo["result"] and "error_types" in report_repo["result"] :
                if report_repo["result"]["number_models"] ==1:   
                    row["Error_Name"]=report_repo["result"]["number_models"][0]
                else:
                    row["Error_Name"]="Multiple_Errors"
            
        if "result" in report_repo:
            HuggingFaceParser.__add_result_errors__(data,report_repo,row)
        
    
    
    def __fill_csv_report__(self,repo_data:ModelInfo,report_repo,date,try_again=False):
        with self._lock:
            df = self._metrics_data
            self._dirty=True
            new_row = {"repo_id":repo_data.id,
                    "number_of_files":report_repo["number_files"],
                    "hugginface_repo_size":report_repo["before_size"],
                    "rdf_repo_size":report_repo["after_size"],
                    "date":date}

            
            if not try_again:
                HuggingFaceParser.__add_time_report__(new_row,report_repo,"download_time","downloading_time")
                HuggingFaceParser.__add_time_report__(new_row,report_repo,"metadata_time","metadata_time")
                HuggingFaceParser.__add_time_report__(new_row,report_repo,"load_elapsed_time","load_elapsed_time")
            else:
                rows = df[df['repo_id'] == repo_data.id]
                if len(rows)>0:
                    row= rows.iloc[0]
                    new_row["downloading_time"] = row["downloading_time"].item()
                    new_row["metadata_time"] = row["downloading_time"].item()
                    new_row["load_elapsed_time"] = row["downloading_time"].item()
                else:
                    new_row["downloading_time"] = 0
                    new_row["metadata_time"] = 0
                    HuggingFaceParser.__add_time_report__(new_row,report_repo,"load_elapsed_time","load_elapsed_time")
            
            HuggingFaceParser.__add_time_report__(new_row,report_repo,"preprocess_elapsed_time","preprocess_elapsed_time")
            HuggingFaceParser.__add_time_report__(new_row,report_repo,"yarrr2rml_elapsed_time","yarrr2rml_elapsed_time")
            HuggingFaceParser.__add_time_report__(new_row,report_repo,"rml_parsing_elapsed_time","rml_parsing_elapsed_time")
            HuggingFaceParser.__add_time_report__(new_row,report_repo,"global_elapsed_time","global_elapsed_time")
            
            try:
                new_row["global_elapsed_time"] = new_row["global_elapsed_time"] + new_row["downloading_time"] + new_row["metadata_time"]
            except Exception:
                pass
            HuggingFaceParser.__add_error_data__(df,new_row,report_repo)
            df = df[df['repo_id'] != repo_data.id].copy()
            df.loc[-1] = new_row
            df.index = df.index + 1
            df = df.sort_index()
            self._metrics_data=df
            self.__save_metrics__(df)

    
    def is_work_done(self) -> bool:
        with self._lock:
            return len(self._repo_data_queue) == 0
      
    def __build_report__(self,error_found,error_name="",error_type="",number_files=pd.NA,before_size=pd.NA,after_size=pd.NA,other_times:dict={},result=None):
        
        report = {"error_found":error_found,
                "error_name":error_name,
                "error_type":error_type,
                "number_files":number_files,
                "before_size":before_size,
                "after_size":after_size}

        if result!=None:
            report["result"]=result

            
        for key,value in other_times.items():
            report["result"][key]=value
        return report
    
    @staticmethod
    def __build_model_name__(repo_id):
        return f"huggingface-{repo_id}"
    
    
    
    
    def __build_tmp_metadata__(self,repo_data:ModelInfo,id_process="",uris=[]):
        
        metadata_folder = os.path.join(self._work_folder,self._metadata_folder,str(id_process))
        
        mapping_path = os.path.join(self._script_path,self._metadata_mapping_folder,self._metadata_mapping_file)
        
        
        
        os.makedirs(metadata_folder,exist_ok=True)
        metadata_mappings_path=""
        try:
            metadata_path = created_metadata_json(repo_data.id,metadata_folder,model_info_extra=repo_data,model_uris=uris)
            metadata_mappings_path = edit_copy_mappings(mapping_path,metadata_folder,metadata_path,id_process,config_file=self._config)
        except Exception:
            delete_meta_files(metadata_folder)
            return None,None
        return metadata_folder,metadata_mappings_path
    

    def __process_repo__(self,repo_data:ModelInfo,id_process="",logger=None,try_again=False):
        
        start_download =time.time()
        repo_id=repo_data.id
        url = f"https://huggingface.co/{repo_data.id}"
        
        disk_space = psutil.disk_usage("/").free
        
        
        
        try:
            
            
            
            model_path = os.path.join(self._work_folder,self._models_folder,repo_id)
            if not os.path.exists(model_path):
                os.makedirs(model_path)
            paths = self.__get_onnx_paths__(repo_id,logger=logger)
            paths_data = self.__get__onnx_data__(repo_id)


            total_size = 0
            total_size_data = 0
            try:
                for filename in paths:
                    file_url = hf_hub_url(repo_id=repo_id,filename=filename)
                    info = get_hf_file_metadata(file_url)
                    total_size += info.size
                    
                for filename in paths_data:
                    file_url = hf_hub_url(repo_id=repo_id,filename=filename)
                    info = get_hf_file_metadata(file_url)
                    total_size_data += info.size
            except Exception as e:
                if isinstance(e,conn_err):
                    self._logger.info(connection_error)
                    self._hard_stop=True
                raise
            
            
                
            
            
  
            disk_space = psutil.disk_usage("/").free
            buffer = 1 * 1024 ** 3 #1GB
            if disk_space-buffer< total_size:
                warnings.warn(f"Not Enough Memory to Download Repo ({repo_data.id}) with URL ({url})")
                return self.__build_report__(True,"NO_ENOUGH_MEMORY","HuggingFace_Error")
            if len(paths)==0:
                
                warnings.warn(f"Not ONNX Files found at repo ({repo_data.id}) with URL ({url})")
                return self.__build_report__(True,"No_ONNX_FILES","HuggingFace_Error")
            self.__check_is_stoped__()  
        except Exception as e:
            self.__remove_files__(repo_id)
            if not self._hard_stop:
                self._logger.error(f"Error Getting Files Paths of HuggingFace Repo at repo ({repo_data.id}) with URL ({url}) : got unexcpeted error\n {traceback.format_exc()}")
            return self.__build_report__(True,type(e).__name__,"HuggingFace_Error")
        
        
            
        number_files = len(paths)
        
        
        
        
        
        try:
            
            _ = self.__download_models__(repo_id,paths,local_dir=model_path,logger=logger,just_paths=try_again,
                                                        work_folder_parser=self._rdf_parsers[id_process].get_work_folder())
            before_size = total_size + total_size_data
            
        except (Exception,KeyboardInterrupt) as e:
            
            self.__remove_files__(repo_id)
            if not self._hard_stop:
                self._logger.error(f"Error Downloading HuggingFace Repo ({repo_data.id}) with URL ({url}) : got unexcpeted error\n {traceback.format_exc()}")
            return self.__build_report__(True,type(e).__name__,"Downloading_Model",number_files)
        
        
        finish_download = time.time()
        elapsed_download = finish_download-start_download

        times_extra = {"download_time":elapsed_download,"metadata_time":-1}
        
        after_size=pd.NA
        try:
            self.__check_is_stoped__()
            self._logger.info(f"Starting ONNX2RDF Parser for repo ({repo_id})")
            parser :ONNX2RDFParser = self._rdf_parsers[id_process]
            uri_name = self.__build_model_name__(repo_id)
            args = {"model_path":model_path,"model_name":uri_name,"id_process":id_process,"base_resource_url":self._resource_url}
            result = self.__delegate_to_process__(func=parser.parse_file,kwargs=args)
            
            
            self.__check_is_stoped__()
            if result["stopped"]:
                self._hard_stop=True
                raise RuntimeError("Parser was stoped and results are incorrect")
            if result["errors_found"]:
                self.__remove_files__(repo_id)
                return self.__build_report__(True,error_type="Parsing_Error",number_files=number_files,before_size=before_size,other_times=times_extra,result=result)
            after_size = calculate_after_size(result)
            
            if result["warnings_caught"]:
                self.__remove_files__(repo_id)
                
                return self.__build_report__(True,error_type="Parsing_Warning",number_files=number_files,before_size=before_size,after_size=after_size,other_times=times_extra,result=result)
            
            
            
            
            
        except ValueError as e:
            self.__remove_files__(repo_id)
            
            if not result:
                result=None
            self._logger.error(f"Error Parsing HuggingFace Repo ({repo_data.id}) with URL ({url}) : got unexcpeted error\n {traceback.format_exc()}")
            if not self._hard_stop:
                self._logger.error(f"Error Parsing HuggingFace Repo ({repo_data.id}) with URL ({url}) : got unexcpeted error\n {traceback.format_exc()}")
            return self.__build_report__(True,type(e).__name__,"Parsing_Error",number_files=number_files,before_size=before_size,after_size=after_size,other_times=times_extra,result=result)
            
            
        start_metadata = time.time()
        try:
            metadata_folder,metadata_mapping_path = self.__build_tmp_metadata__(repo_data,id_process,result["model_uris"])
            rdf_path = os.path.join(parser.work_folder,parser.get_target_path(),self.__build_model_name__(repo_id))
            if metadata_folder and metadata_mapping_path:
                result_path = parser.yarrml2_rdf_pipeline(metadata_mapping_path,file_name="metadata",output_folder=rdf_path)
                self.__fix_incorrect_separator__(result_path)
        except Exception as e:
            self.__remove_files__(repo_id)
            self._logger.error(f"Error Preparing HuggingFace Metadata of Repo ({repo_data.id}) with URL ({url}) : got unexcpeted error\n {traceback.format_exc()}")
            if metadata_folder:
                delete_meta_files(metadata_folder)
            return self.__build_report__(True,type(e).__name__,"Metadata_Error",number_files=number_files,before_size=before_size)
        finish_metadata = time.time()
        elapsed_metadata = finish_metadata-start_metadata    
            
        times_extra["metadata_time"]=elapsed_metadata    
            
        if metadata_folder:
            delete_meta_files(metadata_folder)    
            
        self.__remove_files__(repo_id)    
            
        return self.__build_report__(False,number_files=number_files,before_size=before_size,after_size=after_size,other_times=times_extra,result=result)
        
    def __fix_incorrect_separator__(self,rdf_path):
        with open(rdf_path, 'r', encoding='utf-8') as f:
            content = f.read()
        new_content = content.replace('%2F', '/')

        with open(rdf_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        
        
    def __remove_files__(self,repo_id):
        _model_folder = os.path.join(self._work_folder, self._models_folder, repo_id)

        # Delete the folder and all its contents if it exists
        if os.path.isdir(_model_folder):
            shutil.rmtree(_model_folder)
        
        base_folder = os.path.join(self._work_folder, self._models_folder)
        parts = repo_id.split("/")

        for i in reversed(range(1, len(parts))):  # Skip index 0 to preserve models_folder
            dir_path = os.path.join(base_folder, *parts[:i])
            if os.path.exists(dir_path):
                try:
                    os.rmdir(dir_path)  # Only removes if empty
                except OSError:
                    break  # Stop if folder not empty
        
        
   
   
   
        
def __parse_args__():
    # Configuración del parser de argumentos
    parser = argparse.ArgumentParser(description="Parses to rdf HuggingFace Models using ONNX2RDF. \nThe models are taken randomly form the list of not done yet models (HuggingFace list minus already done repos) and the list of models stopped on the last execution\n"+
                                     "The lists with the already done models, models with errors, models with warnings, models stopped are stored on a json file as cache that can be edited")
    
    parser.add_argument("num_repos", type=int, help="Number of repo of huggingface to parse (integer) -1 for ALL. They will be taken as randomly from the not_done_list + re_try_list")
    parser.add_argument("--rdf_format", default="nquads", help="Available rdf formats (nquads (default), turtle, trig, trix, jsonld, hdt).")
    parser.add_argument("--work_folder", default="", help="Change the relative folder for searching models, creating logs folder or rdf folders. (default: 'folder of execution')")
    parser.add_argument('--num_threads', type=int, help="Number of threads (integer)", default=1)
    parser.add_argument('--try_again', action=argparse.BooleanOptionalAction, help="Retry models that failed while parsing to rdf (warnings included)", default=False)
    parser.add_argument('--try_error', action=argparse.BooleanOptionalAction, help="Retry models that failed with errors (parsing error, download error, hugginface_errors, unexcpeted errors) ", default=False)
    parser.add_argument('--order_method', default="random", help="Order method for selecting the models for the list. Ex: random applies a random sample, while m_downs orders it by most_downloads \n"+
                        "Available methods (random (default), m_downs, l_downs)")
    return parser.parse_args()    
        
def __call_main_with_args__():
    # Obtener los argumentos desde la línea de comandos
    args = __parse_args__()
    
    parser  = HuggingFaceParser()
    
    parser.__set_with_args__(args)
    parser.run(args.num_repos,args.try_again,args.try_error,args.order_method)
    


if __name__ == "__main__":
    # Ejecutar la función call_main_with_args solo cuando se ejecuta como script
    __call_main_with_args__()