class DefaultAgentConfig:
    def __init__(self):
        self.data ={   
            "name": "Default",
            "problem_type": "Default",
                         
            "number_training_episodes": 1000,
            "number_training_repeats": 5,
            "number_training_seeds": 1,

            "test_agent_type":"best",
            "number_test_episodes": 200,
            "number_test_repeats": 10,

            "agent_select": ["Qlearntab"],
            "adapter_select": ["default"],
            "agent_parameters":{
                "Qlearntab":{
                    "alpha": 0.1,
                    "gamma": 0.95,
                    "epsilon": 1,
                    "epsilon_step":0
                    },
            }
        }
