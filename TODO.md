# TODO

## 현재 — 데이터 수집/정리

- [ ] 기존 장애인콜택시 fleet 및 2025 호출·배차 원자료 확보
- [ ] PV5 WAV 제원·UD 현행 월 100건 운영규칙의 공식근거 확인
- [ ] 충전소, 연료/전력가격, 연비/전비, 탄소계수, 운영비 수집
- [ ] 일반택시 수요·매출 자료와 행정동/OD·시간대 이동시간 자료 확보
- [ ] 정보공개 대기자료 등록 및 상태 업데이트

## 다음 주 — 모델 개발

### 수요예측

- [ ] 150만 건 로드, 품질검사, 결측/취소 처리, 행정동 코드 정규화
- [ ] 시간변수 및 행정동×시간 수요 생성
- [ ] Historical Average, LightGBM, 그래프 생성, ST-MGCN
- [ ] 시간순 Train/Validation/Test 및 MAE/RMSE 비교

### 시뮬레이션

- [ ] SimPy 환경, Request/Vehicle class, event 구조
- [ ] 기존 장애인콜택시 운영과 S0 재현
- [ ] 배차 cost/matching, 재배치, SOC, 충전, 일반영업, Rolling Horizon, S1
- [ ] KPI 출력 및 입력·시드 동일성 검증

## UD 실데이터 확보 후

- [ ] 데이터 구조 확인·cleaning 및 장애인/일반 운행, 거리, 충전, SOC, 근무, 100건 달성 패턴 분석
- [ ] S0 calibration 및 재현성 검증
- [ ] S0 vs S1 최종실험
