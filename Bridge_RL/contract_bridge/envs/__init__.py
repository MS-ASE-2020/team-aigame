from gym.envs.registration import register
from .bridge_trick_taking import BridgeEnv

register(
    id='contract-bridge-v0',
    entry_point='contract_bridge.envs:BridgeEnv',
)