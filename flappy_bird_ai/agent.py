import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from collections import deque
import random
from flappy_RI import FlappyBirdEnv
import os

################# QNET COMPLETE ######################

class QNet(nn.Module):
    def __init__(self, input_dim, f1_dim, f2_dim, output_dim):
        super(QNet, self).__init__()
        self.fc1 = nn.Linear(input_dim, f1_dim)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(f1_dim, f2_dim)
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(f2_dim, output_dim)

    def forward(self, x):
        x = self.relu1(self.fc1(x))
        x = self.relu2(self.fc2(x))
        x = self.fc3(x)
        return x


################# AGENT ######################
class DQNAgent:
    def __init__(self, state_size, action_size):
        self.DQN = QNet(state_size, 32, 32, action_size)
        self.target_net = QNet(state_size, 32, 32, action_size)
        self.target_net.load_state_dict(self.DQN.state_dict())
        self.optimizer = optim.Adam(self.DQN.parameters(), lr=0.001)
        self.replay_buffer = deque(maxlen=10000)
        self.gamma = 0.99  # Discount factor
        self.epsilon = 1  # Initial exploration rate
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.001

    def select_action(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randint(0, 20) > 18  # Explore
        else:
            q_values = self.DQN(torch.FloatTensor(state))
            return torch.argmax(q_values).item()  # Exploit

    def remember(self, state, action, reward, next_state, done):
        self.replay_buffer.append((state, action, reward, next_state, done))

    def experience_replay(self, batch_size):
        if len(self.replay_buffer) < batch_size:
            return

        minibatch = random.sample(self.replay_buffer, batch_size)
        states, actions, rewards, next_states, dones = map(list, zip(*minibatch))

        # Convert lists to PyTorch tensors
        states = torch.tensor(states, dtype=torch.float32)
        actions = torch.tensor(actions, dtype=torch.long)
        rewards = torch.tensor(rewards, dtype=torch.float32)
        next_states = torch.tensor(next_states, dtype=torch.float32)
        dones = torch.tensor(dones, dtype=torch.float32)

        q_values = self.DQN(torch.FloatTensor(states))
        next_q_values = self.target_net(torch.FloatTensor(next_states)).max(dim=1).values

        targets = q_values.clone()
        targets[np.arange(batch_size), actions] = rewards + (1 - dones) * self.gamma * next_q_values

        loss = nn.MSELoss()(q_values, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def update_target_network(self):
        self.target_net.load_state_dict(self.DQN.state_dict())


################# TRAINING ######################
def train(env, agent, num_episodes, batch_size):
    for episode in range(num_episodes):
        state = env.reset()
        total_reward = 0

        while True:
            action = agent.select_action(state)
            next_state, reward, done = env.step(action)
            agent.remember(state, action, reward, next_state, done)
            agent.experience_replay(batch_size)

            total_reward += reward
            state = next_state

            if done:
                break

        agent.update_target_network()

        # Decay exploration rate
        agent.epsilon = max(agent.epsilon * agent.epsilon_decay, agent.epsilon_min)

        # Print episode information
        print(f"Episode: {episode + 1}, Total Reward: {total_reward}")

################# Autoplay ######################
def play(env, agent):
    state = env.reset()
    agent.epsilon = 0
    while True:
        action = agent.select_action(state)
        state, reward, done = env.step(action)

        if done:
            break


################# MAIN ######################
save_data = True
train_model = False

# define the state_size and action_size based on environment
state_size = 4
action_size = 2
agent = DQNAgent(state_size, action_size)

if os.path.exists("pre_train.pth") and train_model == False:
    # load pretrained weights
    checkpoint = torch.load("pre_train.pth")
    loaded_model = agent.DQN
    loaded_model.load_state_dict(checkpoint['model_state_dict'])

env = FlappyBirdEnv()
batch_size = 15
if train_model == True:
    train(env, agent, 350, batch_size)
else:
    for i in range(1,10):
        play(env, agent)

if save_data == True and train_model == True:
    checkpoint_path = 'pre_train.pth'
    torch.save({'model_state_dict': agent.DQN.state_dict(),
                'target_model_dict': agent.target_net.state_dict(),
                'optimizer_state_dict': agent.optimizer.state_dict(),
                'replay_buffer': list(agent.replay_buffer),
                'gamma': agent.gamma,
                'epsilon': agent.epsilon,
                'epsilon_decay': agent.epsilon_decay
                }, checkpoint_path)