import pickle
import torch
import numpy as np
from elsciRL.agents.agent_abstract import QLearningAgent
import gymnasium as gym
from stable_baselines3 import A2C
from PIL import Image # Used to generate GIF


class SB_A2C(QLearningAgent):
    def __init__(self, policy:str='MlpPolicy', env:gym.Env = None, learning_rate=0.0007, n_steps=500):
        self.epsilon: int = 0 # Not used currently but required for compatibility
        self.device = "auto" if torch.cuda.is_available() else "cpu" # A2C is meant to be run primarily on the CPU, especially when you are not using a CNN.
        self.a2c = A2C(policy, env, verbose=0, device="cpu", 
                       learning_rate=learning_rate, n_steps=n_steps)
        if torch.cuda.is_available():
            print("---- A2C is meant to be run primarily on the CPU ----")
            print("Device:", self.a2c.device)

    def policy(self, state: any) -> str:
        # TODO: make sure output is int
        return self.a2c.predict(state)

    def learn(self, total_steps:int=100) -> float:
        self.a2c.learn(total_timesteps=total_steps)
    
    def test(self, env, render:bool=False):
        #mean_reward, std_reward = evaluate_policy(self.a2c, env, n_eval_episodes=1)
        # Using environment from agent may limit episodes based on prior experience
        #vec_env = self.a2c.get_env()
        
        vec_env = env
        obs, info = vec_env.reset()
        
        actions = []
        states = []

        done = False
        episode_reward = 0
        render_stack = []
        if render:
            render_stack.append(
                Image.fromarray(vec_env.render().astype('uint8'))
                )
        while not done: 
            action, _state = self.a2c.predict(obs, deterministic=True)
            if isinstance(action, np.int64):
                actions.append(action.item())
            else:
                actions.append(action)
            # actions.append(int(action))
            obs, r, done, truncated, info = vec_env.step(action)
            episode_reward += r
            if render:
                render_stack.append(Image.fromarray(vec_env.render().astype('uint8')))
        
            #states.append(info[0]['obs'])
            states.append(info['obs'])
            #vec_env.render("human")

        #episode_reward = info[0]['episode']['r']
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
    
    