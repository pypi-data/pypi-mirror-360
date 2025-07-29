import pickle
import torch
import numpy as np
from elsciRL.agents.agent_abstract import QLearningAgent
import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy
from PIL import Image # Used to generate GIF

class SB_PPO(QLearningAgent):
    def __init__(self, policy:str='MlpPolicy', env:gym.Env = None, learning_rate:float=0.0003, n_steps:int=2048):
        self.epsilon: int = 0 # Not used currently but required for compatibility
        self.device = "auto" if torch.cuda.is_available() else "cpu"
        self.ppo = PPO(policy, env, verbose=0, device=self.device, 
                       learning_rate=learning_rate, n_steps=n_steps)
        if torch.cuda.is_available():
            print("---- Using GPU ----")
            print("Device:", self.ppo.device)
    
    def policy(self, state: any) -> str:
        return self.ppo.predict(state)

    def learn(self, total_steps:int=100) -> float:
        self.ppo.learn(total_timesteps=total_steps)
    
    def test(self, env, render:bool=False):
        #mean_reward, std_reward = evaluate_policy(self.a2c, env, n_eval_episodes=1)
        vec_env = self.ppo.get_env()
        obs = vec_env.reset()
        
        actions = []
        states = []

        done = False
        render_stack = []
        if render:
            render_stack.append(
                Image.fromarray(vec_env.render().astype('uint8'))
                )
        while not done: 
            action, _state = self.ppo.predict(obs, deterministic=True)
            if isinstance(action, np.int64):
                actions.append(action.item())
            else:
                actions.append(action[0])
            #actions.append(action[0])
            
            obs, r, done, info = vec_env.step(action)
            states.append(info[0]['obs'])
            if render:
                render_stack.append(
                    Image.fromarray(vec_env.render().astype('uint8'))
                    )
            
            #vec_env.render("human")
        episode_reward = info[0]['episode']['r']
        if episode_reward > 0.5:
            print("----> ", episode_reward)
            
        return episode_reward, actions, states, render_stack
    
    def q_result(self):
        results = [0,0]
        total_q = results[0]
        mean_q = results[1]
        return total_q, mean_q
    
    def clone(self):
        clone = pickle.loads(pickle.dumps(self))
        return clone
    
    