# PROJECT_CONTEXT — 숲과나눔 공모전

## 단일 기준

본 문서는 로컬 AI와 연구진이 먼저 읽는 Single Source of Truth이다. 연구방향을 바꾸는 내용은 이 문서를 먼저 갱신한다.

## 연구 배경과 질문

서울시 장애인콜택시와 전기 UD택시를 하나의 통합 이동지원 공급체계로 본다. 최종 질문은 **동일한 차량 자원에서, 현행 UD택시의 차량당 월 100건 장애인 우선배차 후 일반영업 방식과 통합 동적 운영을 비교할 때 장애인 서비스 수준·탄소배출·운영비·일반영업 성과가 어떻게 달라지는가**이다.

2030년 UD택시 1,000대 목표는 12대 시범 단계에서 운영체계를 검증해야 한다는 정책적 배경일 뿐, 본 연구의 직접적인 확대효과 추정 대상이 아니다.

## 범위와 제외

- 대상: 2025년 서울시 장애인콜택시 약 150만 건, 기존 장애인콜택시와 UD택시 12대.
- 제외: UD 최적 증차대수 결정, 기존 장애인콜택시의 UD택시 대체대수 결정, 2030년 1,000대 직접 시뮬레이션, 임의 UD 결과 생성.

## 비교 시나리오

|항목|S0: 현행 운영|S1: 통합 동적 운영|
|---|---|---|
|차량|기존 장애인콜택시 + UD 12대|동일|
|UD 규칙|월 100건 장애인 우선배차 후 일반영업; 실제 세부규칙으로 calibration|장애인 호출, 일반영업, 충전, 재배치, 대기를 동적으로 결정|
|공통 조건|동일 장애인 호출, 차량 수, 이동시간, 차량제원|동일|

S0와 S1에서 변경되는 것은 운영정책뿐이다. S0의 실제 배차·운영규칙은 자료 확보 후 최대한 재현한다.

## 수요예측 계획

행정동 × 시간 단위에서 t+1 행정동별 장애인콜택시 호출건수를 예측한다. 선행연구 「딥러닝을 활용한 서울시 행정동별 장애인콜택시 수요예측 방법 연구」의 ST-MGCN 용어와 방법을 참고한다. 후보 그래프는 공간 인접성, 도로 이동거리/시간, 의료시설·장애인 특성·차고지·공급 특성의 기능 유사성이다. Historical Average, LightGBM, ST-MGCN을 MAE/RMSE로 비교하며 random split 없이 시간순 Train/Validation/Test를 쓴다.

## 시뮬레이션 계획

Python + SimPy 기반 DES를 우선 검토한다. 차량 agent의 주요 상태는 `vehicle_id`, `vehicle_type`, `location`, `status`, `available_time`이며 UD에는 `SOC`, `battery_capacity`, `remaining_range`, `charging_status`를 추가한다. 상태는 IDLE, PICKUP, DISABLED_TRIP, NORMAL_TAXI, REPOSITIONING, CHARGING, BREAK, OFF_DUTY다.

주요 사건은 호출생성, 배차, 도착, 탑승, 운행 시작/완료, 재배치 시작/완료, 충전 시작/완료, 일반택시 운행 시작/완료다. Rolling Horizon은 우선 30분 간격으로 미래수요·차량상태를 재평가해 배차·충전·일반영업·재배치를 재결정한다. 배차비용 후보는 pickup time/distance, SOC risk, service penalty, opportunity cost의 가중합이며 Hungarian Algorithm 또는 OR-Tools를 후속 검토한다. SUMO와 강화학습은 현 단계의 주모델이 아니다.

## KPI와 검증 원칙

장애인 평균·P95 대기시간, 미배차율, 완료건수, 차량 가용률, 장애인/일반영업 성과, 운영비, 충전비, CO₂e를 분리 보고한다. 서비스 기준을 먼저 충족하는 대안끼리 비용·탄소·일반영업을 비교한다. 동일 입력·차량·이동조건과 재현 가능한 random seed를 유지하며, 원자료를 절대 덮어쓰지 않는다.

## UD 데이터 상태 및 calibration

상태값은 `CONFIRMED`, `TEMPORARY_ASSUMPTION`, `WAITING_DATA`, `OBSERVED_DATA`로 관리한다. 공식 제원(배터리, 공인전비/주행거리, 충전성능, 가격)은 확인 후 CONFIRMED로 기록한다. 실제 일일거리, 장애인/일반 운행·거리·매출, 충전·SOC, 근무시간, 월 100건 달성일은 현재 WAITING_DATA다. 임시값은 실행시험에만 사용하며 정책결론을 내리지 않는다. 실제 UD 자료가 들어오면 S0을 calibration하고 재현성 검증 후 S0 vs S1 최종실험을 한다.
