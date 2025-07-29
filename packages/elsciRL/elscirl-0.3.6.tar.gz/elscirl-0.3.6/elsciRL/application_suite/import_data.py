#  Define data through class function so it can be called within package
# Instead of using a .json file which is hard to load from local install
# NOTE: MAKE SURE TO TRUST REPOSITORIES BEFORE RUNNING CODE
# - Can set branch to specific commit to ensure no changes are made without knowledge
#   |-----> changed to commit id which is tied to branch and more stable
# - Compatibility defined to a single engine file
#   |-----> Adapters must be compatible with the given engine
# - Experiment configs are defined in the experiment_configs folder
#   |-----> NOTE: AT LEAST TWO EXPERIMENT CONFIGS MUST BE DEFINED
#       |-----> This is so that it triggers the selection swap on the server side
# - OBSERVED STATES MUST MATCH ADAPTER SELECTION NAMING
#    |-----> ENCODED STATES MUST MATCH OBSERVED STATES NAMING
#    |-----> For multiple versions from same adapter, use -v2, -v3, etc.
class Applications:
    def __init__(self):
        self.data ={
            "Sailing":{
                "github_user": "pdfosborne",
                "repository": "elsciRL-App-Sailing",
                "commit_id": "*",
                "engine_folder": "environment",
                "engine_filename": "engine",
                "config_folder": "configs",
                "experiment_config_filenames": {"quick-test":"testing.json", 
                                                "Osborne-2024":"config.json"},
                "local_config_filenames": {"easy":"config_local.json"},
                "local_adapter_folder": "adapters",
                "adapter_filenames": {"default":"default", "language":"language", "LLM":"LLM_adapter"},
                "local_analysis_folder": "analysis",
                "local_analysis_filenames": {"sailing_graphs":"sailing_graphs"},
                "prerender_data_folder": "prerender",
                "prerender_data_filenames": {"language-v1":"observed_states_language_1000000.txt",
                                            "LLM-llama-v1":"observed_states_Sailing_easy_LLM_llama32_100000_v1.jsonl"},
                "prerender_data_encoded_filenames":{},
                "prerender_image_filenames": {"Setup":"sailing_setup.png"},
                "instruction_folder": "instructions",
                "instruction_filenames": {"osborne2025":"Osborne2025_instruction_results_Sailing_LLM-llama-v1.json"}
                },
            "Classroom":{
                "github_user": "pdfosborne",
                "repository": "elsciRL-App-Classroom",
                "commit_id": "*",
                "engine_folder": "environment",
                "engine_filename": "engine",
                "config_folder": "configs",
                "experiment_config_filenames": {"default":"config.json"},
                "local_config_filenames": {"classroom_A":"classroom_A.json"},
                "local_adapter_folder": "adapters",
                "adapter_filenames": {"default":"default", "classroom_A_language":"classroom_A_language", "LLM":"LLM_adapter"},
                "local_analysis_folder": "analysis",
                "local_analysis_filenames": {},
                "prerender_data_folder": "prerender",
                "prerender_data_filenames": {"classroom_A_language-v1":"observed_states_Classroom_classroom_A_classroom_A_language_100.txt", 
                                            "LLM-v1":"observed_states_Classroom_classroom_A_LLM_llama32_100.txt"},
                "prerender_data_encoded_filenames":{"classroom_A_language-v1":"encoded_observed_states_Classroom_classroom_A_classroom_A_language_100.txt",
                                                    "LLM-v1":"encoded_observed_states_Classroom_classroom_A_LLM_llama32_100.txt"},
                "prerender_image_filenames": {"Classroom_A_Setup":"Classroom_A_Summary.png"},
                "instruction_folder": "instructions",
                "instruction_filenames": {"test":"instruction_results_Classroom_test.json",
                                          "osborne2025":"Osborne2025_instruction_results_Classroom_LLM.json"}
                },
            "Gym-FrozenLake":{
                "github_user": "pdfosborne",
                "repository": "elsciRL-App-GymFrozenLake",
                "commit_id": "*",
                "engine_folder": "environment",
                "engine_filename": "engine",
                "config_folder": "configs",
                "experiment_config_filenames": {"quick_test":"fast_agent.json", "Osborne2024_agent":"Osborne2024_agent.json"},
                "local_config_filenames": {"Osborne2024_env":"Osborne2024_env.json"},
                "local_adapter_folder": "adapters",
                "adapter_filenames": {"numeric_encoder":"numeric", "language":"language", "LLM":"LLM_adapter"},
                "local_analysis_folder": "analysis",
                "local_analysis_filenames": {},
                "prerender_data_folder": "prerender",
                "prerender_data_filenames": {"language-v1":"observed_states_Gym-FrozenLake_Osborne2024_env_language_100.txt", 
                                            "LLM-v1":"observed_states_Gym-FrozenLake_Osborne2024_env_LLM_llama32_100.txt"},
                "prerender_data_encoded_filenames": {"language-v1":"encoded_observed_states_Gym-FrozenLake_Osborne2024_env_language_100.txt",
                                            "LLM-v1":"encoded_observed_states_Gym-FrozenLake_Osborne2024_env_LLM_llama32_100.txt"},
                "prerender_image_filenames": {"FrozenLake_Setup":"FrozenLake_4x4.png"},
                "instruction_folder": "instructions",
                "instruction_filenames": {"osborne2025":"Osborne2025_instruction_results_Gym-FrozenLake_LLM.json"}
                },
            "Chess":{
                "github_user": "pdfosborne",
                "repository": "elsciRL-App-Chess",
                "commit_id": "*",
                "engine_folder": "environment",
                "engine_filename": "engine",
                "config_folder": "configs",
                "experiment_config_filenames": {"Osborne2024_agent":"config.json"},
                "local_config_filenames": {"Osborne2024_env":"config_local.json"},
                "local_adapter_folder": "adapters",
                "adapter_filenames": {"numeric_board_mapping": "numeric_board",
                                      "numeric_piece_counter":"numeric_piece_counter", 
                                      "active_pieces_language":"language_active_pieces",
                                      "LLM":"LLM_adapter"},
                "local_analysis_folder": "analysis",
                "local_analysis_filenames": {},
                "prerender_data_folder": "prerender",
                "prerender_data_filenames": {"active_pieces_language-v1":"observed_states_active_pieces_language_50000.txt",
                                             "LLM-v1": "observed_states_Chess_Osborne2024_env_LLM_llama32_100000.jsonl",},
                "prerender_data_encoded_filenames":{},
                "prerender_image_filenames": {"Board_Setup":"board_start.png"},
                "instruction_folder": "instructions",
                "instruction_filenames": {"osborne2025":"Osborne2025_instruction_results_Chess_LLM-v1.json"}
                },
            # "TextWorldExpress":{
            #     "github_user": "pdfosborne",
            #     "repository": "elsciRL-App-TextWorldExpress",
            #     "commit_id": "*",
            #     "engine_folder": "environment",
            #     "engine_filename": "engine",
            #     "config_folder": "configs",
            #     "experiment_config_filenames": {"Osborne2024_agent":"config.json"},
            #     "local_config_filenames": {"twc-easy":"twc-easy.json", 
            #                                 "twc-medium":"twc-medium.json",
            #                                 "twc-hard":"twc-hard.json", 
            #                                 "cookingworld-easy":"cookingworld-easy.json",
            #                                 "cookingworld-medium":"cookingworld-medium.json",
            #                                 "cookingworld-hard":"cookingworld-hard.json", 
            #                                 "coincollector":"coincollector.json",
            #                                 "mapreader":"mapreader.json"},
            #     "local_adapter_folder": "adapters",
            #     "adapter_filenames": {"language_default":"language", "LLM":"LLM_adapter"},
            #     "local_analysis_folder": "analysis",
            #     "local_analysis_filenames": {},
            #     "prerender_data_folder": "prerender",
            #     "prerender_data_filenames": {
            #         "language-v1":
            #             "observed_states_TextWorldExpress_twc-easy_language_default_10000_29-05-2025_15-53.txt",
            #         "LLM-v1":
            #             "observed_states_TextWorldExpress_cookingworld-easy_language_default_10000_29-05-2025_16-02.txt",},
            #     "prerender_data_encoded_filenames":{},
            #     "prerender_image_filenames": {},
            #     "instruction_folder": "instructions",
            #     "instruction_filenames": {}
            #     },
            "Maze":{
                "github_user": "pdfosborne",
                "repository": "elsciRL-App-Maze",
                "commit_id": "*",
                "engine_folder": "environment",
                "engine_filename": "engine",
                "config_folder": "configs",
                "experiment_config_filenames": {"default_agent":"config.json"},
                "local_config_filenames": {"umaze":"umaze.json",
                                           "double_t_maze":"double_t_maze.json",
                                           "medium":"medium.json",
                                           "large":"large.json",
                                           #"random":"random.json"
                                           },
                "local_adapter_folder": "adapters",
                "adapter_filenames": {"language_default":"language", "LLM":"LLM_adapter"},
                "local_analysis_folder": "analysis",
                "local_analysis_filenames": {},
                "prerender_data_folder": "prerender",
                "prerender_data_filenames": {'language-umaze-v1':'observed_states_Maze_umaze_language_default_1000.txt',
                                            'LLM-umaze-v1':'observed_states_Maze_umaze_LLM_llama32_100.txt',
                                            'language-double_t_maze-v1':'observed_states_Maze_double_t_maze_language_default_1000.txt',
                                            'LLM-double_t_maze-v1':'observed_states_Maze_double_t_maze_LLM_llama32_1000.txt',
                                            'language-medium-v1':'observed_states_Maze_medium_language_default_1000.txt',
                                            'LLM-medium-v1':'observed_states_Maze_medium_LLM_llama32_1000.txt',
                                            'language-large-v1':'observed_states_Maze_large_language_default_1000.txt',
                                            'LLM-large-v1':'observed_states_Maze_large_LLM_llama32_1000.txt'
                                            },
                "prerender_data_encoded_filenames":{'language-umaze-v1':'encoded_observed_states_Maze_umaze_language_default_1000.txt',
                                            'LLM-umaze-v1':'encoded_observed_states_Maze_umaze_LLM_llama32_100.txt',
                                            'language-double_t_maze-v1':'encoded_observed_states_Maze_double_t_maze_language_default_1000.txt',
                                            'LLM-double_t_maze-v1':'encoded_observed_states_Maze_double_t_maze_LLM_llama32_1000.txt',
                                            'language-medium-v1':'encoded_observed_states_Maze_medium_language_default_1000.txt',
                                            'LLM-medium-v1':'encoded_observed_states_Maze_medium_LLM_llama32_1000.txt',
                                            'language-large-v1':'encoded_observed_states_Maze_large_language_default_1000.txt',
                                            'LLM-large-v1':'encoded_observed_states_Maze_large_LLM_llama32_1000.txt'
                                            },
                "prerender_image_filenames": {},
                "instruction_folder": "instructions",
                "instruction_filenames": {"osborne2025umaze":"Osborne2025_instruction_results_Maze_LLM-umaze-v1.json",
                                          "osborne2025double_t_maze":"Osborne2025_instruction_results_Maze_LLM-double_t_maze-v1.json",
                                          "osborne2025medium":"Osborne2025_instruction_results_Maze_LLM-medium-v1.json",
                                          "osborne2025large":"Osborne2025_instruction_results_Maze_LLM-large-v1.json"}
                }
        }