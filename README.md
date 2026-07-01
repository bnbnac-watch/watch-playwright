# watch-playwright

Playwright 브라우저 서버. 크롤러들이 WebSocket으로 연결해 Chromium 인스턴스를 공유한다.

## 연결

```python
browser = await playwright.chromium.connect("ws://watch-playwright:3000")
```

## 포트

| 포트 | 용도 |
|------|------|
| 3000 | Playwright WebSocket 서버 |
