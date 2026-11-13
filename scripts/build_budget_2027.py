from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, DataBarRule
from openpyxl.chart import BarChart, Reference
from openpyxl.utils import get_column_letter as L
from datetime import date

F="Arial"; VERDE="2F6B4F"; CHIARO="E8F1EC"; INPUT="FFF8DC"
hdr=Font(name=F,bold=True,color="FFFFFF",size=10); hfill=PatternFill("solid",fgColor=VERDE)
base=Font(name=F,size=10); bold=Font(name=F,size=10,bold=True)
thin=Side(style="thin",color="D0D7D3"); box=Border(top=thin,bottom=thin,left=thin,right=thin)
EUR='#,##0.00 €;-#,##0.00 €;"-"'
inp=PatternFill("solid",fgColor=INPUT)
mesi=["Gennaio","Febbraio","Marzo","Aprile","Maggio","Giugno","Luglio","Agosto","Settembre","Ottobre","Novembre","Dicembre"]

def head(ws,r,vals,c0=1):
    for i,v in enumerate(vals):
        c=ws.cell(r,c0+i,v); c.font=hdr; c.fill=hfill; c.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True); c.border=box

wb=Workbook()
# --- Istruzioni
ws=wb.active; ws.title="Istruzioni"; ws.sheet_view.showGridLines=False
ws.column_dimensions["B"].width=95
ws["B2"]="Budget Familiare 2027"; ws["B2"].font=Font(name=F,size=20,bold=True,color=VERDE)
ws["B3"]="Il tuo anno sotto controllo, mese per mese."; ws["B3"].font=Font(name=F,size=11,italic=True,color="555555")
righe=["COME SI USA (3 passi)",
"1. Foglio «Categorie»: rinomina le categorie se vuoi e scrivi il budget mensile di ogni spesa (celle gialle).",
"2. Foglio «Movimenti»: registra ogni entrata e uscita. Scegli la categoria dal menu a tendina: il tipo (Entrata/Uscita) si compila da solo.",
"3. Fogli «Riepilogo» e «Cruscotto»: si aggiornano automaticamente. Non serve toccare nulla.",
"",
"LEGENDA",
"Celle gialle = da compilare. Tutte le altre celle contengono formule: meglio non modificarle.",
"Nel foglio Movimenti c'è una riga d'esempio: cancellala quando inizi.",
"",
"COMPATIBILITÀ",
"Funziona con Microsoft Excel (2010 o successivi), Google Fogli (File → Importa) e LibreOffice Calc.",
"",
"Grazie per l'acquisto! Se ti è utile, una recensione aiuta tantissimo un piccolo negozio."]
for i,t in enumerate(righe):
    c=ws.cell(5+i,2,t); c.font=bold if t.isupper() and t else base; c.alignment=Alignment(wrap_text=True)

# --- Categorie
cs=wb.create_sheet("Categorie"); cs.sheet_view.showGridLines=False
cs.column_dimensions["A"].width=30; cs.column_dimensions["B"].width=12; cs.column_dimensions["C"].width=18
head(cs,1,["Categoria","Tipo","Budget mensile (€)"])
cats=[("Stipendio","Entrata",0),("Altre entrate","Entrata",0),
("Affitto / Mutuo","Uscita",700),("Bollette (luce, gas, acqua)","Uscita",150),("Spesa alimentare","Uscita",400),
("Trasporti e carburante","Uscita",120),("Telefono e internet","Uscita",40),("Salute e farmacia","Uscita",50),
("Abbigliamento","Uscita",60),("Casa e manutenzione","Uscita",50),("Svago e uscite","Uscita",100),
("Abbonamenti","Uscita",30),("Animali","Uscita",40),("Figli e scuola","Uscita",0),("Regali","Uscita",30),
("Viaggi","Uscita",80),("Assicurazioni","Uscita",40),("Risparmio / Investimenti","Uscita",150),("Altro","Uscita",50),("(categoria libera)","Uscita",0)]
N=len(cats)
for i,(n,t,b) in enumerate(cats,2):
    for j,v in enumerate([n,t,b],1):
        c=cs.cell(i,j,v); c.font=base; c.border=box; c.fill=inp
    cs.cell(i,3).number_format=EUR
dv=DataValidation(type="list",formula1='"Entrata,Uscita"',allow_blank=False); cs.add_data_validation(dv); dv.add(f"B2:B{N+1}")
CR=f"Categorie!$A$2:$A${N+1}"

# --- Movimenti
ms=wb.create_sheet("Movimenti"); ms.freeze_panes="A2"
for col,w in zip("ABCDEF",[12,36,30,10,14,10]): ms.column_dimensions[col].width=w
head(ms,1,["Data","Descrizione","Categoria","Tipo","Importo (€)","Mese"])
R=1000
dvc=DataValidation(type="list",formula1=f"={CR}",allow_blank=True); ms.add_data_validation(dvc); dvc.add(f"C2:C{R+1}")
for r in range(2,R+2):
    for c in (1,2,3,5):
        x=ms.cell(r,c); x.fill=inp; x.border=box; x.font=base
    ms.cell(r,1).number_format="DD/MM/YYYY"; ms.cell(r,5).number_format=EUR
    ms.cell(r,4,f'=IF(C{r}="","",IFERROR(INDEX(Categorie!$B$2:$B${N+1},MATCH(C{r},{CR},0)),""))').font=base
    ms.cell(r,6,f'=IF(A{r}="","",MONTH(A{r}))').font=base
ms["A2"]=date(2027,1,3); ms["B2"]="Esempio: spesa al supermercato (cancellami)"; ms["C2"]="Spesa alimentare"; ms["E2"]=64.80

# --- Riepilogo
rs=wb.create_sheet("Riepilogo"); rs.freeze_panes="C2"
rs.column_dimensions["A"].width=30; rs.column_dimensions["B"].width=14
for k in range(3,17): rs.column_dimensions[L(k)].width=12
head(rs,1,["Categoria","Budget/mese"]+mesi+["Totale anno","Budget anno"])
for i in range(N):
    r=i+2
    rs.cell(r,1,f"=Categorie!A{r}").font=base
    b=rs.cell(r,2,f"=Categorie!C{r}"); b.number_format=EUR; b.font=Font(name=F,size=10,color="008000")
    for m in range(12):
        c=rs.cell(r,3+m,f'=SUMIFS(Movimenti!$E:$E,Movimenti!$C:$C,$A{r},Movimenti!$F:$F,{m+1})'); c.number_format=EUR; c.font=base; c.border=box
    rs.cell(r,15,f"=SUM(C{r}:N{r})").number_format=EUR
    rs.cell(r,16,f"=B{r}*12").number_format=EUR
    for k in (1,2,15,16): rs.cell(r,k).border=box
    rs.cell(r,15).font=bold
# Totali
t=N+3
lab=[("Totale entrate","Entrata"),("Totale uscite","Uscita")]
for j,(l,tp) in enumerate(lab):
    r=t+j; rs.cell(r,1,l).font=bold
    for k in range(3,16):
        col=L(k); c=rs.cell(r,k,f'=SUMIFS({col}$2:{col}${N+1},Categorie!$B$2:$B${N+1},"{tp}")'); c.number_format=EUR; c.font=bold; c.fill=PatternFill("solid",fgColor=CHIARO)
r=t+2; rs.cell(r,1,"Saldo del mese").font=bold
for k in range(3,16):
    col=L(k); c=rs.cell(r,k,f"={col}{t}-{col}{t+1}"); c.number_format=EUR; c.font=bold; c.fill=PatternFill("solid",fgColor=CHIARO)
r=t+3; rs.cell(r,1,"Tasso di risparmio").font=bold
for k in range(3,16):
    col=L(k); c=rs.cell(r,k,f'=IF({col}{t}=0,"",{col}{t+2}/{col}{t})'); c.number_format="0.0%"; c.font=bold
rs.conditional_formatting.add(f"C{t+2}:O{t+2}",CellIsRule(operator="lessThan",formula=["0"],font=Font(color="C0392B",bold=True)))

# --- Cruscotto
ds=wb.create_sheet("Cruscotto"); ds.sheet_view.showGridLines=False
ds.column_dimensions["A"].width=2; ds.column_dimensions["B"].width=30
for c in "CDEF": ds.column_dimensions[c].width=16
ds["B2"]="Cruscotto 2027"; ds["B2"].font=Font(name=F,size=18,bold=True,color=VERDE)
ds["B4"]="Mese da analizzare (1-12):"; ds["B4"].font=bold
ds["C4"]=1; ds["C4"].fill=inp; ds["C4"].font=bold; ds["C4"].border=box
dvm=DataValidation(type="whole",operator="between",formula1="1",formula2="12"); ds.add_data_validation(dvm); dvm.add("C4")
ds["D4"]=f'=INDEX({{"Gennaio","Febbraio","Marzo","Aprile","Maggio","Giugno","Luglio","Agosto","Settembre","Ottobre","Novembre","Dicembre"}},C4)'
ds["D4"].font=Font(name=F,size=10,bold=True,color=VERDE)
kpi=[("Entrate del mese",t),("Uscite del mese",t+1),("Saldo del mese",t+2)]
for j,(l,rr) in enumerate(kpi):
    ds.cell(6+j,2,l).font=bold
    c=ds.cell(6+j,3,f"=INDEX(Riepilogo!$C${rr}:$N${rr},$C$4)"); c.number_format=EUR; c.font=Font(name=F,size=12,bold=True); c.border=box
ds["B9"]="Saldo da inizio anno"; ds["B9"].font=bold
ds["C9"]=f"=Riepilogo!O{t+2}"; ds["C9"].number_format=EUR; ds["C9"].font=Font(name=F,size=12,bold=True); ds["C9"].border=box
head(ds,11,["Spesa per categoria","Budget","Speso","Differenza","% usato"],2)
uscite=[i for i,(n,tp,b) in enumerate(cats) if tp=="Uscita"]
r0=12
for j,i in enumerate(uscite):
    r=r0+j; src=i+2
    ds.cell(r,2,f"=Riepilogo!A{src}").font=base
    ds.cell(r,3,f"=Riepilogo!B{src}")
    ds.cell(r,4,f"=INDEX(Riepilogo!$C${src}:$N${src},$C$4)")
    ds.cell(r,5,f"=C{r}-D{r}")
    ds.cell(r,6,f'=IF(C{r}=0,"",D{r}/C{r})')
    for k in (3,4,5): ds.cell(r,k).number_format=EUR
    ds.cell(r,6).number_format="0%"
    for k in range(2,7): ds.cell(r,k).border=box; ds.cell(r,k).font=base
rl=r0+len(uscite)-1
ds.conditional_formatting.add(f"E{r0}:E{rl}",CellIsRule(operator="lessThan",formula=["0"],font=Font(color="C0392B",bold=True)))
ds.conditional_formatting.add(f"F{r0}:F{rl}",DataBarRule(start_type="num",start_value=0,end_type="num",end_value=1,color="6FA287"))
ch=BarChart(); ch.type="bar"; ch.title="Budget vs speso nel mese"; ch.height=11; ch.width=18
ch.add_data(Reference(ds,min_col=3,max_col=4,min_row=11,max_row=rl),titles_from_data=True)
ch.set_categories(Reference(ds,min_col=2,min_row=r0,max_row=rl))
ch.roundedCorners=False; ch.legend.overlay=False; ch.x_axis.delete=False; ch.y_axis.delete=False; ch.title.overlay=False
ds.add_chart(ch,"H4")
for wsx in wb.worksheets: wsx.sheet_properties.tabColor=VERDE
wb.move_sheet("Cruscotto",offset=-3)
wb.save("prodotti/Budget_Familiare_2027.xlsx")
