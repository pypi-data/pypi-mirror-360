import json
import re

import loguru

WARNING_FLAG = False


def check_hive_reward_json_valid(hive_reward_data: json):
    """
    校验 hive-reward.json 文件是否符合 HIVE-REWARD-DATASET 规范
    :param hive_reward_data: hive-reward.json 文件内容
    :return: None
    """
    assert 'topic' in hive_reward_data, "hive_reward_data must have topic"
    assert 'checkpoint' in hive_reward_data, "hive_reward_data must have checkpoint"
    assert len(hive_reward_data['topic']) > 0, "topic must not be empty"
    assert len(hive_reward_data['checkpoint']) > 0, "checkpoint must not be empty"
    if 'matchingmethod' in hive_reward_data:
        assert len(hive_reward_data['matchingmethod']) == len(
            hive_reward_data['checkpoint']), "matchingmethod and checkpoint must have the same length"

    for item in hive_reward_data['checkpoint']:
        for keyword, score in item.items():
            assert isinstance(keyword, str), f"keyword must be a string: {item.items()}"
            assert isinstance(score, (int, float)), f"score must be a number: {item.items()}"
            assert score >= 0, f"score must be greater than or equal to 0: {item.items()}"


def calc_normal_mode_reward(checkpoint: dict, response: str) -> float:
    """
    计算normal模式的奖励: checkpoint其中有关键词命中，加对应的分数
    :param checkpoint: 参考答案
    :param response: 用户答案
    """
    for keyword, score in checkpoint.items():
        return score if keyword in response else 0.0


def calc_regex_mode_reward(checkpoint: dict, response: str) -> float:
    """
    计算regex模式的奖励: checkpoint其中有正则表达式命中，加对应的分数
    """
    for restr, score in checkpoint.items():
        return score if re.search(restr, response) else 0.0


def parse_hive_reward(hive_reward_data: json, response: str) -> float:
    """
    根据输入的hive-reward.json和response进行打分
    """
    global WARNING_FLAG
    hit_response = response
    check_hive_reward_json_valid(hive_reward_data)
    data = {
        "checkpoint": hive_reward_data['checkpoint'],
        "matchingmethod": hive_reward_data.get('matchingmethod', 'normal'),
    }
    total_score = -1.0
    for i in range(len(data['checkpoint'])):
        if data['matchingmethod'][i] == 'regex':
            total_score += calc_regex_mode_reward(data['checkpoint'][i], response)
        else:
            if not WARNING_FLAG:
                WARNING_FLAG = True
                loguru.logger.warning(f"unknown matchingmethod: {data['matchingmethod'][i]},default to normal mode")
            total_score += calc_normal_mode_reward(data['checkpoint'][i], response)
    return total_score
