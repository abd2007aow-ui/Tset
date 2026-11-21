# -*- coding: utf-8 -*-
"""Builds the illustrated explainer «النبوة والرسالة» as HTML (then PDF via pdf2.js)."""
import re, sys, html

AR = '٠١٢٣٤٥٦٧٨٩'
def ar(n): return ''.join(AR[int(c)] for c in str(n))

def T(t):
    """inline formatting: **bold**, ﴿verse﴾, «quote»"""
    t = html.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(﴿[^﴾]*﴾)', r'<span class="q">\1</span>', t)
    t = re.sub(r'«([^»]*)»', r'<span class="g">«\1»</span>', t)
    return t

def P(*ps): return ''.join(f'<p>{T(p)}</p>' for p in ps)
def AYA(t, ref=''):
    r = f'<div class="ref">{ref}</div>' if ref else ''
    return f'<div class="aya">{T(t)}{r}</div>'
def BOX(kind, title, body):
    icons = {'idea': '💡', 'eg': '🔍', 'warn': '⚖️', 'key': '🗝️', 'sum': '📌'}
    return f'<div class="box {kind}"><div class="bt">{icons[kind]} {title}</div>{body}</div>'
def FIG(svg, cap=''):
    c = f'<figcaption>{cap}</figcaption>' if cap else ''
    return f'<figure>{svg}{c}</figure>'
def SEC(n, title, sub, body):
    first, rest = body[0], ''.join(body[1:])
    return (f'<section class="sec"><div class="keep"><div class="sh"><div class="sn">{ar(n)}</div>'
            f'<div><h2>{title}</h2><div class="sub">{sub}</div></div></div>{first}</div>{rest}</section>')

# ---------- tiny SVG helpers (RTL diagrams) ----------
C = dict(teal='#0f5a52', teal2='#e3f1ee', amber='#c7831f', amber2='#fbefd9', rose='#a64b3c', rose2='#f8e4df',
         ink='#25302e', grey='#8a948f', line='#c9d3cf', blue='#2f5d8a', blue2='#e2ebf5')

def svg(w, h, inner):
    return (f'<svg viewBox="0 0 {w} {h}" width="100%" xmlns="http://www.w3.org/2000/svg" direction="rtl">'
            '<defs><marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0 0L10 5L0 10z" fill="{C["grey"]}"/></marker></defs>{inner}</svg>')

def box(x, y, w, h, lines, fill, stroke, size=17, bold=False, color=None, r=12):
    if isinstance(lines, str): lines = [lines]
    color = color or C['ink']
    out = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
    lh = size * 1.45
    y0 = y + h / 2 - (len(lines) - 1) * lh / 2
    for i, l in enumerate(lines):
        fw = 'bold' if (bold and i == 0) else 'normal'
        fs = size if i == 0 else size * .82
        col = color if i == 0 else C['grey'] if not bold else color
        out += (f'<text x="{x + w/2}" y="{y0 + i*lh}" text-anchor="middle" dominant-baseline="middle" '
                f'font-size="{fs}" font-weight="{fw}" fill="{col}">{html.escape(l)}</text>')
    return out

def arrow(x1, y1, x2, y2, dash=False):
    d = ' stroke-dasharray="6 5"' if dash else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{C["grey"]}" stroke-width="2.2" marker-end="url(#ar)"{d}/>'

def text(x, y, t, size=15, color=None, weight='normal', anchor='middle'):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" dominant-baseline="middle" font-size="{size}" '
            f'font-weight="{weight}" fill="{color or C["ink"]}">{html.escape(t)}</text>')

def chain(items, w=760, bh=86, fills=None):
    """horizontal chain right→left"""
    n = len(items); gap = 34; bw = (w - gap * (n - 1)) / n
    out = ''
    for i, it in enumerate(items):
        x = w - (i + 1) * bw - i * gap
        f, s = (fills[i] if fills else (C['teal2'], C['teal']))
        out += box(x, 10, bw, bh, it, f, s, size=17, bold=True)
        if i < n - 1: out += arrow(x - 2, 10 + bh / 2, x - gap + 4, 10 + bh / 2)
    return svg(w, bh + 20, out)

# ---------- diagrams ----------
D_MAP = chain([['الإنسان', 'لماذا خُلق؟'], ['الحاجة', 'لماذا الأنبياء؟'], ['الكلمتان', 'نبي و رسول'],
               ['الفروق', 'الثلاثة'], ['النتيجة', 'كيف نفهم السنة']],
              fills=[(C['teal2'], C['teal']), (C['blue2'], C['blue']), (C['amber2'], C['amber']),
                     (C['rose2'], C['rose']), (C['teal'], C['teal'])])
D_MAP = D_MAP.replace(f'fill="{C["teal"]}" stroke="{C["teal"]}" stroke-width="2"/><text', f'fill="{C["teal"]}" stroke="{C["teal"]}" stroke-width="2"/><text style="fill:#fff"', 1)

D_HUMAN = chain([['اصطفاء', 'اختاره الله'], ['استخلاف', 'جعله خليفة'], ['أمانة', 'حمل ما أبت الجبال'],
                 ['عمران', 'يبني الأرض']],
                fills=[(C['amber2'], C['amber'])] * 4)

def d_stairs():
    steps = [('العقل الحسّي', 'يرى الشمس قوة فيعبدها'), ('عاجز وحده', 'لا يصل من الخلق للخالق'),
             ('عدوّ يتربّص', 'الشيطان يزيّن ويُغوي'), ('رحمة الله', 'إرسال الأنبياء')]
    out = ''
    for i, (a, b) in enumerate(steps):
        x = 760 - (i + 1) * 180 - i * 8; y = 190 - i * 50
        last = i == 3
        out += box(x, y, 180, 100 + i * 50 - i * 50 + 60 if False else 70, [a, b],
                   C['teal'] if last else C['teal2'], C['teal'], size=16, bold=True,
                   color='#fff' if last else None)
        if last:
            out = out.replace(f'fill="{C["grey"]}">{html.escape(b)}', f'fill="#d9efe9">{html.escape(b)}')
        if i < 3: out += arrow(x + 4, y + 10, x - 4, y - 20)
    return svg(760, 270, out)
D_STAIRS = d_stairs()

def d_two():
    out = ''
    out += box(400, 10, 360, 64, ['موكب النبوات', 'يقود إلى الاستقامة والسجود'], C['teal2'], C['teal'], 18, True)
    out += box(0, 10, 360, 64, ['موكب إبليس وجنوده', 'يدفع إلى الانحراف'], C['rose2'], C['rose'], 18, True)
    for i, t in enumerate(['نوح', 'إبراهيم', 'موسى', 'عيسى', 'محمد ﷺ']):
        out += f'<circle cx="{730 - i*72}" cy="118" r="26" fill="#fff" stroke="{C["teal"]}" stroke-width="2"/>'
        out += text(730 - i * 72, 119, t, 12.5, C['teal'], 'bold')
    out += arrow(760, 160, 410, 160)
    out += text(585, 182, 'أمة واحدة، دعوة واحدة', 14, C['teal'])
    for i in range(5):
        out += f'<circle cx="{40 + i*70}" cy="118" r="20" fill="{C["rose2"]}" stroke="{C["rose"]}" stroke-width="1.5" stroke-dasharray="4 3"/>'
    out += arrow(0, 160, 350, 160, dash=True)
    out += text(175, 182, 'يحتال الناس عن السجود', 14, C['rose'])
    return svg(760, 200, out)
D_TWO = d_two()

def d_cycle():
    import math
    cx, cy, R = 380, 165, 125
    pts = [('يعارضونه', 'وهو حيّ', 0), ('يموت', '', 90), ('يقدّسون قبره', '', 180), ('يتخذونه إلهاً', '', 270)]
    out = f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{C["rose2"]}" stroke-width="16"/>'
    for ang in (45, 135, 225, 315):
        t = math.radians(ang - 90); out += text(cx + R*math.cos(t), cy + R*math.sin(t) + 1, '◄', 14, C['rose'])
    for a, b, ang in pts:
        t = math.radians(ang - 90); x = cx + R*math.cos(t); y = cy + R*math.sin(t)
        out += box(x - 66, y - 26, 132, 52, [a, b] if b else [a], '#fff', C['rose'], 15, True)
    out += text(cx, cy - 12, 'ما وقع', 15, C['rose'], 'bold')
    out += text(cx, cy + 14, 'للأمم السابقة', 15, C['rose'], 'bold')
    out += box(400, 330, 340, 64, ['السبب', 'ضاعت الفروق الدقيقة'], C['amber2'], C['amber'], 16, True)
    out += box(20, 330, 340, 64, ['النتيجة', 'الهداية تصير ضلالاً'], C['rose2'], C['rose'], 16, True)
    return svg(760, 400, out)
D_CYCLE = d_cycle()

def d_root():
    out = box(290, 8, 180, 64, ['نَبِيّ'], C['amber'], C['amber'], 28, True, '#fff')
    out += f'<path d="M380 72 V100 H190 V122 M380 100 H570 V122" fill="none" stroke="{C["grey"]}" stroke-width="2"/>'
    out += box(430, 122, 300, 110, ['من النَّبَأ', 'الخبر المهم', 'فهو من أنبأ عن الله'], C['amber2'], C['amber'], 19, True)
    out += box(30, 122, 300, 110, ['من النَّبْوَة', 'الارتفاع', 'رفيع القدر، عَلَمٌ يُهتدى به'], C['amber2'], C['amber'], 19, True)
    return svg(760, 245, out)
D_ROOT = d_root()

def d_send():
    out = box(290, 8, 180, 64, ['الإرسال'], C['blue'], C['blue'], 24, True, '#fff')
    out += f'<path d="M380 72 V100 H190 V122 M380 100 H570 V122" fill="none" stroke="{C["grey"]}" stroke-width="2"/>'
    out += box(430, 122, 300, 100, ['إرسال الأنبياء', 'بالوحي', '= تكليف بالإنذار والهداية'], C['teal2'], C['teal'], 18, True)
    out += box(30, 122, 300, 100, ['إرسال الشياطين', 'على الكافرين', '= تخلية، لا تكليف'], C['rose2'], C['rose'], 18, True)
    return svg(760, 235, out)
D_SEND = d_send()

def d_musa():
    items = [(['موسى', 'نزلت عليه الرسالة'], C['teal'], '#fff'), (['هارون', 'وزير يدعو لرسالة أخيه'], C['teal2'], None),
             (['أنبياء بني إسرائيل', 'تابعون لرسالة موسى'], C['teal2'], None), (['عيسى', 'رسالة جديدة'], C['teal'], '#fff')]
    out = f'<line x1="20" y1="60" x2="740" y2="60" stroke="{C["line"]}" stroke-width="4"/>'
    for i, (l, f, col) in enumerate(items):
        x = 740 - (i + 1) * 180 + 10
        out += box(x, 18, 160, 84, l, f, C['teal'], 16, True, col)
    out = out.replace(f'fill="{C["grey"]}">نزلت', 'fill="#d9efe9">نزلت').replace(f'fill="{C["grey"]}">رسالة جديدة', 'fill="#d9efe9">رسالة جديدة')
    out += text(560, 125, '◄ زمن رسالة موسى (التوراة) ►', 14, C['grey'])
    return svg(760, 140, out)
D_MUSA = d_musa()

def d_isma():
    out = f'<rect x="10" y="10" width="740" height="290" rx="18" fill="{C["blue2"]}" stroke="{C["blue"]}" stroke-width="2"/>'
    out += text(690, 38, 'الرسول', 20, C['blue'], 'bold')
    out += f'<rect x="400" y="62" width="330" height="220" rx="14" fill="#fff" stroke="{C["teal"]}" stroke-width="2"/>'
    out += text(565, 90, 'بوصفه نبياً (وكل الأنبياء)', 17, C['teal'], 'bold')
    out += text(565, 135, '✔ عصمة إرادية: يعصم نفسه بعلمه', 15)
    out += text(565, 162, 'من الكذب والمعاصي والفواحش', 14, C['grey'])
    out += text(565, 205, '✘ ليس معصوماً من القتل', 15, C['rose'])
    out += text(565, 237, '✘ يجوز عليه الخطأ والنسيان البشري', 15, C['rose'])
    out += text(205, 90, 'وبوصفه صاحب رسالة يُضاف:', 17, C['blue'], 'bold')
    out += box(30, 115, 350, 70, ['عصمة من القتل', 'حتى يتم رسالته'], '#fff', C['blue'], 17, True)
    out += box(30, 200, 350, 82, ['عصمة في التبليغ', 'حفظ النص، سلامة النطق، لا مرض ولا سحر يقدح فيه'], '#fff', C['blue'], 17, True)
    return svg(760, 310, out)
D_ISMA = d_isma()

D_ROLE = chain([['يتلقّى الوحي', ''], ['يبلّغه كما هو', 'مقام الرسول • معصوم'], ['يعمل به ويعلّمه', 'مقام النبي • يجتهد']],
               fills=[(C['blue2'], C['blue']), (C['blue2'], C['blue']), (C['teal2'], C['teal'])])

def d_time():
    out = f'<line x1="20" y1="120" x2="740" y2="120" stroke="{C["line"]}" stroke-width="3"/>'
    out += f'<rect x="470" y="40" width="250" height="44" rx="10" fill="{C["amber2"]}" stroke="{C["amber"]}" stroke-width="2"/>'
    out += text(595, 62, 'النبوة: مع شخص النبي', 16, C['amber'], 'bold')
    out += f'<line x1="470" y1="30" x2="470" y2="130" stroke="{C["amber"]}" stroke-width="2" stroke-dasharray="5 4"/>'
    out += text(470, 145, 'وفاة النبي', 13, C['amber'])
    out += f'<rect x="20" y="160" width="700" height="44" rx="10" fill="{C["teal2"]}" stroke="{C["teal"]}" stroke-width="2"/>'
    out += text(370, 182, 'الرسالة: باقية ومستمرة حتى اليوم ←', 16, C['teal'], 'bold')
    out += text(720, 145, 'البعثة', 13, C['grey'])
    out += text(35, 145, 'اليوم', 13, C['grey'])
    return svg(760, 215, out)
D_TIME = d_time()

def d_circles():
    out = f'<circle cx="380" cy="160" r="150" fill="{C["teal2"]}" stroke="{C["teal"]}" stroke-width="2"/>'
    out += f'<circle cx="380" cy="205" r="72" fill="{C["amber2"]}" stroke="{C["amber"]}" stroke-width="2"/>'
    out += text(380, 52, 'الرسالة', 22, C['teal'], 'bold')
    out += text(380, 80, 'للناس جميعاً، في كل زمان', 15, C['teal'])
    out += text(380, 195, 'النبوة', 20, C['amber'], 'bold')
    out += text(380, 222, 'العرب، زمن البعثة', 14, C['amber'])
    return svg(760, 320, out)
D_CIRCLES = d_circles()

def d_qul():
    out = box(280, 8, 200, 60, ['خطاب يبدأ بـ «قُل»'], C['ink'], C['ink'], 18, True, '#fff')
    out += arrow(380, 68, 380, 92)
    out += box(255, 92, 250, 56, ['ماذا فيه؟'], '#fff', C['grey'], 17, True)
    out += f'<path d="M380 148 V168 H190 V186 M380 168 H570 V186" fill="none" stroke="{C["grey"]}" stroke-width="2"/>'
    out += box(430, 186, 300, 120, ['حكم وتشريع', '﴿قُلْ هُوَ أَذًى﴾ عن المحيض', 'المخاطَب: الرسول'], C['blue2'], C['blue'], 18, True)
    out += box(30, 186, 300, 120, ['توجيه وتعليم', '﴿قُلْ هُوَ اللَّهُ أَحَدٌ﴾', 'المخاطَب: النبي'], C['teal2'], C['teal'], 18, True)
    return svg(760, 320, out)
D_QUL = d_qul()

# ---------- content ----------
S = []
S.append(SEC(1, 'من أين بدأت المشكلة؟', 'قبل أن نعرّف أي شيء، لنفهم لماذا نسأل أصلاً', ([
    P('في زمن النبي ﷺ لم يكن عند الصحابة «مشكلة» اسمها السنة. القرآن هو المرجع، والنبي ﷺ بينهم يعلّمهم كيف يعيشون به ويحوّلونه إلى حياة.',
      'المشكلة ظهرت لاحقاً، حين ضاعت مفاهيم أساسية من أذهان الناس. وأولها سؤالان يبدوان بسيطين: **من هو النبي؟ ومن هو الرسول؟**',
      'لماذا يهمّك هذا؟ لأن من خلط بين الكلمتين، خلط بعدها في سؤال أكبر: هل كل ما قاله النبي ﷺ أو فعله تشريع ملزم إلى يوم القيامة؟ أم أن بعضه كان اجتهاداً وتعليماً لزمانه؟'),
    BOX('idea', 'تشبيه للتقريب، مع الفارق العظيم', P('تخيّل معلماً كلّفته الوزارة بتوصيل منهج رسمي. حين يقرأ نص المنهج، لا يغيّر فيه حرفاً واحداً. لكنه حين يشرح ويضرب الأمثلة وينظّم الصف، يجتهد بعلمه وخبرته.',
        'هذا الشرح كله يدور حول التمييز بين هذين المقامين: مقام **التبليغ** ومقام **التعليم والاجتهاد**.')),
    FIG(D_MAP, 'رحلة الشرح: من الإنسان إلى فهم السنة'),
])))

S.append(SEC(2, 'الإنسان: لماذا خُلق؟', 'الحكاية تبدأ منك أنت، لا من الأنبياء', ([
    AYA('﴿إِنَّ اللَّهَ اصْطَفَىٰ آدَمَ وَنُوحًا وَآلَ إِبْرَاهِيمَ وَآلَ عِمْرَانَ عَلَى الْعَالَمِينَ﴾', 'آل عمران: ٣٣'),
    AYA('﴿إِنِّي جَاعِلٌ فِي الْأَرْضِ خَلِيفَةً﴾', 'البقرة: ٣٠'),
    P('الملائكة خُلقوا على التسبيح والتحميد، هذه فطرتهم. أما الإنسان فلم يُخلق ليكرر ما تفعله الملائكة فقط، بل **استُخلف** في الأرض: ليعمّرها، ويُبتلى، ويتدافع مع غيره، فيظهر من هو أحسن عملاً.',
      'فالعبادة هنا أوسع مما نتخيل: هي عبادة تشمل **العمران**، والقيام بحق **الأمانة** التي عُرضت على السماوات والأرض والجبال فأبين أن يحملنها، وحملها الإنسان.'),
    FIG(D_HUMAN, 'أربع كلمات تلخّص مهمة الإنسان'),
    BOX('sum', 'وماذا أعطاه الله ليقوم بالمهمة؟', '<div class="tools"><span>خلقه في أحسن تقويم</span><span>علّمه الأسماء كلها</span><span>سخّر له الشمس والقمر والليل والنهار</span><span>أودع فيه الفطرة والعقل والقدرة على الاستنباط</span></div>'),
])))

S.append(SEC(3, 'لماذا احتاج الإنسان إلى الأنبياء؟', 'العقل وحده لم يكن كافياً، وهذه هي القصة', ([
    P('في بداياته، كان الإنسان يفكّر بعقل حسّي بسيط، يسمّى «العقل الأحيائي البدائي». يرى الأشياء بعينه فقط: الشمس أقوى منه، والقمر، والمطر. فيظن أنها مصادر قوة، فيتجه إليها برجاء أو خوف، وقد يعبدها.',
      'هذا العقل لا يستطيع وحده أن يكتشف النظام الذي يربط الأشياء، ولا أن ينتقل من الجزئيات إلى الكليات، ولا أن يصل من المخلوق إلى الخالق. ولهذا كان فضل إبراهيم عليه السلام عظيماً: اهتدى إلى ذلك، فصار خليل الله وأبا الأنبياء.'),
    FIG(D_STAIRS, 'من عقل يعبد الشمس، إلى رحمة الله بإرسال الأنبياء'),
    P('وفوق ضعف العقل، هناك عدوّ أقسم أن يضلّ الإنسان:'),
    AYA('﴿لَأُزَيِّنَنَّ لَهُمْ فِي الْأَرْضِ وَلَأُغْوِيَنَّهُمْ أَجْمَعِينَ﴾', 'الحجر: ٣٩'),
    P('فلم يترك الله الإنسان وحده. أرسل الأنبياء يتلون آياته، ويعلّمون الكتاب والحكمة، ويزكّون النفوس. وبذلك لم يبقَ لأحد عذر:'),
    AYA('﴿لِئَلَّا يَكُونَ لِلنَّاسِ عَلَى اللَّهِ حُجَّةٌ بَعْدَ الرُّسُلِ﴾', 'النساء: ١٦٥'),
])))

S.append(SEC(4, 'موكبان يسيران في التاريخ', 'صورة تختصر قصة البشرية كلها', ([
    P('تخيّل التاريخ البشري كله طريقاً يسير فيه موكبان متقابلان: **موكب النبوات** يدعو الناس إلى الاستقامة ويضمّهم إلى الساجدين، و**موكب إبليس وجنوده** يدفعهم نحو الانحراف ويصرفهم عن السجود.'),
    FIG(D_TWO, 'كل الأنبياء في موكب واحد، يكمل بعضهم بعضاً'),
    P('والأنبياء كلهم أمة واحدة، دعوتهم واحدة:'),
    AYA('﴿إِنَّ هَٰذِهِ أُمَّتُكُمْ أُمَّةً وَاحِدَةً وَأَنَا رَبُّكُمْ فَاعْبُدُونِ﴾', 'الأنبياء: ٩٢'),
    P('ولهذا جاء القرآن مصدّقاً لتجارب الأنبياء قبله ومهيمناً عليها، وأُمر النبي ﷺ أن يقتدي بهم:'),
    AYA('﴿أُولَٰئِكَ الَّذِينَ هَدَى اللَّهُ ۖ فَبِهُدَاهُمُ اقْتَدِهْ﴾', 'الأنعام: ٩٠'),
])))

hadiths = [
    ('يحكم بالظاهر', '«إنما أنا بشر، وإنكم تختصمون إليّ، ولعل بعضكم أن يكون ألحن بحجته من بعض، فأقضي له على نحو ما أسمع»', 'يقضي بما يسمع، كما يقضي البشر.'),
    ('ينسى كما ننسى', 'صلّى يوماً فزاد أو نقص، فلما سُئل قال: «إنما أنا بشر أنسى كما تنسون»', 'النسيان من طبيعة البشر.'),
    ('لست بملك', 'ارتجف رجل من هيبته، فقال: «هوّن عليك، فإني لست بملك، إنما أنا ابن امرأة تأكل القديد»', 'يطمئن الناس إلى بشريته.'),
    ('لا تجعلوا قبري عيداً', '«لا تتخذوا قبري عيداً، وصلّوا عليّ فإن صلاتكم تبلغني»', 'يسدّ باب التقديس من بعده.'),
    ('لا تجمعني مع الله', 'قال خطيب: «ومن يعصهما فقد غوى»، فقال له: «بئس الخطيب أنت، قل: ومن يعص الله ورسوله»', 'حتى في الضمير، لا مساواة بين الخالق والمخلوق.'),
]
hcards = '<div class="hgrid">' + ''.join(
    f'<div class="hcard"><div class="hn">{ar(i+1)}</div><div class="ht">{t}</div><div class="hx">{T(x)}</div><div class="hl">← {l}</div></div>'
    for i, (t, x, l) in enumerate(hadiths)) + '</div>'

S.append(SEC(5, 'الخطر: حين يتحوّل النبي إلى إله', 'هنا قلب الفكرة كلها، فاقرأه بتمهّل', ([
    P('قصّ علينا القرآن ما حدث للأمم السابقة مع أنبيائها، فإذا بنمط يتكرر:'),
    FIG(D_CYCLE, 'الدائرة التي وقعت فيها الأمم السابقة'),
    P('لماذا حدث هذا؟ لأن الناس فقدوا القدرة على التمييز بين ثلاثة أزواج من المفاهيم:'),
    '<div class="pairs"><span>النبوة ≠ الرسالة</span><span>الربوبية ≠ الألوهية</span><span>الخالق ≠ المخلوق</span></div>',
    P('ولهذا أكّد القرآن **بشرية** الرسول ﷺ، وأكّد في الوقت نفسه **وجوب طاعته** فيما يبلّغه عن الله. والنبي ﷺ نفسه كان يحرس هذا الحد، ويحذّر من المبالغة في تعظيمه. تأمّل هذه المواقف الخمسة:'),
    hcards,
    P('كل ذلك حتى لا تتكرر المأساة: أن يذهب نور النبوة، وينساق الناس بعواطفهم نحو تأليه الأنبياء وطلب الشفاعة منهم.'),
    BOX('warn', 'وفي أمتنا أيضاً', P('أصاب هذه الأمة شيء من هذه الفتنة في بعض فتراتها، فانقسم الناس إلى طرفين: قوم يذكرون اسم النبي ﷺ مجرداً من وصف النبوة والرسالة، وقوم يضفون عليه صفات من صفات الربوبية. ولو انتبهت الأمة لضبط المفاهيم كما انتبه الصحابة، لما وقعت في كثير من الخلط الذي جعل بعضها يكفّر بعضاً.')),
])))

S.append(SEC(6, 'ما معنى كلمة «نبي»؟', 'نرجع إلى اللغة لنفهم الكلمة من جذورها', ([
    FIG(D_ROOT, 'للكلمة أصلان في اللغة، وكلاهما صحيح المعنى'),
    P('من الأصل الثاني قوله تعالى عن إدريس:'),
    AYA('﴿وَرَفَعْنَاهُ مَكَانًا عَلِيًّا﴾', 'مريم: ٥٧'),
    BOX('eg', 'موقف لطيف', P('نادى رجل النبي ﷺ: «يا نبيء الله» بالهمز، فرفض وقال: «لستُ بنبيء الله، ولكن نبيُّ الله». لماذا؟ لأن العرب تقول «نبأ من أرض إلى أرض» إذا خرج منها، فكأن الكلمة بالهمز توحي بمعنى الخروج والطرد.')),
    P('وعند أهل الكتاب تُطلق كلمة «نبي» على كل مُلهَم يخبر بشيء من الغيب أو المستقبل. أما في القرآن فالنبي هو **من أوحى الله إليه وحياً**، وقد أغلق القرآن هذا الباب بعد محمد ﷺ:'),
    AYA('﴿مَا كَانَ مُحَمَّدٌ أَبَا أَحَدٍ مِنْ رِجَالِكُمْ وَلَٰكِنْ رَسُولَ اللَّهِ وَخَاتَمَ النَّبِيِّينَ﴾', 'الأحزاب: ٤٠'),
    P('فكل من ادّعى الوحي بعده فهو كذّاب.'),
])))

S.append(SEC(7, 'ما معنى كلمة «رسول»؟', 'الكلمة الثانية، وفيها حركة وانطلاق', ([
    P('أصل «الرَّسْل» في اللغة: الانبعاث على تؤدة وهدوء. يقال: ناقة رَسْلة، أي سهلة السير. ومنه الرسول: **المنبعث الذي يحمل القول والرسالة ويبلّغها**.',
      'ولهذا تُطلق الكلمة في القرآن على الملائكة وعلى البشر معاً:'),
    AYA('﴿إِنَّهُ لَقَوْلُ رَسُولٍ كَرِيمٍ﴾', 'التكوير: ١٩ (جبريل عليه السلام)'),
    AYA('﴿وَمَا مُحَمَّدٌ إِلَّا رَسُولٌ قَدْ خَلَتْ مِنْ قَبْلِهِ الرُّسُلُ﴾', 'آل عمران: ١٤٤'),
    P('وانتبه: ليس كل «إرسال» في القرآن تكريماً:'),
    FIG(D_SEND),
    AYA('﴿أَلَمْ تَرَ أَنَّا أَرْسَلْنَا الشَّيَاطِينَ عَلَى الْكَافِرِينَ تَؤُزُّهُمْ أَزًّا﴾', 'مريم: ٨٣'),
])))

S.append(SEC(8, 'الفارق الأول: نوع الوحي', 'الآن نصل إلى السؤال الكبير: ما الفرق؟', ([
    P('النبي والرسول كلاهما يوحى إليه. لكن **نوع الوحي مختلف**:'),
    '''<table class="cmp"><tr><th></th><th class="r">الرسول</th><th class="n">النبي</th></tr>
<tr><td>الوحي</td><td>فيه <b>تشريع جديد</b></td><td>بلا تشريع جديد</td></tr>
<tr><td>علاقته بالشريعة</td><td>صاحب رسالة</td><td>يتبع رسالة رسول سبقه</td></tr>
<tr><td>وظيفته</td><td>التلاوة والتبليغ</td><td>الدعوة والتعليم والقيادة</td></tr>
<tr><td>طبيعة المقام</td><td>مقام تبليغ</td><td>مقام علمي</td></tr></table>''',
    AYA('﴿وَمَا عَلَى الرَّسُولِ إِلَّا الْبَلَاغُ الْمُبِينُ﴾', 'النور: ٥٤'),
    P('**أوضح مثال: موسى وهارون عليهما السلام.** قال تعالى عن هارون:'),
    AYA('﴿وَوَهَبْنَا لَهُ مِنْ رَحْمَتِنَا أَخَاهُ هَارُونَ نَبِيًّا﴾', 'مريم: ٥٣'),
    P('ثم خاطبهما معاً: ﴿فَقُولَا إِنَّا رَسُولُ رَبِّ الْعَالَمِينَ﴾. فكيف يكون هارون نبياً ورسولاً؟',
      'موسى هو من نزلت عليه الرسالة. أما هارون فلم يوحَ إليه برسالة مستقلة، بل كان **وزيراً** لأخيه يدعو إلى رسالته: ﴿وَاجْعَلْ لِي وَزِيرًا مِنْ أَهْلِي ۝ هَارُونَ أَخِي﴾. فصار رسولاً **بالتبعية**.'),
    FIG(D_MUSA, 'كل أنبياء بني إسرائيل بعد موسى تبعوا رسالته، حتى جاء عيسى برسالة جديدة'),
    BOX('warn', 'للأمانة العلمية', P('التعريف المشهور عند جمهور العلماء قريب من هذا: الرسول من أوحي إليه بشرع وأُمر بتبليغه، والنبي من بُعث بتقرير شرع من قبله. وتفاصيل الفرق محل اجتهاد بين العلماء.')),
])))

S.append(SEC(9, 'الفارق الثاني: العصمة', 'من ماذا يحفظ الله أنبياءه ورسله؟', ([
    P('الأنبياء، بوصفهم أنبياء، ليسوا معصومين من القتل. يجوز عليهم ما يجوز على البشر، ولهذا قتل بنو إسرائيل أنبياءهم. وليسوا معصومين من العوارض البشرية كالخطأ والنسيان.',
      'لكن لهم عصمة من نوع آخر: **عصمة إرادية**. النبي عالم بالله، فيعصم نفسه بإيمانه عن الكذب والمعاصي والفواحش:'),
    AYA('﴿إِنَّمَا يَخْشَى اللَّهَ مِنْ عِبَادِهِ الْعُلَمَاءُ﴾', 'فاطر: ٢٨'),
    P('وهذه العصمة مطلوبة منا جميعاً: ﴿وَاعْتَصِمُوا بِحَبْلِ اللَّهِ جَمِيعًا﴾. أما الرسول فيُضاف له نوعان خاصّان بالرسالة:'),
    FIG(D_ISMA, 'عصمة الرسول في الحقيقة حماية للرسالة، لا للشخص'),
    P('ولهذا كان أولو العزم، نوح وإبراهيم وموسى وعيسى ومحمد عليهم السلام، معصومين من القتل حتى أتمّوا رسالاتهم.'),
    BOX('key', 'الفكرة الذهبية في هذا القسم', P('حين ينتهي الرسول من التلاوة والتبليغ، ينتهي دوره **رسولاً**، ويبدأ دوره **نبياً**: يتفاعل مع الرسالة، ويكون أول من يعمل بها، ثم يعلّمها الناس.') + FIG(D_ROLE)),
    BOX('warn', 'للأمانة العلمية', P('جمهور العلماء يرون أن الأنبياء جميعاً معصومون من الكبائر ومن كل ما يخلّ بالتبليغ. وما ذُكر هنا من حصر عصمة النبي في «العصمة الإرادية» رأيٌ خاص.')),
])))

S.append(SEC(10, 'الفارق الثالث: الاجتهاد', 'هل كان النبي ﷺ يجتهد برأيه؟', ([
    P('النبوة لا تلغي البشرية. حين صار النبي رسولاً لم تنتفِ عنه البشرية، بل أُضيف إليه مقام الرسالة:'),
    AYA('﴿قُلْ إِنَّمَا أَنَا بَشَرٌ مِثْلُكُمْ يُوحَىٰ إِلَيَّ﴾', 'الكهف: ١١٠'),
    P('والآن تابع هذا التسلسل المنطقي:'),
    chain([['النبوة', 'مقام علمي'], ['الأنبياء', 'سادة العلماء'], ['الاجتهاد', 'حق للعلماء'], ['إذن', 'النبي أولى به']],
          fills=[(C['blue2'], C['blue'])] * 3 + [(C['blue'], C['blue'])]).replace(f'fill="{C["blue"]}" stroke="{C["blue"]}" stroke-width="2"/><text', f'fill="{C["blue"]}" stroke="{C["blue"]}" stroke-width="2"/><text style="fill:#fff"'),
    P('وإلا لصار العالم المجتهد أفضل من النبي! فالنبي يجتهد في الدعوة والتعليم، ويستنبط من الرسالة. وإن كان هو الرسول نفسه، فيجتهد في فهم الرسالة التي أُنزلت عليه وتطبيقها.'),
    BOX('idea', 'عبارة تستحق التوقف', P('المشهور: «كل رسول نبي، وليس كل نبي رسولاً». لكن بحسب الفروق التي رأيناها، يمكن القول: الرسول التابع هو نبي، والنبي صاحب الرسالة هو رسول. وفي النهاية كلاهما مرسَل من الله إلى الناس:') + AYA('﴿وَمَا أَرْسَلْنَا مِنْ قَبْلِكَ مِنْ رَسُولٍ وَلَا نَبِيٍّ﴾', 'الحج: ٥٢')),
    '''<div class="card2"><div class="c2 n"><h4>النبوة</h4><ul><li>اصطفاء إلهي، لا اكتساب</li><li>مقام علم ودعوة وقيادة</li><li>يجوز عليه ما يجوز على الإنسان</li><li>له حق الاجتهاد</li><li>عصمته إرادية</li></ul></div>
<div class="c2 r"><h4>الرسالة</h4><ul><li>تكليف بإيصال رسالة الله كما هي</li><li>ليس فيها إلا التلاوة والتبليغ</li><li>لا اجتهاد في نص الرسالة</li><li>معصوم في حفظها ونطقها، ومن القتل حتى يتمها</li></ul></div></div>''',
])))

S.append(SEC(11, 'ما يموت وما يبقى', 'نتيجة مهمة جداً تخرج من كل ما سبق', ([
    P('**النبوة مرتبطة بشخص النبي**، فتنتهي فاعليتها بموته. حين مات هارون عليه السلام انتهت نبوته.',
      '**الرسالة مرتبطة بالرسالة نفسها**، وجودها منفصل عن شخص الرسول. حين مات موسى عليه السلام بقيت التوراة.'),
    FIG(D_TIME, 'خط الزمن: أين تنتهي النبوة، وإلى أين تمتد الرسالة'),
    BOX('key', 'ماذا يعني هذا لك؟', P('الصحابة الذين عاشوا مع النبي ﷺ تعاملوا مع المقامين معاً: النبوة والرسالة. أما نحن والأجيال اللاحقة، فعلاقتنا الأساسية بـ**الرسالة**. النبوة خاصة بزمانها ومكانها، والرسالة عامة ومستمرة.')),
])))

S.append(SEC(12, 'دائرتان: العرب والعالمين', 'كيف تتسع الرسالة لتشمل الناس جميعاً؟', ([
    FIG(D_CIRCLES, 'النبوة في قلب الرسالة، والرسالة أوسع منها'),
    P('رسالة محمد ﷺ للناس جميعاً:'),
    AYA('﴿قُلْ يَا أَيُّهَا النَّاسُ إِنِّي رَسُولُ اللَّهِ إِلَيْكُمْ جَمِيعًا﴾', 'الأعراف: ١٥٨'),
    P('أما بعثته نبياً فكانت في قومه:'),
    AYA('﴿هُوَ الَّذِي بَعَثَ فِي الْأُمِّيِّينَ رَسُولًا مِنْهُمْ يَتْلُو عَلَيْهِمْ آيَاتِهِ وَيُزَكِّيهِمْ وَيُعَلِّمُهُمُ الْكِتَابَ وَالْحِكْمَةَ﴾', 'الجمعة: ٢'),
    P('فلما توفي ﷺ توقفت فاعلية مقام النبوة، واستمر مقام الرسالة في الرسالة ذاتها. والدليل من الواقع: القرآن انتشر بين الناس جميعاً واتفقوا عليه، بينما بقي الحديث محل نقاش وقبول ورفض بين المسلمين أنفسهم.',
      'ولما اكتمل الدين، من نوح إلى إبراهيم وموسى وعيسى وانتهاءً بمحمد ﷺ، خُتمت النبوة. وحمل العلماء الرسالة الخاتمة، كلٌّ في زمانه وبأدوات عصره: يعلّمون الناس، ويدعونهم إلى الحق والعدل، ويستنبطون من الرسالة أحكاماً لما يستجدّ في حياتهم.'),
    BOX('warn', 'للأمانة العلمية', P('القول بأن نبوته ﷺ كانت للعرب خاصة رأيٌ يخالف ما عليه جمهور العلماء، فهم يرون أن نبوته ورسالته ﷺ عامة للناس جميعاً. فاقرأه على أنه اجتهاد يستحق التأمل والنقاش.')),
])))

S.append(SEC(13, 'مفتاح قرآني: كلمة «قُل»', 'أداة عملية تساعدك وأنت تقرأ القرآن', ([
    P('القاعدة: كل خطاب في القرآن موجّه إلى النبي، صراحة أو ضمناً، هو خطاب **تعليمي توجيهي** نحو الأحسن والحل الأمثل لظرفه، وليس تشريعاً بالضرورة.',
      'أما الخطاب الذي يبدأ بـ«قُل»، فننظر في مضمونه:'),
    FIG(D_QUL, 'شجرة قرار بسيطة لفهم خطاب «قُل»'),
    P('وبالطريقة نفسها: إذا جاءت كلمة «الرسول» في سياق **الطاعة والأحكام**، فالمقصود مقام الرسالة. وإذا جاءت في سياق **التوجيه والتعليم**، فالمقصود مقام النبوة، واستُعمل لفظ الرسالة من باب مخاطبته بالمقام الأعلى.'),
    BOX('warn', 'للأمانة العلمية', P('هذا مفتاح اجتهادي في القراءة، وليس قاعدة متفقاً عليها بين المفسرين.')),
])))

S.append(SEC(14, 'وهم «العبقرية»', 'مديح يبدو جميلاً، لكنه يخفي شيئاً خطيراً', ([
    P('انتشر في بعض الكتابات المعاصرة وصف الأنبياء بـ«العباقرة»، كأنهم زعماء أذكياء أو قادة قوميون جاؤوا لإنقاذ شعوبهم. وهذا يشبه خلط أهل الكتاب بين الوحي والإلهام والتأملات.'),
    '''<table class="cmp vs"><tr><th></th><th class="g2">العبقرية</th><th class="r">النبوة</th></tr>
<tr><td>مصدرها</td><td>كسب بشري</td><td>اصطفاء إلهي</td></tr>
<tr><td>من يملكها؟</td><td>صفة مشتركة بين الناس</td><td>خاصة بمن اختاره الله</td></tr>
<tr><td>هل تُتعلّم؟</td><td>نعم، بالتدريب والجهد</td><td>لا معاهد لتأهيل الأنبياء</td></tr>
<tr><td>هل يطلبها صاحبها؟</td><td>يسعى إليها</td><td>لا يدري أنه سيُصطفى، ولا يطلبها</td></tr></table>''',
    AYA('﴿اللَّهُ يَصْطَفِي مِنَ الْمَلَائِكَةِ رُسُلًا وَمِنَ النَّاسِ﴾', 'الحج: ٧٥'),
    AYA('﴿اللَّهُ أَعْلَمُ حَيْثُ يَجْعَلُ رِسَالَتَهُ﴾', 'الأنعام: ١٢٤'),
    BOX('warn', 'لماذا هذا خطير؟', P('لأن بعضهم أراد أن يمدح النبي ﷺ فوصفه بالعبقري، فنفى عنه، من حيث لا يشعر، **الجانب الغيبي**: النبوة والرسالة. فصار المديح إنكاراً مقنّعاً، دون أن يصرّح أحد بالإنكار.')),
])))

summary = ['النبوة اصطفاء إلهي، وليست عبقرية ولا اكتساباً.', 'النبي بشر، يجوز عليه ما يجوز على البشر، وله حق الاجتهاد.',
           'الرسول مبلّغ أمين، معصوم في حفظ الرسالة وتبليغها.', 'النبوة مرتبطة بشخص صاحبها وزمانه، والرسالة باقية للناس جميعاً.']
quiz = [('ما الفرق الأساسي بين وحي الرسول ووحي النبي؟', 'وحي الرسول فيه تشريع جديد، ووحي النبي بلا تشريع جديد، فهو يتبع رسالة من سبقه.'),
        ('لماذا يُعدّ هارون عليه السلام رسولاً مع أن الرسالة نزلت على موسى؟', 'لأنه كان وزيراً يدعو إلى رسالة أخيه، فصار رسولاً بالتبعية.'),
        ('عصمة الرسول من القتل، هل هي حماية لشخصه؟', 'لا، هي في الحقيقة حماية للرسالة حتى يتم تبليغها.'),
        ('ما الذي انتهى بوفاة النبي ﷺ، وما الذي بقي؟', 'انتهت فاعلية مقام النبوة المرتبط بشخصه، وبقيت الرسالة.'),
        ('لماذا يُعدّ وصف النبي بـ«العبقري» خطيراً؟', 'لأنه يجعل النبوة كسباً بشرياً، فينفي الجانب الغيبي: الاصطفاء والوحي.')]

S.append('<section class="sec end"><div class="keep"><div class="sh"><div class="sn">١٥</div><div><h2>الخلاصة</h2><div class="sub">كل ما سبق في أربع جمل</div></div></div></div>'
         + '<ol class="final">' + ''.join(f'<li><span class="fn">{ar(i+1)}</span><span>{T(s)}</span></li>' for i, s in enumerate(summary)) + '</ol>'
         + BOX('key', 'لماذا كل هذا؟', P('لأن هذا التمييز هو المدخل لفهم السنة كلها: كيف نفرّق بين ما صدر عن رسول الله ﷺ بوصفه **رسولاً مبلّغاً** عن الله، وما صدر عنه بوصفه **نبياً معلّماً وقائداً** في زمانه؟'))
         + '<div class="quiz"><div class="qh">✍️ اختبر فهمك</div><p class="qi">جاوب في ذهنك أولاً، ثم انظر الإجابة تحتها.</p>'
         + ''.join(f'<div class="qq"><div class="qn">{ar(i+1)}</div><div><div class="qt">{T(q)}</div><div class="qa">الإجابة: {T(a)}</div></div></div>' for i, (q, a) in enumerate(quiz))
         + '</div><div class="next"><small>الموضوع التالي</small><div>الأنبياء في القرآن</div></div></section>')

TOC = ['من أين بدأت المشكلة؟', 'الإنسان: لماذا خُلق؟', 'لماذا احتاج الإنسان إلى الأنبياء؟', 'موكبان يسيران في التاريخ',
       'الخطر: حين يتحوّل النبي إلى إله', 'ما معنى «نبي»؟', 'ما معنى «رسول»؟', 'الفارق الأول: نوع الوحي', 'الفارق الثاني: العصمة',
       'الفارق الثالث: الاجتهاد', 'ما يموت وما يبقى', 'دائرتان: العرب والعالمين', 'مفتاح قرآني: «قُل»', 'وهم «العبقرية»', 'الخلاصة واختبر فهمك']

PAT = ('<svg class="pat" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%"><defs><pattern id="p" width="90" height="90" patternUnits="userSpaceOnUse">'
       '<g fill="none" stroke="#e3b866" stroke-width="1" opacity=".35"><rect x="25" y="25" width="40" height="40"/><rect x="25" y="25" width="40" height="40" transform="rotate(45 45 45)"/>'
       '<circle cx="45" cy="45" r="11"/><path d="M0 0L25 25M90 0L65 25M0 90L25 65M90 90L65 65"/></g></pattern></defs><rect width="100%" height="100%" fill="url(#p)"/></svg>')

CSS = '''
:root{--teal:#0f5a52;--teal2:#e3f1ee;--amber:#c7831f;--amber2:#fbefd9;--rose:#a64b3c;--rose2:#f8e4df;--blue:#2f5d8a;--blue2:#e2ebf5;--ink:#25302e;--grey:#6f7a75}
@page{size:A4;margin:18mm 17mm 18mm 17mm}
@page cover{margin:0}
body{margin:0;font-family:"IBM Plex Sans Arabic",sans-serif;font-size:11.6pt;line-height:1.95;color:var(--ink)}
svg{font-family:"IBM Plex Sans Arabic",sans-serif}
b{color:var(--teal);font-weight:700}
.q{font-family:"Amiri Quran",serif;color:var(--teal);font-size:1.08em}
.g{color:#8a5a12}
p{margin:0 0 9px;text-align:justify;orphans:3;widows:3}
.cover{page:cover;height:297mm;width:210mm;position:relative;background:linear-gradient(160deg,#0f5a52 0%,#0b3f3a 60%,#082e2b 100%);color:#fff;overflow:hidden;break-after:page}
.cover .pat{position:absolute;inset:0}
.ctext{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 26mm}
.tag{font-size:12pt;background:rgba(227,184,102,.18);border:1px solid #e3b866;color:#f3d79c;padding:4px 18px;border-radius:30px;margin-bottom:22px}
.cover h1{font-family:"El Messiri";font-weight:700;font-size:56pt;margin:0;line-height:1.3}
.cover .s1{font-family:"El Messiri";font-size:20pt;color:#f3d79c;margin-top:8px}
.cover .s2{font-size:13pt;color:#cfe3de;margin-top:26px;line-height:1.9}
.cover .medal{margin-bottom:30px}
.intro{break-after:page}
.intro h3{font-family:"El Messiri";color:var(--teal);font-size:20pt;margin:6mm 0 4mm;text-align:center}
.bigq{display:grid;gap:10px;margin:8mm 0}
.bigq div{background:var(--teal2);border-radius:14px;padding:14px 20px;font-family:"El Messiri";font-size:16pt;color:var(--teal);line-height:1.7}
.bigq div:nth-child(2){background:var(--amber2);color:#8a5a12}
.bigq div:nth-child(3){background:var(--rose2);color:var(--rose)}
.howto{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin:6mm 0;font-size:10.5pt}
.howto span{border:1px solid #dfe5e2;border-radius:30px;padding:3px 14px}
.toc{list-style:none;padding:0;margin:0;columns:2;column-gap:10mm;font-size:11pt;line-height:2.15}
.toc li span{display:inline-block;width:26px;height:22px;line-height:22px;text-align:center;border-radius:6px;background:var(--teal);color:#fff;font-size:9.5pt;margin-left:8px}
.sec{margin:0 0 10mm}
.end{break-before:page}
.keep{break-inside:avoid;break-after:avoid}
.sh{display:flex;align-items:center;gap:14px;margin-bottom:6mm;padding-bottom:4mm;border-bottom:2px solid var(--teal2)}
.sn{flex:none;width:52px;height:52px;border-radius:16px;background:var(--teal);color:#fff;font-family:"El Messiri";font-weight:700;font-size:20pt;display:flex;align-items:center;justify-content:center;transform:rotate(-4deg)}
h2{font-family:"El Messiri";font-weight:700;font-size:21pt;color:var(--teal);margin:0;line-height:1.35}
.sub{color:var(--grey);font-size:10.5pt;line-height:1.5}
.aya{background:linear-gradient(90deg,#fff,#f2f8f6,#fff);border-top:1px solid #cfe3de;border-bottom:1px solid #cfe3de;text-align:center;padding:8px 10px 6px;margin:8px 0 12px;break-inside:avoid}
.aya .q{font-size:17pt;line-height:2}
.ref{font-size:9pt;color:var(--grey);margin-top:-2px}
figure{margin:10px 0 14px;break-inside:avoid;text-align:center}
figcaption{font-size:9.5pt;color:var(--grey);margin-top:4px}
.box{border-radius:14px;padding:10px 16px 6px;margin:10px 0 14px;break-inside:avoid}
.bt{font-family:"El Messiri";font-weight:700;font-size:13pt;margin-bottom:4px}
.box.idea{background:var(--amber2);border-right:5px solid var(--amber)} .box.idea .bt{color:#8a5a12}
.box.eg{background:var(--blue2);border-right:5px solid var(--blue)} .box.eg .bt{color:var(--blue)}
.box.warn{background:#f6f6f3;border:1px dashed #b9b9ad} .box.warn .bt{color:#6b6b5e;font-size:11.5pt} .box.warn p{font-size:10.5pt;color:#55554c}
.box.key{background:var(--teal2);border-right:5px solid var(--teal)} .box.key .bt{color:var(--teal)}
.box.sum{background:#fff;border:1.5px solid var(--amber2)} .box.sum .bt{color:#8a5a12}
.tools{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:6px 0 8px}
.tools span{background:var(--amber2);border-radius:10px;padding:6px 12px;font-size:10.8pt}
.pairs{display:flex;gap:10px;justify-content:center;margin:6px 0 14px}
.pairs span{background:var(--rose2);color:var(--rose);font-weight:700;border-radius:30px;padding:4px 16px}
.hgrid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:8px 0 14px}
.hcard{border:1.5px solid var(--amber2);border-radius:14px;padding:10px 14px;position:relative;break-inside:avoid;background:#fffdf8}
.hcard:last-child{grid-column:1/-1}
.hn{position:absolute;top:10px;left:12px;width:26px;height:26px;border-radius:50%;background:var(--amber);color:#fff;font-size:10pt;display:flex;align-items:center;justify-content:center}
.ht{font-family:"El Messiri";font-weight:700;color:#8a5a12;font-size:13pt}
.hx{font-family:"Amiri";font-size:13pt;line-height:1.85}
.hx .g{color:#5c3d0c}
.hl{font-size:10pt;color:var(--teal);font-weight:600}
table.cmp{width:100%;border-collapse:separate;border-spacing:0;margin:8px 0 14px;font-size:11pt;break-inside:avoid;border-radius:12px;overflow:hidden;border:1px solid #dfe5e2}
.cmp th{padding:8px;font-family:"El Messiri";font-size:14pt;color:#fff;background:#9aa5a0}
.cmp th.r{background:var(--blue)} .cmp th.n{background:var(--teal)} .cmp th.g2{background:#8f8f86}
.cmp td{padding:7px 10px;border-top:1px solid #e6ebe9;text-align:center}
.cmp td:first-child{background:#f6f8f7;font-weight:700;color:var(--grey);width:24%}
.card2{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:10px 0;break-inside:avoid}
.c2{border-radius:14px;padding:8px 16px;color:#fff}
.c2.n{background:var(--teal)} .c2.r{background:var(--blue)}
.c2 h4{font-family:"El Messiri";font-size:16pt;margin:4px 0}
.c2 ul{margin:0;padding-right:18px;font-size:10.5pt;line-height:1.9}
.final{list-style:none;padding:0;margin:0 0 12px;display:grid;gap:8px}
.final li{display:flex;align-items:center;gap:12px;background:var(--teal);color:#fff;border-radius:12px;padding:10px 16px;font-family:"El Messiri";font-size:14pt}
.fn{flex:none;width:30px;height:30px;border-radius:50%;background:#e3b866;color:var(--teal);display:flex;align-items:center;justify-content:center;font-weight:700}
.quiz{border:2px solid var(--amber2);border-radius:16px;padding:10px 16px;margin-top:8mm}
.qh{font-family:"El Messiri";font-weight:700;color:#8a5a12;font-size:16pt}
.qi{font-size:10pt;color:var(--grey)}
.qq{display:flex;gap:12px;padding:8px 0;border-top:1px dashed #eadbbd;break-inside:avoid}
.qn{flex:none;width:28px;height:28px;border-radius:8px;background:var(--amber);color:#fff;display:flex;align-items:center;justify-content:center;margin-top:4px}
.qt{font-weight:700}
.qa{font-size:10.3pt;color:var(--teal);background:var(--teal2);border-radius:8px;padding:2px 10px;margin-top:4px}
.next{margin-top:8mm;text-align:center;background:linear-gradient(160deg,#0f5a52,#0b3f3a);border-radius:16px;padding:8mm;color:#fff;break-inside:avoid}
.next small{color:#f3d79c;font-size:11pt}
.next div{font-family:"El Messiri";font-size:24pt;font-weight:700}
'''

MEDAL = ('<svg class="medal" viewBox="0 0 100 100" width="130" height="130"><g fill="none" stroke="#e3b866" stroke-width="1.6">'
         '<circle cx="50" cy="50" r="46"/><rect x="22" y="22" width="56" height="56"/><rect x="22" y="22" width="56" height="56" transform="rotate(45 50 50)"/>'
         '<circle cx="50" cy="50" r="16"/><circle cx="50" cy="50" r="7" fill="#e3b866"/></g></svg>')

doc = ('<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>النبوة والرسالة</title>'
       '<link href="https://fonts.googleapis.com/css2?family=Amiri&family=Amiri+Quran&family=El+Messiri:wght@500;700&family=IBM+Plex+Sans+Arabic:wght@400;600;700&display=swap" rel="stylesheet">'
       f'<style>{CSS}</style></head><body>'
       f'<div class="cover">{PAT}<div class="ctext">{MEDAL}<div class="tag">شرح مبسّط بالرسومات</div>'
       '<h1>النبوة والرسالة</h1><div class="s1">الفرق الذي غاب عنا</div>'
       '<div class="s2">هل كل نبي رسول؟ ولماذا يهمّك أن تعرف الفرق؟<br>رحلة في خمس عشرة محطة</div></div></div>'
       '<div class="intro"><h3>قبل أن تبدأ، فكّر في هذه الأسئلة</h3><div class="bigq">'
       '<div>هل كلّ نبيٍّ رسول؟</div><div>هل كلّ ما قاله النبي ﷺ تشريعٌ ملزمٌ إلى يوم القيامة؟</div>'
       '<div>لماذا حرص القرآن، في آيات كثيرة، على أن يذكّرنا أن محمداً ﷺ بشرٌ مثلنا؟</div></div>'
       f'{P("هذه الأسئلة ليست ترفاً فكرياً. فمن خلط بين «النبوة» و«الرسالة» خلط بعد ذلك في فهم السنة كلها: ما الذي نتّبعه؟ وما الذي كان اجتهاداً لزمانه؟ في هذا الشرح ستجد الجواب خطوة خطوة.")}'
       '<div class="howto"><span>💡 تشبيه للتقريب</span><span>🔍 مثال</span><span>🗝️ فكرة أساسية</span><span>⚖️ للأمانة العلمية</span></div>'
       '<h3 style="font-size:15pt">المحطات</h3><ul class="toc">'
       + ''.join(f'<li><span>{ar(i+1)}</span>{html.escape(t)}</li>' for i, t in enumerate(TOC)) +
       '</ul></div>' + ''.join(S) + '</body></html>')

open(sys.argv[1], 'w', encoding='utf-8').write(doc)
print('ok')
