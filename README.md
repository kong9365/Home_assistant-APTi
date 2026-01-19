# Home Assistant APT.i 통합구성요소

APT.i (아파트아이) 관리비 정보를 Home Assistant에 연동하는 커스텀 컴포넌트입니다.

## 주요 기능

- **관리비 정보**: 관리비 총액, 납부 마감일, 항목별 상세 정보
- **에너지 정보**: 전기, 가스, 수도 등 에너지 사용량 및 요금
- **납부 내역**: 최근 납부 내역 조회
- **Webhook 기반**: GitHub Actions를 통한 자동 데이터 수집

## 작동 방식

```
GitHub Actions (매일 자동 실행)
    ↓ Playwright로 APT.i 사이트 파싱
    ↓
Home Assistant Webhook (데이터 수신)
    ↓
센서 자동 업데이트
```

## 설치 방법

### 1. Custom Component 설치

1. Home Assistant의 `config/custom_components/` 폴더에 `apti` 폴더를 복사합니다.
2. Home Assistant를 재시작합니다.

### 2. 통합구성요소 추가

1. Home Assistant 설정 → 통합구성요소 → 추가
2. "APT.i" 검색
3. 아파트 이름 입력 후 제출
4. 설정 완료 후 Webhook ID가 생성됩니다.

### 3. GitHub Actions 설정

자세한 설정 방법은 [SETUP_GUIDE.md](SETUP_GUIDE.md)를 참고하세요.

**요약:**
1. GitHub에 새 저장소 생성 (Private 권장)
2. 이 저장소의 파일들을 업로드:
   - `.github/workflows/parse.yml`
   - `apti_parser.py`
   - `requirements.txt`
3. GitHub Secrets 설정:
   - `APTI_USER_ID`: APT.i 로그인 ID
   - `APTI_PASSWORD`: APT.i 비밀번호
   - `HA_WEBHOOK_URL`: `https://your-domain/api/webhook/{webhook_id}`

## 센서

설정 완료 후 다음 센서들이 자동으로 생성됩니다:

### 관리비 센서
- `sensor.apti_관리비`: 관리비 총액
- `sensor.apti_납부마감일`: 납부 마감일
- `sensor.apti_{항목명}`: 관리비 항목별 센서 (일반관리비, 청소비 등)

### 에너지 센서
- `sensor.apti_{에너지종류}_요금`: 전기, 가스, 수도 등 요금
- `sensor.apti_{에너지종류}_상세`: 에너지 종류별 상세 정보

### 납부 내역 센서
- `sensor.apti_최근_납부`: 최근 납부 상태 및 내역

## 설정

통합구성요소 설정에서 Webhook URL을 확인할 수 있습니다. 이 URL을 GitHub Actions의 `HA_WEBHOOK_URL` Secret에 설정하세요.

**중요**: GitHub Actions에서 접근 가능한 URL이어야 합니다 (DuckDNS, Nabu Casa 등).

## 문제 해결

### 센서가 업데이트되지 않음
1. GitHub Actions가 정상 실행되었는지 확인
2. Webhook URL이 올바른지 확인
3. Home Assistant 로그 확인

### GitHub Actions 실패
1. APT.i 자격증명 확인
2. Webhook URL이 외부에서 접근 가능한지 확인
3. GitHub Actions 로그 확인

자세한 문제 해결 방법은 [SETUP_GUIDE.md](SETUP_GUIDE.md)를 참고하세요.

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 기여

버그 리포트나 기능 제안은 [Issues](https://github.com/kong9365/Home_assistant-APTi/issues)에 등록해주세요.

## 참고

- [APT.i 공식 사이트](https://apti.co.kr)
- [Home Assistant 커스텀 컴포넌트 개발 가이드](https://developers.home-assistant.io/docs/creating_integration_manifest)
