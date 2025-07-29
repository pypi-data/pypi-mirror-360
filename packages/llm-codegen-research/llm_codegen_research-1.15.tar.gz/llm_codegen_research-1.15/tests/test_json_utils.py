"""Tests the JSON utilities."""

from llm_cgr import load_json, load_jsonl, save_json, save_jsonl


def test_json_utils(temp_dir):
    """
    Test the save_json and load_json functions.
    """
    # test saving and loading json dict
    original_dict = {"name": "Test Data", "value": 42}
    save_json(data=original_dict, file_path=f"{temp_dir}/test_data.json")
    loaded_dict = load_json(file_path=f"{temp_dir}/test_data.json")
    assert loaded_dict == original_dict

    # test saving and loading json list
    original_list = [{"name": "Test Data 1"}, {"name": "Test Data 2"}]
    save_json(data=original_list, file_path=f"{temp_dir}/test_data_list.json")
    loaded_list = load_json(file_path=f"{temp_dir}/test_data_list.json")
    assert loaded_list == {"data": original_list}


def test_jsonl_utils(temp_dir):
    """
    Test the save_jsonl and load_jsonl functions.
    """
    # test saving and loading json list
    original_list = [{"name": "Test Data 1"}, {"name": "Test Data 2"}]
    save_jsonl(data=original_list, file_path=f"{temp_dir}/test_data.jsonl")
    loaded_list = load_jsonl(file_path=f"{temp_dir}/test_data.jsonl")
    assert loaded_list == original_list

    # test saving and loading json dict
    original_dict = {"name": "Test Data", "value": 42}
    save_jsonl(data=original_dict, file_path=f"{temp_dir}/test_data_dict.jsonl")
    loaded_dict = load_jsonl(file_path=f"{temp_dir}/test_data_dict.jsonl")
    assert loaded_dict == [original_dict]
