from datetime import datetime
import os
import torch
import urllib.request
import json 
import numpy as np
import httpimport
import subprocess
import sys
# Local imports
from elsciRL.application_suite.import_data import Applications
from elsciRL.application_suite.experiment_agent import DefaultAgentConfig

class PullApplications:
    """Simple applications class to run a setup tests of experiments.
        - Problem selection: problems to run in format ['problem1', 'problem2',...]

    Applications:
        - Sailing: {'easy'},
        - Classroom: {'classroom_A'}
    """
    # TODO: Make it so it pulls all possible configs and adapters from the repo
    # TODO: Allow a blank entry for repo for experimental testing to pull most recent commit by default
    # TODO: Auto install libraries from application repo requirements.txt
    # TODO: Improve process for adding local application, cache to local directory to check from
    def __init__(self) -> None:
        imports = Applications()
        self.imports = imports.data
        self.current_test = {}
        
        
    def pull(self, problem_selection:list=[]):
        # Pull all problems if none are selected
        if len(problem_selection)>0:
            self.problem_selection = problem_selection
        else:
            self.problem_selection = list(self.imports.keys())
        
        # Extract data from imports
        for problem in list(self.problem_selection):
            print("-----------------------------------------------")
            print(problem)
            engine = self.imports[problem]['engine_filename']
            if problem not in self.imports:
                raise ValueError(f"Problem {problem} not found in the setup tests.")
            else:
                self.current_test[problem] = {}
                # Store engine filename
                self.current_test[problem]['engine_filename'] = engine
                # If commit ID is '*' or empty, use main branch
                if self.imports[problem]['commit_id'] in ['*', '']:
                    # Update commit_id to use main branch
                    self.imports[problem]['commit_id'] = 'main'
                    print('Pulling data from current version of main branch.')
                # current_test = {'problem1': {'engine':engine.py, 'local_configs': {'config1':config.json, 'config2':config.json}, 'adapters': {'adapter1':adapter.py, 'adapter2':adapter.py}}}
                root = 'https://raw.githubusercontent.com/'+ self.imports[problem]['github_user'] + "/" + self.imports[problem]['repository'] + "/" + self.imports[problem]['commit_id']
                print("Source: ", root)
                # NOTE - This requires repo to match structure with engine inside environment folder
                engine_module = httpimport.load(engine, root+'/'+self.imports[problem]['engine_folder']) 
                # TODO: Pull class name directly from engine file to be called
                self.current_test[problem]['source'] = {str(root): {
                                            'engine_folder': self.imports[problem]['engine_folder'],
                                            'engine_filename': self.imports[problem]['engine_filename'],
                                            'config_folder': self.imports[problem]['config_folder'],
                                            'experiment_config_filenames': self.imports[problem]['experiment_config_filenames'],
                                            'local_config_filenames': self.imports[problem]['local_config_filenames'],
                                            'local_adapter_folder': self.imports[problem]['local_adapter_folder'],
                                            'adapter_filenames': self.imports[problem]['adapter_filenames'],
                                            'local_analysis_folder': self.imports[problem]['local_analysis_folder'],
                                            'local_analysis_filenames': self.imports[problem]['local_analysis_filenames'],
                                            'prerender_data_folder': self.imports[problem]['prerender_data_folder'],
                                            'prerender_data_filenames': self.imports[problem]['prerender_data_filenames'],
                                            'instruction_folder': self.imports[problem]['instruction_folder'],
                                            'instruction_filenames': self.imports[problem]['instruction_filenames']}}

                try:
                    self.current_test[problem]['engine'] = engine_module.Engine
                except:
                    print("Engine error, attempting to install requirements.")
                    try:
                        requirements = urllib.request.urlopen(root+'/'+'requirements.txt').read()
                        # Install packages from requirements.txt
                        requirements = requirements.decode('utf-8').split('\n')
                        for req in requirements:
                            if req.strip():  # Skip empty lines
                                try:
                                    subprocess.check_call([sys.executable, "-m", "pip", "install", req.strip()])
                                    print(f"Successfully installed {req}")
                                except subprocess.CalledProcessError:
                                    print(f"Failed to install {req}")
                        # Try importing engine again after installing requirements
                        self.current_test[problem]['engine'] = engine_module.Engine
                        print("Successfully loaded engine after installing requirements.")
                    except:
                        print("Failed to load engine and no requirements.txt found.")
            # ------------------------------------------------
            # - Pull Adapters, Configs and Analysis
            self.current_test[problem]['adapters'] = {}
            for adapter_name, adapter in self.imports[problem]['adapter_filenames'].items():
                adapter_module = httpimport.load(adapter, root+'/'+self.imports[problem]['local_adapter_folder'])   
                # TODO: Pull class name directly from adapter file to be 
                self.current_test[problem]['adapters'][adapter_name] = adapter_module.Adapter
            # ---
            self.current_test[problem]['experiment_configs'] = {}
            for config_name,config in self.imports[problem]['experiment_config_filenames'].items():
                experiment_config = json.loads(urllib.request.urlopen(root+'/'+self.imports[problem]['config_folder']+'/'+config).read())
                self.current_test[problem]['experiment_configs'][config_name] = experiment_config
            # ---
            self.current_test[problem]['local_configs'] = {}
            for config_name,config in self.imports[problem]['local_config_filenames'].items():
                local_config = json.loads(urllib.request.urlopen(root+'/'+self.imports[problem]['config_folder']+'/'+config).read())
                self.current_test[problem]['local_configs'][config_name] = local_config
            # ---
            self.current_test[problem]['local_analysis'] = {}
            for analysis_name,analysis in self.imports[problem]['local_analysis_filenames'].items():
                try:
                    local_analysis = httpimport.load(analysis, root+'/'+self.imports[problem]['local_analysis_folder'])  
                    # TODO: Pull class name directly from analysis file to be called 
                    self.current_test[problem]['local_analysis'][analysis_name] = local_analysis.Analysis
                except:
                    print("No analysis file found.")
                    self.current_test[problem]['local_analysis'][analysis_name] = {}
            
            # ------------------------------------------------
            # Pull prerender data
            self.current_test[problem]['prerender_data'] = {}
            self.current_test[problem]['prerender_data_encoded'] = {}
            if self.imports[problem]['prerender_data_folder'] != '':
                print("Pulling prerender data...")
                try:
                    for prerender_name, prerender in self.imports[problem]['prerender_data_filenames'].items():
                        if prerender.endswith(('.txt', '.json', '.xml', '.jsonl')):
                            # Load JSON or text file
                            if prerender.endswith('.jsonl') or prerender.endswith('.json'):
                                # Load JSONL file
                                data = {}
                                with urllib.request.urlopen(root+'/'+self.imports[problem]['prerender_data_folder']+'/'+prerender) as f:
                                    for line in f:
                                        row = (json.loads(line.decode('utf-8')))
                                        data.update(row)
                            elif prerender.endswith('.txt'):
                                # Load text file
                                data = json.loads(urllib.request.urlopen(root+'/'+self.imports[problem]['prerender_data_folder']+'/'+prerender).read().decode('utf-8'))
                            elif prerender.endswith('.xml'):
                                # Load XML file (assuming it contains numerical data)
                                import xml.etree.ElementTree as ET
                                tree = ET.parse(urllib.request.urlopen(root+'/'+self.imports[problem]['prerender_data_folder']+'/'+prerender))
                                root_xml = tree.getroot()
                                data = []
                                for elem in root_xml.findall('.//data'):
                                    data.append(float(elem.text))
                            else:
                                raise ValueError(f"Unsupported file format for prerender data: {prerender}")
                            print(f"Pulling prerender data for {prerender_name}...")
                            self.current_test[problem]['prerender_data'][prerender_name] = data
                except:
                    print(root+'/'+self.imports[problem]['prerender_data_folder']+'/'+prerender)
                    print("No prerender data found.")
                    self.current_test[problem]['prerender_data'] = {}
                try:
                    for prerender_name, prerender in self.imports[problem]['prerender_data_encoded_filenames'].items():
                        if prerender.endswith(('.txt', '.json', '.xml', '.jsonl')):
                            map_location= 'cpu' if torch.cuda.is_available() else 'cpu'
                            if (prerender.endswith('.jsonl') or prerender.endswith('.json')):
                                # Load JSONL file
                                data = []
                                with urllib.request.urlopen(root+'/'+self.imports[problem]['prerender_data_folder']+'/'+prerender) as f:
                                    for line in f:
                                        data.append(json.loads(line.decode('utf-8')))
                                data = torch.tensor(data, dtype=torch.float32).to(map_location)
                            elif prerender.endswith('.txt'):
                                data = torch.from_numpy(np.loadtxt(urllib.request.urlopen(root+'/'+self.imports[problem]['prerender_data_folder']+'/'+prerender), dtype=np.float32)).to(map_location)
                            elif prerender.endswith('.xml'):
                                # Load XML file (assuming it contains numerical data)
                                import xml.etree.ElementTree as ET
                                tree = ET.parse(urllib.request.urlopen(root+'/'+self.imports[problem]['prerender_data_folder']+'/'+prerender))
                                root_xml = tree.getroot()
                                data = []
                                for elem in root_xml.findall('.//data'):
                                    data.append(float(elem.text))
                                data = torch.tensor(data, dtype=torch.float32).to(map_location)
                            else:
                                raise ValueError(f"Unsupported file format for prerender data: {prerender}")
                            print(f"Pulling prerender encoded data for {prerender_name}...")
                            self.current_test[problem]['prerender_data_encoded'][prerender_name] = data
                except:
                    print("No prerender encoded data found.")
                    self.current_test[problem]['prerender_data_encoded'] = {}
            else:
                print("No prerender data found.")
                self.current_test[problem]['prerender_data'] = {}
                self.current_test[problem]['prerender_data_encoded'] = {}
            # ------------------------------------------------
            # Pull prerender images
            self.current_test[problem]['prerender_images'] = {}
            if self.imports[problem]['prerender_data_folder'] != '':
                try:
                    for image_name, image in self.imports[problem]['prerender_image_filenames'].items():
                        if image.endswith(('.png', '.jpg', '.svg', '.gif')):
                            image_url = root + '/' + self.imports[problem]['prerender_data_folder'] + '/' + image
                            image_data = urllib.request.urlopen(image_url).read()
                            self.current_test[problem]['prerender_images'][image_name] = image_data
                    print("Pulling prerender images...")
                except:
                    print("No prerender images found.")
                    self.current_test[problem]['prerender_images'] = {}
            else:
                print("No prerender images found.")
                self.current_test[problem]['prerender_images'] = {}
            # -----------------------------------------------
            # Pull instructions
            if self.imports[problem]['instruction_filenames'] != {}:
                try:
                    self.current_test[problem]['instructions'] = {}
                    for instruction_name, instruction in self.imports[problem]['instruction_filenames'].items():
                        instruction_data = json.loads(urllib.request.urlopen(root+'/'+self.imports[problem]['instruction_folder']+'/'+instruction).read())
                        self.current_test[problem]['instructions'][instruction_name] = instruction_data
                        print(f"Pulling instruction data for {instruction_name}...")
                except:
                    print("No instruction data found.")
                    self.current_test[problem]['instructions'] = {}
            else:
                print("No instructions found.")
                self.current_test[problem]['instructions'] = {}
            # -----------------------------------------------
        print("-----------------------------------------------")
        return self.current_test

    def setup(self, agent_config:dict={}) -> None:
        if agent_config == {}:
            agent_config = DefaultAgentConfig()
            self.ExperimentConfig = agent_config.data  
        else:
            self.ExperimentConfig = agent_config 

        return self.ExperimentConfig
    
    def add_applicaiton(self, problem:str, application_data:dict) -> None:
        """ Add a new application to the list of applications. 
        Reqired form:
            - engine: <engine.py>
            - experiment_configs: {experiment_config:experiment_config_path|<experiment_config.json>}
            - local_configs: {local_config:experiment_config_path|<local_config.json>}
            - adapters: {adapter:<adapter.py>}
            - local_analysis: {analysis:<analysis.py>}
            - prerender_data: {data:data_path|<data.txt>}
            - prerender_images: {image:<image.png>}
        """
        # ---
        # Get configs and data from path directory to imported json/txt files
        if type(list(application_data['experiment_configs'].values())[0])==str:
            experiment_config = {}
            for name,experiment_config_dir in application_data['experiment_configs'].items():
                with open (experiment_config_dir, 'r') as f:
                    # Load the JSON data from the file
                    agent_config = json.loads(f.read())
                    experiment_config[name] = agent_config
            application_data['experiment_configs'] = experiment_config

        if type(list(application_data['local_configs'].values())[0])==str:
            local_config = {}
            for name,local_config_dir in application_data['local_configs'].items():
                with open (local_config_dir, 'r') as f:
                    # Load the JSON data from the file
                    agent_config = json.loads(f.read())
                    local_config[name] = agent_config
            application_data['local_configs'] = local_config

        if len(application_data['prerender_data'])>0:
            if type(list(application_data['prerender_data'].values())[0])==str:
                data = {}
                for name,data_dir in application_data['prerender_data'].items():
                    with open (data_dir, 'r') as f:
                        # Load the JSON data from the file
                        agent_config = json.loads(f.read().decode('utf-8'))
                        data[name] = agent_config
                application_data['prerender_data'] = data
        # ---
        self.imports[problem] = application_data
        self.current_test[problem] = application_data
        print(f"Added {problem} to the list of applications.")
        print(f"Current applications: {self.imports.keys()}")

        return self.current_test
    
    def remove_application(self, problem:str) -> None:
        # Remove an application from the list of applications
        if problem in self.imports:
            del self.imports[problem]
            del self.current_test[problem]
            print(f"Removed {problem} from the list of applications.")
        else:
            print(f"{problem} not found in the list of applications.")

        return self.imports

            