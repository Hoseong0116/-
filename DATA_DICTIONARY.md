# DATA_DICTIONARY

상태: `CONFIRMED` / `TEMPORARY_ASSUMPTION` / `WAITING_DATA` / `OBSERVED_DATA`. 구분: RAW, DERIVED, MODEL_INPUT, MODEL_OUTPUT, SIMULATION_STATE, KPI.

|variable_name|korean_name|description|unit|source|raw_or_derived|status|used_in|notes|
|---|---|---|---|---|---|---|---|---|
|call_timestamp|호출시각|장애인콜택시 호출 발생 시각|datetime|2025 호출 원자료|RAW|OBSERVED_DATA|forecast, DES|시간대 기준 정규화 필요|
|origin_admd_cd|출발 행정동 코드|출발지 표준 행정동 코드|code|2025 호출 원자료/공간자료|RAW|OBSERVED_DATA|forecast, DES|코드 정규화 필요|
|destination_admd_cd|도착 행정동 코드|도착지 표준 행정동 코드|code|2025 호출 원자료/공간자료|RAW|OBSERVED_DATA|DES|결측·서울 외 통행 규칙 기록|
|demand_count_t1|다음 시점 호출건수|행정동×시간 t+1 호출수|calls|전처리 결과|DERIVED|OBSERVED_DATA|forecast|예측 target|
|travel_time_od|OD 이동시간|행정동 OD·시간대별 이동시간|minutes|교통/지도 자료|MODEL_INPUT|WAITING_DATA|DES|S0/S1 공통|
|vehicle_id|차량ID|차량 고유 식별자|text|fleet/log|SIMULATION_STATE|WAITING_DATA|DES|비식별 처리|
|vehicle_type|차량유형|disabled_taxi 또는 UD|category|fleet|SIMULATION_STATE|WAITING_DATA|DES||
|location|차량 위치|행정동 또는 좌표|code/coordinate|vehicle log|SIMULATION_STATE|WAITING_DATA|DES||
|status|운행상태|차량 상태 열거값|category|simulation|SIMULATION_STATE|DERIVED|DES|IDLE 등|
|soc|충전상태|배터리 잔량 비율|0–1|UD log|SIMULATION_STATE|WAITING_DATA|DES|임시값 결론 금지|
|battery_kwh|배터리용량|PV5 사용가능 배터리용량|kWh|공식 제원|MODEL_INPUT|CONFIRMED|DES|값은 출처 확인 후 config 입력|
|efficiency_km_per_kwh|전비|공인/실측 km당 kWh 효율|km/kWh|공식 제원/UD log|MODEL_INPUT|CONFIRMED|DES|실전비는 별도|
|normal_taxi_revenue|일반영업 기대수익|시간·지역별 일반택시 수익|KRW|운영/매출 자료|MODEL_INPUT|WAITING_DATA|DES||
|pickup_time|픽업시간|호출부터 차량 도착까지|minutes|배차 log/DES|KPI|OBSERVED_DATA|DES, evaluation|정의 고정 필요|
|unserved_rate|미배차율|유효 요청 중 미배차 비율|%|DES|KPI|DERIVED|evaluation|취소와 구분|
|co2e|온실가스 배출량|운행·충전 관련 배출|kgCO2e|거리·전력·계수|KPI|WAITING_DATA|evaluation|LCA 제외|
|operating_cost|운영비|차량·에너지·충전 관련 비용|KRW|공식/운영 자료|KPI|WAITING_DATA|evaluation|회계 주체 분리|
