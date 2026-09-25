from pathlib import Path
import requests, json
ROOT=Path(__file__).resolve().parent
# Reuse the established template and visual primitives without building v1.
exec((ROOT/'build_deck.py').read_text().split('# 01 —')[0],globals())

for name,num in [('farmer.jpg','29912210'),('flood.jpg','25189241')]:
    if not (A/name).exists():
        r=requests.get(f'https://images.pexels.com/photos/{num}/pexels-photo-{num}.jpeg?auto=compress&cs=tinysrgb&w=1800',timeout=45)
        r.raise_for_status();(A/name).write_bytes(r.content)

def flow(s,x1,y1,x2,y2,col=TE,end=True):
    sh=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x1),Inches(y1),Inches(x2),Inches(y2))
    sh.line.color.rgb=RGBColor.from_string(col);sh.line.width=Pt(1.65)
    if end:
        e=OxmlElement('a:tailEnd');e.set('type','triangle');sh._element.spPr.get_or_add_ln().append(e)

def box(s,title,body,x,y,w,h,col=WH,size=14):
    rect(s,x,y,w,h,col,True,line=LINE if col==WH else None)
    textcol=WH if col==N else N
    txt(s,title,x+.13,y+.12,w-.26,.31,size,textcol,True,align=PP_ALIGN.CENTER)
    if body:txt(s,body,x+.13,y+.48,w-.26,h-.53,11.7,'D2DFE0' if col==N else MUT,align=PP_ALIGN.CENTER)

def credit(s,text):txt(s,text,.52,6.73,12.2,.17,8.2,MUT)

# 01: use the original template artwork and the Idea_3 content order/layout.
s=prs.slides[0]
for sh in list(s.shapes):
    if sh.has_text_frame:
        sh._element.getparent().remove(sh._element)
    elif sh.shape_type==13 and sh.left>Inches(10):
        sh._element.getparent().remove(sh._element)
image_fit(s,A/'template_2.png',10.72,.02,2.42,1.12)
txt(s,'SMART INDIA HACKATHON 2026',.44,.27,10.18,.65,32,'244E78',True,font='Liberation Serif')
txt(s,'PRAHARI — The Countdown Band',1.9,1.38,9.0,.49,27,'BB531D',True,align=PP_ALIGN.CENTER)
txt(s,'Warns before the emergency — the flood, cyclone or heatwave coming at you,\nand the heat strain building inside you — and reaches workers no tower reaches.',.59,1.98,6.48,.72,13,MUT)
txt(s,'•   Problem Statement ID  –  26181',.45,2.98,6.7,.4,17,N,True)
txt(s,'•',.45,3.51,.23,.3,15,N)
ps='Problem Statement Title  –  A secure, AI-powered Personal Health Companion that delivers real-time, privacy-preserving health monitoring and early warning capabilities, helping individuals recognize health risks before they become emergencies. The solution should improve resilience during heat waves, floods, pollution events, and other disasters common in India while enabling continuous health support through on-device intelligence.'
txt(s,ps,.79,3.49,5.62,1.49,12.5,N)
for y,t in [(5.16,'•   Theme  –  MedTech / BioTech / HealthTech'),(5.70,'•   PS Category  –  Hardware'),(6.24,'•   Team ID  –  <your team id>'),(6.78,'•   Team Name  –  Point Break')]:txt(s,t,.45,y,7.1,.39,17,N,True)
note(s,'Title slide follows PRAHARI_SIH2026_Idea_3.pdf: original SIH artwork, title and tagline, then PS ID, full PS title, theme, hardware category, Team ID and Point Break. Team ID is still absent from supplied materials. The tagline describes intended coverage, not a demonstrated radio range. New official alerts need at least one connected entry point.')

# 02: expanded solution with two real contextual photographs.
s=prs.slides[1];base(s,2,'IDEA TITLE')
txt(s,'PRAHARI: two warnings, one system.',.5,1.32,12.1,.46,29,N,True)
txt(s,'Proposed solution  /  Personal heat-strain awareness + official multi-hazard early warning',.5,1.86,12.1,.26,14,MUT)
for x,img,title,body in [(.5,'flood.jpg','THE HAZARD OUTSIDE','Flood, cyclone, heatwave and lightning alerts can fail to reach the last mile.'),(6.81,'farmer.jpg','THE STRAIN INSIDE','Heat exposure and incomplete recovery differ from one worker to the next.')]:
    photo(s,A/img,x,2.29,1.90,1.41)
    txt(s,title,x+2.08,2.34,3.9,.31,16,TE,True)
    txt(s,body,x+2.08,2.81,3.88,.80,15,N)
rect(s,.5,3.94,6.01,1.41,N,True);rect(s,6.81,3.94,6.01,1.41,N,True)
txt(s,'01  THE BAND',.71,4.10,5.57,.29,17,AM,True)
txt(s,'• Heart rate, skin temperature, ambient heat and motion\n• Local risk trend, OLED status and distinct haptic patterns\n• LoRa peer relaying extends alerts beyond the gateway',.71,4.51,5.58,.73,13.6,WH)
txt(s,'02  THE COMPANION APP',7.03,4.10,5.57,.29,17,AM,True)
txt(s,'• Fetches official NDMA SACHET CAP alerts when online\n• Sends relevant alerts by BLE to a LoRa gateway band\n• Keeps offline history and recovery records on the phone',7.03,4.51,5.55,.73,13.6,WH)
txt(s,'INNOVATION & UNIQUENESS',.52,5.61,6,.23,11,TE,True)
for x,t,b in [(.52,'Personal countdown*','Estimate time to a heat-risk threshold\nonly when signal quality permits.'),(4.77,'Thermal debt ledger*','Carry cumulative strain and recovery\nacross shifts and overnight.'),(9.0,'Two warnings, one wrist','Separate hazard and strain patterns;\nlocal reception needs no personal phone.')]:
    txt(s,t,x,5.96,3.85,.31,17,N,True);txt(s,b,x,6.35,3.86,.36,11.4,MUT)
credit(s,'*Proposed, to validate. Photos: Dibakar Roy (Kolkata flood); Abhishek Gupta (Indian farmer) / Pexels. Context images, not trials.')
note(s,'The personal countdown is a research feature: estimate time to a chosen risk threshold, not guaranteed minutes until collapse. Thermal debt means tracking accumulated strain and recovery rather than resetting the story each shift. A phone is not a LoRa radio: it uses BLE to a gateway band. Body monitoring is intended to work offline; new CAP alerts need connected ingress. Photos: https://www.pexels.com/photo/flood-on-street-in-city-in-india-25189241/ by Dibakar Roy; https://www.pexels.com/photo/indian-farmer-working-in-a-field-during-summer-29912210/ by Abhishek Gupta. Pexels License. Architecture and features are proposed except documented sensor/OLED bench work.')

# 03: actual editable system architecture flowchart, with directed edges.
s=prs.slides[2];base(s,3,'TECHNICAL APPROACH')
txt(s,'System architecture  /  two inputs, one wrist.',.5,1.30,12.3,.5,28,N,True)
txt(s,'Proposed end-to-end flow · body processing stays local; official alerts enter through a connected gateway',.5,1.85,12.2,.3,13,MUT)
txt(s,'A  /  PERSONAL HEAT-STRAIN PATH',.51,2.23,8.5,.25,11,TE,True)
box(s,'SENSOR INPUTS','MAX30102 · heart rate\nMAX30208 · skin temp\nAHT20 · air temp / RH\nIMU · motion',.5,2.65,2.34,1.59,size=14)
box(s,'XIAO nRF52840','Filter + sample signals\nCalculate signal quality\nC/C++ on the band',3.23,2.65,2.39,1.59,N,14)
sh=s.shapes.add_shape(MSO_SHAPE.DIAMOND,Inches(6.0),Inches(2.81),Inches(1.51),Inches(1.23));sh.fill.solid();sh.fill.fore_color.rgb=RGBColor.from_string(PALE);sh.line.color.rgb=RGBColor.from_string(TE)
for ref in sh._element.xpath('.//a:effectRef'):ref.set('idx','0')
txt(s,'Usable\nsignal?',6.19,3.13,1.13,.58,13,N,True,align=PP_ALIGN.CENTER)
box(s,'ESTIMATE + FORECAST','Kalman + personal baseline\nTrend to threshold*\nRecovery ledger*',7.91,2.65,2.48,1.59,N,13)
box(s,'LOCAL WARNING','OLED risk / time*\nStrain vibration\nPrompt to take action',10.79,2.65,2.04,1.59,size=13)
for a,b in [(2.84,3.23),(5.62,6.0),(7.51,7.91),(10.39,10.79)]:flow(s,a,3.43,b,3.43)
txt(s,'YES',7.51,3.06,.40,.20,9,TE,True)
flow(s,6.75,4.04,6.75,4.41)
box(s,'Estimate unavailable · refit / resample','',5.12,4.42,3.8,.50,PALE,11)
txt(s,'NO',6.92,4.13,.37,.2,9,MUT,True)
txt(s,'B  /  OFFICIAL HAZARD-ALERT PATH',.51,4.67,4.50,.25,11,TE,True)
for x,t,b,w in [(.5,'NDMA SACHET','Official CAP / RSS alerts',2.0),(2.90,'PHONE APP','Fetch · location · expiry',2.18),(5.49,'GATEWAY BAND','BLE in → SX1262 LoRa',2.18),(8.08,'PEER BANDS','Deduplicate · hop limit',2.18),(10.67,'HAZARD WARNING','Distinct wrist vibration',2.16)]:box(s,t,b,x,5.12,w,.92,size=12)
for a,b in [(2.50,2.90),(5.08,5.49),(7.67,8.08),(10.26,10.67)]:flow(s,a,5.59,b,5.59)
rect(s,.5,6.30,12.33,.32,PALE,True)
txt(s,'PLANNED STACK  C/C++ · Kalman / TinyML evaluation · Flutter + local storage · protected keys · raw physiology kept local',.66,6.38,12.0,.21,10.3,TE,True)
credit(s,'*Validation required. Low-quality data must not imply safety. New CAP alerts need connected ingress. Air temp + RH alone are not full WBGT.')
note(s,'Architecture is an editable flowchart. The body branch routes unusable signals to estimate-unavailable / refit / resample; that is not a safe classification. A valid estimate drives a local strain alert. The external branch preserves issuer, location, timestamp and expiry checks, then sends via BLE to a LoRa-equipped gateway and peers. Payload deduplication and hop limits are proposed to reduce repeated flooding. Official alerts do not depend on physiological signal quality. Full radio protocol, forecasting, app and secure-key integration are not yet demonstrated. References and evidence are on slide 6.')

# 04: more concrete implementation content + real component image.
s=prs.slides[3];base(s,4,'FEASIBILITY AND VIABILITY')
txt(s,'From a working sensing core to a supervised pilot.',.5,1.31,12.3,.49,28,N,True)
image_fit(s,A/'xiao_sense.png',.54,2.05,1.52,1.25)
txt(s,'COMPACT, MODULAR HARDWARE',2.23,2.10,3.65,.27,13,TE,True)
txt(s,'XIAO + sensor modules\nTwo-layer rev B carrier PCB\nLiPo protection + haptic output',2.23,2.52,3.65,.78,15,N)
rect(s,.5,3.49,5.43,1.46,N,True)
txt(s,'VERIFIED',.71,3.67,1.80,.24,11,AM,True)
txt(s,'Live PPG / heart rate, OLED and I²C diagnostics.',.71,4.00,4.98,.32,15,WH)
txt(s,'IN PROGRESS',.71,4.42,1.80,.24,11,AM,True)
txt(s,'Radio bring-up; PCB checks; app + forecast integration.',2.25,4.40,3.38,.42,12,WH)
txt(s,'CHALLENGES → MITIGATION',6.27,2.07,6.56,.27,13,TE,True)
for j,(t,b) in enumerate([('Motion / uncertainty','Quality gating + reference-device testing; no false reassurance.'),('Radio outages / old alerts','Expiry, deduplication and hop limits; measure delivery and range.'),('Battery / fit / robustness','Duty-cycle sensing and radio; test comfort, sweat and shift use.'),('Data protection','Keep physiology local; validate access control and key handling.')]):
    y=2.53+j*.64
    txt(s,t,6.28,y,2.29,.45,13.7,N,True);txt(s,b,8.69,y,4.12,.48,12.6,MUT)
    rule(s,6.28,y+.54,6.53)
txt(s,'ECONOMIC & OPERATIONAL VIABILITY',.52,5.23,6.0,.26,12,TE,True)
txt(s,'Off-the-shelf parts simplify repair and sourcing. Quote the full rev B assembly, enclosure and battery before setting a device price.',.52,5.61,5.36,.73,14,N)
txt(s,'IMPLEMENTATION GATES',6.27,5.23,6.0,.26,12,TE,True)
for x,n,t in [(6.28,'01','Close hardware\nand radio issues'),(8.55,'02','Validate sensing,\nrelay and power'),(10.84,'03','Supervised pilot\nand user feedback')]:
    txt(s,n,x,5.63,.49,.36,21,TE,True);txt(s,t,x+.59,5.64,1.54,.64,12.8,N)
credit(s,'Photo: Seeed Studio, actual XIAO module. Bench results do not establish clinical accuracy or field readiness; full-device cost remains to be quoted.')
note(s,'Documented bench evidence is sensor/OLED operation, not a completed countdown or radio mesh. Latest project notes identify unresolved SPI radio bring-up and PCB check failures; older PCB README clean results refer to another state. Rev B carrier is 70 x 40 mm. Its specified protection circuit and haptic driver are design choices, not validated enclosure safety. The older ₹3,468 estimate only covers selected rev A modules. The implementation sequence is proposed; no unsupported 12-week guarantee. Manufacturer component image from https://wiki.seeedstudio.com/XIAO_BLE/.')

# 05: photo-rich beneficiary strip and expanded impact dimensions.
s=prs.slides[4];base(s,5,'IMPACT AND BENEFITS')
txt(s,'Put the warning where action can start.',.5,1.31,12.3,.49,29,N,True)
for x,img,t in [(.5,'workers_mumbai.jpg','OUTDOOR WORK CREWS'),(4.71,'farmer.jpg','FARMING COMMUNITIES'),(8.92,'flood.jpg','DISASTER-EXPOSED AREAS')]:
    photo(s,A/img,x,2.01,3.9,1.45);rect(s,x,3.16,3.9,.30,N);txt(s,t,x+.12,3.24,3.66,.20,10,WH,True)
txt(s,'57%',.51,3.76,1.76,.78,44,TE,True)
txt(s,'of Indian districts at high to very high heat risk\nCEEW, 2025 [1]',2.43,3.88,9.7,.57,18,N,True)
for x,t,b in [(.52,'SOCIAL','Distinct haptics support simple warnings.\nNo personal phone needed for reception.\nLocal crews can act on shared alerts.'),(4.74,'ECONOMIC','Timely rest prompts aim to reduce disruption.\nCrew deployment can share gateway access.\nMeasure time to action before claiming savings.'),(8.95,'SYSTEMIC & ENVIRONMENTAL','Extend official alerts into local peer networks.\nRechargeable, modular design aims for repair.\nValidate durability and lifetime in the pilot.')]:
    rule(s,x,4.73,3.86);txt(s,t,x,4.94,3.86,.28,13,TE,True);txt(s,b,x,5.37,3.83,.92,12.4,N)
rect(s,.5,6.36,12.33,.28,PALE,True)
txt(s,'PILOT METRICS   Delivery time  •  Missed / false alerts  •  Time to action  •  Battery per shift  •  Comfort and comprehension',.65,6.42,12.04,.20,10.3,TE,True)
credit(s,'Real photographs: yajna S R; Abhishek Gupta; Dibakar Roy / Pexels. Intended benefits, not measured health or economic outcomes.')
note(s,'CEEW source: https://www.ceew.in/publications/mapping-climate-risks-and-impacts-of-extreme-heatwave-disaster-in-indian-districts . Benefits are intended. Community response requires training and an escalation protocol. Do not imply mortality reduction or quantified savings. Environmental intent is rechargeable, repairable deployment, not a lifecycle claim. Photos show context only and do not establish participation or endorsement. Credits/links in slide 6 notes.')

# 06: keep concise evidence rows, add explicit research questions and credits.
s=prs.slides[5];base(s,6,'RESEARCH AND REFERENCES')
txt(s,'Research foundations. Evidence. Next questions.',.5,1.31,12.3,.49,28,N,True)
refs=[('01','CEEW · Extreme heat in Indian districts (2025)','Heat-risk evidence and target-user context.','https://www.ceew.in/publications/mapping-climate-risks-and-impacts-of-extreme-heatwave-disaster-in-indian-districts'),('02','NDMA · SACHET CAP / RSS alerts','Official alert source for hazard dissemination.','https://sachet.ndma.gov.in/'),('03','Buller et al. · Wearable physiological estimation','Kalman-filter research; not PRAHARI validation.','https://ojs.aaai.org/index.php/AAAI/article/view/18809'),('04','Seeed Studio · XIAO nRF52840 documentation','MCU, BLE, Sense IMU and component image.','https://wiki.seeedstudio.com/XIAO_BLE/'),('05','PRAHARI · firmware, KiCad and project notes','Sensor/OLED work, BOM and bring-up evidence; private repo.','https://github.com/P-r-i-t-h-v-i/PRAHARI')]
for j,(n,t,b,u) in enumerate(refs):
    y=2.15+j*.77;txt(s,n,.53,y,.49,.39,21,TE,True);txt(s,t,1.20,y,7.04,.33,15,N,True,url=u);txt(s,b,1.20,y+.40,7.03,.26,12,MUT);rule(s,.53,y+.69,7.81)
rect(s,8.75,2.10,4.08,3.70,N,True)
txt(s,'WHAT THE PILOT MUST TEST',8.97,2.35,3.64,.5,15,AM,True)
txt(s,'01  Does the forecast stay useful\n      during movement and recovery?\n\n02  Do alerts arrive reliably across\n      the actual deployment terrain?\n\n03  Can users distinguish, trust\n      and act on the warning?',8.97,3.00,3.59,2.10,14,WH)
txt(s,'Obsidian brain + Idea_3 PDF\n+ project report informed this deck.',8.97,5.26,3.59,.45,11,'D2DFE0')
txt(s,'REAL IMAGE CREDITS · PEXELS LICENSE',.53,6.19,12.1,.24,11,TE,True)
txt(s,'yajna S R — Mumbai workers  |  Abhishek Gupta — Indian farmer  |  Dibakar Roy — Kolkata flood  |  Seeed Studio — XIAO',.53,6.51,12.22,.27,10.7,MUT)
note(s,'Images, all non-AI: https://www.pexels.com/photo/construction-workers-working-on-top-of-a-building-20591230/ (yajna S R); https://www.pexels.com/photo/indian-farmer-working-in-a-field-during-summer-29912210/ (Abhishek Gupta); https://www.pexels.com/photo/flood-on-street-in-city-in-india-25189241/ (Dibakar Roy); license https://www.pexels.com/license/ . XIAO component image: https://files.seeedstudio.com/wiki/XIAO-BLE/xiaonrf52840sence.png from Seeed Studio documentation. SIH artwork from supplied template. All stock photographs are contextual, not team prototype trials. Local inputs: Obsidian Projects/PRAHARI.md and linked topics, repository README/PCB README, PRAHARI_SIH2026_Idea_3.pdf, PRAHARI_Project_Report.pdf. Research findings are not achieved device results.')

prs.core_properties.title='PRAHARI — The Countdown Band | SIH 2026 | Revised'
prs.core_properties.author='Point Break'
prs.save(ROOT/'PRAHARI_SIH2026_v2.pptx')
issues=[]
for i,s in enumerate(prs.slides,1):
    for sh in s.shapes:
        if sh.left<0 or sh.top<0 or sh.left+sh.width>prs.slide_width+1000 or sh.top+sh.height>prs.slide_height+1000:issues.append((i,sh.name))
(ROOT/'v2_layout_check.json').write_text(json.dumps({'slides':len(prs.slides),'outside_slide':issues},indent=2))
assert len(prs.slides)==6 and not issues,issues
print('Saved',ROOT/'PRAHARI_SIH2026_v2.pptx')
