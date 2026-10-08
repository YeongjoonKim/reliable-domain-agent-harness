# Scope & Limitations

새 공개 코어는 명시적 계획, 정형 근거 검증, 제한된 복구, 주장별 출처, configuration/evidence replay,
선택형 Docker 수치 분석과 최소 MCP stdio를 구현합니다. [계약과 제한](public-core.md).

자연어 LLM 플래너·일반 텍스트 의미 검증·운영 connector·영속 개인 메모리·multi-agent·학습형 개선·RL은
공개 코어에 없습니다. 합성 평가는 독립 모델 성능 benchmark가 아닙니다. Docker는 악의적 다중 사용자
환경의 완전한 보안 경계가 아니며 MCP도 인증된 완성형 구현이 아닙니다.

초기 lightweight demo의 두 fixture·메모리·화면은 호환성 예제로 보존합니다. session 문자열은 인증이
아닙니다. 실제 서비스 경험과 별도 비공개 Scientific Harness는 [실제 구현 대응](actual-engineering.md)으로
구분하며 공개 코드에서 운영 기능을 추정하지 않습니다.

[Core Evidence Explorer](../demo/index.html)는 공개 Python Runtime에서 생성한 저장 산출물을
선택해 보는 정적 화면입니다. 브라우저에서 live LLM·도구·Docker를 실행하지 않으며,
화면 재생은 새 실행이나 독립 성능 평가가 아닙니다. [보존된 legacy UI](../demo/legacy.html)의
PROPOSED 표시와 Public Core의 구현 상태는 서로 다른 범위입니다. Replay는 저장된 설정·근거를
재검증하며 전체 외부 환경이나 확률적 모델 출력을 재생성하지 않습니다.
