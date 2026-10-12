"""Build the 500 kVA dataset without inventing meter totals or inverter records."""
import csv, hashlib, json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
ROOT=Path(__file__).parent
points={};inventory=[]
for path in sorted((ROOT/'raw/500kVA').glob('*.csv')):
    rows=list(csv.DictReader(path.open(encoding='utf-8-sig')))
    stamps=[]
    for r in rows:
        ts=datetime.strptime(r['Measurement Time'],'%b %d, %Y %I:%M %p')
        assert ts not in points, f'Duplicate timestamp: {ts}'
        values={k.split(' (')[0]:float(v)*(1000 if '(MW)' in k else 1) for k,v in r.items() if k!='Measurement Time'}
        assert all(v>=0 for v in values.values())
        assert abs(values['Production']-values['To Building']-values['To Grid'])<=20.00001
        assert abs(values['Consumption']-values['From Solar']-values['From Grid'])<=20.00001
        points[ts]=values;stamps.append(ts)
    inventory.append(dict(file=path.name,rows=len(rows),columns=list(rows[0]),start=str(min(stamps)),end=str(max(stamps)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),missing_cells=0))
expected={datetime(2026,9,1)+timedelta(minutes=15*i) for i in range(2880)}
assert set(points)==expected
hours=defaultdict(list)
for ts,v in sorted(points.items()):hours[ts.replace(minute=0)].append(v)
hourly=[];days=defaultdict(list)
for ts,values in sorted(hours.items()):
    assert len(values)==4
    r={'timestamp':ts.strftime('%Y-%m-%d %H:%M'),'sample_count':4}
    for k in values[0]:
        r[k+'_mean_kW']=sum(v[k] for v in values)/4
        r[k+'_estimated_kWh']=sum(v[k] for v in values)*.25
    hourly.append(r);days[ts.strftime('%Y-%m-%d')].append(r)
daily=[]
for date,rows in sorted(days.items()):
    r={'date':date}
    for k in rows[0]:
        if k.endswith('_estimated_kWh'):r[k]=sum(x[k] for x in rows)
    for dest,src in [('Inverters Produced','Production'),('Consumed Energy','Consumption'),('Imported Energy','From Grid'),('Exported Energy','To Grid')]:r[dest+'_kWh']=r[src+'_estimated_kWh']
    r['self_consumed_solar_kWh']=r['To Building_estimated_kWh']
    daily.append(r)
summary={k:sum(r[k] for r in daily) for k in daily[0] if k.endswith('_kWh')}
summary.update(self_consumption_pct=100*summary['self_consumed_solar_kWh']/summary['Inverters Produced_kWh'],solar_share_pct=100*summary['self_consumed_solar_kWh']/summary['Consumed Energy_kWh'],files=len(inventory),quarter_hour_rows=len(points),hourly_rows=len(hourly),daily_rows=len(daily),monthly_inverter_sum_kWh=None)
data=dict(summary=summary,daily=daily,hourly=hourly,inventory=inventory,inverters=[],inverterDaily=[],estimated=True,transformer_kVA=500)
(ROOT/'data/500kva.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
(ROOT/'feeder-data.js').write_text('const SMALL_FEEDER_DATA='+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+';\n')
print(json.dumps(summary,indent=2))
