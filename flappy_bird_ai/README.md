# Flappy-bird-python
A basic Flappy Bird game made in Python

I took the assets from https://github.com/zhaolingzhi/FlapPyBird-master | Credits to him

## How to run 
The Agent program can be set to training or to play automatically.
<pre>
To play automatically, under the main heading set:
  save_data = False
  train_model = False
To train, under the main heading set:
  save_data = True (This will continue previous training)
  train_model = True
</pre>

## Tips and Notes
- Flappy.py contains the base game, Flappy_RI contains the modified environment for the agent
- Under pretrained models folder, you will find old models that have been trained before, pre_train_200 means I used 200 epochs ect.
So far 350 has provided best results, and 1000 has been overtrained meaning the agent quickly dies. You can observe the automatic play
of these models by making a copy and bringing them out of the folder, renaming them to simply pre_train.pth.

## Current State:
![Screenshot](https://github.com/LeonMarqs/Flappy-bird-python/blob/master/Screenshot_1.png)

## Dependence:
* pygame

## Contribution
It's a simple model, so I'd be very grateful if you could help me to improve the game.



