
base_url = "https://jolly-accepted-bonefish.ngrok-free.app"

import requests


if __name__ == "__main__":
    stage = "learn"
    block_json = {
        "line": [
            {
                "block_id": 1,
                "type": "UNIT",
                "name": "Start",
                "next": 2
            },
            {
                "block_id": 2,
                "type": "ACTION",
                "name": "이동한다",
                "next": 3
            },
            {
                "block_id": 3,
                "type": "UNIT",
                "name": "백신 멍멍이"
            }
        ]
    }

    import json
    block_json_str = json.dumps(block_json, ensure_ascii=False)
    print(block_json_str)

    endpoint = "ai_npc/execution_log"
    url = f"{base_url}/{endpoint}"

    payload = {
        "stage": stage,
        "block_json": block_json_str
    }
    response = requests.post(url, json=payload)

    print("Status Code", response.status_code)