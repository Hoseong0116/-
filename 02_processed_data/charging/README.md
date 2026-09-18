# 충전소 가공 데이터

- 입력: `01_raw_data/charging/서울시 소유 전기차 충전소 정보.csv`
- 출력: `charger_clean.csv`
- 처리: 원자료 433기 중 `하이서울유스호스텔(지하주차장)`의 `AC3상`·`완속(7kW단독)` 1기만 제외
- 결과: 432기

## 변환 원칙

- 원자료의 충전기 1기당 출력 1행으로 저장한다. 따라서 `number_of_chargers`와 `simultaneous_capacity`는 각 행에서 1이다.
- `power_kw`는 원자료 `충전용량`의 kW 숫자만 추출했다.
- 위치 좌표, 충전요금, 택시 전용 이용 가능 여부는 원자료에 없어 빈값으로 둔다.
- `charger_id`는 충전소명과 원자료 충전기ID를 결합해 고유하게 만들었다.
- `charger_clean.csv`는 한글 Windows Excel에서 바로 열 수 있도록 UTF-8 BOM으로 저장했다.
