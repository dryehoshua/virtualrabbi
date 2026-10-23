#!/usr/bin/env python3
"""Install the single reviewed opening lesson; never overwrite personal progress."""
import json
import shutil
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server
from pypdf import PdfReader

DOC_ID = '1e7e1e7a202610240000000000000001'
SOURCE = 'https://www.chabad.org/torah-texts/7440873'

# Public-domain Hebrew passage from the Alter Rebbe, checked against Chabad's
# Kehot text and the user's scanned opening passage. Explanations are editorial.
DATA = [
('Avram: la sabiduría todavía oculta', 'Avram: wisdom still concealed',
'''הנה אברם הוא השכל הנעלם מכל רעיון א"ב ר"ם וצ"ל בבחי' גילוי דהיינו להיות סדר השתלשלות מבחי' חכים ולא בחכמה ידיעה''',
'Avram representa el intelecto oculto a todo pensamiento: Av Ram. Debe llegar a revelarse; es decir, debe haber un orden de encadenamiento desde el nivel de «sabio, pero no con una sabiduría conocida».',
'Avram represents intellect concealed beyond every conception: Av Ram. It must come into revelation; that is, an ordered chain must unfold from the level of “wise, but not with a knowable wisdom.”',
'Av Ram designa aquí la sabiduría elevada y oculta. El maamar comienza preguntando cómo esa sabiduría llega a revelarse mediante la avodá de Avraham.',
'Av Ram here denotes elevated, concealed wisdom. The discourse begins by asking how this wisdom becomes revealed through Avraham’s avodah.',
'¿Qué diferencia hay entre poseer una idea y poder revelarla?', 'What is the difference between possessing an idea and being able to reveal it?', 'right',1,'right',3),
('El descenso y su propósito', 'Descent and its purpose',
'''בבחי' ירידה ממדרגה למדרגה עד סוף כו' והתכלית הוא להיות גילוי בבי"ע ג"ע עליון ותחתון תענוג הנבראים שיוכלו לקבל גילוי התענוג כו'.''',
'Es un descenso de nivel en nivel hasta el extremo final. Su propósito es que haya revelación en Beriá, Yetzirá y Asiá, en el Gan Eden superior e inferior: el deleite de los seres creados, para que puedan recibir su revelación.',
'It is a descent from level to level, to the very end. Its purpose is revelation in Beriah, Yetzirah and Asiyah, in the higher and lower Gan Eden: the delight of created beings, so that they can receive its revelation.',
'El descenso permite que los seres creados reciban la revelación. La sabiduría se extiende hacia Beriá, Yetzirá y Asiyá, de acuerdo con la capacidad de recepción de esos mundos.',
'Descent enables created beings to receive revelation. Wisdom extends into Beriah, Yetzirah, and Asiyah according to those worlds’ capacity to receive.',
'¿Por qué la capacidad del receptor importa para una revelación?', 'Why does the recipient’s capacity matter for revelation?', 'right',3,'right',5),
('Revelación y vínculo', 'Revelation and connection',
'''וזהו ענין חסד אתגלי בפומא דאמה להיות גילוי ההשפעה בבחי' התקשרות והוא יושב פתח האהל כו'.''',
'Este es el sentido de «el jésed se revela en la abertura del órgano [del pacto]»: que la influencia se revele como vinculación; «y él estaba sentado a la entrada de la tienda».',
'This is the meaning of “chesed is revealed at the opening of the organ [of the covenant]”: the influence is revealed as a connection; “and he was sitting at the entrance of the tent.”',
'El maamar relaciona el jésed con el pacto y con hitkashrut, el vínculo. La influencia se revela de una manera que une al transmisor con el receptor.',
'The discourse connects Chesed with the covenant and with hitkashrut, a bond. The influence is revealed in a way that joins the giver and the recipient.',
'¿Qué añade la idea de vínculo a la de transmisión?', 'What does connection add to the idea of transmission?', 'right',5,'right',6),
('Un mundo que existe y se anula', 'A world that exists and yields',
'''אך גילוי זה הוא ע"י צמצומים והעלם בחי' חשך דיצחק ויהי ערב ויהי בקר יום א' כדי להיות בחי' יש ובו יהיה יום אחד המשכת אחד שיהיה היש בטל דהיינו שיהיה בחי' יש ובטל כו'.''',
'Pero esta revelación ocurre mediante contracciones y ocultamiento, el aspecto de oscuridad de Yitzjak. «Y fue tarde y fue mañana, día uno»: para que exista el yesh y en él se extienda la unidad, de modo que el yesh esté anulado; que sea yesh y, a la vez, esté anulado.',
'But this revelation comes through contractions and concealment, the aspect of darkness associated with Yitzchak. “There was evening and there was morning, one day”: so that yesh exists, and unity extends within it, making that yesh nullified—existent, yet yielding.',
'Yesh designa la existencia creada que se percibe como algo. El propósito es que esa existencia reconozca su dependencia de Hashem: que sea yesh y, a la vez, batel.',
'Yesh denotes created existence perceived as something. The purpose is for that existence to recognize its dependence on Hashem: to be yesh and, at the same time, batel.',
'¿Cómo puede haber existencia y bitul a la vez?', 'How can existence and bitul coexist?', 'right',6,'right',9),
('Retirar lo que obstruye', 'Removing what obstructs',
'''והנה להיות גילוי זה צ"ל מצות מילה להסיר ערלה היא קליפת נוגה החופפת כו' שלא יהיה לה יניקה שא"א להמשיך בחי' גילוי בעודה שם כ"א כשיעור חיותה כו'.''',
'Para que tenga lugar esta revelación es necesaria la mitzvá de milá: retirar la orlá, que es la kelipat noga que recubre, para que no tenga de dónde nutrirse; mientras permanezca allí no puede extenderse esa revelación, salvo en la medida de su vitalidad.',
'For this revelation, the mitzvah of milah is necessary: removing the orlah, identified with the covering kelipat nogah, so that it cannot draw sustenance. While it remains, that revelation cannot be extended except to the measure of its vitality.',
'La orlá encubre la revelación y permite la yeniká, la nutrición de la kelipá. El maamar explica que la milá retira ese encubrimiento para hacer posible el gilui.',
'The orlah covers revelation and allows yenikah, the nourishment of kelipah. The discourse explains that milah removes this covering to make gilui possible.',
'¿Qué obstáculo a la revelación describe este fragmento?', 'What obstacle to revelation does this passage describe?', 'right',9,'right',12),
('Padre de una multitud', 'Father of a multitude',
'''ולכן כתיב אחר מצות מילה כי אב המון גוים שלכאורה אינו מובן מה ענין גוים לכאן אלא שנעשה כח הבירור ע"י גילוי זה''',
'Por eso, después de la mitzvá de milá, está escrito «porque [te he hecho] padre de multitud de naciones». No parece claro qué relación tienen aquí las naciones; mediante esta revelación se produce la capacidad de birur.',
'Therefore, after the mitzvah of milah it is written, “for [I have made you] father of a multitude of nations.” The connection to nations seems unclear; through this revelation the capacity for birur is brought about.',
'La pregunta del Alter Rebbe impide pasar por alto el giro hacia las naciones. Birur alude a discernir y refinar. El hilo del argumento conduce de la revelación recibida por Abraham a su capacidad de actuar sobre lo que está fuera de él.',
'The Alter Rebbe’s question draws attention to the turn toward the nations. Birur concerns discernment and refinement. The argument moves from revelation received by Abraham toward his capacity to affect what is outside himself.',
'¿Por qué el texto pregunta por las naciones justo aquí?', 'Why does the text ask about the nations at this point?', 'right',12,'right',13),
('La vela ante la gran llama', 'A candle before a great flame',
'''כי למה הצדיקים דומים בפני השכינה כנר בפני האבוקה שנכללים בבחי' בטול באבוקה.''',
'Pues, ¿a qué se parecen los justos ante la Shejiná? A una vela ante una gran llama: quedan incluidos en ella en un estado de bitul.',
'For what are the righteous like before the Shechinah? A candle before a great flame: they become included within it in a state of bitul.',
'Ante una gran llama, la luz de la vela queda incluida en ella. Así explica el maamar el bitul de los tzadikim ante la Shejiná: inclusión en una revelación mayor.',
'Before a great flame, the candle’s light becomes included within it. This is how the discourse explains the bittul of the tzaddikim before the Shechinah: inclusion within a greater revelation.',
'¿Qué diferencia hay entre ser suprimido y quedar incluido?', 'What is the difference between being suppressed and becoming included?', 'right',13,'right',15),
('Las chispas y el refinamiento', 'Sparks and refinement',
'''ואמרו גלו לאדום כו' כי לא גלו אלא כדי שיתוסף עליהם גרים והן הניצוצות שבק"נ שבמאכלים ומשקים שמתעלים להתכלל בקדושה מפני גילוי שכינה שעי"ז הם בטלים ונכללים כנר בפני אבוקה כו'.''',
'Y dijeron que fueron exiliados a Edom, pues el exilio tiene como propósito que se les añadan conversos. En esta lectura, son las chispas de kelipat noga presentes en alimentos y bebidas, que ascienden para incorporarse a la santidad por la revelación de la Shejiná: se anulan y quedan incluidas como una vela ante una gran llama.',
'It is said that they were exiled to Edom so that converts would be added to them. In this reading, these are the sparks of kelipat nogah within food and drink, which ascend to become included in holiness through the revelation of the Shechinah, yielding and becoming included like a candle before a great flame.',
'El maamar aplica la imagen de la vela al birur de las chispas presentes en alimentos y bebidas. La revelación de la Shejiná permite que esas chispas asciendan y se incluyan en la kedushá.',
'The discourse applies the candle image to the birur of sparks present in food and drink. Revelation of the Shechinah enables these sparks to rise and become included in kedushah.',
'¿Cómo continúa aquí la imagen de la vela?', 'How does the candle image continue here?', 'right',15,'left',3),
('Del ocultamiento al tikún', 'From concealment to tikkun',
'''וזהו ענין פ' זו ויאמר ה' אל אברם א"ב ר"ם שיהא יורד ומשתלשל בבחי' גילוי כדי להיות תיקון ובירור כי עד אברם הי' שבה"כ דור המבול כו'.''',
'Este es el sentido de este pasaje: «Y dijo Hashem a Avram», Av Ram: que descendiera y se desplegara como revelación para que hubiera reparación y refinamiento; hasta Avram estaba el aspecto de la ruptura de los recipientes, la generación del Diluvio.',
'This is the meaning of this passage: “Hashem said to Avram,” Av Ram—that he should descend and unfold into revelation, bringing repair and refinement; before Avram there was the aspect of the shattering of the vessels, the generation of the Flood.',
'El texto vuelve al viaje de Avraham como un descenso desde la sabiduría oculta hacia el tikún. La revelación que recibe hace posible el birur y la incorporación de las chispas a la kedushá.',
'The text returns to Avraham’s journey as descent from concealed wisdom toward tikkun. The revelation he receives makes birur and the inclusion of sparks in kedushah possible.',
'¿Cómo cambió tu lectura de «Lej Lejá» tras las unidades anteriores?', 'How has your reading of “Lech Lecha” changed after the preceding units?', 'left',3,'left',5),
('La tierra que te mostraré', 'The land that I will show you',
'''ומאברם מתחיל עולם התיקון לך לך יציאת שם מ"ה המתקן ומברר כו'. וצ"ל ירידה אחר ירידה מא"ב ר"ם בחי' יסוד אבא עד אל הארץ בחי' מל'. אשר אראך. פי' אראה ואגלה אותך בעצמך כלומר שאתה תבא לידי התגלות במצות מילה. והיה שמך אברהם אב המון גוים כו':''',
'Y con Avram comienza el mundo del tikún: «Lej Lejá», la salida del Nombre Mah que repara y refina. Debe haber descenso tras descenso desde Av Ram, el aspecto de Yesod Abba, hasta «la tierra», el aspecto de Maljut. «Que te mostraré»: te mostraré y te revelaré a ti mismo; llegarás a revelarte mediante la mitzvá de milá. «Y será tu nombre Abraham», padre de multitud de naciones.',
'With Avram begins the world of tikkun: “Lech Lecha,” the emergence of the Name Mah that repairs and refines. There must be descent after descent from Av Ram, the aspect of Yesod Abba, to “the land,” the aspect of Malchut. “That I will show you”: I will show and reveal you to yourself; you will come into revelation through the mitzvah of milah. “Your name shall be Abraham,” father of a multitude of nations.',
'«La tierra que te mostraré» se explica como revelación de Avraham mismo mediante la milá. El paso de Avram a Avraham une el descenso hacia Maljut con la capacidad de refinar e incluir las chispas.',
'“The land that I will show you” is explained as Avraham’s own revelation through milah. The passage from Avram to Avraham connects descent into Malchut with the ability to refine and include sparks.',
'¿Cuál es la pregunta que queda abierta para el siguiente párrafo?', 'What question remains open for the next paragraph?', 'left',5,'left',9),
]


def seed():
    target = server.folder(DOC_ID)
    if (target / 'documento.json').exists():
        print('Lección existente: se conserva el progreso.')
        return
    target.mkdir(parents=True, exist_ok=True)
    original = Path('/Users/dabbabot/Downloads/Lej Lejah Torah Or.pdf')
    guide = Path('/Users/dabbabot/Downloads/Torah_Or_Lej_Leja_guia_estudio_01.pdf')
    shutil.copy2(original, target / 'original.pdf')
    shutil.copy2(guide, target / 'guia.pdf')
    guide_text = '\n\n'.join(p.extract_text() or '' for p in PdfReader(guide).pages)
    (target / 'guia.txt').write_text(guide_text, encoding='utf-8')
    units = []
    for i, (title,title_en,hebrew,translation,translation_en,explanation,explanation_en,q,q_en,col,line,endcol,endline) in enumerate(DATA):
        unit_id = f'lej-leja-01-{i+1:02}'
        source_note = 'Texto primario: Torá Or, Lej Lejá, comienzo del maamar «הנה אברם»; edición Kehot en Chabad.org. Traducción y explicación editoriales, no citas literales de un comentario del Rebe. La guía aportada es apoyo parcial y se han señalado discrepancias.'
        source_note_en = 'Primary text: Torah Or, Lech Lecha, opening of the discourse “Hinei Avram”; Kehot text on Chabad.org. Translation and explanation are editorial, not quotations from a Rebbe’s commentary. The supplied guide is partial supporting material; discrepancies are noted.'
        regions = json.loads((server.ROOT / 'Estudio/lej-leja/08-mapa-hoja.json').read_text())['units'][unit_id]
        units.append(dict(id=unit_id,title=title,title_en=title_en,hebrew=hebrew,translation=translation,translation_en=translation_en,explanation=explanation,explanation_en=explanation_en,questions=[q],questions_en=[q_en],source_notes=source_note,source_notes_en=source_note_en,pages=[1],sources=[{'title':'Torá Or · Lej Lejá · Texto hebreo Kehot / Chabad.org','url':SOURCE,'checked_at':'2026-10-22','kind':'primary_text'}],research='',source_status='primary_text',review_state='curated',location={'start':{'page':1,'column':col,'line':line},'end':{'page':1,'column':endcol,'line':endline},'basis':'Líneas del maamar: derecha desde הנה אברם; izquierda desde שיתוסף. No se cuenta el final del discurso anterior.','printed_page':'יא'},regions=regions))
    doc = dict(id=DOC_ID,slug='lej-leja',title='Lej Lejá · Torá Or',title_en='Lech Lecha · Torah Or',author='Rabí Shneur Zalman de Liadí · Alter Rebbe',filename=original.name,created_at=server.now(),status='ready',preparation='curated_primary',pages=[{'number':i+1,'raw':'','hebrew':'','warnings':['Hoja escaneada conservada para consulta humana. No se presenta como transcripción completa.'],'approved':False,'ocr_done':False} for i in range(6)],units=units,current_unit=0,completed=[],error='',study_language='es',location=units[0]['location']['start'],cursor={'unit_id':units[0]['id'],'phase':'introduction','interrupted':False},guide={'filename':guide.name,'pages':3,'text':guide_text,'status':'supporting_material'},
    scope='Lej Lejá: comenzar en el encabezado פרשת לך לך, en הנה אברם, parte inferior de la primera hoja. El texto de arriba pertenece al discurso anterior. Identificar otros maamarim posteriores por sus encabezados.',
    introduction='Estudiaremos la apertura de Lej Lejá en Torá Or, la colección de maamarim del Alter Rebbe, publicada por primera vez en 1837. El pasaje pregunta cómo la sabiduría oculta llega a revelarse y a refinar la existencia. Leeremos una idea en hebreo, después su traducción y explicación, y haremos una pausa para tus preguntas.',
    introduction_en='We will study the opening of Lech Lecha in Torah Or, the Alter Rebbe’s collection of Chassidic discourses, first published in 1837. The passage asks how concealed wisdom becomes revealed and refines existence. We will read one idea in Hebrew, then its translation and explanation, and pause for your questions.',
    coverage='Entrega 01 · Primer párrafo del maamar הנה אברם · 10 unidades. Las seis hojas están disponibles como facsímil; esta entrega no afirma transcribirlas por completo. Líneas contadas desde el comienzo del maamar en cada columna.',
    coverage_en='Installment 01 · First paragraph of the Hinei Avram discourse · 10 units. All six scanned sheets are available; this installment does not claim to transcribe them in full. Lines are counted from the start of the discourse within each column.',
    weekly={'parasha':'Lej Lejá','hebrew':'לך לך','shabbat':'2026-10-24','hebrew_date':'י״ג חשוון תשפ״ז','source':'https://www.chabad.org/parshah/torahreading_cdo/aid/2474599/p/complete/jewish/Lech-Lecha-Torah-Reading.htm'})
    server.save(doc)
    from extend_lej_leja import extend
    extend()
    print('Instalada una lección: Lej Lejá, trece unidades bilingües, seis hojas de consulta.')

if __name__ == '__main__':
    seed()
