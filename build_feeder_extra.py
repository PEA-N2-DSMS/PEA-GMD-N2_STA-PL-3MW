import csv,json,hashlib
from pathlib import Path
from collections import defaultdict
from datetime import datetime
P=Path(__file__).parent;R=P/'raw/500kVA-extra'
def read(name):return list(csv.DictReader((R/name).open(encoding='utf-8-sig')))
def summarize(daily):
 s={k:sum(r.get(k,0) for r in daily) for k in daily[0] if k.endswith('_kWh')}
 s['self_consumption_pct']=100*s['self_consumed_solar_kWh']/s['Inverters Produced_kWh'] if s['Inverters Produced_kWh'] else 0
 s['solar_share_pct']=100*s['self_consumed_solar_kWh']/s['Consumed Energy_kWh'] if s['Consumed Energy_kWh'] else 0
 return s
small=json.loads((P/'data/500kva.json').read_text());inv=read('inverter-energy-generati.csv');meter={r['DateTime'][:10]:r for r in read('meter-export-import-brea.csv')};energy={r['DateTime'][:10]:r for r in read('accumulated-energy.csv')};dailyInv=[]
for r in inv:
 for k,v in r.items():
  if k.startswith('Energy Produced for Inverter'):dailyInv.append(dict(date=r['DateTime'][:10],inverter=k,energy_kWh=float(v)/1000))
for r in small['daily']:
 date=r['date'];m=meter[date];e=energy[date];r['Inverters Produced_kWh']=float(e['Accumulated Energy Produced'])/1000
 r['Imported Energy_kWh']=float(next(v for k,v in m.items() if k.startswith('Imported')))/1000
 r['Exported Energy_kWh']=float(next(v for k,v in m.items() if k.startswith('Exported')))/1000
 r['self_consumed_solar_kWh']=r['Inverters Produced_kWh']-r['Exported Energy_kWh'];r['Consumed Energy_kWh']=r['Imported Energy_kWh']+r['self_consumed_solar_kWh']
small['summary']=summarize(small['daily']);small['estimated']=False;small['consumptionDerived']=True;small['inverterDaily']=dailyInv
sums=defaultdict(float)
for r in dailyInv:sums[r['inverter']]+=r['energy_kWh']
small['inverters']=[dict(inverter=k,energy_kWh=v) for k,v in sums.items()]
extraInventory=[]
for path in sorted(R.glob('*.csv')):
 rows=read(path.name);dates=[r.get('DateTime') for r in rows if r.get('DateTime')]
 extraInventory.append(dict(file=path.name,rows=len(rows),columns=list(rows[0]),start=min(dates) if dates else None,end=max(dates) if dates else None,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),missing_cells=sum(v=='' for r in rows for v in r.values()),source_dir='raw/500kVA-extra'))
small['inventory']+=extraInventory
# October report dates are authoritative, irrespective of the ZIP name.
octdaily=[]
for r in read('energy-overview.csv'):
 d={'date':r['DateTime'][:10]}
 for k in ['Consumed Energy','Exported Energy','Imported Energy','Inverters Produced']:d[k+'_kWh']=float(r[k])/1000
 d['self_consumed_solar_kWh']=d['Inverters Produced_kWh']-d['Exported Energy_kWh'];octdaily.append(d)
october=dict(daily=octdaily,summary=summarize(octdaily),hourly=[],inverters=[],inverterDaily=[],inventory=[i for i in extraInventory if i['start'] and i['start'].startswith('2026-10')],estimated=False)
hours={}
for feeder,path in [('large',P/'raw/Solar/inverter-production-time SEP2026.csv'),('small',R/'inverter-production-time.csv')]:
 days={}
 for r in csv.DictReader(path.open(encoding='utf-8-sig')):
  values=[float(v) for k,v in r.items() if k.startswith('Inverter Production Time')]
  assert all(0<=v<=24 for v in values)
  days[r['DateTime'][:10]]={'hours':sum(values)/len(values),'total':sum(values),'inverters':len(values),'samples':len(values)}
 assert len(days)==30;hours[feeder]=dict(sorted(days.items()))
output=dict(small={'2026-09':small,'2026-10':october},hours=hours)
(P/'data/feeder-extra.json').write_text(json.dumps(output,ensure_ascii=False,indent=2));(P/'feeder-extra.js').write_text('const FEEDER_EXTRA='+json.dumps(output,ensure_ascii=False).replace('</','<\\/')+';\n')
print('September Feeder 10',small['summary']);print('Inverters',len(sums));print('Hours average',{k:sum(v['hours'] for v in d.values())/len(d) for k,d in hours.items()})
