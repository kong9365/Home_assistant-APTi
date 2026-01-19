# APT.i GitHub Actions + Home Assistant Webhook 설정 가이드

## 개요

GitHub Actions에서 매일 APT.i 사이트를 파싱하고, 결과를 Home Assistant Webhook으로 전송하는 방식입니다.

```
GitHub Actions (매일 한국시간 오전 9시)
    ↓ Playwright로 파싱
    ↓
Home Assistant Webhook (데이터 수신)
    ↓
센서 업데이트
```

## 1단계: Home Assistant 설정

### 1.1 Custom Component 설치

1. `custom_components/apti/` 폴더를 Home Assistant의 `config/custom_components/`에 복사
2. Home Assistant 재시작

### 1.2 통합구성요소 추가

1. 설정 → 통합구성요소 → 추가
2. "APT.i" 검색
3. 아파트 이름 입력 후 제출

### 1.3 Webhook URL 확인

설정 완료 후 통합구성요소 페이지에서 Webhook ID를 확인합니다.

Webhook URL 형식:
```
https://your-ha-domain.duckdns.org/api/webhook/{webhook_id}
```

또는 로컬:
```
http://homeassistant.local:8123/api/webhook/{webhook_id}
```

**중요**: GitHub Actions에서 접근 가능한 URL이어야 합니다 (DuckDNS, Nabu Casa 등).

---

## 2단계: GitHub 저장소 설정

### 2.1 새 저장소 생성

1. GitHub에서 새 저장소 생성 (예: `apti-parser`)
2. Private 저장소 권장 (자격증명 보호)

### 2.2 파일 업로드

다음 파일들을 저장소에 업로드:

```
apti-parser/
├── .github/
│   └── workflows/
│       └── parse.yml      # workflow.yml 내용 복사
├── apti_parser.py         # 파싱 스크립트
└── requirements.txt       # 의존성
```

### 2.3 GitHub Secrets 설정

저장소 Settings → Secrets and variables → Actions → New repository secret

| Secret 이름 | 값 |
|-------------|-----|
| `APTI_USER_ID` | APT.i 아이디 또는 휴대폰 번호 (예: 01012345678) |
| `APTI_PASSWORD` | APT.i 비밀번호 |
| `HA_WEBHOOK_URL` | Home Assistant Webhook URL 전체 |

---

## 3단계: workflow.yml 설정

`.github/workflows/parse.yml`:

```yaml
name: APT.i 관리비 파싱

on:
  # 매일 한국시간 오전 9시 (UTC 0시)
  schedule:
    - cron: '0 0 * * *'

  # 수동 실행
  workflow_dispatch:

jobs:
  parse-apti:
    runs-on: ubuntu-latest

    steps:
      - name: 코드 체크아웃
        uses: actions/checkout@v4

      - name: Python 설정
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: 의존성 설치
        run: |
          pip install -r requirements.txt
          playwright install chromium
          playwright install-deps chromium

      - name: APT.i 파싱 실행
        env:
          APTI_USER_ID: ${{ secrets.APTI_USER_ID }}
          APTI_PASSWORD: ${{ secrets.APTI_PASSWORD }}
          HA_WEBHOOK_URL: ${{ secrets.HA_WEBHOOK_URL }}
        run: python apti_parser.py
```

---

## 4단계: 테스트

### 수동 실행 테스트

1. GitHub 저장소 → Actions 탭
2. "APT.i 관리비 파싱" 워크플로우 선택
3. "Run workflow" 클릭
4. 실행 로그 확인

### Home Assistant 확인

1. 개발자 도구 → 상태 탭
2. `sensor.apti_` 로 시작하는 센서 검색
3. 데이터가 업데이트되었는지 확인

---

## 문제 해결

### Webhook 전송 실패

1. Home Assistant URL이 외부에서 접근 가능한지 확인
2. HTTPS 설정 확인 (DuckDNS + Let's Encrypt 권장)
3. Webhook ID가 올바른지 확인

### 파싱 실패

1. APT.i 자격증명 확인
2. 사이트 구조 변경 여부 확인
3. GitHub Actions 로그에서 오류 메시지 확인

### 스케줄 변경

cron 표현식 수정:
```yaml
schedule:
  - cron: '0 12 * * *'  # 매일 한국시간 오후 9시 (UTC 12시)
```

---

## Webhook 데이터 형식

GitHub Actions에서 전송하는 JSON 형식:

```json
{
  "timestamp": "2026-01-18T09:00:00.000000",
  "dong_ho": "13061001",
  "maint_items": [
    {"item": "일반관리비", "current": "49950", "previous": "49780", "change": "170"},
    ...
  ],
  "maint_payment": {
    "amount": "347220",
    "charged": "347220",
    "month": "1",
    "deadline": "2026-01-25",
    "status": "납기내"
  },
  "energy_category": [
    {"type": "전기", "usage": "180", "cost": "67470", "comparison": "-31%"},
    ...
  ],
  "energy_type": [
    {"type": "전기", "total": "67470", "세대전기료": "35010", ...},
    ...
  ],
  "payment_history": [
    {"date": "2026.01.15", "amount": "340000", "status": "완납"},
    ...
  ]
}
```

---

## 보안 참고사항

1. **GitHub 저장소를 Private으로 설정** - 자격증명이 포함된 Actions 로그 보호
2. **Secrets 사용** - 자격증명을 코드에 직접 입력하지 않음
3. **Webhook URL 보호** - URL을 공개하지 않음 (URL만 알면 데이터 전송 가능)
