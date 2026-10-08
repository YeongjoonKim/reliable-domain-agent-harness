# Validation / 검증 기록

## Public Core evidence entry points · 2026-10-08

메인 [Core Evidence Explorer](../demo/index.html)는 공개 Python Core를 실행해 생성한 5개 합성
시나리오의 실행·검증·거부·복구·provenance·replay를 탐색합니다.
[전체 실행 JSON](../demo/core-evidence.json)과 원본 소스·관련 테스트를 연결하며,
[기존 Lightweight Demo](../demo/legacy.html) 및 아래 운영·별도 Scientific 캡처와 구분합니다.
2026-10-08 변경본의 로컬 검증 결과입니다. commit별 원격 결과는
[GitHub Actions](https://github.com/YeongjoonKim/reliable-domain-agent-harness/actions/workflows/ci.yml)에서 확인합니다.

| 검증 | 실제 결과와 범위 |
|---|---|
| Python 3.10 로컬 회귀 | **76 passed / 0 failed**: 기존 57 + exporter 11 + subprocess CLI 5 + HTML 링크 3 |
| 합성 평가 재실행 | Baseline 8/24 · Harness 24/24, 설계된 verification/recovery ablation |
| Artifact | 실제 Runtime 4개 실행 + 동일 recovery bundle의 Replay 항목, 5개 시나리오; JSON/JS 일치·원본 무결성·신선도 검사 통과 |
| 실제 Chrome | 실제 viewport 1440×913 및 500×757에서 모든 시나리오·timeline·검증 signal·claim/provenance·원문 offset·키보드 탭·상대 링크 검사 통과 |
| 추가 화면 검토 | 기존 로컬 브라우저 도구로 1440×1100 및 휴대폰 390×844 확인·캡처; 모든 시나리오 전환, 복구 채택/거부 span, 가로 넘침·JS 오류 없음 |
| Legacy | 원래 HTML·JS·CSS·실행 snapshot 보존, 3개 시나리오와 모든 탭 전환 통과 |
| 저장소 / 아키텍처 | 로컬 링크·JSON·PNG manifest·제한된 secret/history 검사 및 9개 SVG/Mermaid 동기화 통과 |
| 기본 명령 | 새 결과는 `outputs/`에 저장; 추적 예제 JSON·주요 소스의 추가 변경 없음 |
| Docker / 운영 | 이번 변경에서 실행·접근하지 않음. 기존 Docker 기록과 승인된 운영 캡처는 보존 |

브라우저 검사 스크립트는 설치된 Chrome과 Python 표준 라이브러리만 사용하며, 별도 UI 검증입니다.
추가 휴대폰 캡처는 이미 설치된 로컬 도구를 사용했고 새 프로젝트 의존성은 추가하지 않았습니다.
브라우저 결과·캡처는 로컬 검토용 `outputs/`에 두며 공개 운영 기록으로 취급하지 않습니다.
독립 LLM·실제 도메인 정확도·외부 환경 전체 Replay·호스팅된 사이트 검증은 수행하지 않았습니다.
아래 57개·23개·229개 수치는 기존 날짜의 이력이며 새 합산 결과가 아닙니다.

## Static demo and Pages

GitHub README의 HTML 링크는 소스 보기입니다. 인터랙티브 화면은 저장소 루트에서
`python3 -m http.server 8000 --bind 127.0.0.1` 실행 후 [localhost:8000/demo/](http://localhost:8000/demo/)로 확인합니다.
정적 파일과 저장된 실행 산출물만 사용하며 외부 API·LLM·DB 연결은 없습니다.

저장소 메타데이터의 `has_pages`는 `false`이며 Pages 설정 조회 API는 404였습니다.
게시된 사이트의 작동을 확인하지 않았으며 이번 작업에서 사이트 활성화·저장소 공개 범위는 변경하지 않았습니다.
호스팅을 승인한 권한 있는 사용자는 GitHub **Settings → Pages**에서 기존 배포 방식을 확인하고,
branch 배포를 사용하는 경우 승인된 branch의 **/(root)**를 선택할 수 있습니다.
배포 완료 후 표시되는 사이트의 `/demo/`에서 상대 asset·JSON·legacy 링크와 시나리오 전환을
직접 확인해야 합니다. 배포 성공이나 사이트 접근성은 로컬 정적 검사를 대신하지 않습니다.

## Public Core validation · 2026-10-02

당시 전체 공개 57 tests passed, 별도 실제 Docker 격리/수치 분석과 MCP stdio 왕복 통과. [실행 범위](public-core.md). 아래 기록은 기존 데모 검증 이력입니다.

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
