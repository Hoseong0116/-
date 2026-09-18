import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const data=JSON.parse(await fs.readFile(path.join(root,'02_processed_data/cost/profitability_workbook_data.json'),'utf8'));
const output=path.join(root,'outputs/profitability_20260918');
await fs.mkdir(output,{recursive:true});
const wb=Workbook.create();
function col(n){let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;}
const configs=[];
function table(name,title,notes,headers,rows,widths,height=55){
 const sh=wb.worksheets.add(name);sh.showGridLines=false;
 const end=col(headers.length), start=notes.length+3, last=start+rows.length;
 sh.getRange(`A1:${end}${last}`).format.font.name='Arial';
 sh.getRange(`A1:${end}${last}`).format.font.size=10;
 sh.getRange(`A1:${end}1`).merge();sh.getRange('A1').values=[[title]];
 sh.getRange(`A1:${end}1`).format.fill='#173B50';sh.getRange(`A1:${end}1`).format.font.color='#FFFFFF';sh.getRange(`A1:${end}1`).format.font.bold=true;sh.getRange(`A1:${end}1`).format.font.size=17;sh.getRange('A1').format.rowHeight=36;
 notes.forEach((t,i)=>{let r=i+2;sh.getRange(`A${r}:${end}${r}`).merge();sh.getRange(`A${r}`).values=[[t]];sh.getRange(`A${r}:${end}${r}`).format.wrapText=true;sh.getRange(`A${r}`).format.rowHeight=32;});
 sh.getRange(`A${start}:${end}${last}`).values=[headers,...rows];
 sh.getRange(`A${start}:${end}${last}`).format.wrapText=true;
 sh.getRange(`A${start}:${end}${last}`).format.verticalAlignment='center';
 sh.getRange(`A${start}:${end}${start}`).format.fill='#226578';
 sh.getRange(`A${start}:${end}${start}`).format.font.color='#FFFFFF';
 sh.getRange(`A${start}:${end}${start}`).format.font.bold=true;
 sh.getRange(`A${start}:${end}${start}`).format.rowHeight=35;
 sh.getRange(`A${start+1}:${end}${last}`).format.rowHeight=height;
 widths.forEach((w,i)=>sh.getRange(`${col(i+1)}1:${col(i+1)}${last}`).format.columnWidth=w/7);
 for(let r=start+1;r<=last;r++)if((r-start)%2===0)sh.getRange(`A${r}:${end}${r}`).format.fill='#F0F5F7';
 sh.tables.add(`A${start}:${end}${last}`,true,'Data'+configs.length);
 sh.freezePanes.freezeRows(start);
 configs.push({name,start,last,end});return sh;
}
const inputRows=data.parameters.map(r=>[r.label,r.value,r.unit,r.reference_date,r.status,r.note,r.source_id,r.source_url]);
for(const r of data.fuel)inputRows.push([r.fuel_type+' 서울 일평균',r.price_per_liter,r.unit,r.observation_date,r.status,r.note,r.source_id,r.source_url]);
for(const r of data.cost)inputRows.push([r.label,r.value,r.unit,null,r.status,r.required+'。'+r.note,null,null]);
const main=table('수익성 입력','UD 12대 운영방식 비교 | 수익성 입력자료',[
 '조회 2026-09-17 · 작성 2026-09-18. 확인된 값만 수록. 빈칸은 미확인 또는 해당없음이며 0으로 대체하지 않습니다.',
 'S0: 차량별 월 100건 우선 후 일반영업. S1: 같은 차량·수요에서 의무건수 없이 수요기반 동적운영. 기존 장애인콜택시 fleet 유지.',
 '비교지표: 운영사 귀속 수입 − 변동비. 공통 고정비 제외 시 순이익이 아닌 공헌이익입니다. 보조금 산식·일반영업 실적은 아직 필요합니다.'
],['항목','값','단위','기준일 / 확인일','상태','적용 조건','출처ID','공식 원문'],inputRows,[230,95,120,140,145,420,70,340],65);
inputRows.forEach((r,i)=>main.getRange(`B${configs[0].start+1+i}`).setNumberFormat(Number.isInteger(r[1])?'#,##0':'#,##0.00'));
const feeRows=data.fees.map(r=>[r.operator,...['lt30_kw','ge30_lt50_kw','ge50_lt100_kw','ge100_lt200_kw','ge200_kw'].map(k=>r[k]==='-'?null:Number(r[k])),new Date(r.updated_date+'T00:00:00Z')]);
const fee=table('사업자별 충전요금','충전사업자 회원 공시요금',[
 '단위: 원/kWh. 101개 사업자, 5출력구간. 실제 청구단가는 회원·로밍·계약·충전소별로 확인해야 합니다. 빈칸은 공시없음입니다.',
 '출처 S04 무공해차 통합누리집: '+data.sources.find(r=>r.source_id==='S04').url,
 '2026-09-17 표시된 표 전사 후 101행 전체 대조 완료. 공식 배포 CSV나 실제 거래자료가 아닙니다. 갱신일 ≠ 요금 시행일.'
],['사업자','30kW 미만','30~49kW','50~99kW','100~199kW','200kW 이상','갱신일'],feeRows,[210,105,105,105,115,115,115],25);
fee.getRange(`B7:F${configs[1].last}`).setNumberFormat('0.0');fee.getRange(`G7:G${configs[1].last}`).setNumberFormat('yyyy-mm-dd');
const hourlyRows=data.hourly.map(r=>[Number(r.hour),r.weekday_type==='weekday'?'평일':'주말',...Array(6).fill(null),'정보공개/이용신청 필요']);
const hourly=table('일반택시 시간대','일반택시 시간대별 영업자료 입력 틀',[
 '서울 법인 중형택시 기준. 최신 관측값은 확보하지 못했습니다. 기존 48개 시간대 틀을 유지하며 임의 추정값을 넣지 않았습니다.',
 '시간당 건수·매출의 분모: 영업가능 차량시간. 공차율은 거리 기준으로 통일하고 공차시간율과 구분합니다. 지역·관측기간은 원자료 수령 후 추가합니다.'
],['시간(시)','요일구분','건수/차량시간','평균 승차거리(km)','평균 운임(원/건)','매출(원/차량시간)','공차거리율','평균 공차시간(분/건)','상태'],hourlyRows,[80,85,130,145,145,155,115,160,190],28);
hourly.getRange('A6:A53').setNumberFormat('0');
const requests=table('사용자 요청사항','직접 신청·협조 요청이 필요한 자료',[
 '공개 요금·제원·연료가격은 확보했습니다. 아래는 비공개 정산 또는 승인형 운행자료입니다. 전화나 정보공개 요청은 아직 보내지 않았습니다.',
 '최신 기간 우선: UD는 2026년 7~8월 완료월, 일반택시는 2025년 전체 또는 2026년 최신 완료월. 오래된 수치 사용 전 승인 필요.'
],['자료','요청기관','희망기간','필요 필드','필요 이유','신청 / 확인 링크','진행상태','참고'],data.requests.map(r=>[r.item,r.request_to,r.period,r.fields,r.reason,r.route,r.status,r.note]),[165,220,185,390,300,270,160,310],150);
table('원자료 목록','공식 출처와 원자료 확보상태',[
 '원본 HTML·추출 텍스트·다운로드 기록은 프로젝트의 01_raw_data/profitability/2026-09-17에 보관했습니다.',
 'S04는 브라우저 표시 표를 별도 CSV로 보관. S08·S09는 신청경로이며 영업 원시파일이 아닙니다. S10의 2023년 관측값은 미채택입니다.'
],['ID','자료명','공식 링크','조회일','채택 / 확보상태','원자료 설명'],data.sources.map(r=>[r.source_id,r.title,r.url,new Date(r.retrieved_date+'T00:00:00Z'),r.status,r.note]),[65,245,390,110,180,470],70);
wb.worksheets.getItem('원자료 목록').getRange('D6:D17').setNumberFormat('yyyy-mm-dd');
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'수익성 입력!A6:H10',include:'values,formulas',tableMaxRows:5,tableMaxCols:8,maxChars:2600})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:20},summary:'Error scan'})).ndjson);
for(const c of configs){
 const last=Math.min(c.last,c.start+5);
 const png=await wb.render({sheetName:c.name,range:`A1:${c.end}${last}`,scale:1,format:'png'});
 await fs.writeFile(path.join(output,c.name+'.png'),new Uint8Array(await png.arrayBuffer()));
}
const xlsx=await SpreadsheetFile.exportXlsx(wb);await xlsx.save(path.join(output,'UD_수익성_입력자료_20260918.xlsx'));
console.log(JSON.stringify({sheets:configs,output}));
