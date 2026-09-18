from pathlib import Path
import csv, json, hashlib
from collect_public_sources import SOURCES

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'01_raw_data/profitability/2026-09-17'
OUT=ROOT/'02_processed_data/cost'
OUT.mkdir(parents=True,exist_ok=True)
URL={s[0]:s[2] for s in SOURCES}
def save(name, rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

fees=list(csv.DictReader((RAW/'S04_member_fee_table_transcribed.csv').open(encoding='utf-8-sig')))
canonical='\n'.join(','.join(r.values()) for r in fees)
h=2166136261
for c in canonical:h=((h^ord(c))*16777619)&0xffffffff
assert len(fees)==101 and h==3317249625, 'Browser transcription mismatch'
for sid,value in [('S05','1156.69'),('S12','1885.45'),('S02','4,800'),('S03','1,500'),('S07','4.4')]:
    assert value in (RAW/(sid+'_text.txt')).read_text(encoding='utf-8')

fuel=[]
for name,value,sid in [('LPG',1156.69,'S05'),('diesel',1885.45,'S12')]:
    fuel.append(dict(fuel_type=name,region='서울',price_per_liter=value,unit='KRW/L',observation_date='2026-09-16',retrieved_date='2026-09-17',statistic='서울 일평균 판매가격',vat_included=True,source_id=sid,source_url=URL[sid],status='공개값 확인',note='단일일자 스냅샷. 월평균·연평균 아님. PV5 12대 간 비교에는 직접 사용하지 않음.'))
save('fuel_price.csv',fuel)

params=[]
def add(key,label,value,unit,date,sid,note,status='공개값 확인'):
    params.append(dict(parameter=key,label=label,value=value,unit=unit,reference_date=date,source_id=sid,source_url=URL.get(sid,''),status=status,note=note))
add('ud_fleet_size','UD 차량 수',12,'대','2026-07','S01','두 시나리오 동일. 기존 장애인콜택시 fleet 별도 유지.')
add('s0_monthly_quota','S0 차량별 월 장애인운행 우선 건수',100,'건/대/월','연구 시나리오','S01','차량별 누적. 전체 1,200건을 한 차량에 몰아 적용하지 않음.','연구규칙')
add('s1_monthly_quota','S1 의무 건수',None,'건/대/월','연구 시나리오','','의무 건수 미적용. 수요기반 동적배차. 공란은 0건 운행 뜻이 아님.','해당없음')
for band,base,inc in [('day_04_22',4800,100),('night_22_23_02_04',5800,120),('night_23_02',6700,140)]:
    add(band+'_base','일반택시 '+band+' 기본요금',base,'원','2026-04-03','S02','2023-02-01 시행 요금. 2026년 갱신 공식 페이지에서 현행 확인. 기본거리 1.6km.')
    add(band+'_increment','일반택시 '+band+' 추가요금',inc,'원/요금단위','2026-04-03','S02','거리 131m 또는 시간 30초 단위. 전체 주행시간을 거리요금에 단순 중복 가산하지 않음.')
add('taxi_base_km','일반택시 기본거리',1.6,'km','2026-04-03','S02','서울 중형택시')
add('taxi_distance_step_m','일반택시 거리요금 단위',131,'m','2026-04-03','S02','교통상황별 미터 적용조건 별도 반영')
add('taxi_time_step_sec','일반택시 시간요금 단위',30,'초','2026-04-03','S02','저속구간 시간요금 적용. 전체 운행시간 아님.')
add('taxi_outside_surcharge','시계외 할증률',0.2,'비율','2026-04-03','S02','시계외 적용 대상/구간 확인. 서울 내부 운행은 미적용.')
add('disability_base_fare','장애인 승객 기본요금',1500,'원','2026-09-17 확인','S03','5km까지. UD 동일요금 확인 S11. 회사 수입 전체가 아님.')
add('disability_base_km','장애인 기본거리',5,'km','2026-09-17 확인','S03','승객 요금 기준')
add('disability_middle_limit_km','장애인 중간구간 상한',10,'km','2026-09-17 확인','S03','5km 초과~10km')
add('disability_5_10_rate','장애인 5~10km 추가요금',280,'원/km','2026-09-17 확인','S03','시간·지역 할증 없음')
add('disability_over10_rate','장애인 10km 초과 추가요금',70,'원/km','2026-09-17 확인','S03','최종 금액 100원 미만 절사')
add('disability_rounding','장애인 요금 절사 단위',100,'원','2026-09-17 확인','S03','주차·통행료 승객 부담. 보전분 중복 매출/비용 주의.')
add('pv5_efficiency','PV5 WAV 복합 공인전비',4.4,'km/kWh','2026-09-17 확인','S07','실운행 전비 아님. 충전량과 배터리 소비량 경계 일치 필요. 손실률 임의 추가 금지.')
add('ud_subsidy_per_trip','UD 장애인운행 보조금',None,'원/건','','','건당/차액/월정액 여부부터 확인 필요. 공개 요금으로 대체 금지.','기관 정산자료 필요')
add('actual_charging_price','실제 적용 충전단가',None,'원/kWh','','S04','사업자·출력·회원/로밍·계약 조건별 결정. 사업자별 공시요금은 별도 표.','계약/영수증 필요')
save('profitability_parameters.csv',params)

cost=[]
for key,label,unit,need,note in [
 ('charging','충전 전력비','원/kWh','필수','세션별 과금 kWh × 실제 단가. 공시 회원요금은 대안 입력값이며 실제 정산과 구분.'),
 ('platform_fee','플랫폼·호출 수수료','원/건 또는 매출비율','조건부 필수','운영사 계약 확인. 일반/장애인 영업별 적용 및 VAT 경계 통일.'),
 ('payment_fee','카드결제 수수료','매출비율','조건부 필수','실제 정산기준. 플랫폼 수수료에 포함되면 이중계상 금지.'),
 ('maintenance_per_km','주행거리 비례 정비비','원/km','변동비 비교에 필요','타이어·소모품 등 운영사 최근 실적. 공통 고정비와 분리.'),
 ('incremental_labor','추가 근무 인건비','원/시간','근무시간이 달라질 때','두 시나리오 동일 근무시간/임금이면 공통 고정비는 차이에서 상쇄.'),
 ('unreimbursed_parking_toll','미보전 주차·통행료','원','발생 시','승객에게 전액 보전되는 금액은 별도 통과항목으로 처리.'),
 ('fixed_cost','보험·감가상각·기본 인건비','원/월','절대 순이익 산출 시','12대·기간·근무조건 동일하면 증분 비교에서 상쇄. 전체 운영기관 손익은 별도 범위.')]:
    cost.append(dict(cost_item=key,label=label,value=None,unit=unit,required=need,reference_date='',source_url='',status='운영사 자료 필요',note=note))
save('operating_cost.csv',cost)
long=[]
bands=[('lt30_kw',0,30),('ge30_lt50_kw',30,50),('ge50_lt100_kw',50,100),('ge100_lt200_kw',100,200),('ge200_kw',200,None)]
for r in fees:
    for col,low,high in bands:
        long.append(dict(operator=r['operator'],min_power_kw_inclusive=low,max_power_kw_exclusive=high,price_per_kwh=None if r[col]=='-' else float(r[col]),unit='KRW/kWh',tariff_type='사업자 회원 공시요금',updated_date=r['updated_date'],retrieved_date='2026-09-17',source_id='S04',source_url=URL['S04'],status='공시없음' if r[col]=='-' else '공개값 확인',note='실제 사이트/회원카드/로밍/계약조건 확인 후 적용. 커넥터 호환성과 요금은 별도. 갱신일은 시행일 아님.'))
save('electricity_price_by_operator.csv',long)

requests=[
 dict(item='UD 운영·보조금 정산',request_to='서울시 택시정책과 / 서울시설공단 / 참여 법인택시회사',period='2026-07~08 완료월 우선, 이후 최신 완료월',fields='차량 익명ID, 근무시간, 장애인·일반 운행별 승하차시각/거리/운임, 공차거리·시간, 월100건 도달시각, 보조금 산식·지급조건·실지급액·귀속주체',reason='승객운임만으로 회사 수입을 알 수 없음. S1에도 지급할 보조금 정책을 명시해야 함.',route='https://www.open.go.kr/',status='사용자 정보공개/협조요청',note='개인정보 없이 차량-일 또는 시간대 집계 가능. 서울시택시조합 02-2033-9241, 공단 02-2290-7924 (S11).'),
 dict(item='일반택시 시간대별 영업실적',request_to='서울시 택시정책과 / 서울 빅데이터캠퍼스',period='2025년 전체 또는 2026년 최신 완료월',fields='서울 법인 중형택시, 시간대×요일×승차지역별 운행건수/운임합계/유상거리/공차거리/유상시간/공차탐색시간/영업가능 차량시간 및 지표 정의',reason='시간당 매출·건수의 분모인 영업가능 차량시간 필요. 승차수요만으로 차량당 매출 대체 불가.',route=URL['S08'],status='사용자 이용신청/정보공개',note='최신 수록기간 먼저 문의. 공개 소개 페이지는 확인했으나 최신 원시 운행파일은 확보하지 못함.'),
 dict(item='실제 변동비 정산',request_to='참여 법인택시회사',period='2026년 최근 완료월',fields='충전소/사업자/출력/카드 및 로밍조건, 세션별 kWh·결제금액, 호출·결제 수수료 계약, 거리비례 정비비, 추가근무 단가',reason='공시요금과 실제 적용요금 차이 및 동적운영의 추가 운행비 산정',route='',status='사용자 운영사 협조요청',note='동일 차량·근무시간의 공통 보험·차량구입비 등은 증분 비교에서 우선 제외 가능.')]
save('profitability_missing_requests.csv',requests)

meta=json.loads((RAW/'download_manifest.json').read_text(encoding='utf-8'))
if isinstance(meta,dict): print('manifest keys',list(meta)); meta=meta.get('sources',meta.get('downloads',[]))
source_rows=[]
for sid,title,url in SOURCES:
    status='값 확인' if sid in ['S01','S02','S03','S05','S07','S11','S12'] else '경로 안내만'
    note='공식 웹페이지 원본 HTML 및 텍스트 저장'
    if sid=='S04':status='브라우저 표 전사 검증';note='HTML은 보안 스크립트로 본문 없음. 별도 회원요금 CSV 101행을 브라우저 표시값과 해시 대조. 공식 배포 CSV가 아님.'
    if sid=='S06':status='미채택';note='전국 제품별 가격 페이지. 서울값은 S12 사용.'
    if sid=='S10':status='구자료 수치 미채택';note='2025년 논문이나 분석 원자료 2023년. 수치 사용 전 사용자 승인 필요.'
    if sid in ['S08','S09']:note='최신 영업 원시자료 자체 미확보. 소개/신청 경로만 저장.'
    source_rows.append(dict(source_id=sid,title=title,url=url,retrieved_date='2026-09-17',status=status,note=note))
save('profitability_sources.csv',source_rows)
hourly=list(csv.DictReader((OUT/'taxi_revenue_hourly.csv').open(encoding='utf-8-sig')))
hourly=[{k.lstrip('\ufeff'):v for k,v in r.items()} for r in hourly]
assert len(hourly)==48 and {int(r['hour']) for r in hourly}==set(range(24))
data=dict(parameters=params,fuel=fuel,cost=cost,fees=fees,hourly=hourly,requests=requests,sources=source_rows)
(OUT/'profitability_workbook_data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
validation=dict(ev_operators=len(fees),ev_band_rows=len(long),ev_browser_fnv1a=h,matched=True,raw_table_method='browser visible table transcription',source_collection_date='2026-09-17',prepared_date='2026-09-18')
(RAW/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(validation,ensure_ascii=False))
