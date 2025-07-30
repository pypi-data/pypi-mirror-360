from collections import Counter
from typing import Optional
from pathlib import Path
from util.uitl import read_jsonl_from_path, save_jsonl_from_data


# for line in init_data:
#     msg = line["messages"]
#     for i, item in enumerate(msg):
#         if item["role"] == "user":
#             new_data.append({"prompt": msg[:i+1]})

def loop(file_path: Optional[Path],
         save_path: Optional[Path],
         sample_size: Optional[int]=20000):
    """
        在数据中只保留存在， 问诊或者套电的prompt 数据
    """
    data = read_jsonl_from_path(file_path)
    count = Counter()
    new_data = []
    for line in data:
        action = line["prompt"][-1]["content"].split("action:")[1]
        if "问诊" in action:
            count["问诊"] += 1
            new_data.append(line)
        elif "套电" in action and "套电后" not in action:
            count["套电"] += 1
            new_data.append(line)
        else:
            count["*"] += 1
    import random
    random.shuffle(new_data[:sample_size])
    print(count)
    save_jsonl_from_data(new_data, save_path)