"""Print the summary tables behind the Superstore findings.
Usage: python scripts/analyze.py   (run clean_and_chart.py first)"""
import pandas as pd, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]   # repo root, so the script runs from anywhere
pd.set_option('display.width',200)
df=pd.read_csv(ROOT/'data'/'superstore_clean.csv')
tot=df[['Sales','Profit']].sum(); print("TOTAL",tot.round(0).to_dict(),"margin",round(tot.Profit/tot.Sales*100,1),"rows",len(df))
d2=df.drop_duplicates(); t2=d2[['Sales','Profit']].sum(); print("dedup",len(d2),t2.round(0).to_dict())
def g(cols):
    x=df.groupby(cols).agg(Sales=('Sales','sum'),Profit=('Profit','sum'),Lines=('Sales','size'),AvgDisc=('Discount','mean'))
    x['Margin%']=x.Profit/x.Sales*100; return x.round(2).sort_values('Profit')
for c in ['Region','Category','Segment','Ship Mode']: print(g(c),"\n")
print(g('Sub-Category'))
print(g(['Region','Category']))
df['DiscBand']=pd.cut(df.Discount,[-0.01,0,0.1,0.2,0.3,0.5,0.8],labels=['0%','1-10%','11-20%','21-30%','31-50%','51-80%'])
x=df.groupby('DiscBand',observed=True).agg(Lines=('Sales','size'),Sales=('Sales','sum'),Profit=('Profit','sum'),LossShare=('Profit',lambda p:(p<0).mean()))
x['Margin%']=x.Profit/x.Sales*100; print(x.round(3))
print(df.groupby('Discount').agg(n=('Sales','size'),margin=('Profit',lambda p: p.sum()), sales=('Sales','sum')).assign(m=lambda t:t.margin/t.sales*100).round(1))
s=g('State'); print(s.head(8)); print(s.tail(5))
loss=df[df.Profit<0]; print("loss lines",len(loss),round(len(loss)/len(df)*100,1),"loss total",round(loss.Profit.sum()), "share with disc>=0.3",round((loss.Discount>=0.3).mean()*100,1))
print("disc>0.2 lines", (df.Discount>0.2).sum(), "profit", round(df[df.Discount>0.2].Profit.sum()), "profit if those were zero ->", round(df[df.Discount<=0.2].Profit.sum()))
# tables/bookcases discount
print(df[df['Sub-Category'].isin(['Tables','Bookcases','Supplies'])].groupby('Sub-Category').Discount.describe())
# Central region discounts
print(df.groupby(['Region']).Discount.mean())
print(df.groupby(['State']).Discount.mean().sort_values().tail(6))
