
from huggingface_hub.hf_api import ModelInfo,model_info
from huggingface_hub import ModelCard
import shutil
import json
import os
from ruamel.yaml import YAML
import configparser

def combine_metadata_priority(obj1, obj2,keys):
        combined = ModelInfo(id=obj1.id)
        for attr in keys:  # all attributes
            val1 = getattr(obj1, attr, None)
            val2 = getattr(obj2, attr, None)

            if val2 is not None:
                setattr(combined, attr, val2)
            elif val1 is not None:
                setattr(combined, attr, val1)
            else:
                setattr(combined, attr, None)
        return combined
def combine_model_card_model_info(dict_model_info:dict,dict_model_card:dict):

    new_dict = dict_model_info.copy()
    for (key,value) in dict_model_card.items():
        if key not in dict_model_info.keys():
            new_dict[key]=value
        elif key == "tags" and isinstance(value,list):
            for tag in value:
                new_dict["tags"].append(tag)
                
        
def __dump_json__(path,data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4,default=str,cls=XSDDateTimeEncoder)
            
def __load_json__(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
               
import huggingface_hub as hg
from datetime import datetime,timezone

class XSDDateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            if obj.tzinfo is None:
                obj = obj.replace(tzinfo=timezone.utc)
            return obj.isoformat().replace("+00:00", "Z")
        return super().default(obj)

    
def created_metadata_json(repo_id,meta_folder,model_info_extra=None,model_uris=[]):
    metadata = model_info(repo_id,files_metadata=True,securityStatus=True)
    
    keys = [item for item in dir(metadata) if not item.startswith('_')]
    if model_info_extra:
       metadata = combine_metadata_priority(model_info_extra,metadata,keys)
    model_card=None
    try:
        model_card = ModelCard.load(repo_id)
    except Exception:
        pass    
    
    
    
    
    dict_meta = vars(metadata)
    clean_dict = {k: v for k, v in dict_meta.items() if v is not None and k in keys}
    
    if model_card:
        clean_dict["model_card_content"]=model_card.content
        
    url = f"https://huggingface.co/{repo_id}"
    
    clean_dict["repo_url"]=url
    clean_dict["models_uris"]=model_uris
    
    

    json_file = os.path.join(meta_folder,"metadata.json")
    
    __dump_json__(json_file,clean_dict)
    return json_file

def edit_copy_mappings(mapping_path:str,meta_folder:str,metadata_path,id_process:str,config_file):
    
    file_name = "modified_mapping"
    
    if id_process!="":    
        file_name = file_name+"_"+str(id_process)
        
   
        
    output_yaml_path = os.path.join(meta_folder,file_name+".yaml")
    
    
    yaml_dumper=YAML() 
    yaml_dumper.allow_duplicate_keys = True
    
    with open(mapping_path,'r') as f:
        
        yaml_dumper.preserve_quotes = True
        yaml_f = yaml_dumper.load(f)
        
    for source in yaml_f["sources"].values():
        source["access"]=metadata_path
    
    
    
    
    
    yaml_f["prefixes"]["hugg_base"]=config_file.get("URIS","hugginface_base")   
    yaml_f["prefixes"]["resource_base"]=config_file.get("URIS","resource_url")
    
    pos = yaml_f["mappings"]["test"]["po"]
    for po in pos:   
        if isinstance(po,dict) and "predicates" in po and po["predicates"]=="hugg_base:has_model":
            po["objects"] = f"{config_file.get("URIS","resource_url")}$(models_uris[*])/Model~iri"
        
    os.makedirs(os.path.dirname(output_yaml_path), exist_ok=True)

    with open(output_yaml_path, 'w',) as f :
        yaml_dumper.dump(yaml_f,stream=f)

    return output_yaml_path

def delete_meta_files(metadata_folder):
    try:
        if os.path.isdir(metadata_folder):
            shutil.rmtree(metadata_folder)
    except Exception:
        pass
    
    

   