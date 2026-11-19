"""Clean the Sample Superstore data and draw the four case study charts.
Usage: python scripts/clean_and_chart.py   (writes data/superstore_clean.csv and charts/*.png)"""
import sys, pandas as pd, matplotlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]   # repo root, so the script runs from anywhere
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.ticker import FuncFormatter
src = ROOT/'data'/'raw'/'SampleSuperstore.csv.gz'; out = ROOT/'charts'
import logging; logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)  # quiet if Inter isn't installed
SLATE='#4A3F48'; PEANUT='#BF9A84'; INK='#2E262C'; PLUM='#6B5E62'; LINEN='#E0D8CC'; BG='#FBFAF7'; WOOL='#C9C0B0'
plt.rcParams.update({'font.family':['Inter','DejaVu Sans'],'font.size':11,'text.color':INK,'axes.labelcolor':PLUM,'xtick.color':PLUM,'ytick.color':PLUM,
 'axes.edgecolor':LINEN,'figure.facecolor':BG,'axes.facecolor':BG,'savefig.facecolor':BG,'axes.spines.top':False,'axes.spines.right':False})
df=pd.read_csv(src)
# ---- clean
df['Postal Code']=df['Postal Code'].astype(int).astype(str).str.zfill(5)
df['Profit Margin']=(df.Profit/df.Sales).round(4)
df['Discount Band']=pd.cut(df.Discount,[-0.01,0,0.1,0.2,0.3,0.5,0.8],labels=['No discount','1-10%','11-20%','21-30%','31-50%','51-80%'])
df['Loss Line']=df.Profit<0
df.to_csv(ROOT/'data'/'superstore_clean.csv',index=False)
money=lambda v,_=None: f"-${abs(v)/1000:,.0f}K" if v<0 else f"${v/1000:,.0f}K"
def title(ax,t,s):
    ax.set_title(t,loc='left',fontsize=15,fontweight='semibold',color=INK,pad=26)
    ax.text(0,1.02,s,transform=ax.transAxes,fontsize=10.5,color=PLUM,va='bottom')
def save(fig,name): fig.tight_layout(); fig.savefig(f'{out}/{name}',dpi=200); plt.close(fig)

# 1 margin by discount band
b=df.groupby('Discount Band',observed=True).agg(S=('Sales','sum'),P=('Profit','sum'),N=('Sales','size'))
b['M']=b.P/b.S*100
fig,ax=plt.subplots(figsize=(9,5))
cols=[SLATE if m>=0 else PEANUT for m in b.M]
bars=ax.bar(b.index.astype(str),b.M,color=cols,width=0.62)
ax.axhline(0,color=PLUM,lw=1)
for r,m,n in zip(bars,b.M,b.N):
    y=m+(3 if m>=0 else -3); ax.text(r.get_x()+r.get_width()/2,y,f"{m:.0f}%",ha='center',va='bottom' if m>=0 else 'top',fontsize=11,fontweight='semibold',color=INK)
    ax.text(r.get_x()+r.get_width()/2,-138,f"{n:,} lines",ha='center',va='top',fontsize=9,color=PLUM)
ax.set_ylim(-150,45); ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:.0f}%")); ax.set_ylabel('Profit margin')
ax.grid(axis='y',color=LINEN,lw=0.8); ax.set_axisbelow(True); ax.tick_params(axis='x',length=0)
title(ax,'Discounts above 20% turn profit into losses','Profit margin by discount level, all 9,994 order lines')
save(fig,'01_margin_by_discount.png')

# 2 profit by sub-category
s=df.groupby('Sub-Category').agg(S=('Sales','sum'),P=('Profit','sum')).sort_values('P')
fig,ax=plt.subplots(figsize=(9,6.6))
cols=[SLATE if p>=0 else PEANUT for p in s.P]
bars=ax.barh(s.index,s.P,color=cols,height=0.66)
ax.axvline(0,color=PLUM,lw=1)
for r,p in zip(bars,s.P):
    ax.text(p+(800 if p>=0 else -800),r.get_y()+r.get_height()/2,money(p),va='center',ha='left' if p>=0 else 'right',fontsize=9.5,color=INK)
ax.xaxis.set_major_formatter(FuncFormatter(money)); ax.set_xlim(-30000,64000)
ax.grid(axis='x',color=LINEN,lw=0.8); ax.set_axisbelow(True); ax.tick_params(axis='y',length=0)
title(ax,'Tables, Bookcases and Supplies lose money','Total profit by sub-category')
save(fig,'02_profit_by_subcategory.png')

# 3 category sales vs profit
c=df.groupby('Category').agg(Sales=('Sales','sum'),Profit=('Profit','sum')).loc[['Technology','Office Supplies','Furniture']]
fig,ax=plt.subplots(figsize=(9,5))
import numpy as np
x=np.arange(len(c)); w=0.36
b1=ax.bar(x-w/2-0.01,c.Sales,w,color=WOOL,label='Sales')
b2=ax.bar(x+w/2+0.01,c.Profit,w,color=SLATE,label='Profit')
for r,v in list(zip(b1,c.Sales))+list(zip(b2,c.Profit)):
    ax.text(r.get_x()+r.get_width()/2,v+12000,money(v),ha='center',va='bottom',fontsize=10,color=INK)
for i,(sv,pv) in enumerate(zip(c.Sales,c.Profit)):
    ax.text(i,-75000,f"{pv/sv*100:.1f}% margin",ha='center',fontsize=10.5,fontweight='semibold',color=INK)
ax.set_xticks(x); ax.set_xticklabels(c.index); ax.tick_params(axis='x',length=0,pad=30)
ax.yaxis.set_major_formatter(FuncFormatter(money)); ax.set_ylim(0,980000)
ax.grid(axis='y',color=LINEN,lw=0.8); ax.set_axisbelow(True)
ax.legend(frameon=False,loc='upper right',ncol=2)
title(ax,'Furniture sells well but keeps almost none of it','Total sales and profit by product category')
save(fig,'03_category_sales_vs_profit.png')

# 4 region margin and discount (two panels, no dual axis)
r=df.groupby('Region').agg(S=('Sales','sum'),P=('Profit','sum'),D=('Discount','mean')); r['M']=r.P/r.S*100
r=r.sort_values('M')
fig,(a1,a2)=plt.subplots(1,2,figsize=(10,4.4),sharey=True)
for ax,col,fmt,lab in [(a1,'M',lambda v:f"{v:.1f}%",'Profit margin'),(a2,'D',lambda v:f"{v*100:.0f}%",'Average discount')]:
    colors=[PEANUT if reg=='Central' else SLATE for reg in r.index]
    bs=ax.barh(r.index,r[col],color=colors,height=0.6)
    for bb,v in zip(bs,r[col]): ax.text(v+(r[col].max()*0.02),bb.get_y()+bb.get_height()/2,fmt(v),va='center',fontsize=10.5,color=INK)
    ax.set_xlim(0,r[col].max()*1.25); ax.set_xticks([]); ax.spines['bottom'].set_visible(False); ax.tick_params(axis='y',length=0)
    ax.set_title(lab,loc='left',fontsize=11.5,color=PLUM,pad=8)
fig.suptitle('Central has the deepest discounts and the thinnest margin',x=0.02,ha='left',fontsize=15,fontweight='semibold',color=INK)
fig.tight_layout(); fig.savefig(f'{out}/04_region_margin_and_discount.png',dpi=200); plt.close(fig)
print('ok')
