# 다음 주 모델 구축 시작 프롬프트

`PROJECT_CONTEXT.md`, `DATA_DICTIONARY.md`, `TODO.md`, `SOURCE_MASTER.md`를 먼저 전부 읽고 연구 범위를 준수하라. 이 연구의 메인 비교는 차량 수와 UD택시 12대를 동일하게 고정한 S0(현행 월 100건 장애인 우선배차 후 일반영업)와 S1(통합 동적 운영)이며, UD 증차·대체대수·2030년 1,000대 효과를 메인 문제로 바꾸지 마라.

먼저 `01_raw_data/disabled_taxi/`의 2025 장애인콜택시 원자료를 절대 수정하지 않고 로드하여 품질검사, 결측·취소 처리 기준 문서화, 행정동 코드 정규화, 시간변수 생성, 행정동×시간 호출량을 만든 뒤 `02_processed_data/demand/`에 Parquet로 저장하라. 시간순 Train/Validation/Test를 사용해 Historical Average → LightGBM → ST-MGCN 순으로 구현·평가하고 MAE/RMSE를 비교하라. 이어서 행정동 공간인접·OD 이동시간·기능유사성 그래프를 명시적으로 구성하라.

그 다음 SimPy 기반 DES를 구현하라. 우선 실제 규칙과 실제 UD 자료로 S0을 calibration하고, 같은 호출·차량·이동시간·차량제원·시드에서 S1의 Rolling Horizon(초기 30분)을 비교하라. UD 행동은 장애인 대응·일반영업·충전·재배치·대기다. 서비스 KPI를 우선 평가하고, 탄소·운영비·일반영업 성과는 별도로 보고하라. `WAITING_DATA`와 `TEMPORARY_ASSUMPTION`은 명확히 표시하며, 임시값으로 정책결론을 내리지 마라.
