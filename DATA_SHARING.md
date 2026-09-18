# 팀 공유용 Git 데이터 구성

이 저장소에는 현재 분석에 필요한 공개 기준자료, 공개자료에서 만든 전처리 CSV, 출처·결측 설명, 재생성 스크립트와 결과 엑셀을 올린다. Git에 올리는 CSV가 모두 관측자료인 것은 아니다. 빈 입력 틀과 옛 대리계수는 각 파일의 상태 열과 `02_processed_data/model_inputs/README.md`를 확인한다.

| 구역 | 공유 내용 | 해석 |
|---|---|---|
| `01_raw_data/charging/` | 서울시 소유 충전기 공개 CSV 원본 | 433행, 서울 밖 4행 포함. 원본은 수정하지 않음 |
| `01_raw_data/profitability/2026-09-17/` | 충전사업자 회원요금 표시표 전사본, 공식 페이지의 URL·검증 기록 | 사이트 표시값 전사이며 실제 결제·청구 원장은 아님. 원문 HTML·텍스트는 Git 제외 |
| `02_processed_data/` | 차량·충전·비용·탄소 기준표 및 모델 입력용 CSV | 모델 준비 상태와 결측을 유지. `model_inputs`의 427기는 조사 후보 |
| `00_reference/policy/`, `00_reference/disclosure/` | 시나리오 규칙과 자료요청 항목 | 2026 fleet·S0 실제 전환규칙은 추가 확인 필요 |
| `03_scripts/` | 공개 출처 수집 및 모델 입력 재생성 코드 | 원본을 덮어쓰지 않고 새 가공 파일 생성 |
| `outputs/profitability_20260918/` | 수익성 입력 엑셀 1개 | 실제 매출·보조금 결측으로 수익률 결과는 아님 |

## 공유 제외

실제 장애인 호출·배차·승하차 이력, 차량별 운행·SOC·정산 로그, 사용자/운전자 ID, 개인정보가 포함된 팀원 파일은 기본적으로 Git에 올리지 않는다. `.gitignore`에서 이 유형의 raw 및 새 processed CSV를 기본 제외하고, 검토된 공개·집계 자료만 예외로 허용한다. 팀원 자료를 수령하면 권한·비식별화·공유 범위를 확인한 뒤 공유 방법을 결정한다.

논문 PDF, HWP 신청서, 웹페이지 HTML 복사본, 미리보기 이미지, 실행 캐시·가상환경은 이번 데이터 업로드 대상이 아니다. 공개자료의 원문 링크는 CSV의 `source_url`, `SOURCE_MASTER.md`, `02_processed_data/cost/profitability_sources.csv`에 있다. 재생성 전 원문을 내려받을 때에는 `03_scripts/profitability/collect_public_sources.py`를 사용한다.

빈 폴더 표시는 팀원이 자료를 넣을 `01_raw_data/disabled_taxi/`, `general_taxi/`, `spatial/`만 유지한다. 중복 `.gitkeep`, 실행 시 생성할 `06_outputs/`의 빈 하위 폴더, 이전 증차 시나리오 표와 오래된 방법론 초안은 Git 공유 목록에서 제외했다. 로컬 파일은 보존했다. 현재 비교의 기준은 `PROJECT_CONTEXT.md`와 `02_processed_data/model_inputs/scenario_core.csv`다.

## 팀 파일을 합칠 때

`02_processed_data/model_inputs/README.md`의 필수 열·키·단위에 맞춰 원본은 `01_raw_data`에 보존하고 새 가공 파일만 별도로 만든다. 2025 공식 fleet 854대와 출처 미확인 2026년 세부 집계는 서로 덮어쓰지 않는다. 2023년 전력·차종 대리계수는 승인 전 최종 계산에 투입하지 않는다.
