# SOURCE_MASTER

등급: A 최신 공식 직접자료, B 공식자료(시점/대상 차이), C 학술연구, D 연구가정. 원본은 변경하지 않고 경로를 기록한다.

|자료명|기관|기준연도|URL 또는 파일경로|공식자료|사용 변수|등급|비고|
|---|---|---:|---|---|---|---|---|
|딥러닝을 활용한 서울시 행정동별 장애인콜택시 수요예측 방법 연구|대한교통학회|2022|`선행연구 논문/딥러닝을 활용한 서울시 행정동별 장애인콜택시 수요예측 방법 연구.pdf.pdf`|아니오|ST-MGCN, 행정동×시간, MAE/RMSE|C|방법론 참고; 자체 성능 재검증 필요|
|서울시 장애인 콜택시 이용특성 및 대기시간 영향 요인 분석|국토계획|2023|`선행연구 논문/서울시 장애인 콜택시 이용특성 및 대기시간 영향 요인 분석 장애인 콜택시 빅데이터와 Community Detection을 활용하여.pdf.pdf`|아니오|대기·지역 특성|C|과거 집계 결과를 현재 입력값으로 전용하지 않음|
|서울시 장애인 콜택시 고객 대기시간 감소를 위한 자동배차 알고리즘 및 최적 차량 공급 제안|학술대회|2015|`선행연구 논문/서울시 장애인 콜택시 고객 대기시간 감소를 위한 자동배차 알고리즘 및 최적 차량 공급 제안.pdf.pdf`|아니오|배차 제약, KPI|C|총 차량 증차 연구로 확장하지 않음|
|UD dynamic operation research package|내부 정리|2026|`UD_dynamic_operation_research_package_20260915/ud_dynamic_research_20260915/`|부분|PV5, fleet, 충전, 비용, 탄소, 정책|B/C/D 혼재|각 CSV의 상태·출처를 재확인|
|UD 택시 선행연구 검증|내부 정리|2026|`UD_taxi_literature_verified.md`|아니오|문헌 활용·제약|C|인용 전 원문·공식출처 확인|
|데이터 역할 분담(B)|내부 연구계획|2026|`00_reference/source_notes/project_planning/데이터 역할 분담(B).md`|아니오|차량·UD·EV·비용·탄소 수집범위|D|보유현황은 disclosure/DATA_COLLECTION_STATUS.md 참조|
|데이터 수집 보유현황 점검|내부 점검|2026|`00_reference/disclosure/DATA_COLLECTION_STATUS.md`|아니오|수집 우선순위·결측관리|D|파일 존재와 실제 값 확보를 구분|
|2025 서울시 장애인콜택시 호출/배차 원자료|운영기관/정보공개|2025|`01_raw_data/disabled_taxi/`|예정|호출, OD, 대기, 배차|A 예정|직접 추가 필요|
|UD 실제 운영 로그|운영기관/정보공개|2026|`01_raw_data/ud_taxi/`|예정|운행, SOC, 충전, 매출, 근무|A 예정|WAITING_DATA|
|장애인콜택시 현황|원 출처 미확인 (사용자 전달)|2026-01|`00_reference/source_notes/disabled_taxi/2026-01_disabled_taxi_fleet_status.md`|미확인|운영구분별·차종별 차량 대수|B 보류|총 824대; 원 출처 확인 후 등급 재평가|
|UD택시 월 100건 후 일반택시 전환 보도|한겨레|2026|https://www.hani.co.kr/arti/area/capital/1265653.html|언론 보도|월 100건 우선배차 후 일반 중형택시 전환|B|사용자 제공 링크; 원문 자동 접근 제한, 운영지침 원본으로 재확인 필요|
|기아 PV5 WAV 국내 공식 카탈로그|기아|2026|https://www.kia.com/content/dam/kwp/kr/ko/vehicles/pdf/catalog/catalog_pv5-wav.pdf|예|배터리·전비·주행거리·급속충전|A|국내 WAV 롱레인지 제원; 완속 충전 세부사양 미기재|
|서울시 소유 전기차 충전소 정보|원 출처 미확인 (보유 원자료)|미상|`01_raw_data/charging/서울시 소유 전기차 충전소 정보.csv`|미확인|충전기 유형·용량·운영시간·주소|B 보류|433기 중 AC3상 단독 1기를 제외해 `02_processed_data/charging/charger_clean.csv`에 432기 저장|
