# Changelog — Agent Harness

## 2026-10-08 — Core Evidence Explorer

- 공개 Python Core의 실제 실행·검증·복구·Replay 산출물을 탐색하는 정적 데모를 추가하고 기존 경량 데모를 보존했습니다.
- README 첫 화면에서 데모·로컬 실행·테스트·CI로 이어지는 검증 경로와 구현별 경계를 정리했습니다.
- 실행 산출물 생성·무결성·신선도 검사와 브라우저 회귀를 연결하고 기본 CLI 출력을 `outputs/`로 분리했습니다.
- 운영 코드·데이터·승인된 캡처·게시 정책·라이선스는 변경하지 않았습니다.

## 2026-10-03 — Execution evidence and current architecture

- 관리자 실행 제어와 현재 저장된 실행·모델·배치 화면을 보강했습니다.
- 아키텍처 SVG·Mermaid를 현재 구현에 맞추고 동일 명세 기반 렌더러를 추가했습니다.
- 운영 경험·별도 Scientific 실행·독립 공개 예제의 책임과 캡처 범위를 연결했습니다.

## 2026-10-02 — Technical portfolio polish

- Key Engineering Facts를 아키텍처 직후 배치하고 운영 구현과 공개 코어의 역할을 요약했다.
- 실행·검증 절을 통합하고 세부 집계·평가·캡처 조건을 상세 문서에 정리했다.
- 화면 설명과 공통 제목을 한국어로 통일했다. 코드·화면·평가 artifact는 유지했다.

## 2026-10-02 — Portfolio hardening

- 독립 실행 코어, 정보 요구별 근거 회귀, 재현, 실제 Docker 격리 검사와 MCP 왕복을 추가했다. 기존 데모는 보존했다.
- 저장소별 publication, security, rights 경계를 개별화했다.
- 기존 공개 이력과 실제 화면을 유지하며 과거 개발일이나 평가 결과를 소급 생성하지 않았다.

## Existing public package

독립 예제, 회귀 검사, 비식별 실제 화면, 읽기 전용 권한의 GitHub Actions가 기존에 공개되었다.
현재 변경의 hosted CI 상태는 README의 실제 workflow 링크와 해당 PR을 기준으로 한다.
별도 release tag는 생성하지 않았다.
