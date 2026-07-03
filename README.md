# watch-playwright

브라우저 렌더링 서버. 크롤러가 HTTP로 URL을 보내면 Chromium으로 렌더한 HTML을 반환한다.
`asyncio.Semaphore`로 동시 Chromium 수를 강제하므로, 크롤러가 몇 개든 브라우저 자원은 여기서 통제된다.

## API

### POST /render

```json
{
  "url": "https://example.com",
  "wait_until": "networkidle",
  "wait_for": "li.item",
  "sleep": 0,
  "goto_timeout_ms": 30000,
  "wait_for_timeout_ms": 10000
}
```

- `url` (필수): 렌더할 페이지
- `wait_until`: goto 대기 조건 (기본 `networkidle`)
- `wait_for`: 이 셀렉터가 나타날 때까지 대기 (선택)
- `sleep`: 렌더 후 추가 대기 초 (선택)

응답: `{"html": "<렌더된 HTML>"}`
실패 시: 500 + `{"detail": "<에러 메시지>"}`

### GET /health

`{"status": "ok"}`

## 환경변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `MAX_CONCURRENCY` | 1 | 동시 Chromium 인스턴스 수 |

## 포트

| 포트 | 용도 |
|------|------|
| 8080 | HTTP API |

## 동작 특성

- Chromium은 요청마다 생성/종료된다. idle 시 브라우저 RAM 점유 없음, 대신 요청마다 기동 비용(~1초).
