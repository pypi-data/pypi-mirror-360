import json
import random

import loguru

from finetune.GRPO.hive_reward_parser import parse_hive_reward


def hive_reward(completions, **kwargs):
    """
    根据reward-hive.json进行打分
    """
    try:
        scores = []
        if random.random() < 0.01:
            loguru.logger.debug(f"Completions: {completions}")
            loguru.logger.debug(f"Len of completions: {len(completions)}")
        for completion in completions:
            assert 'metadata' in kwargs, "metadata is required."
            assert 'hive-reward' in kwargs['metadata'][0], f"hive-reward is required,now: {kwargs['metadata']}"
            metadata = kwargs['metadata']
            hive_reward_data = json.loads(metadata[0]['hive-reward'])
            scores.append(parse_hive_reward(hive_reward_data=hive_reward_data, response=completion[0]['content']))
        return scores
    except Exception as e:
        loguru.logger.trace(e)
        loguru.logger.error(f"Completions: {completions}")
        return [-1.0] * len(completions)
