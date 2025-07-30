import threading

import portal
import gymnasium as gym
from functools import partial
from portal_env.config import config
from portal_env.utils import handle_raw_integer
from typing import Callable, Any


class EnvSidePortal:
    def __init__(self, env_factory: Callable[[Any], gym.Env], port: int = config.port):
        self.portal = portal.BatchServer(port)
        self.env_factory = env_factory
        self._envs = {}
        self._lock = threading.Lock()
        self._next_id = 0

        self.portal.bind('create', self._create_env)
        self.portal.bind('reset', self._reset_handler)
        self.portal.bind('step', self._step_handler)
        self.portal.bind('action_space', partial(self._space_handler, space_type='action_space'))
        self.portal.bind('observation_space', partial(self._space_handler, space_type='observation_space'))

    def _create_env(self, *args, **kwargs):
        env = self.env_factory(*args, **kwargs)
        
        with self._lock:
            env_id = self._next_id
            self._envs[env_id] = env
            self._next_id += 1
        return env_id

    def _reset_handler(self, env_id: int):
        env_id = handle_raw_integer(env_id)
        assert env_id in self._envs, f"Invalid env_id: {env_id}"
        env = self._envs[env_id]
        return env.reset()

    def _step_handler(self, env_id, action):
        env_id = handle_raw_integer(env_id)
        assert isinstance(env_id, int), f"Got invalid env_id: {env_id}"
        assert env_id in self._envs, f"Invalid env_id: {env_id}"
        env = self._envs[env_id]
        return env.step(action)

    def _space_handler(self, env_id: int, space_type: str):
        env_id = handle_raw_integer(env_id)
        assert isinstance(env_id, int), f"Got invalid env_id: {env_id}"
        print(f"Got env_id: {env_id}, space_type: {space_type}")
        assert env_id in self._envs, f"Invalid env_id: {env_id}"
        env = self._envs[env_id]
        return str(getattr(env, space_type))

    def start(self):
        self.portal.start()


