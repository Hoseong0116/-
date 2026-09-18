from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import urllib.request, json, hashlib, datetime, re, html

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / '01_raw_data' / 'profitability' / '2026-09-17'
SOURCES = [
 ('S01','서울시 UD택시 시범운영','https://www.seoul.go.kr/news/news_report.do?nttNo=460523&srchCtgry=467'),
 ('S02','서울 중형택시 현재 요금','https://news.seoul.go.kr/traffic/archives/1659'),
 ('S03','장애인콜택시 이용기준과 요금','https://sisul.or.kr/open_content/calltaxi/introduce/receipt.jsp'),
 ('S04','사업자별 전기차 충전요금','https://ev.or.kr/nportal/evcarInfo/initEvcarChargePriceV2.do'),
 ('S05','서울 LPG 지역별 평균가격','https://www.opinet.co.kr/user/dopvsavsel/dopVsAreaselSelect.do'),
 ('S06','주유소 지역별 평균가격','https://www.opinet.co.kr/user/dopospdrg/dopOsPdrgSelect.do'),
 ('S07','PV5 WAV 공식 제원','https://www.kia.com/kr/vehicles/pv5-wav/specification'),
 ('S08','서울 빅데이터캠퍼스 데이터 안내','https://bigdata.seoul.go.kr/cnts.do?r_id=P210'),
 ('S09','서울교통빅데이터플랫폼','https://t-data.seoul.go.kr/'),
 ('S10','서울 택시 수요예측 선행연구','https://www.jkst.or.kr/articles/xml/91v9/'),
 ('S11','UD택시 요금관련 공단 답변','https://sisul.or.kr/open_content/calltaxi/qna/qnaMsgDetail.do?qnaid=QNAS20260714000005'),
 ('S12','서울 경유 지역별 평균가격','https://www.opinet.co.kr/user/dopospdrg/dopOsPdrgAreaView.do'),
]

def fetch(item):
    sid, title, url = item
    row = dict(source_id=sid,title=title,url=url,retrieved_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req,timeout=25) as response:
            data=response.read(); row.update(http_status=response.status,final_url=response.url,content_type=response.headers.get('Content-Type',''))
        path=OUT / (sid+'.html'); path.write_bytes(data)
        encoding='utf-8'
        try: decoded=data.decode(encoding)
        except UnicodeDecodeError: decoded=data.decode('cp949',errors='replace')
        decoded=re.sub(r'<(script|style)\b[^>]*>.*?</\1>', '', decoded, flags=re.S|re.I)
        txt=html.unescape(re.sub(r'<[^>]+>', '\n', decoded))
        txt='\n'.join(line.strip() for line in txt.splitlines() if line.strip())
        (OUT/(sid+'_text.txt')).write_text(txt,encoding='utf-8')
        row.update(status='DOWNLOADED_UNVALIDATED',bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),local_file=str(path.relative_to(ROOT)))
    except Exception as exc:
        row.update(status='DOWNLOAD_FAILED',error=str(exc))
    return row

if __name__=='__main__':
    import sys
    OUT.mkdir(parents=True,exist_ok=True)
    selected=[s for s in SOURCES if s[0] in sys.argv[1:]] if len(sys.argv)>1 else SOURCES
    with ThreadPoolExecutor(max_workers=6) as pool: results=list(pool.map(fetch,selected))
    if len(sys.argv)>1 and (OUT/'download_manifest.json').exists():
        old=json.loads((OUT/'download_manifest.json').read_text(encoding='utf-8'))
        results=[r for r in old if r['source_id'] not in {s[0] for s in selected}]+results
    (OUT/'download_manifest.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    for row in results: print(row['source_id'],row['status'],row.get('bytes'),row.get('error',''))
