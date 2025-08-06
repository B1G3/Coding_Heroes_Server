from core.database import init_db, delete_messages_by_ids

base_url = "http://localhost:8000"


from core.models import Base, User, Message
import requests

from core.database import save_user
from core.database import delete_playrecord

def save_sample_user_test(user_id, username):
    save_user(user_id, username)


def save_playrecord_test(stage, block_data):
    endpoint = "ai_npc/playrecord"
    url = f"{base_url}/{endpoint}"

    import json
    json_str = json.dumps(block_data, ensure_ascii=False)

    payload = {
        "stage": stage,
        "json_str": json_str
    }
    response = requests.post(url, json=payload)

    print("Status Code", response.status_code)
    print("Response", response.json())



def delete_playrecord_api_test(ids: list):
    delete_playrecord(ids)


if __name__ == "__main__":
    # save_sample_user("u001", "은빈빈")

    playrecord_ids = [1]
    delete_playrecord_api_test(playrecord_ids)


        # JSON 구조를 Python dict로 먼저 선언
    stage = "1"
    block_data = {
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
                "name": "공격한다",
                "next": 4
            },
            {
                "block_id": 3,
                "type": "ACTION",
                "name": "이동한다",
                "next": 4
            },
            {
                "block_id": 4,
                "type": "UNIT",
                "name": "백신 멍멍이"
            }
        ]
    }

    save_playrecord_test(stage, block_data)
