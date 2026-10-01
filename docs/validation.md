# Validation / 검증 기록

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

검사 통과는 모델 정확도나 고용/IP에 관한 법적 확인이 아닙니다.
공개 승인은 받았으며 별도의 오픈소스 라이선스는 아직 선택하지 않았습니다.
