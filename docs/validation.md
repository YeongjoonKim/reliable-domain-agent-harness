# Validation / 검증 기록

2026-10-02 추가 검증: 전체 공개 57 tests passed, 별도 실제 Docker 격리/수치 분석과 MCP stdio 왕복 통과. [실행 범위](public-core.md). 아래 기록은 기존 데모 검증 이력입니다.

## README에서 분리한 검증 범위

- 별도 private Scientific Harness 선택 회귀는 229 passed이며, 이 중 20개는 합성 제어 시나리오입니다. 공개 CI와 합산하지 않습니다.
- Verification 캡처의 요청은 검증을 통과했고 repair는 실행되지 않았습니다. 의도 신뢰도는 내부 추정값입니다.
- Trace는 한 요청의 저장된 단계 시간입니다. 전체 평균 latency나 병렬 waterfall로 해석하지 않습니다.
- Architecture·Trace·회귀 화면은 2026-10-02, 일부 Harness Engineering View는 2026-09-30 캡처입니다.
- 계정·개인 질문/답변 원문은 공개 범위에서 제외했습니다. 메모리 화면은 개인 원문이 아닌 구성 설명입니다.

## Actual Engineering Review · 2026-10-02

공개 예제 검증과 별도로 실제 구현·설정·읽기 전용 API·관리자 화면을 재검토했습니다.
[실제 근거](actual-engineering.md)와 [화면 갤러리](screenshots.md)에 관측 범위를 기록합니다.
운영 데이터·학습·모델 적용·발송·정책 승인은 변경하지 않았습니다.

## Public Sample Validation · 2026-10-01

2026-10-01. 공개 재구성 예제만 검증했으며 운영 API·DB·GPU를 사용하지 않았습니다.

- 로컬 Python 3.10.12: **23개 테스트 통과**.
- 기본 CLI와 execution exporter 실행 성공.
- 저장된 실행 artifact와 재계산 결과를 회귀 테스트로 비교.
- 공개 실행 snapshot을 Chrome으로 캡처하고, 별도 승인된 운영 UI 크롭/마스킹 사본을 시각 검토.
- 무편집 원본은 비공개로 보존. 공개 사본은 픽셀 평탄화·metadata 제외·SHA-256 manifest 검사.
- 상대 문서 링크, Python 구문, JSON, 제한된 secret pattern과 Git history 검사.
- PNG는 검토한 hash와 구조/metadata를 검사. 이미지 속 개인정보 부재는 자동 보증하지 않음.
- 첫 공개 main의 GitHub CI(Python 3.10/3.12)는 성공 상태를 확인함.
- 보완본의 정확한 CI 상태는 [Actions](https://github.com/YeongjoonKim/reliable-domain-agent-harness/actions/workflows/ci.yml)에서 commit별로 확인.

UI는 3개 시나리오 × 6개 view를 제공하며 설명 카드와 실제 실행 snapshot을 구분합니다.

코드 계약 검증, 모델 품질 평가, 공개 권리 검토는 각각 별도로 수행합니다.
공개 승인은 받았으며 별도의 오픈소스 라이선스는 아직 선택하지 않았습니다.
