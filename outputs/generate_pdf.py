import os
import sys
from reportlab.lib.pagesizes import a4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfgen import canvas

# 1. Register Fonts (Noto Sans Devanagari for Unicode support)
REGULAR_FONT_PATH = "/workspace/outputs/NotoSansDevanagari-Regular.ttf"
BOLD_FONT_PATH = "/workspace/outputs/NotoSansDevanagari-Bold.ttf"

pdfmetrics.registerFont(TTFont('NotoSansDevanagari', REGULAR_FONT_PATH))
pdfmetrics.registerFont(TTFont('NotoSansDevanagari-Bold', BOLD_FONT_PATH))
registerFontFamily('NotoSansDevanagari', normal='NotoSansDevanagari', bold='NotoSansDevanagari-Bold')

# 2. NumberedCanvas for Running Header and Footer (dynamic page counting)
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_elements(num_pages)
            super().showPage()
        super().save()

    def draw_page_elements(self, page_count):
        self.saveState()
        self.setFont("NotoSansDevanagari", 8)
        self.setFillColor(colors.HexColor("#4A5568"))
        
        # Draw running header (except first page)
        if self._pageNumber > 1:
            self.drawString(54, 795, "हिंदी फोरम - महबूबनगर | पाठशाला व्याकरण (त्वरित पुनरावृत्ति)")
            self.drawRightString(541.27, 795, "एम. गोपी कृष्णा, स्कूल सहायक (हिंदी)")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(54, 788, 541.27, 788)
            
        # Draw running footer (all pages)
        self.drawString(54, 40, "संकलनकर्ता: एम. गोपी कृष्णा, स्कूल सहायक (हिंदी), जि.प.उ.पा. मणिकोंडा - मो. 9441612678")
        self.drawRightString(541.27, 40, f"पृष्ठ {self._pageNumber} / {page_count}")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(54, 52, 541.27, 52)
        
        self.restoreState()

# 3. Create PDF Flowable Story
def build_pdf():
    pdf_filename = "/workspace/outputs/hindi_grammar_revision.pdf"
    
    # Page template setup
    # Margins: Left=54, Right=54 (giving printable width of 595.27 - 108 = 487.27 pt)
    # Top=72 (leaves 841.89 - 72 - 54 = 715.89 pt height for content)
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=a4,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )

    # Styles Setup
    styles = getSampleStyleSheet()
    
    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='NotoSansDevanagari-Bold',
        fontSize=22,
        leading=28,
        textColor=colors.HexColor("#1A365D"),
        alignment=1, # Center
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='NotoSansDevanagari',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#2C5282"),
        alignment=1, # Center
        spaceAfter=15
    )
    
    info_box_style = ParagraphStyle(
        'InfoBox',
        parent=styles['Normal'],
        fontName='NotoSansDevanagari',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#2D3748"),
        alignment=1, # Center
        spaceAfter=25
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Dev',
        parent=styles['Normal'],
        fontName='NotoSansDevanagari-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1A365D"),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Heading2_Dev',
        parent=styles['Normal'],
        fontName='NotoSansDevanagari-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2C5282"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Dev',
        parent=styles['Normal'],
        fontName='NotoSansDevanagari',
        fontSize=9.2,
        leading=12.5,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=5
    )
    
    bullet_style = ParagraphStyle(
        'Bullet_Dev',
        parent=styles['Normal'],
        fontName='NotoSansDevanagari',
        fontSize=9.2,
        leading=12.5,
        textColor=colors.HexColor("#2D3748"),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='NotoSansDevanagari',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#2D3748")
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='NotoSansDevanagari-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )

    story = []

    # Helpers for Paragraph Construction
    def p(text):
        return Paragraph(text, body_style)
        
    def b(text):
        return Paragraph(f"• {text}", bullet_style)
        
    def h1(text):
        return Paragraph(text, h1_style)
        
    def h2(text):
        return Paragraph(text, h2_style)

    # 4. COVER PAGE / HEADER
    story.append(Spacer(1, 15))
    story.append(Paragraph("HINDI FORUM - MAHABUB NAGAR (हिंदी फोरम - महबूबनगर)", subtitle_style))
    story.append(Paragraph("पाठशाला व्याकरण (त्वरित पुनरावृत्ति)", title_style))
    story.append(Paragraph("<b>स्कूल सहायक (हिंदी) और भाषा पंडित (LP) भर्ती परीक्षाओं हेतु अत्यंत उपयोगी हस्तपुस्तिका</b>", subtitle_style))
    
    info_html = """
    <b>संकलनकर्ता: एम. गोपी कृष्णा</b>, स्कूल सहायक (हिंदी), जि.प.उ.पा. मणिकोंडा - महबूबनगर (मो. 9441612678)<br/>
    <i>प्रतियोगी परीक्षाओं (TS TET, DSC, LP, SGT, SA, CTET) की त्वरित और सटीक तैयारी के लिए संपूर्ण व्याकरण का एक संक्षिप्त संकलन।</i>
    """
    story.append(Paragraph(info_html, info_box_style))
    story.append(Spacer(1, 10))

    # --- TOPIC 1: वर्ण विचार ---
    story.append(h1("1. वर्ण विचार (Phonology / Phonetics)"))
    story.append(p("<b>वर्ण (Letter):</b> भाषा की सबसे छोटी ध्वनि-इकाई जिसके और टुकड़े न किए जा सकें, वर्ण कहलाती है (जैसे: अ, क, त)।"))
    story.append(p("<b>वर्णमाला:</b> वर्णों के व्यवस्थित समूह को वर्णमाला कहते हैं। मानक देवनागरी वर्णमाला में कुल <b>52 वर्ण</b> हैं।"))
    
    story.append(h2("क. स्वर (Vowels) - कुल 11"))
    story.append(p("जो वर्ण बिना किसी अन्य वर्ण की सहायता के स्वतंत्र रूप से उच्चरित होते हैं, उन्हें स्वर कहते हैं (अ, आ, इ, ई, उ, ऊ, ऋ, ए, ऐ, ओ, औ)।"))
    story.append(b("<b>ह्रस्व स्वर (लघु):</b> जिनके उच्चारण में बहुत कम (एक मात्रा का) समय लगता है: <b>अ, इ, उ, ऋ</b> (संख्या: 4)"))
    story.append(b("<b>दीर्घ स्वर:</b> जिनके उच्चारण में ह्रस्व से दुगना समय लगता है: <b>आ, ई, ऊ, ए, ऐ, ओ, औ</b> (संख्या: 7)"))
    story.append(b("<b>प्लुत स्वर:</b> जिनके उच्चारण में तिगुना समय लगता है (जैसे- ओऽम, रामऽ)।"))
    story.append(b("<b>अयोगवाह:</b> <b>अं (अनुस्वार)</b> और <b>अः (विसर्ग)</b>। ये न तो पूर्णतः स्वर हैं और न ही व्यंजन।"))
    
    story.append(h2("ख. व्यंजन (Consonants) - कुल 33"))
    story.append(p("जो वर्ण स्वरों की सहायता से बोले जाते हैं, उन्हें व्यंजन कहते हैं। इनके मुख्य तीन भेद हैं:"))
    story.append(b("<b>स्पर्श व्यंजन (25):</b> क-वर्ग से प-वर्ग तक के 25 वर्ण (क, ख, ग, घ, ङ; च, छ, ज, झ, ञ; ट, ठ, ड, ढ, ण; त, थ, द, ध, न; प, फ, ब, भ, म)।"))
    story.append(b("<b>अंतस्थ व्यंजन (4):</b> य, र, ल, व"))
    story.append(b("<b>ऊष्म व्यंजन (4):</b> श, ष, स, ह"))
    story.append(b("<b>संयुक्त व्यंजन (4):</b> क्ष (क् + ष), त्र (त् + र), ज्ञ (ज् + ञ), श्र (श् + र)"))
    story.append(b("<b>द्विगुण (उत्क्षिप्त) व्यंजन (2):</b> ड़, ढ़"))
    
    story.append(Spacer(1, 5))
    story.append(h2("ग. उच्चारण स्थान (Places of Pronunciation)"))
    
    # Pronunciation Places Table
    # Widths: 120 pt, 367.27 pt = 487.27 pt total
    t1_data = [
        [Paragraph("उच्चारण स्थान", table_header_style), Paragraph("संबंधित वर्ण", table_header_style)],
        [Paragraph("<b>कंठ्य (Throat)</b>", table_cell_style), Paragraph("अ, आ, क-वर्ग (क, ख, ग, घ, ङ), ह, विसर्ग (अः)", table_cell_style)],
        [Paragraph("<b>तालव्य (Palate)</b>", table_cell_style), Paragraph("इ, ई, च-वर्ग (च, छ, ज, झ, ञ), य, श", table_cell_style)],
        [Paragraph("<b>मूर्धन्य (Cerebral)</b>", table_cell_style), Paragraph("ऋ, ट-वर्ग (ट, ठ, ड, ढ, ण), र, ष", table_cell_style)],
        [Paragraph("<b>दंत्य (Teeth)</b>", table_cell_style), Paragraph("त-वर्ग (त, थ, द, ध, न), ल, स", table_cell_style)],
        [Paragraph("<b>ओष्ठ्य (Lips)</b>", table_cell_style), Paragraph("उ, ऊ, प-वर्ग (प, फ, ब, भ, म)", table_cell_style)],
        [Paragraph("<b>नासिक्य (Nose)</b>", table_cell_style), Paragraph("ङ, ञ, ण, न, म, अनुस्वार (अं)", table_cell_style)],
        [Paragraph("<b>कंठतालव्य (Throat + Palate)</b>", table_cell_style), Paragraph("ए, ऐ", table_cell_style)],
        [Paragraph("<b>कंठोष्ठ्य (Throat + Lips)</b>", table_cell_style), Paragraph("ओ, औ", table_cell_style)],
        [Paragraph("<b>दंतोष्ठ्य (Teeth + Lips)</b>", table_cell_style), Paragraph("व", table_cell_style)]
    ]
    t1 = Table(t1_data, colWidths=[120, 367.27])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,0), 5),
        ('TOPPADDING', (0,0), (-1,0), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('BOTTOMPADDING', (0,1), (-1,-1), 4),
        ('TOPPADDING', (0,1), (-1,-1), 4),
    ]))
    story.append(t1)
    
    story.append(Spacer(1, 8))
    story.append(h2("घ. घोष-अघोष तथा अल्पप्राण-महाप्राण"))
    story.append(b("<b>घोष (सघोष):</b> जिनके उच्चारण में स्वर-तंत्रियों में कंपन होता है। प्रत्येक वर्ग का <b>तीसरा, चौथा, पाँचवाँ वर्ण</b> (जैसे: ग, घ, ङ), य, र, ल, व, ह तथा <b>सभी स्वर</b>।"))
    story.append(b("<b>अघोष:</b> जिनके उच्चारण में स्वर-तंत्रियों में कंपन नहीं होता। प्रत्येक वर्ग का <b>पहला और दूसरा वर्ण</b> (जैसे: क, ख, च, छ) तथा श, ष, स।"))
    story.append(b("<b>अल्पप्राण:</b> जिनके उच्चारण में मुख से कम हवा निकलती है। प्रत्येक वर्ग का <b>पहला, तीसरा, पाँचवाँ वर्ण</b> (जैसे: क, ग, ङ), य, र, ल, व तथा <b>सभी स्वर</b>।"))
    story.append(b("<b>महाप्राण:</b> जिनके उच्चारण में मुख से अधिक हवा निकलती है। प्रत्येक वर्ग का <b>दूसरा, चौथा वर्ण</b> (जैसे: ख, घ, छ, झ) तथा श, ष, स, ह।"))

    story.append(PageBreak()) # Move to next page for Topic 2

    # --- TOPIC 2: शब्द विचार ---
    story.append(h1("2. शब्द विचार (Morphology / Word Study)"))
    story.append(p("<b>शब्द (Word):</b> वर्णों के सार्थक संघात (समूह) को शब्द कहते हैं। वाक्यों में प्रयुक्त होने पर शब्द <b>'पद'</b> बन जाता है।"))
    
    story.append(h2("क. उत्पत्ति या स्रोत के आधार पर शब्द भेद:"))
    story.append(b("<b>तत्सम शब्द (Tatsam):</b> संस्कृत भाषा के वे शब्द जो हिंदी में अपने मूल रूप में प्रयुक्त होते हैं। (जैसे: अग्नि, दुग्ध, सूर्य, हस्त, दधि, रात्रि)"))
    story.append(b("<b>तद्भव शब्द (Tadbhav):</b> संस्कृत के वे शब्द जो थोड़े परिवर्तन के साथ हिंदी में प्रयुक्त होते हैं। (जैसे: आग (अग्नि), दूध (दुग्ध), सूरज (सूर्य), हाथ (हस्त), दही (दधि), रात (रात्रि))"))
    story.append(b("<b>देशज शब्द (Deshaj):</b> वे शब्द जो देश की विभिन्न बोलियों या क्षेत्रीय प्रभाव से हिंदी में आए हैं। (जैसे: लोटा, डिबिया, पगड़ी, खिचड़ी, तेंदुआ)"))
    story.append(b("<b>विदेशज (विदेशी) शब्द (Videshi):</b> जो शब्द अन्य विदेशी भाषाओं (अंग्रेजी, अरबी, फारसी, तुर्की, पुर्तगाली) से हिंदी में आए हैं। (जैसे: स्कूल, डॉक्टर, किताब, अखबार, कैंची, तोप, अलमारी, बाल्टी)"))
    story.append(b("<b>संकर शब्द (Hybrid Words):</b> दो अलग-अलग भाषाओं के शब्दों के मेल से बने शब्द। (जैसे: रेलगाड़ी (अंग्रेजी रेल + हिंदी गाड़ी), वर्षगाँठ (संस्कृत वर्ष + हिंदी गाँठ))"))
    
    story.append(h2("ख. रचना या बनावट के आधार पर शब्द भेद:"))
    story.append(b("<b>रूढ़ शब्द:</b> जिनके टुकड़े करने पर कोई अर्थ न निकले और वे किसी विशेष अर्थ के लिए प्रसिद्ध हों। (जैसे: घर, जल, पुस्तक, नल)"))
    story.append(b("<b>यौगिक शब्द:</b> जो दो या दो से अधिक सार्थक शब्दों/शब्दांशों के योग से बनते हैं। (जैसे: विद्यालय = विद्या + आलय, देवालय = देव + आलय)"))
    story.append(b("<b>योगरूढ़ शब्द:</b> जो शब्द यौगिक होते हुए भी सामान्य अर्थ को छोड़कर किसी तीसरे विशेष अर्थ को प्रकट करते हैं। (जैसे: लंबोदर (लंबा + उदर अर्थात गणेश), जलज (जल + ज अर्थात कमल), पंकज, दशानन)"))
    
    story.append(h2("ग. अर्थ के आधार पर शब्द भेद:"))
    story.append(b("<b>पर्यायवाची शब्द (Synonyms):</b> समान अर्थ देने वाले शब्द (जैसे: सूर्य - भानु, रवि, दिवाकर, दिनेश, भास्कर; कमल - जलज, पंकज, नीरज, वारिज, सरोज)"))
    story.append(b("<b>विलोम शब्द (Antonyms):</b> विपरीत अर्थ देने वाले शब्द (जैसे: दिन - रात, अमृत - विष, प्रत्यक्ष - परोक्ष, सगुण - निर्गुण)"))
    story.append(b("<b>अनेकार्थक शब्द:</b> जिसके अनेक अर्थ हों (जैसे: कनक = सोना/धतूरा/गेहूँ; कर = हाथ/टैक्स/किरण; काल = समय/मृत्यु/यमराज)"))
    story.append(b("<b>श्रुतिसमभिन्नार्थक शब्द:</b> सुनने में समान पर अर्थ में भिन्न (जैसे: अनल = आग, अनिल = हवा; गृह = घर, ग्रह = नक्षत्र)"))

    # --- TOPIC 3: संज्ञा, लिंग, वचन, कारक ---
    story.append(Spacer(1, 10))
    story.append(h1("3. संज्ञा, लिंग, वचन, कारक (Noun & Modifiers)"))
    story.append(p("<b>संज्ञा (Noun):</b> किसी व्यक्ति, वस्तु, स्थान, भाव, गुण या अवस्था के नाम को संज्ञा कहते हैं। संज्ञा के मुख्यतः <b>3 भेद</b> (कुल 5 भेद) होते हैं:"))
    story.append(b("<b>1. व्यक्तिवाचक संज्ञा:</b> जो किसी विशेष व्यक्ति, स्थान या वस्तु का बोध कराए। (जैसे: राम, हिमालय, दिल्ली, गंगा, भारत)"))
    story.append(b("<b>2. जातिवाचक संज्ञा:</b> जो पूरी जाति, वर्ग या समुदाय का बोध कराए। (जैसे: लड़का, नदी, पर्वत, पुस्तक, गाय, शहर)"))
    story.append(b("<b>क. द्रव्यवाचक संज्ञा:</b> द्रव्य, धातु या पदार्थों का बोध कराने वाले। (जैसे: सोना, ताँबा, लोहा, दूध, पानी, तेल, कोयला)"))
    story.append(b("<b>ख. समूहवाचक संज्ञा:</b> व्यक्तियों या वस्तुओं के समूह का बोध कराने वाले। (जैसे: सेना, सभा, भीड़, कक्षा, चाबी का गुच्छा, दल)"))
    story.append(b("<b>3. भाववाचक संज्ञा:</b> किसी भाव, गुण, दोष, दशा या अवस्था का बोध कराने वाले शब्द। (जैसे: बुढ़ापा, मिठास, बचपन, क्रोध, ईमानदारी, थकावट)"))
    
    story.append(h2("क. लिंग (Gender):"))
    story.append(p("संज्ञा के जिस रूप से उसके पुरुष या स्त्री होने का पता चले। हिंदी में दो लिंग हैं: <b>पुल्लिंग</b> और <b>स्त्रीलिंग</b>।"))
    story.append(b("<b>पुल्लिंग:</b> लड़का, बैल, पर्वत, पेड़, भारत, घी, दूध। (अपवाद: स्त्रीलिंग: लस्सी, छाछ, चाय, लीची आदि)"))
    story.append(b("<b>स्त्रीलिंग:</b> लड़की, गाय, नदी, भाषा, तिथि, नदी, हवा। (अपवाद: पुल्लिंग: हिमालय, प्रशांत महासागर आदि)"))
    
    story.append(h2("ख. वचन (Number):"))
    story.append(p("संज्ञा के जिस रूप से एक या अनेक होने का पता चले। हिंदी में दो वचन हैं: <b>एकवचन</b> और <b>बहुवचन</b>।"))
    story.append(b("<b>एकवचन:</b> लड़का, पुस्तक, नदी, माला, चिड़िया, कमरा।"))
    story.append(b("<b>बहुवचन:</b> लड़के, पुस्तकें, नदियाँ, मालाएँ, चिड़ियाँ, कमरे।"))
    
    story.append(PageBreak()) # Move to next page for Case (Karak)

    story.append(h2("ग. कारक (Case) - कुल 8 कारक"))
    story.append(p("संज्ञा या सर्वनाम का वाक्य में क्रिया तथा अन्य पदों के साथ संबंध स्थापित करने वाले रूप को कारक कहते हैं। इनके चिह्न <b>विभक्ति (परसर्ग)</b> कहलाते हैं।"))
    
    # Case Table
    # Widths: 90 pt, 120 pt, 277.27 pt = 487.27 pt total
    t2_data = [
        [Paragraph("कारक का नाम", table_header_style), Paragraph("विभक्ति चिह्न (परसर्ग)", table_header_style), Paragraph("अर्थ / उदाहरण वाक्य", table_header_style)],
        [Paragraph("<b>1. कर्ता (Nominative)</b>", table_cell_style), Paragraph("ने (या शून्य)", table_cell_style), Paragraph("कार्य करने वाला। जैसे: <b>राम ने</b> पुस्तक पढ़ी।", table_cell_style)],
        [Paragraph("<b>2. कर्म (Accusative)</b>", table_cell_style), Paragraph("को (या शून्य)", table_cell_style), Paragraph("जिस पर क्रिया का प्रभाव पड़े। जैसे: उसने <b>चोर को</b> पकड़ा।", table_cell_style)],
        [Paragraph("<b>3. करण (Instrumental)</b>", table_cell_style), Paragraph("से, के द्वारा", table_cell_style), Paragraph("क्रिया का साधन/माध्यम। जैसे: वह <b>कलम से</b> लिखता है।", table_cell_style)],
        [Paragraph("<b>4. संप्रदान (Dative)</b>", table_cell_style), Paragraph("को, के लिए", table_cell_style), Paragraph("जिसके लिए कार्य किया जाए। जैसे: पिता <b>बच्चों के लिए</b> खिलौने लाए।", table_cell_style)],
        [Paragraph("<b>5. अपादान (Ablative)</b>", table_cell_style), Paragraph("से (अलगाव/पृथकता)", table_cell_style), Paragraph("अलग होना, डरना, तुलना करना। जैसे: <b>पेड़ से</b> फल गिरा।", table_cell_style)],
        [Paragraph("<b>6. संबंध (Genitive)</b>", table_cell_style), Paragraph("का, की, के, रा, री, रे", table_cell_style), Paragraph("एक पद का दूसरे से संबंध। जैसे: यह <b>मोहन का</b> भाई है।", table_cell_style)],
        [Paragraph("<b>7. अधिकरण (Locative)</b>", table_cell_style), Paragraph("में, पर", table_cell_style), Paragraph("क्रिया का आधार या स्थान। जैसे: पक्षी <b>डाल पर</b> बैठे हैं।", table_cell_style)],
        [Paragraph("<b>8. संबोधन (Vocative)</b>", table_cell_style), Paragraph("हे! अरे! अजी!", table_cell_style), Paragraph("पुकारना या ध्यान आकर्षित करना। जैसे: <b>हे ईश्वर!</b> दया करो।", table_cell_style)]
    ]
    t2 = Table(t2_data, colWidths=[100, 110, 277.27])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,0), 5),
        ('TOPPADDING', (0,0), (-1,0), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('BOTTOMPADDING', (0,1), (-1,-1), 4),
        ('TOPPADDING', (0,1), (-1,-1), 4),
    ]))
    story.append(t2)
    
    story.append(Spacer(1, 8))
    story.append(p("<b>विशेष अंतर ध्यान दें (अत्यंत महत्वपूर्ण):</b>"))
    story.append(b("<b>करण और अपादान में अंतर:</b> दोनों का चिह्न 'से' है। परंतु करण कारक में 'से' का प्रयोग <b>साधन (Instrument)</b> के रूप में होता है (जैसे: वह कुल्हाड़ी से पेड़ काटता है)। अपादान कारक में 'से' का प्रयोग <b>अलग होने (Separation)</b>, डरने या तुलना करने के भाव में होता है (जैसे: वह बिल्ली से डरता है; गंगा हिमालय से निकलती है)।"))
    story.append(b("<b>कर्म और संप्रदान में अंतर:</b> दोनों में 'को' परसर्ग आता है। परंतु संप्रदान कारक में जहाँ <b>दान देने</b> या हमेशा के लिए कुछ सौंपने का भाव हो, वहाँ संप्रदान होता है (जैसे: राजा ने भिखारी को दान दिया - भिखारी संप्रदान है)। जहाँ केवल क्रिया का प्रभाव पड़ता है, वहाँ कर्म कारक होता है (जैसे: राम ने कुत्ते को डंडा मारा)।"))

    # --- TOPIC 4: सर्वनाम और विशेषण ---
    story.append(Spacer(1, 10))
    story.append(h1("4. सर्वनाम और विशेषण (Pronoun & Adjective)"))
    story.append(p("<b>सर्वनाम (Pronoun):</b> संज्ञा के स्थान पर प्रयुक्त होने वाले शब्दों को सर्वनाम कहते हैं। मूल सर्वनामों की संख्या <b>11</b> है (मैं, तू, आप, यह, वह, जो, सो, कोई, कुछ, कौन, क्या)। सर्वनाम के <b>6 भेद</b> हैं:"))
    story.append(b("<b>1. पुरुषवाचक सर्वनाम:</b> वक्ता, श्रोता या अन्य के लिए। इसके तीन उपभेद हैं: <b>उत्तम पुरुष</b> (मैं, हम), <b>मध्यम पुरुष</b> (तू, तुम, आप), <b>अन्य पुरुष</b> (वह, वे, यह, ये)।"))
    story.append(b("<b>2. निश्चयवाचक सर्वनाम:</b> पास या दूर की निश्चित वस्तु या व्यक्ति के लिए। (जैसे: <b>यह</b> मेरी कार है; <b>वह</b> सोहन का घर है)"))
    story.append(b("<b>3. अनिश्चयवाचक सर्वनाम:</b> जिससे किसी निश्चित व्यक्ति या वस्तु का बोध न हो। (जैसे: बाहर <b>कोई</b> खड़ा है; दाल में <b>कुछ</b> गिरा है)"))
    story.append(b("<b>4. संबंधवाचक सर्वनाम:</b> जो वाक्य में दूसरे सर्वनामों से संबंध दर्शाएं। (जैसे: <b>जो</b> बोएगा, <b>सो</b> काटेगा; <b>जैसी</b> करनी, <b>वैसी</b> भरनी)"))
    story.append(b("<b>5. प्रश्नवाचक सर्वनाम:</b> प्रश्न पूछने के लिए। (जैसे: तुम <b>क्या</b> कर रहे हो? वहाँ <b>कौन</b> आया है?)"))
    story.append(b("<b>6. निजवाचक सर्वनाम:</b> कर्ता के अपने स्वयं के भाव को व्यक्त करने के लिए। (जैसे: मैं अपना काम <b>स्वयं/खुद/अपने आप</b> करूँगा)"))
    
    story.append(Spacer(1, 5))
    story.append(p("<b>विशेषण (Adjective):</b> संज्ञा या सर्वनाम की विशेषता (गुण, संख्या, मात्रा आदि) बताने वाले शब्दों को विशेषण कहते हैं। जिसकी विशेषता बताई जाए, वह <b>विशेष्य</b> कहलाता है। विशेषण के <b>4 प्रमुख भेद</b> हैं:"))
    story.append(b("<b>1. गुणवाचक विशेषण:</b> संज्ञा/सर्वनाम के गुण, दोष, रंग, आकार, दशा का बोध कराए। (जैसे: सुंदर लड़की, ईमानदार बालक, गोल मेज, काला घोड़ा)"))
    story.append(b("<b>2. संख्यावाचक विशेषण:</b> संज्ञा/सर्वनाम की संख्या का बोध कराए। इसके दो उपभेद हैं: <b>निश्चित संख्यावाचक</b> (चार लड़के, पहला स्थान) और <b>अनिश्चित संख्यावाचक</b> (कुछ लोग, कई पुस्तकें)।"))
    story.append(b("<b>3. परिमाणवाचक विशेषण:</b> माप-तोल, मात्रा या वजन का बोध कराए। इसके भी दो उपभेद हैं: <b>निश्चित परिमाणवाचक</b> (दो किलो चीनी, पाँच मीटर कपड़ा) और <b>अनिश्चित परिमाणवाचक</b> (थोड़ा दूध, बहुत सारा अनाज)।"))
    story.append(b("<b>4. सार्वनामिक (संकेतवाचक) विशेषण:</b> जब कोई सर्वनाम संज्ञा से ठीक पहले आकर विशेषण की तरह काम करे। (जैसे: <b>यह</b> घर मेरा है; <b>वह</b> लड़का बहुत चतुर है - यहाँ 'यह' और 'वह' सार्वनामिक विशेषण हैं)"))
    story.append(b("<b>प्रविशेषण (Pradjective):</b> जो शब्द विशेषण की भी विशेषता बताते हैं। (जैसे: वह <b>बहुत</b> तेज दौड़ता है; चाय <b>अत्यंत</b> गर्म है - यहाँ 'बहुत' और 'अत्यंत' प्रविशेषण हैं)"))
    story.append(b("<b>विशेषण की तीन अवस्थाएँ:</b> <b>मूलावस्था</b> (लघु, उच्च), <b>उत्तरावस्था</b> (लघुतर, उच्चतर), <b>उत्तमावस्था</b> (लघुतम, उच्चतम) - क्रमशः Positive, Comparative, Superlative डिग्री हैं।"))

    story.append(PageBreak()) # Move to next page for Verbs and Tenses

    # --- TOPIC 5: क्रिया, काल, वाच्य ---
    story.append(h1("5. क्रिया, काल, वाच्य (Verb, Tense, Voice)"))
    story.append(p("<b>क्रिया (Verb):</b> जिस शब्द से किसी कार्य के होने या करने का बोध हो, उसे क्रिया कहते हैं। क्रिया का मूल रूप <b>धातु (Root)</b> कहलाता है (जैसे: पढ़, लिख)। धातु में 'ना' जोड़ने पर क्रिया बनती है (पढ़ना, लिखना)।"))
    
    story.append(h2("क. कर्म के आधार पर क्रिया के भेद:"))
    story.append(b("<b>1. अकर्मक क्रिया (Intransitive Verb):</b> जिस क्रिया का फल सीधा कर्ता पर पड़े, जिसमें कर्म की आवश्यकता नहीं होती। (जैसे: राम सोता है; पक्षी उड़ते हैं; बालक हँसता है)"))
    story.append(b("<b>2. सकर्मक क्रिया (Transitive Verb):</b> जिस क्रिया में कर्म होता है और क्रिया का फल कर्म पर पड़ता है। (जैसे: मोहन आम खाता है; सीता पत्र लिखती है)"))
    story.append(p("<i>सकर्मक क्रिया के दो भेद हैं:</i> <b>एककर्मक</b> (एक कर्म - जैसे: वह पुस्तक पढ़ता है) और <b>द्विकर्मक</b> (दो कर्म - जैसे: शिक्षक ने <b>छात्रों को</b> <b>हिंदी</b> पढ़ाई - यहाँ 'छात्रों' और 'हिंदी' दो कर्म हैं)।"))
    
    story.append(h2("ख. रचना या प्रयोग के आधार पर क्रिया के भेद:"))
    story.append(b("<b>संयुक्त क्रिया:</b> दो या अधिक क्रियाओं के मेल से बनी क्रिया। (जैसे: वह रोने लगा; उसने खाना खा लिया)"))
    story.append(b("<b>नामधातु क्रिया:</b> संज्ञा, सर्वनाम या विशेषण शब्दों से बनने वाली क्रियाएँ। (जैसे: हाथ -> हथियाना; बात -> बतियाना; गरम -> गरमाना; लाठी -> लठियाना)"))
    story.append(b("<b>प्रेरणार्थक क्रिया:</b> जहाँ कर्ता स्वयं कार्य न करके किसी दूसरे को कार्य करने के लिए प्रेरित करता है। इसके दो रूप हैं: <b>प्रथम प्रेरणार्थक</b> (जैसे: पढ़ाना, कराना) और <b>द्वितीय प्रेरणार्थक</b> (जैसे: पढ़वाना, करवाना)।"))
    story.append(b("<b>पूर्वकालिक क्रिया:</b> जब कर्ता एक क्रिया समाप्त करके दूसरी क्रिया शुरू करता है, तो पहली क्रिया पूर्वकालिक कहलाती है। (जैसे: वह <b>खाकर</b> सो गया - यहाँ 'खाकर' पूर्वकालिक क्रिया है)"))
    story.append(b("<b>कृदंत क्रिया:</b> क्रिया शब्दों में प्रत्यय जोड़कर बनी क्रियाएँ। (जैसे: चलता, दौड़ता, लिखकर)"))
    
    story.append(Spacer(1, 4))
    story.append(h2("ग. काल (Tense) - क्रिया का समय"))
    
    # Tense Table
    # Widths: 90 pt, 150 pt, 247.27 pt = 487.27 pt total
    t3_data = [
        [Paragraph("काल का मुख्य भेद", table_header_style), Paragraph("उपभेद", table_header_style), Paragraph("उदाहरण वाक्य", table_header_style)],
        [Paragraph("<b>1. भूतकाल (Past)</b>", table_cell_style), Paragraph("सामान्य भूत<br/>आसन्न भूत<br/>पूर्ण भूत<br/>अपूर्ण भूत<br/>संदिग्ध भूत<br/>हेतुहेतुमद् भूत", table_cell_style), Paragraph("राम ने पत्र लिखा।<br/>राम ने पत्र लिखा है (अभी-अभी)।<br/>राम ने पत्र लिखा था (बहुत पहले)।<br/>राम पत्र लिख रहा था।<br/>राम ने पत्र लिखा होगा (संदेह)।<br/>यदि तुम पढ़ते, तो उत्तीर्ण हो जाते (आश्रित)।", table_cell_style)],
        [Paragraph("<b>2. वर्तमानकाल (Present)</b>", table_cell_style), Paragraph("सामान्य वर्तमान<br/>तात्कालिक (अपूर्ण)<br/>पूर्ण वर्तमान<br/>संदिग्ध वर्तमान<br/>संभाव्य वर्तमान", table_cell_style), Paragraph("राम पत्र लिखता है।<br/>राम पत्र लिख रहा है (जारी)।<br/>राम ने पत्र लिखा है।<br/>राम पत्र लिखता होगा (संदेह)।<br/>शायद राम पत्र लिखता हो।", table_cell_style)],
        [Paragraph("<b>3. भविष्यतकाल (Future)</b>", table_cell_style), Paragraph("सामान्य भविष्यत<br/>संभाव्य भविष्यत<br/>हेतुहेतुमद् भविष्यत", table_cell_style), Paragraph("राम पत्र लिखेगा।<br/>शायद राम कल पत्र लिखे।<br/>यदि तुम बुलाओगे, तो मैं आऊँगा।", table_cell_style)]
    ]
    t3 = Table(t3_data, colWidths=[100, 140, 247.27])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,0), 5),
        ('TOPPADDING', (0,0), (-1,0), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('BOTTOMPADDING', (0,1), (-1,-1), 4),
        ('TOPPADDING', (0,1), (-1,-1), 4),
    ]))
    story.append(t3)
    
    story.append(Spacer(1, 8))
    story.append(h2("घ. वाच्य (Voice):"))
    story.append(p("क्रिया के जिस रूप से यह जाना जाए कि वाक्य में क्रिया का मुख्य विषय कर्ता है, कर्म है या भाव। इसके 3 भेद हैं:"))
    story.append(b("<b>1. कर्तृवाच्य (Active Voice):</b> क्रिया का संबंध कर्ता से होता है, क्रिया का लिंग-वचन कर्ता के अनुसार बदलता है। (जैसे: <b>राम</b> पुस्तक पढ़ता है; <b>सीता</b> फल खाती है)"))
    story.append(b("<b>2. कर्मवाच्य (Passive Voice):</b> क्रिया कर्म के अनुसार चलती है। कर्ता के बाद 'से' या 'के द्वारा' लगता है। (जैसे: राम <b>के द्वारा</b> पुस्तक पढ़ी जाती है; सीता <b>से</b> फल खाया जाता है)"))
    story.append(b("<b>3. भाववाच्य (Impersonal Voice):</b> क्रिया वाक्य के भाव (निषेध/असमर्थता) के अनुसार सदा पुल्लिंग, एकवचन, अन्य पुरुष में होती है। अकर्मक क्रियाओं से बनता है। (जैसे: मुझसे अब <b>चला नहीं जाता</b>; पक्षियों से <b>उड़ा जाता है</b>)"))

    story.append(Spacer(1, 10))
    # --- TOPIC 6: अव्यय या अविकारी शब्द ---
    story.append(h1("6. अव्यय या अविकारी शब्द (Indeclinables)"))
    story.append(p("जिन शब्दों के रूप में लिंग, वचन, कारक या काल के कारण कोई परिवर्तन (विकार) नहीं होता, वे <b>अव्यय</b> कहलाते हैं। इनके 5 प्रमुख भेद हैं:"))
    story.append(b("<b>1. क्रियाविशेषण (Adverb):</b> जो क्रिया की विशेषता बताते हैं। इसके 4 भेद हैं: <b>कालवाचक</b> (आज, कल, सदा), <b>स्थानवाचक</b> (यहाँ, वहाँ, ऊपर, नीचे), <b>परिमाणवाचक</b> (कम, बहुत, थोड़ा, ज़रा), <b>रीतिवाचक</b> (धीरे-धीरे, अचानक, ध्यानपूर्वक, तेज)।"))
    story.append(b("<b>2. संबंधबोधक अव्यय (Postpositions):</b> जो संज्ञा/सर्वनाम के बाद आकर वाक्य के अन्य पदों से संबंध दर्शाते हैं। (যেমন: घर <b>के पीछे</b> बगीचा है; राम <b>के बिना</b> मैं नहीं जाऊँगा)"))
    story.append(b("<b>3. समुच्चयबोधक अव्यय (Conjunctions):</b> दो शब्दों या वाक्यों को जोड़ने वाले। (जैसे: और, किंतु, परंतु, क्योंकि, इसलिए, या, अथवा)"))
    story.append(b("<b>4. विस्मयादिबोधक अव्यय (Interjections):</b> हर्ष, शोक, घृणा, आश्चर्य आदि व्यक्त करने वाले। (जैसे: अरे!, वाह!, हाय!, छी!)"))
    story.append(b("<b>5. निपात (Particles):</b> जो किसी पद के बाद लगकर उस पर विशेष बल देते हैं। (जैसे: <b>ही, भी, तक, तो, मात्र, भर</b> - वह <b>भी</b> पढ़ेगा; राम <b>ही</b> जाएगा; उसने बात <b>तक</b> नहीं की)"))

    story.append(PageBreak()) # Move to next page for Sandhi

    # --- TOPIC 7: संधि ---
    story.append(h1("7. संधि (Sandhi - Word Junction)"))
    story.append(p("<b>संधि:</b> दो निकटवर्ती वर्णों के मेल से जो विकार (परिवर्तन) उत्पन्न होता है, उसे संधि कहते हैं। संधि के <b>3 भेद</b> हैं:"))
    
    story.append(h2("क. स्वर संधि (Vowel Sandhi) - दो स्वरों का मेल (इसके 5 उपभेद हैं):"))
    story.append(b("<b>1. दीर्घ संधि:</b> ह्रस्व या दीर्घ अ, इ, उ जब परस्पर मिलते हैं तो दीर्घ (आ, ई, ऊ) बन जाते हैं। (अ/आ + अ/आ = आ; इ/ई + इ/ई = ई; उ/ऊ + उ/ऊ = ऊ)<br/>• हिम + आलय = <b>हिमालय</b>; रवि + इंद्र = <b>रवींद्र</b>; भानु + उदय = <b>भानूदय</b>"))
    story.append(b("<b>2. गुण संधि:</b> अ/आ के बाद इ/ई आए तो 'ए', उ/ऊ आए तो 'ओ' तथा ऋ आए तो 'अर' हो जाता है।<br/>• देव + इंद्र = <b>देवेन्द्र</b>; महा + उत्सव = <b>महोत्सव</b>; देव + ऋषि = <b>देवर्षि</b>"))
    story.append(b("<b>3. वृद्धि संधि:</b> अ/आ के बाद ए/ऐ आए तो 'ऐ' तथा ओ/औ आए तो 'औ' हो जाता है।<br/>• एक + एक = <b>एकैक</b>; सदा + एव = <b>सदैव</b>; वन + औषधि = <b>वनौषधि</b>"))
    story.append(b("<b>4. यण संधि:</b> इ/ई का 'य्', उ/ऊ का 'व्' और ऋ का 'र्' हो जाता है, जब इनके बाद कोई असमान स्वर आए।<br/>• अति + अधिक = <b>अत्यधिक</b>; सु + आगत = <b>स्वागत</b>; पितृ + आज्ञा = <b>पित्राज्ञा</b>"))
    story.append(b("<b>5. अयादि संधि:</b> ए, ऐ, ओ, औ के बाद कोई भिन्न स्वर आए तो वे क्रमशः 'अय', 'आय', 'अव', 'आव' में बदल जाते हैं।<br/>• ने + अन = <b>नयन</b>; नै + अक = <b>नायक</b>; पो + अन = <b>पवन</b>; पौ + अक = <b>पावक</b>"))
    
    story.append(h2("ख. व्यंजन संधि (Consonant Sandhi):"))
    story.append(p("व्यंजन का व्यंजन से या किसी स्वर से मेल होने पर जो परिवर्तन होता है, उसे व्यंजन संधि कहते हैं। इसके कुछ प्रमुख नियम हैं:"))
    story.append(b("वर्ग के पहले वर्ण का तीसरे वर्ण में परिवर्तन (क् -> ग्, च् -> ज्, ट् -> ड्, त् -> द्, प् -> ब्)।<br/>• दिक् + अंबर = <b>दिगंबर</b>; वाक् + ईश = <b>वागीश</b>; जगत् + ईश = <b>जगदीश</b>"))
    story.append(b("वर्ग के पहले वर्ण का पाँचवें वर्ण में परिवर्तन (क् -> ङ्, त् -> न्)।<br/>• वाक् + मय = <b>वाङ्मय</b>; जगत् + नाथ = <b>जगन्नाथ</b>; उत् + नति = <b>उन्नति</b>"))
    story.append(b("त् संबंधी नियम (त् के बाद च/छ हो तो च्, ज/झ हो तो ज्, ल हो तो ल् हो जाता है)।<br/>• उत् + चारण = <b>उच्चारण</b>; सत् + जन = <b>सज्जन</b>; उत् + लेख = <b>उल्लेख</b>"))
    story.append(b("म् संबंधी नियम (म् के बाद कोई स्पर्श व्यंजन आए तो म् अनुस्वार (ं) या पंचम वर्ण में बदल जाता है)।<br/>• सम् + कल्प = <b>संकल्प</b>; सम् + तोष = <b>संतोष</b>; सम् + पूर्ण = <b>संपूर्ण</b>"))
    
    story.append(h2("ग. विसर्ग संधि (Visarga Sandhi):"))
    story.append(p("विसर्ग (ः) के साथ स्वर या व्यंजन के मेल से जो परिवर्तन होता है, उसे विसर्ग संधि कहते हैं। इसके प्रमुख नियम हैं:"))
    story.append(b("विसर्ग का 'ओ' हो जाना (यदि विसर्ग से पहले 'अ' हो और बाद में सघोष वर्ण हो)।<br/>• मनः + हर = <b>मनोहर</b>; यशः + दा = <b>यशोदा</b>; तपः + बल = <b>तपोबल</b>"))
    story.append(b("विसर्ग का 'र' हो जाना (यदि विसर्ग से पहले अ/आ से भिन्न स्वर हो और बाद में स्वर या सघोष वर्ण हो)।<br/>• निः + धन = <b>निर्धन</b>; दुः + बल = <b>दुर्बल</b>; निः + आशा = <b>निराशा</b>"))
    story.append(b("विसर्ग का 'श, ष, स' हो जाना।<br/>• निः + चल = <b>निश्चल</b>; दुः + कर = <b>दुष्कर</b>; नमः + ते = <b>नमस्ते</b>; निः + संदेह = <b>निःसंदेह</b>"))
    story.append(b("विसर्ग का लोप और ह्रस्व स्वर का दीर्घ हो जाना।<br/>• निः + रोग = <b>निरोग</b>; निः + रस = <b>नीरस</b>"))

    # --- TOPIC 8: समास ---
    story.append(Spacer(1, 10))
    story.append(h1("8. समास (Samas - Compound Words)"))
    story.append(p("<b>समास:</b> दो या दो से अधिक शब्दों को मिलाकर संक्षिप्त करने की प्रक्रिया को समास कहते हैं। समास विग्रह पदों को पुनः अलग-अलग करने को कहते हैं। इसके <b>6 मुख्य भेद</b> हैं:"))
    story.append(b("<b>1. अव्ययीभाव समास:</b> प्रथम पद प्रधान और अव्यय होता है। पूरा पद क्रियाविशेषण अव्यय की तरह काम करता है। (जैसे: <b>यथाशक्ति</b> = शक्ति के अनुसार; <b>आजन्म</b> = जन्म भर; <b>प्रतिदिन</b> = प्रत्येक दिन; <b>रातोंरात</b> = रात ही रात में)"))
    story.append(b("<b>2. तत्पुरुष समास:</b> उत्तर पद (दूसरा पद) प्रधान होता है और विग्रह करने पर कारक चिह्न (ने को छोड़कर अन्य) प्रकट होते हैं।<br/>• <b>कर्म तत्पुरुष:</b> यशप्राप्त = यश को प्राप्त | <b>करण तत्पुरुष:</b> हस्तलिखित = हाथ से लिखित<br/>• <b>संप्रदान तत्पुरुष:</b> रसोईघर = रसोई के लिए घर | <b>अपादान तत्पुरुष:</b> पथभ्रष्ट = पथ से भ्रष्ट<br/>• <b>संबंध तत्पुरुष:</b> राजपुत्र = राजा का पुत्र | <b>अधिकरण तत्पुरुष:</b> घुड़सवार = घोड़े पर सवार<br/>• <i>विशेष उपभेद - नञ् तत्पुरुष (नकारात्मक):</i> अधर्म = न धर्म; असभ्य = न सभ्य; अनहोनी = न होनी"))
    story.append(b("<b>3. कर्मधारय समास:</b> दोनों पदों में विशेषण-विशेष्य या उपमेय-उपमान का संबंध होता है। (जैसे: <b>नीलकमल</b> = नीला है जो कमल; <b>चंद्रमुख</b> = चंद्रमा के समान मुख; <b>चरणकमल</b> = कमल रूपी चरण; <b>महात्मा</b> = महान है जो आत्मा)"))
    story.append(b("<b>4. द्विगु समास:</b> पहला पद संख्यावाचक विशेषण होता है और वह किसी समूह या समाहार का बोध कराता है। (जैसे: <b>चौराहा</b> = चार राहों का समूह; <b>त्रिफला</b> = तीन फलों का समूह; <b>नवग्रह</b> = नौ ग्रहों का समूह; <b>शताब्दी</b> = सौ वर्षों का समूह)"))
    story.append(b("<b>5. द्वंद्व समास:</b> दोनों पद प्रधान होते हैं, विग्रह करने पर 'और', 'या', 'अथवा' लगता है। (जैसे: <b>माता-पिता</b> = माता और पिता; <b>रात-दिन</b> = रात और दिन; <b>पाप-पुण्य</b> = पाप या पुण्य; <b>भला-बुरा</b> = भला या बुरा)"))
    story.append(b("<b>6. बहुव्रीहि समास:</b> कोई भी पद प्रधान नहीं होता, दोनों पद मिलकर किसी तीसरे अन्य अर्थ का बोध कराते हैं। (जैसे: <b>दशानन</b> = दस मुख हैं जिसके अर्थात रावण; <b>पीतांबर</b> = पीले वस्त्र हैं जिसके अर्थात श्रीकृष्ण; <b>लंबोदर</b> = लंबा पेट है जिसका अर्थात श्री गणेश; <b>त्रिलोचन</b> = तीन आँखें हैं जिसकी अर्थात शिव)"))

    story.append(PageBreak()) # Move to next page for Syntax and Poetics

    # --- TOPIC 9: वाक्य विचार ---
    story.append(h1("9. वाक्य विचार (Syntax / Sentence Study)"))
    story.append(p("<b>वाक्य (Sentence):</b> सार्थक शब्दों का वह व्यवस्थित समूह जिससे वक्ता का पूर्ण अभिप्राय स्पष्ट होता है। वाक्य के दो मुख्य अंग हैं: <b>उद्देश्य (Subject)</b> (जिसके बारे में बात की जाए) और <b>विधेय (Predicate)</b> (उद्देश्य के बारे में जो कहा जाए)। (जैसे: 'राम पुस्तक पढ़ता है' में 'राम' उद्देश्य है, और 'पुस्तक पढ़ता है' विधेय है)।"))
    
    story.append(h2("क. रचना के आधार पर वाक्य भेद (3 भेद - अत्यंत महत्वपूर्ण):"))
    story.append(b("<b>1. सरल या साधारण वाक्य:</b> जिस वाक्य में केवल एक उद्देश्य और एक ही विधेय (एक ही मुख्य क्रिया) हो। (जैसे: राम पुस्तक पढ़ता है; बच्चे मैदान में फुटबॉल खेल रहे हैं)"))
    story.append(b("<b>2. संयुक्त वाक्य:</b> जिसमें दो या अधिक स्वतंत्र उपवाक्य समानाधिकरण अव्ययों (और, परंतु, किंतु, इसलिए, या, अथवा) से जुड़े हों। (जैसे: वह सुबह गया <b>और</b> शाम को घर लौट आया; मैंने मेहनत की <b>परंतु</b> सफल न हो सका)"))
    story.append(b("<b>3. मिश्र या मिश्रित वाक्य:</b> जिसमें एक मुख्य वाक्य (Principal Clause) हो और अन्य उपवाक्य उस पर आश्रित (Dependent) हों। (जैसे: जैसे ही शिक्षक आए, वैसे ही छात्र खड़े हो गए; गांधीजी ने कहा कि सदा सत्य बोलो)<br/>• <b>संज्ञा उपवाक्य:</b> जो 'कि' से जुड़े हों (जैसे: मैं जानता हूँ कि वह ईमानदार है)।<br/>• <b>विशेषण उपवाक्य:</b> जो मुख्य वाक्य के संज्ञा/सर्वनाम की विशेषता बताएं, 'जो, जिसने' से जुड़े हों (जैसे: जो कल आया था, वह मेरा मित्र है)।<br/>• <b>क्रियाविशेषण उपवाक्य:</b> जो मुख्य वाक्य की क्रिया की विशेषता (समय, स्थान आदि) बताएं, 'जब...तब, जहाँ...वहाँ' से जुड़े हों।"))
    
    story.append(h2("ख. अर्थ के आधार पर वाक्य भेद (8 भेद):"))
    story.append(b("<b>1. विधानवाचक:</b> सामान्य जानकारी देने वाले। (जैसे: सूर्य पूर्व से उदय होता है)"))
    story.append(b("<b>2. निषेधवाचक:</b> कार्य न होने का बोध कराने वाले। (जैसे: राम ने आज गृहकार्य नहीं किया)"))
    story.append(b("<b>3. प्रश्नवाचक:</b> प्रश्न पूछने वाले। (जैसे: तुम कहाँ जा रहे हो?)"))
    story.append(b("<b>4. आज्ञावाचक:</b> आज्ञा, प्रार्थना, अनुमति देने वाले। (जैसे: तुम यहाँ से बाहर जाओ; कृपया शांत रहें)"))
    story.append(b("<b>5. विस्मयादिवाचक:</b> आश्चर्य, हर्ष, घृणा आदि दर्शाने वाले। (जैसे: अरे! कितना सुंदर दृश्य है!)"))
    story.append(b("<b>6. इच्छावाचक:</b> इच्छा, शुभकामना, आशीर्वाद प्रकट करने वाले। (जैसे: नव वर्ष मंगलमय हो; भगवान कल्याण करे)"))
    story.append(b("<b>7. संदेहवाचक:</b> कार्य होने में संदेह या संभावना का बोध कराने वाले। (जैसे: शायद आज वर्षा होगी)"))
    story.append(b("<b>8. संकेतवाचक:</b> जहाँ एक क्रिया का होना दूसरी क्रिया पर निर्भर हो। (जैसे: यदि तुम परिश्रम करोगे, तो सफल हो जाओगे)"))

    # --- TOPIC 10: काव्य शास्त्र ---
    story.append(Spacer(1, 10))
    story.append(h1("10. काव्य शास्त्र (Poetics - DSC & TET Special)"))
    story.append(p("<b>रस (Rasa):</b> काव्य को पढ़ने, सुनने या नाटक देखने से प्राप्त होने वाले आनंद को रस कहते हैं। रस के 4 अंग हैं: <b>स्थायी भाव</b> (हृदय में स्थायी रहने वाले भाव), <b>विभाव</b> (स्थायी भाव जगाने वाले कारण), <b>अनुभाव</b> (शारीरिक चेष्टाएँ), <b>संचारी भाव</b> (मन में आने-जाने वाले क्षणिक भाव, कुल संख्या: 33)।"))
    
    # Rasa Table
    # Widths: 240 pt, 247.27 pt = 487.27 pt total
    t4_data = [
        [Paragraph("रस का नाम", table_header_style), Paragraph("स्थायी भाव", table_header_style)],
        [Paragraph("<b>1. श्रृंगार रस</b> (रसों का राजा / रसराज)", table_cell_style), Paragraph("रति (प्रेम)", table_cell_style)],
        [Paragraph("<b>2. वीर रस</b>", table_cell_style), Paragraph("उत्साह", table_cell_style)],
        [Paragraph("<b>3. करुण रस</b>", table_cell_style), Paragraph("शोक", table_cell_style)],
        [Paragraph("<b>4. हास्य रस</b>", table_cell_style), Paragraph("हास (हँसी)", table_cell_style)],
        [Paragraph("<b>5. रौद्र रस</b>", table_cell_style), Paragraph("क्रोध", table_cell_style)],
        [Paragraph("<b>6. भयानक रस</b>", table_cell_style), Paragraph("भय", table_cell_style)],
        [Paragraph("<b>7. वीभत्स रस</b>", table_cell_style), Paragraph("जुगुप्सा (घृणा)", table_cell_style)],
        [Paragraph("<b>8. अद्भुत रस</b>", table_cell_style), Paragraph("विस्मय (आश्चर्य)", table_cell_style)],
        [Paragraph("<b>9. शांत रस</b>", table_cell_style), Paragraph("निर्वेद (उदासीनता)", table_cell_style)],
        [Paragraph("<b>10. वात्सल्य रस</b>", table_cell_style), Paragraph("वत्सलता (बच्चों के प्रति स्नेह)", table_cell_style)],
        [Paragraph("<b>11. भक्ति रस</b>", table_cell_style), Paragraph("भगवद् अनुराग / अनुराग", table_cell_style)]
    ]
    t4 = Table(t4_data, colWidths=[240, 247.27])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,0), 4),
        ('TOPPADDING', (0,0), (-1,0), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('BOTTOMPADDING', (0,1), (-1,-1), 3),
        ('TOPPADDING', (0,1), (-1,-1), 3),
    ]))
    story.append(t4)

    story.append(PageBreak()) # Move to next page for Alankars and Extras

    story.append(h2("अलंकार (Alankar - Figures of Speech)"))
    story.append(p("काव्य की शोभा बढ़ाने वाले धर्मों या तत्वों को अलंकार कहते हैं। इसके मुख्य दो भेद हैं:"))
    
    story.append(p("<b>1. शब्दालंकार (चमत्कार शब्दों में हो):</b>"))
    story.append(b("<b>अनुप्रास अलंकार:</b> जहाँ एक ही वर्ण की आवृत्ति बार-बार हो। (जैसे: <b>चा</b>रु <b>चं</b>द्र की <b>चं</b>चल किरणें; <b>त</b>रनि <b>त</b>नूजा <b>त</b>ट <b>त</b>माल <b>त</b>रुवर बहु छाए)"))
    story.append(b("<b>यमक अलंकार:</b> जहाँ एक ही शब्द दो या दो से अधिक बार प्रयुक्त हो और हर बार उसका अर्थ अलग हो। (जैसे: <b>कनक कनक</b> ते सौ गुनी मादकता अधिकाय - यहाँ पहले कनक का अर्थ धतूरा और दूसरे कनक का अर्थ सोना है)"))
    story.append(b("<b>श्लेष अलंकार:</b> जहाँ एक शब्द एक ही बार प्रयुक्त हो परंतु उसके अर्थ कई निकलें। (जैसे: रहिमन <b>पानी</b> राखिए, बिन पानी सब सून, <b>पानी</b> गए न ऊबरे, मोती मानुष चून - यहाँ पानी के तीन अर्थ हैं: चमक (मोती के लिए), प्रतिष्ठा (मनुष्य के लिए), जल (चूने/आटे के लिए))"))
    
    story.append(p("<b>2. अर्थालंकार (चमत्कार अर्थ में हो):</b>"))
    story.append(b("<b>उपमा अलंकार:</b> जहाँ किसी वस्तु या व्यक्ति की तुलना दूसरे समान गुण वाले से की जाए। इसके वाचक शब्द हैं: सा, सी, से, सम, सरिस। (जैसे: पीपर पात <b>सरिस</b> मन डोला - मन की तुलना पीपल के पत्ते से)"))
    story.append(b("<b>रूपक अलंकार:</b> जहाँ उपमेय और उपमान में कोई भेद न करके अभेद आरोप किया जाए (दोनों को एक मान लिया जाए)। (जैसे: मैया मैं तो <b>चंद्र-खिलौना</b> लैहूँ - चन्द्रमा रूपी खिलौना; <b>चरण-कमल</b> बंदौ हरिराई)"))
    story.append(b("<b>उत्प्रेक्षा अलंकार:</b> जहाँ उपमेय में उपमान की संभावना या कल्पना की जाए। इसके वाचक शब्द हैं: मानो, मनु, जानो, जनु। (जैसे: सोहत ओढ़े पीत पट... <b>मनहुँ</b> नीलमनि सैल पर आतपु पर्यो प्रभात)"))
    story.append(b("<b>अतिशयोक्ति अलंकार:</b> जहाँ किसी बात का लोक-सीमा से अधिक बढ़ा-चढ़ाकर वर्णन किया जाए। (जैसे: हनुमान की पूँछ में लगन न पाई आग, लंका सिगरी जल गई गए निसाचर भाग)"))
    story.append(b("<b>मानवीकरण अलंकार:</b> जहाँ जड़ (प्रकृति, पेड़, बादल) पर चेतन मानवीय क्रियाओं का आरोप किया जाए। (जैसे: मेघ आए बड़े बन-ठन के सँवर के; फूल हँसे कलियाँ मुसकाईं)"))
    
    story.append(h2("छंद (Chhand - Metre)"))
    story.append(p("अक्षरों, मात्राओं, यति, गति और लय से बद्ध रचना को छंद कहते हैं। परीक्षा की दृष्टि से मुख्य मात्रिक छंद निम्नलिखित हैं:"))
    story.append(b("<b>दोहा:</b> यह अर्धसम मात्रिक छंद है। इसके प्रथम और तृतीय चरण में <b>13-13 मात्राएँ</b> तथा द्वितीय और चतुर्थ चरण में <b>11-11 मात्राएँ</b> होती हैं।<br/>• रहिमन धागा प्रेम का, मत तोड़ो चटकाय। टूटे से फिर ना मिले, मिले गाँठ परि जाय।"))
    story.append(b("<b>सोरठा:</b> यह दोहा का ठीक विपरीत छंद है। इसके विषम (प्रथम व तृतीय) चरणों में <b>11-11 मात्राएँ</b> तथा सम (द्वितीय व चतुर्थ) चरणों में <b>13-13 मात्राएँ</b> होती हैं।"))
    story.append(b("<b>चौपाई:</b> यह सम मात्रिक छंद है। इसके प्रत्येक चरण में <b>16-16 मात्राएँ</b> होती हैं।<br/>• जय हनुमान ज्ञान गुन सागर, जय कपीस तिहुं लोक उजागर।"))

    # --- TOPIC 11: उपसर्ग, प्रत्यय, विराम चिह्न और मुहावरे ---
    story.append(Spacer(1, 10))
    story.append(h1("11. उपसर्ग, प्रत्यय, विराम चिह्न, मुहावरे (Formation & Miscellany)"))
    story.append(b("<b>उपसर्ग (Prefix):</b> वे शब्दांश जो किसी शब्द के शुरू में लगकर नया शब्द बनाते हैं। (जैसे: <b>अति</b> + अधिक = अत्यधिक; <b>उप</b> + कार = उपकार; <b>निर्</b> + धन = निर्धन; <b>सु</b> + यश = सुयश)"))
    story.append(b("<b>प्रत्यय (Suffix):</b> वे शब्दांश जो शब्दों के अंत में लगकर नया अर्थ देते हैं। इसके 2 भेद हैं: <b>कृत् प्रत्यय</b> (क्रिया/धातु के अंत में - जैसे: लिख + <b>आवट</b> = लिखावट) और <b>तद्धित प्रत्यय</b> (संज्ञा/विशेषण के अंत में - जैसे: मानव + <b>ता</b> = मानवता; मीठा + <b>आस</b> = मिठास)"))
    story.append(b("<b>विराम चिह्न:</b> वाक्यों में रुकने या अर्थ स्पष्ट करने वाले चिह्न। जैसे: <b>पूर्ण विराम (।)</b>, <b>अल्प विराम (,)</b>, <b>अर्ध विराम (;)</b>, <b>प्रश्नवाचक (?)</b>, <b>विस्मयादिबोधक (!)</b>, <b>योजक (-)</b>, <b>उद्धरण चिह्न (“ ”)</b>।"))
    story.append(b("<b>मुहावरे और लोकोक्तियाँ:</b><br/>• <b>मुहावरा:</b> वाक्यांश होता है जो लाक्षणिक अर्थ देता है। (जैसे: <i>अंगूठा दिखाना</i> = ऐन वक्त पर मना करना; <i>नौ दो ग्यारह होना</i> = भाग जाना)<br/>• <b>लोकोक्ति:</b> समाज के अनुभवों पर आधारित पूर्ण वाक्य होती है। (जैसे: <i>अधजल गगरी छलकत जाए</i> = ओछा व्यक्ति अधिक दिखावा करता है; <i>हाथ कंगन को आरसी क्या</i> = प्रत्यक्ष को प्रमाण की आवश्यकता नहीं)"))

    story.append(Spacer(1, 15))
    story.append(Paragraph("<font color='#1A365D'><b>--- अंत और परीक्षा के लिए शुभकामनाएँ! ---</b></font>", subtitle_style))
    story.append(Paragraph("<font color='#4A5568'><b>हिंदी फोरम, महबूबनगर हमेशा आपके साथ है।</b></font>", info_box_style))

    # 5. Build Document using Custom Dynamic Canvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print("PDF build complete!")

if __name__ == "__main__":
    build_pdf()
