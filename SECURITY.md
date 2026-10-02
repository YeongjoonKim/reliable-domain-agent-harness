# Security — Agent Harness

MCP는 로컬 stdio만 제공한다. Docker는 승인된 로컬 image ID, network none, 읽기 전용 root와 자원 제한으로 실행하며 daemon 권한은 강한 권한이다. 공개 인터넷에 노출하지 않는다. replay bundle에는 원문이 포함될 수 있으므로 합성 자료만 공개한다.

## Reporting

GitHub private vulnerability reporting이 활성화된 경우 해당 채널을 사용한다.
비활성화된 경우 민감정보 없이 비공개 연락 채널을 요청한다. 공개 issue에 secret이나
개인 데이터를 첨부하지 않는다. 응답 기한이나 운영 서비스 보안 보증은 제공하지 않는다.

## Checks and limits

`python3 scripts/check_repository.py`는 구문·JSON·로컬 링크·PNG 구조/manifest와
도달 가능한 Git history의 제한된 secret 패턴을 검사한다. semantic/IP 검토, 이미지 내 개인정보,
외부 링크 안전성이나 secret 부재를 증명하는 전문 감사 도구는 아니다.
CI는 고정 action revision, contents read 권한을 사용하고 repository secret을 요구하지 않는다.
GitHub 보안 기능의 활성 상태는 별도로 확인해야 하며 이 문서는 설정 변경을 주장하지 않는다.
