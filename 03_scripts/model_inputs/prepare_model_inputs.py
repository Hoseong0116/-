"""Build conservative, typed simulation inputs without modifying the source files."""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / '02_processed_data' / 'model_inputs'
OUT.mkdir(parents=True, exist_ok=True)


def read_csv(relative: str, encoding: str = 'utf-8-sig', strip_values: bool = True) -> list[dict[str, str]]:
    with (ROOT / relative).open(encoding=encoding, newline='') as stream:
        rows = list(csv.DictReader(stream))
    return [{key.lstrip('\ufeff').strip(): value.strip() if strip_values else value for key, value in row.items()} for row in rows]


def save_csv(name: str, rows: list[dict], fields: list[str] | None = None) -> None:
    if not rows and not fields:
        raise ValueError('Fields required for an empty CSV')
    with (OUT / name).open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields or list(rows[0]), extrasaction='raise')
        writer.writeheader()
        writer.writerows(rows)


def numeric(value: str, *, whole: bool = False):
    if value == '':
        return None
    return int(value) if whole else float(value)


def mins(hhmm: str) -> int:
    hour, minute = map(int, hhmm.split(':'))
    assert 0 <= hour <= 24 and 0 <= minute < 60 and (hour != 24 or minute == 0)
    return hour * 60 + minute


def schedule(value: str) -> tuple[int | None, int | None, int | None, int | None]:
    if value == '24시간 이용가능':
        return 0, 1440, 0, 1440
    pairs = re.findall(r'(\d{2}:\d{2})\s*~\s*(\d{2}:\d{2})', value)
    if len(pairs) == 2 and ('주중' in value or '평일' in value) and '주말' in value:
        return mins(pairs[0][0]), mins(pairs[0][1]), mins(pairs[1][0]), mins(pairs[1][1])
    if len(pairs) == 1:
        start, end = map(mins, pairs[0])
        if '평일' in value or '주중' in value:
            return start, end, None, None
        return start, end, start, end
    raise ValueError(f'Unexpected schedule: {value!r}')


raw_chargers = read_csv('01_raw_data/charging/서울시 소유 전기차 충전소 정보.csv', 'cp949', strip_values=False)
clean_chargers = read_csv('02_processed_data/charging/charger_clean.csv')
assert len(raw_chargers) == 433 and len(clean_chargers) == 432
assert len({(row['충전소'], row['충전기ID']) for row in raw_chargers}) == 433
clean_ids = {row['charger_id'] for row in clean_chargers}
assert len(clean_ids) == 432
charger_rows = []
for source_line, row in enumerate(raw_chargers, start=2):
    charger_id = f"seoul_owned_{row['충전소']}_{row['충전기ID']}"
    connector = row['충전기타입']
    width = re.search(r'(\d+)kW', row['충전용량'])
    if not width:
        raise ValueError(f"Missing nameplate power at source row {source_line}")
    power = int(width.group(1))
    open_weekday, close_weekday, open_weekend, close_weekend = schedule(row['이용가능시간'])
    district = row['시군구'].strip()
    address = row['주소'].strip()
    seoul = district.endswith('구') and (address.startswith('서울') or row['지역'].strip() == '서울특별시')
    incompatible = connector == 'AC3상'
    type_power_conflict = (connector == 'AC완속' and row['충전용량'].startswith('급속')) or (connector != 'AC완속' and row['충전용량'].startswith('완속') and not incompatible)
    dc_combo = 'DC콤보' in connector
    ac_slow = connector == 'AC완속'
    candidate = seoul and not incompatible and not type_power_conflict
    if charger_id not in clean_ids and not incompatible:
        raise AssertionError(f'Unexpected raw to clean key mismatch: {charger_id}')
    if not seoul:
        reason = '서울 밖 충전소'
    elif incompatible:
        reason = 'AC3상 단독'
    elif type_power_conflict:
        reason = '원자료 충전기타입·출력분류 충돌'
    elif ac_slow:
        reason = 'AC완속 물리 커넥터 규격·현장 진입 확인 필요'
    else:
        reason = 'DC콤보 후보. 현장 진입·가용성·요금·좌표 확인 필요'
    charger_rows.append(dict(
        charger_id=charger_id, source_row=source_line, station_name=row['충전소'].strip(),
        owner=row['운영기관'], city='서울특별시' if seoul else '경기도', district=district,
        address=address, facility_major=row['시설구분(대)'], facility_minor=row['시설구분(소)'],
        connector_label=connector, dc_combo_present=dc_combo, ac_slow_label=ac_slow,
        nameplate_power_kw=power, power_share_label='동시' if '동시' in row['충전용량'] else '단독',
        weekday_open_min=open_weekday, weekday_close_min=close_weekday,
        weekend_open_min=open_weekend, weekend_close_min=close_weekend,
        opening_hours_source=row['이용가능시간'], access_note=row['이용자 제한'],
        access_restriction_recorded=bool(row['이용자 제한']),
        seoul_boundary=seoul, connector_or_power_conflict=type_power_conflict,
        pv5_connector_candidate=not incompatible and (dc_combo or ac_slow),
        model_candidate_after_data_checks=candidate,
        lat=None, lon=None, charging_operator=None, billed_krw_per_kwh=None,
        vehicle_entry_verified=None, current_operational_status=None,
        review_reason=reason,
        source_file='01_raw_data/charging/서울시 소유 전기차 충전소 정보.csv',
    ))

assert sum(r['seoul_boundary'] for r in charger_rows) == 429
assert sum(r['model_candidate_after_data_checks'] for r in charger_rows) == 427
assert sum(r['connector_or_power_conflict'] for r in charger_rows) == 1
assert sum(r['access_restriction_recorded'] for r in charger_rows) == 1
save_csv('charger_inventory_prepared.csv', charger_rows)

pv5 = read_csv('02_processed_data/vehicle/pv5_spec.csv')
assert len(pv5) == 1
v = pv5[0]
save_csv('pv5_vehicle_inputs.csv', [dict(
    vehicle_model=v['model'], variant=v['trim'], model_year=int(v['model_year']),
    nominal_battery_kwh=numeric(v['battery_kwh']), usable_battery_kwh=numeric(v['usable_battery_kwh']),
    certified_efficiency_km_per_kwh=numeric(v['efficiency_km_per_kwh']),
    certified_range_km=numeric(v['range_km']),
    test_charge_10_80_min=numeric(v['charge_10_80_min'], whole=True),
    max_dc_input_kw=numeric(v['fast_charge_kw']), max_ac_input_kw=numeric(v['slow_charge_kw']),
    source_status='CONFIRMED_SPEC_WITH_MISSING_OPERATIONAL_PARAMETERS',
    note='공인 제원. 실전비·가용배터리·실제 충전곡선은 미확인. 350kW/11kW 시험충전기 출력은 차량 최대 입력출력이 아님.',
    source_url=v['source_url'],
)])

fleet = read_csv('02_processed_data/vehicle/fleet_master.csv')
fleet_baseline = [r for r in fleet if r['model'] == '전체 차종 합계' and r['base_year'] == '2025']
assert len(fleet_baseline) == 1 and fleet_baseline[0]['fleet_count'] == '854'
scenario_rows=[]
for scenario in ('S0', 'S1'):
    scenario_rows.append(dict(
        scenario=scenario, existing_fleet_count_assumed=854, existing_fleet_reference_year=2025,
        existing_fleet_status='TEMPORARY_ASSUMPTION_FOR_2026', ud_fleet_count=12,
        ud_monthly_priority_completed_trips_per_vehicle=100 if scenario == 'S0' else None,
        dynamic_dispatch=scenario == 'S1', rolling_horizon_min=30 if scenario == 'S1' else None,
        interpretation='차량별 완료 100건 후 일반영업 가능; 전환 세부시각 미확인' if scenario == 'S0' else '의무 100건 미적용; 장애인 서비스 제약 아래 동적 배차',
        source='PROJECT_CONTEXT.md; 00_reference/policy/UD_POLICY_RULES.md; 02_processed_data/vehicle/fleet_master.csv',
    ))
save_csv('scenario_core.csv', scenario_rows)

tariffs = read_csv('02_processed_data/cost/electricity_price_by_operator.csv')
assert len(tariffs) == 505 and len({(r['operator'],r['min_power_kw_inclusive']) for r in tariffs}) == 505
assert all(r['tariff_type'] == '사업자 회원 공시요금' for r in tariffs)
assert all(not r['price_per_kwh'] or float(r['price_per_kwh'])>0 for r in tariffs)

carbon = read_csv('02_processed_data/carbon/carbon_factor_master.csv')
carbon_lookup = {r['variable_name']:r for r in carbon}
assert len(carbon_lookup)==len(carbon)
carbon_rows=[]
for key in ['diesel_co2_per_liter','automotive_lpg_co2_per_liter','electricity_emission_factor_selected','pv5_wav_ev_emission_selected','carnival_ice_emission','grand_starex_ice_emission','staria_ice_emission','staria_lpg_ice_emission_alternative','three_model_equal_weight_diesel_proxy']:
    row=carbon_lookup[key]
    old=row['base_year'] in {'2023','2023/2026','2023 인증차량','2020 전후 인증차량','혼합 인증연도'}
    carbon_rows.append(dict(variable_name=key,value=float(row['value']),unit=row['unit'],base_year=row['base_year'],
        original_status=row['status'],model_status='APPROVAL_REQUIRED_OLDER_PROXY' if old else 'SOURCE_SCOPE_REVIEW',
        note=row['note'],source_url=row['source_url']))
save_csv('carbon_factors_review.csv',carbon_rows)

hourly = read_csv('02_processed_data/cost/taxi_revenue_hourly.csv')
assert len(hourly)==48 and {int(r['hour']) for r in hourly}==set(range(24))
assert all(not r['avg_revenue_hour'] and not r['avg_trip_count'] for r in hourly)
ud_template=read_csv('01_raw_data/ud_taxi/templates/ud_operation_master_template.csv')
assert len(ud_template)==12 and all(not r['date'] for r in ud_template)

manifest=[
 dict(input='2025 장애인콜택시 호출·배차 로그',path='01_raw_data/disabled_taxi/',rows=0,status='BLOCKED_MISSING',needed_for='시간별 행정동 수요, S0/S1 동일 요청, 실제 대기시간 검증',next_step='팀원 파일 수령; 요청ID·시각·행정동 코드·취소 상태 확인'),
 dict(input='2025 기준 행정동 코드·경계',path='01_raw_data/spatial/',rows=0,status='BLOCKED_MISSING',needed_for='수요 공간 집계와 그래프·OD 키',next_step='팀원 코드표·경계 수령; 코드 기준일 및 변경 이력 확인'),
 dict(input='시간대별 OD 이동시간',path='01_raw_data/spatial/',rows=0,status='BLOCKED_MISSING',needed_for='픽업·주행·재배치 시간',next_step='팀원 OD 파일 수령; 행정동/시간 키·단위 확인'),
 dict(input='기존 장애인콜택시 차량 및 가동·시작 위치',path='02_processed_data/vehicle/fleet_master.csv',rows=len(fleet),status='PARTIAL_AGGREGATE_ONLY',needed_for='854대 차량별 DES 초기 상태 및 가동률',next_step='2026 fleet·차종별 대수·차고지·근무교대 자료 필요'),
 dict(input='UD 12대 실제 운행·충전·정산 로그',path='01_raw_data/ud_taxi/templates/ud_operation_master_template.csv',rows=0,status='BLOCKED_TEMPLATE_ONLY',needed_for='S0 보정·수익·SOC/충전 파라미터',next_step='팀원 또는 운영사 실제 차량·일/호출 로그 수령'),
 dict(input='일반택시 시간·지역 영업실적',path='02_processed_data/cost/taxi_revenue_hourly.csv',rows=0,status='BLOCKED_TEMPLATE_ONLY',needed_for='일반영업 기회비용과 수입',next_step='시간·요일·행정동별 건수/매출/공차/가용차량시간 수령'),
 dict(input='PV5 WAV 공인 제원',path='02_processed_data/model_inputs/pv5_vehicle_inputs.csv',rows=1,status='PARTIAL_SPEC_ONLY',needed_for='전비와 nominal SOC 범위',next_step='실전비·사용가능 배터리·충전곡선 또는 보수적 감도분석'),
 dict(input='서울시 소유 충전기 후보 및 운영시간',path='02_processed_data/model_inputs/charger_inventory_prepared.csv',rows=433,status='PREPARED_CANDIDATE_NOT_ROUTABLE',needed_for='충전 가능 시간·출력 후보',next_step='좌표·최신 가동상태·실제 사업자·차량 높이/진입·AC규격 확인'),
 dict(input='사업자별 공시 회원 충전요금',path='02_processed_data/cost/electricity_price_by_operator.csv',rows=len(tariffs),status='REFERENCE_ONLY_NO_SITE_JOIN',needed_for='전력비 민감도',next_step='실제 충전사업자/회원·로밍·세션 청구금액 필요'),
 dict(input='기존 fleet 탄소계수 및 전력계수',path='02_processed_data/model_inputs/carbon_factors_review.csv',rows=len(carbon_rows),status='OLDER_PROXY_APPROVAL_REQUIRED',needed_for='CO2e 계산',next_step='최신 적용연도 원문 확인; 구자료 사용 전 사용자 승인'),
 dict(input='S0/S1 공통 운영규칙',path='02_processed_data/model_inputs/scenario_core.csv',rows=2,status='PARTIAL_2026_FLEET_ASSUMED',needed_for='시나리오 비교',next_step='2026 기존 fleet 대수·S0 100건 완료/전환 세부규칙 확인'),
]
save_csv('model_readiness.csv',manifest)
summary=dict(raw_charger_rows=len(raw_chargers),published_clean_rows=len(clean_chargers),
    seoul_raw_rows=sum(r['seoul_boundary'] for r in charger_rows),model_candidate_rows=sum(r['model_candidate_after_data_checks'] for r in charger_rows),
    excluded_ac3=sum(r['connector_label']=='AC3상' for r in charger_rows),outside_seoul=sum(not r['seoul_boundary'] for r in charger_rows),
    charger_type_power_conflict=sum(r['connector_or_power_conflict'] for r in charger_rows),
    chargers_open_24h=sum(r['weekday_open_min']==0 and r['weekday_close_min']==1440 and r['weekend_open_min']==0 for r in charger_rows),
    tariff_rows=len(tariffs),hourly_observed_rows=sum(bool(r['avg_revenue_hour']) for r in hourly),ud_observed_rows=sum(bool(r['date']) for r in ud_template),
    charger_connector_counts=dict(Counter(r['connector_label'] for r in charger_rows)))
(OUT/'audit_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
