# 스테이지
보스 스테이지

## 스테이지 목표
데이터로드를 통해 들어오는 웜을 퇴치하자.

- 필수 사용블록: 유닛블록, While 제어블록, If 제어블록, 이동한다 행동블록, 공격한다 행동블록, 정수 입력블록
- 권장 사용블록: 함수블록
- 사용유닛: 백신 멍멍이

### 요구사항
- 웜은 백신 멍멍이가 처리할 수 있어.

## 블록 설명
### 함수 블록
- 반복적으로 사용할 것 같은 블록 모음을 함수블록으로 만들어 재사용할 수 있어.
- 바이러스를 함수의 매개변수로 두고, 매개값을 변경하여 백신 멍멍이가 처리할 바이러스를 지정할 수 있어.

## 자주 하는 실수
- 이동블록 없이 공격블록만 연결하여 유닛이 이동하지 않는다.
- 이동블록에 입력블록을 연결하지 않아 유닛이 이동하지 않는다.
- 공격블록 없이 이동블록만 연결하여 유닛이 공격모션을 취하지 않는다.
- 공격블록 후에 이동블록을 연결한다.

## 정답 예시 (JSON)
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
          "name": "바이러스"
        }
      ],
      "line": [
        {
          "block_id": 11,
          "type": "CONTROL",
          "name": "While",
          "input": null,
          "args": null,
          "next": 12
        },
        {
          "block_id": 12,
          "type": "CONTROL",
          "name": "If",
          "input": 
          {
            "type": "INPUT",
            "name": "바이러스",
            "value": null
          },
          "args": null,
          "next": 13
        },
        {
          "block_id": 13,
          "type": "ACTION",
          "name": "이동한다",
          "input": 
          {
            "block_id": 4,
            "type": "INPUT",
            "name": "정수",
            "value": 1
          },
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