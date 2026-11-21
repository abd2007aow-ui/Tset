import re,sys,html
src=open(sys.argv[1],encoding='utf-8').read()
AR='٠١٢٣٤٥٦٧٨٩'
def ar(n): return ''.join(AR[int(c)] for c in str(n))
def inline(t):
    t=html.escape(t,quote=False)
    t=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',t)
    t=re.sub(r'(﴿[^﴾]*﴾)',r'<span class="q">\1</span>',t)
    t=re.sub(r'«([^»]*)»',r'<span class="g">«\1»</span>',t)
    return t
# split sections
parts=re.split(r'^## ',src,flags=re.M)[1:]
secs=[]
for p in parts:
    lines=p.strip('\n').split('\n'); title=lines[0]
    m=re.match(r'المشهد (\d+) — (.*)',title)
    body=[l for l in lines[1:] if l.strip() and l.strip()!='---']
    secs.append((int(m.group(1)),m.group(2),body))
STAR='''<svg viewBox="0 0 100 100" class="star"><g fill="none" stroke="currentColor" stroke-width="2.2"><rect x="18" y="18" width="64" height="64"/><rect x="18" y="18" width="64" height="64" transform="rotate(45 50 50)"/><circle cx="50" cy="50" r="22"/></g></svg>'''
def blocks(n,body):
    out=[];lst=None;items=[]
    def flush():
        nonlocal lst,items
        if not lst: return
        if n==5: out.append('<div class="hadiths">'+''.join(f'<div class="hadith">{inline(i)}</div>' for i in items)+'</div>')
        elif n==8: out.append('<div class="pair">'+''.join(f'<div class="pcard {"r" if k==0 else "n"}">{inline(i)}</div>' for k,i in enumerate(items))+'</div>')
        elif n==15: out.append('<ol class="final">'+''.join(f'<li><span class="num">{ar(k+1)}</span><span>{inline(i)}</span></li>' for k,i in enumerate(items))+'</ol>')
        else:
            cls='cards'
            out.append(f'<div class="{cls}">'+''.join(f'<div class="card"><span class="num">{ar(k+1)}</span><div>{inline(i)}</div></div>' for k,i in enumerate(items))+'</div>')
        lst=None;items=[]
    for l in body:
        m=re.match(r'^(- |\d+\. )(.*)',l)
        if m: lst=lst or 'x'; items.append(m.group(2)); continue
        flush()
        out.append(f'<p>{inline(l)}</p>')
    flush()
    if n==8:
        out.insert(1,'')
    if n==10:
        out.append('''<div class="summary"><div class="sumhead">بطاقة الفرق</div>
<div class="srow"><div class="slabel">النبوة</div><ul><li>اصطفاء إلهي لا اكتساب</li><li>مقام علم ودعوة وقيادة</li><li>يجوز عليه ما يجوز على الإنسان</li><li>له حق الاجتهاد</li><li>عصمته إرادية</li></ul></div>
<div class="srow"><div class="slabel">الرسالة</div><ul><li>تكليف بإيصال رسالة الله كما هي</li><li>ليس فيها إلا التلاوة والتبليغ</li><li>لا اجتهاد في نص الرسالة</li><li>معصوم في حفظها ونطقها، ومن القتل حتى يتمها</li></ul></div></div>''')
    return ''.join(out)
def first(h):
    i=h.find('</p>')
    return h[:i+4]+'</div>'+h[i+4:] if h.startswith('<p>') else '</div>'+h
hook=secs[0]
sections=''
for n,t,b in secs[1:]:
    if n==15: continue
    sections+=f'<section class="sec"><div class="keep"><header><div class="badge">{STAR}<span>{ar(n)}</span></div><h2>{html.escape(t)}</h2></header><div class="orn">۞</div>{first(blocks(n,b))}</section>'
n,t,b=secs[-1]
final=f'<section class="sec end"><div class="keep"><header><div class="badge">{STAR}<span>{ar(n)}</span></div><h2>{html.escape(t)}</h2></header><div class="orn">۞</div>{first(blocks(n,b))}</section>'
toc=''.join(f'<li><span>{ar(n)}</span>{html.escape(t)}</li>' for n,t,b in secs[1:])
PAT='''<svg class="pat" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%"><defs><pattern id="p" width="80" height="80" patternUnits="userSpaceOnUse"><g fill="none" stroke="#c9a45c" stroke-width="1" opacity=".55"><rect x="20" y="20" width="40" height="40"/><rect x="20" y="20" width="40" height="40" transform="rotate(45 40 40)"/><circle cx="40" cy="40" r="12"/><path d="M0 0L20 20M80 0L60 20M0 80L20 60M80 80L60 60"/></g></pattern></defs><rect width="100%" height="100%" fill="url(#p)"/></svg>'''
doc=f'''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>النبوة والرسالة</title>
<link href="https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Amiri+Quran&family=Noto+Naskh+Arabic:wght@400;600;700&family=Reem+Kufi:wght@500;700&display=swap" rel="stylesheet">
<style>
:root{{--ink:#2b2a26;--green:#14463a;--green2:#1f5a49;--gold:#b48a3c;--gold2:#d8bd7e;--paper:#ffffff;--soft:#f3ecdc}}
@page{{size:A4;margin:20mm 18mm 20mm 18mm}}
@page cover{{margin:0}}
html{{background:var(--paper)}}
body{{margin:0;font-family:"Noto Naskh Arabic",serif;font-size:12.6pt;line-height:2.05;color:var(--ink)}}
b{{color:var(--green);font-weight:700}}
.q{{font-family:"Amiri Quran","Amiri",serif;color:var(--green2);font-size:1.12em;line-height:2.3}}
.g{{color:#7a5a22}}
/* cover */
.cover{{page:cover;height:297mm;width:210mm;position:relative;background:radial-gradient(ellipse at 50% 40%,#1d5a4a 0%,#123c32 55%,#0b2a23 100%);color:#f4ead2;overflow:hidden;break-after:page}}
.cover .pat{{position:absolute;inset:0}}
.frame{{position:absolute;inset:14mm;border:1.5px solid var(--gold2);outline:1px solid rgba(216,189,126,.45);outline-offset:-6px}}
.ctext{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 30mm}}
.medal{{width:190px;height:190px;border-radius:50%;background:radial-gradient(circle,#123c32 60%,#0e3129);border:2px solid var(--gold2);display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 8px rgba(18,60,50,.9),0 0 0 9.5px var(--gold2);margin-bottom:34px}}
.medal span{{font-family:"Reem Kufi";font-size:30pt;color:var(--gold2)}}
.cover h1{{font-family:Amiri;font-weight:700;font-size:50pt;margin:0;line-height:1.4;color:#f8edd2}}
.cover .sub{{font-family:Amiri;font-size:22pt;color:var(--gold2);margin-top:4px}}
.rule{{width:120px;height:1px;background:var(--gold2);margin:26px auto;position:relative}}
.rule:after{{content:"◆";position:absolute;top:-11px;left:50%;transform:translateX(-50%);color:var(--gold2);font-size:12px;background:#15463a;padding:0 8px}}
.cover .src{{font-size:12pt;color:#e6d9b8;line-height:1.9}}
.cover .src b{{color:#f8edd2}}
/* intro */
.intro{{break-after:page;padding-top:30mm;text-align:center}}
.intro .bism{{font-family:"Amiri Quran",Amiri;font-size:24pt;color:var(--green)}}
.intro .qs{{margin:22mm 0 10mm;font-family:Amiri;font-size:20pt;line-height:2;color:var(--green)}}
.intro .qs p{{margin:0 0 6mm}}
.intro .lead{{font-size:13.5pt;max-width:140mm;margin:0 auto;color:#4a463d}}
.toc{{list-style:none;padding:0;margin:16mm auto 0;max-width:130mm;columns:2;column-gap:10mm;text-align:right;font-size:11pt;line-height:2.1}}
.toc li span{{display:inline-block;width:22px;color:var(--gold);font-family:"Reem Kufi"}}
.tochead{{font-family:"Reem Kufi";color:var(--gold);letter-spacing:1px;margin-top:14mm;font-size:12pt}}
/* sections */
.sec{{margin:0 0 12mm}}
.keep{{break-inside:avoid}}
.sec header{{display:flex;align-items:center;gap:14px;break-after:avoid;margin-bottom:2px}}
.badge{{position:relative;width:54px;height:54px;color:var(--gold);flex:none}}
.badge .star{{position:absolute;inset:0}}
.badge span{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-family:"Reem Kufi";font-weight:700;font-size:15pt;color:var(--green)}}
h2{{font-family:Amiri;font-weight:700;font-size:21pt;color:var(--green);margin:0;line-height:1.4}}
.orn{{color:var(--gold2);text-align:center;font-size:12pt;margin:2px 0 6px;letter-spacing:6px;break-after:avoid}}
.orn:before,.orn:after{{content:"";display:inline-block;width:38%;height:1px;background:linear-gradient(to left,transparent,var(--gold2));vertical-align:middle;margin:0 10px}}
.orn:after{{background:linear-gradient(to right,transparent,var(--gold2))}}
p{{margin:0 0 9px;text-align:justify;orphans:3;widows:3}}
.hadiths{{margin:8px 0 12px;display:grid;gap:8px}}
.hadith{{background:var(--soft);border-right:3px solid var(--gold);padding:8px 14px;border-radius:2px 0 0 2px;break-inside:avoid;font-size:12.2pt}}
.pair{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:8px 0 14px}}
.pcard{{border:1px solid var(--gold2);background:#fffdf7;padding:12px 14px;break-inside:avoid;position:relative;border-top:4px solid var(--green)}}
.pcard.n{{border-top-color:var(--gold)}}
.cards{{display:grid;gap:8px;margin:8px 0 12px}}
.card{{display:flex;gap:12px;align-items:flex-start;background:#fffdf7;border:1px solid #e6dbc2;padding:10px 14px;break-inside:avoid}}
.num{{flex:none;width:28px;height:28px;border-radius:50%;background:var(--green);color:#f4ead2;font-family:"Reem Kufi";display:flex;align-items:center;justify-content:center;font-size:11pt;margin-top:6px}}
.summary{{margin:12px 0 6px;border:1.5px solid var(--gold);background:linear-gradient(#fffdf7,#f7f0e0);padding:4px 16px 12px;break-inside:avoid}}
.sumhead{{font-family:"Reem Kufi";color:var(--gold);text-align:center;font-size:13pt;margin:6px 0 4px;letter-spacing:1px}}
.srow{{display:flex;gap:14px;align-items:flex-start;border-top:1px dashed var(--gold2);padding-top:8px;margin-top:6px}}
.slabel{{flex:none;width:70px;font-family:Amiri;font-weight:700;font-size:16pt;color:var(--green)}}
.srow ul{{margin:0;padding:0 18px 0 0;font-size:11.8pt;line-height:1.9}}
.end{{break-before:page}}
.final{{list-style:none;padding:0;margin:10px 0 14px;display:grid;gap:9px}}
.final li{{display:flex;gap:12px;align-items:center;background:var(--green);color:#f4ead2;padding:10px 16px;font-family:Amiri;font-size:15pt;break-inside:avoid}}
.final .num{{background:var(--gold2);color:var(--green);margin:0}}
.next{{margin-top:14mm;text-align:center;border:1.5px solid var(--gold2);padding:10mm 8mm;position:relative;background:#fffdf7;break-inside:avoid}}
.next small{{display:block;font-family:"Reem Kufi";color:var(--gold);letter-spacing:1px}}
.next div{{font-family:Amiri;font-weight:700;font-size:26pt;color:var(--green)}}
.colophon{{text-align:center;color:#8a8170;font-size:9.5pt;margin-top:8mm;line-height:1.8}}
</style></head><body>
<div class="cover">{PAT}<div class="frame"></div><div class="ctext">
<div class="medal"><svg viewBox="0 0 100 100" width="120" height="120"><g fill="none" stroke="#d8bd7e" stroke-width="1.6"><rect x="22" y="22" width="56" height="56"/><rect x="22" y="22" width="56" height="56" transform="rotate(45 50 50)"/><circle cx="50" cy="50" r="17"/><circle cx="50" cy="50" r="8" fill="#d8bd7e"/></g></svg></div>
<h1>النبوة والرسالة</h1><div class="sub">الفرق الذي غاب عنا</div><div class="rule"></div>
<div class="src">قراءة في كتاب<br><b>«إشكالية التعامل مع السنة النبوية»</b><br>للدكتور طه جابر العلواني</div></div></div>
<div class="intro"><div class="bism">بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ</div>
<div class="qs">{''.join(f'<p>{inline(l)}</p>' for l in hook[2][:1])}</div>
<div class="lead">{inline(hook[2][1])}</div>
<div class="tochead">محتوى الحلقة</div><ul class="toc">{toc}</ul></div>
{sections}{final}
<div class="next"><small>الحلقة القادمة</small><div>الأنبياء في القرآن</div></div>
<div class="colophon">المصدر: طه جابر العلواني، «إشكالية التعامل مع السنة النبوية»، الفصل الأول، أولاً: النبوة والرسالة، ص ١٩–٣٤</div>
</body></html>'''
open(sys.argv[2],'w',encoding='utf-8').write(doc)
