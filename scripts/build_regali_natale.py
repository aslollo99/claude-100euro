from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, FormulaRule, DataBarRule

F="Arial"; ROSSO="B3263A"; INPUT="FFF8DC"
hdr=Font(name=F,bold=True,color="FFFFFF",size=10); hfill=PatternFill("solid",fgColor=ROSSO)
base=Font(name=F,size=10); bold=Font(name=F,size=10,bold=True)
thin=Side(style="thin",color="D9C7CA"); box=Border(top=thin,bottom=thin,left=thin,right=thin)
EUR='#,##0.00 €;-#,##0.00 €;"-"'; inp=PatternFill("solid",fgColor=INPUT)
def head(ws,r,vals,c0=1):
    for i,v in enumerate(vals):
        c=ws.cell(r,c0+i,v); c.font=hdr; c.fill=hfill; c.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True); c.border=box

wb=Workbook()
ws=wb.active; ws.title="Istruzioni"; ws.sheet_view.showGridLines=False
ws.column_dimensions["B"].width=95
ws["B2"]="Planner Regali di Natale"; ws["B2"].font=Font(name=F,size=20,bold=True,color=ROSSO)
ws["B3"]="Chi, cosa, quanto: nessun regalo dimenticato e nessuna sorpresa sul conto."; ws["B3"].font=Font(name=F,size=11,italic=True,color="555555")
righe=["COME SI USA (3 passi)",
"1. Foglio «Budget»: scrivi quanto vuoi spendere in totale per i regali (cella gialla).",
"2. Foglio «Regali»: una riga per ogni persona. Inserisci idea, budget, prezzo reale, dove compri e lo stato (menu a tendina).",
"3. Foglio «Riepilogo»: vedi subito quanto hai speso, quanto resta e quanti regali mancano. Si aggiorna da solo.",
"",
"LEGENDA",
"Celle gialle = da compilare. Le altre celle contengono formule: meglio non modificarle.",
"Se spendi più del budget di una persona, la differenza diventa rossa.",
"La riga d'esempio nel foglio Regali si può cancellare.",
"",
"COMPATIBILITÀ",
"Funziona con Microsoft Excel, Google Fogli (File → Importa) e LibreOffice Calc.",
"",
"Buone feste! Se il modello ti è utile, una recensione aiuta un piccolo negozio."]
for i,t in enumerate(righe):
    c=ws.cell(5+i,2,t); c.font=bold if t.isupper() and t else base; c.alignment=Alignment(wrap_text=True)

bs=wb.create_sheet("Budget"); bs.sheet_view.showGridLines=False
bs.column_dimensions["A"].width=2; bs.column_dimensions["B"].width=44; bs.column_dimensions["C"].width=16
bs["B2"]="Budget regali"; bs["B2"].font=Font(name=F,size=16,bold=True,color=ROSSO)
bs["B4"]="Budget totale per i regali (€)"; bs["B4"].font=bold
bs["C4"]=300; bs["C4"].fill=inp; bs["C4"].number_format=EUR; bs["C4"].border=box; bs["C4"].font=bold
bs["B5"]="Altre spese natalizie (carta, biglietti…) (€)"; bs["B5"].font=bold
bs["C5"]=20; bs["C5"].fill=inp; bs["C5"].number_format=EUR; bs["C5"].border=box; bs["C5"].font=bold

N=40; R0=2; R1=R0+N-1
rg=wb.create_sheet("Regali"); rg.freeze_panes="B2"
for col,w in zip("ABCDEFGH",[22,30,14,14,14,22,16,28]): rg.column_dimensions[col].width=w
head(rg,1,["Per chi","Idea regalo","Budget (€)","Prezzo reale (€)","Differenza (€)","Dove comprarlo","Stato","Note"])
dv=DataValidation(type="list",formula1='"Da pensare,Idea scelta,Acquistato,Incartato,Consegnato"',allow_blank=True); rg.add_data_validation(dv); dv.add(f"G{R0}:G{R1}")
for r in range(R0,R1+1):
    for c in (1,2,3,4,6,7,8):
        x=rg.cell(r,c); x.fill=inp; x.border=box; x.font=base
    rg.cell(r,3).number_format=EUR; rg.cell(r,4).number_format=EUR
    e=rg.cell(r,5,f'=IF(OR(C{r}="",D{r}=""),"",C{r}-D{r})'); e.number_format=EUR; e.font=base; e.border=box
rg["A2"]="Mamma (esempio)"; rg["B2"]="Sciarpa di lana"; rg["C2"]=30; rg["D2"]=27.5; rg["F2"]="Negozio in centro"; rg["G2"]="Acquistato"
rg.conditional_formatting.add(f"E{R0}:E{R1}",CellIsRule(operator="lessThan",formula=["0"],font=Font(color="C0392B",bold=True)))
rg.conditional_formatting.add(f"G{R0}:G{R1}",FormulaRule(formula=[f'OR(G{R0}="Consegnato",G{R0}="Incartato")'],fill=PatternFill("solid",bgColor="D5EBDD")))

rs=wb.create_sheet("Riepilogo"); rs.sheet_view.showGridLines=False
rs.column_dimensions["A"].width=2; rs.column_dimensions["B"].width=40; rs.column_dimensions["C"].width=18
rs["B2"]="Riepilogo"; rs["B2"].font=Font(name=F,size=18,bold=True,color=ROSSO)
rng=lambda c:f"Regali!${c}${R0}:${c}${R1}"
items=[("Regali in lista",f'=COUNTA({rng("A")})',"0"),                      #4
("Budget assegnato alle persone",f'=SUM({rng("C")})',EUR),                   #5
("Speso finora",f'=SUM({rng("D")})',EUR),                                    #6
("Budget totale regali","=Budget!C4",EUR),                                   #7
("Ancora disponibile","=C7-C6",EUR),                                         #8
("% del budget usato",'=IF(C7=0,"",C6/C7)',"0%"),                            #9
("Budget assegnato oltre il totale",'=MAX(0,C5-C7)',EUR),                    #10
("Regali da pensare / scegliere",f'=COUNTIF({rng("G")},"Da pensare")+COUNTIF({rng("G")},"Idea scelta")',"0"),
("Regali acquistati",f'=COUNTIF({rng("G")},"Acquistato")',"0"),
("Regali incartati",f'=COUNTIF({rng("G")},"Incartato")',"0"),
("Regali consegnati",f'=COUNTIF({rng("G")},"Consegnato")',"0"),
("Spesa totale Natale (regali + extra)","=C6+Budget!C5",EUR)]
for i,(l,f,nf) in enumerate(items):
    r=4+i; rs.cell(r,2,l).font=bold
    c=rs.cell(r,3,f); c.number_format=nf; c.font=Font(name=F,size=11,bold=True); c.border=box
rs.conditional_formatting.add("C8",CellIsRule(operator="lessThan",formula=["0"],font=Font(color="C0392B",bold=True)))
rs.conditional_formatting.add("C9",DataBarRule(start_type="num",start_value=0,end_type="num",end_value=1,color="D1707D"))
for w in wb.worksheets: w.sheet_properties.tabColor=ROSSO
wb.move_sheet("Riepilogo",offset=-2)
wb.save("prodotti/Planner_Regali_Natale.xlsx")
