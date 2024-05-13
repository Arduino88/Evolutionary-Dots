## Evolutionary Dots
A personal project inspired by the one and only **[Code Bullet](https://www.youtube.com/@CodeBullet)**

**This is my first foray into the world of numpy-only genetic algorithms**

#### Overview
In this program, a group of dots are released into an environment with walls and a goal object.
The dots have simulated velocity and acceleration, as well as an input list of acceleration vectors, which is the genetic component.

![](https://github.com/Arduino88/Evolutionary-Dots/blob/main/evolutionary-dots.gif?raw=true)

#### In each run:
- The dots iterate over their respective list, setting their acceleration to the contained vector, and checking for collisions.
- Once every dot has either died or reached the goal, their fitnesses are calculated:
  - fitness = 1 / (distance to goal) ^2.
  - if touching goal, fitness is multiplied by the remaining steps in the list (incentivizes more efficient paths).
  - if dead (collided with wall or screen border), divide fitness by two.
- Then, a new set of dots are created, with a probability of having a dot as a parent proportional to the parent's fitness (fitter dots are more likely as parents).
- Randomly, for each child in the new dot set, A gaussian noise distribution is calculated and applied to existing vectors.
- This is controlled by a mutation rate variable, with a low probability of an individual vector being mutated.
- The best dot is saved from the previous run, and is added to the next generation to prevent detrimental mutations regressing progress (This is the green dot).
- All dots are re-initialized at the beginning of their acceleration list, and placed at the shared starting position.
- The next run is initiated.

