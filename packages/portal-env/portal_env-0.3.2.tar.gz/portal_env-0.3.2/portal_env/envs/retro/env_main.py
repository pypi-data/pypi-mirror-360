from portal_env import EnvSidePortal
import gymnasium
import retro


class GymnasiumWrapper(gymnasium.Env):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.retro_env = retro.make(*args, **kwargs)

    @property
    def action_space(self):
        return self.retro_env.action_space
    
    @property
    def observation_space(self):
        return self.retro_env.observation_space

    def step(self, action):
        obs, reward, done, info = self.retro_env.step(int(action))
        terminated = done
        truncated = False
        return obs, reward, terminated, truncated, info
    
    def reset(self, *, seed = None, options = None):
        return self.retro_env.reset(), {}


def main():
    portal = EnvSidePortal(env_factory=GymnasiumWrapper)
    portal.start()


if __name__ == '__main__':
    main()
