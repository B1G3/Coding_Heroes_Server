# 스테이지 목표
함수 블록을 활용해서 **웜 2마리, 트로이 2마리**를 퇴치하자!

- 난이도: 3/5
- 사용블록: 함수 블록, 반복한다, If See, 이동한다, 공격한다
- 백신 유닛 종류: 백신 멍멍이, 백신 포병

## 요구 조건
- 유닛마다 함수 블록을 호출해. 트로이는 백신 포병이, 웜은 백신 멍멍이가 처리해.
- If See 블록에는 파라미터로 받은 바이러스가 들어가야해.

## 자주 하는 실수
- 공격 블록만 넣고 이동하지 않음   
- 행동 순서가 반대 (공격 → 이동) 

## 정답 예시 (JSON)
- 백신 포병이 트로이를 처리하는 경우
```json
{
  "line": [
    {
      "block_id": 1,
      "type": "UNIT",
      "name": "Start",
      "input": null,
      "args": null,
      "next": 2,
    },
    {
      "block_id": 2,
      "type": "FUNCTION",
      "name": "function1",
      "input": null,
      "args": ["트로이"],
      "next": 3
    },
    {
      "block_id": 3,
      "type": "UNIT",
      "name": "백신 멍멍이",
      "input": null,
      "args": null,
      "next": null,
    }
  ],
  "custom_function": [
    {
      "name": "function1",
      "params": [
        {
          "type": "바이러스",
          "name": "virus"
        }
      ],
      "line": [
        {
          "block_id": 11,
          "type": "CONTROL",
          "name": "반복한다",
          "input": null,
          "args": null,
          "next": 12
        },
        {
          "block_id": 12,
          "type": "CONTROL",
          "name": "만약 본다면",
          "input": "virus",
          "args": null,
          "next": 13
        },
        {
          "block_id": 13,
          "type": "ACTION",
          "name": "이동한다",
          "input": null,
          "args": null,
          "next": 14
        },
        {
          "block_id": 14,
          "type": "ACTION",
          "name": "공격한다",
          "input": null,
          "args": null,
          "next": null
        }
      ],
      "return_": {}
    }
  ]
}
```
유닛이 유닛 멍멍이인 경우 함수 블록의 args에는 백신 포병이 들어가야해.