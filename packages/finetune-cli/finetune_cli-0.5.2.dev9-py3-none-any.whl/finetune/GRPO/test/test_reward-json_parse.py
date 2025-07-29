import json

from finetune.GRPO.hive_reward_parser import parse_hive_reward


def test_hive_reward_parser():
    data_path = "2021QWB-DUTU-php-unserialize.hive-reward.json"
    hive_reward_json = json.loads(open(data_path, encoding='utf-8').read())
    response = '测试，这道题是反序列化题，其中有$a->name->file["filename"]->a= new Room();'
    assert parse_hive_reward(hive_reward_json, response) == -1.0 + 0.2 + 0.2
