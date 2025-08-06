# 스테이지 목표
행동블록을 잘 조합해서 **웜 한마리**를 퇴치하자!

- 난이도: 1/5
- 사용블록: 이동한다, 공격한다
- 유닛 종류: 백신 멍멍이

## 요구 조건

- 백신 멍멍이는 적을 향해 이동한 후 적을 공격해야해.
- 제어문, 조건, 반복 없이 **간단한 직선 흐름**을 사용해.
- 함수, 조건 블록은 사용하지 않는다.

## 자주 하는 실수

- 공격 블록만 넣고 이동하지 않음   
- 행동 순서가 반대 (공격 → 이동) 

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
      "type": "ACTION",
      "name": "이동한다",
      "input": null,
      "args": null,
      "next": 3
    },
    {
      "block_id": 3,
      "type": "ACTION",
      "name": "공격한다",
      "input": null,
      "args": null,
      "next": 4,
    },
    {
      "block_id": 4,
      "type": "UNIT",
      "name": "백신 멍멍이",
      "input": null,
      "args": null,
      "next": null,
    }
  ],
  "custom_function": null
}
```


