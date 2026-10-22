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
'En este maamar, el nombre Avram funciona como una clave de lectura de la sabiduría elevada y aún oculta. La pregunta que abre el estudio es cómo lo que está oculto puede hacerse accesible. No es una descripción psicológica literal de Abraham, sino una lectura jasídica del nombre.',
'In this discourse, the name Avram is a key to understanding elevated, concealed wisdom. The opening question is how what is hidden can become accessible. This is a Chassidic interpretation of the name, rather than a literal psychological description of Abraham.',
'¿Qué diferencia hay entre poseer una idea y poder revelarla?', 'What is the difference between possessing an idea and being able to reveal it?', 'right',1,'right',3),
('El descenso y su propósito', 'Descent and its purpose',
'''בבחי' ירידה ממדרגה למדרגה עד סוף כו' והתכלית הוא להיות גילוי בבי"ע ג"ע עליון ותחתון תענוג הנבראים שיוכלו לקבל גילוי התענוג כו'.''',
'Es un descenso de nivel en nivel hasta el extremo final. Su propósito es que haya revelación en Beriá, Yetzirá y Asiá, en el Gan Eden superior e inferior: el deleite de los seres creados, para que puedan recibir su revelación.',
'It is a descent from level to level, to the very end. Its purpose is revelation in Beriah, Yetzirah and Asiyah, in the higher and lower Gan Eden: the delight of created beings, so that they can receive its revelation.',
'El descenso no se presenta aquí como una pérdida sin finalidad: hace posible que los seres creados reciban una revelación. La edición en línea incluye בבי״ע, una abreviatura ausente en la guía de ejemplo. La conservamos y la traducimos como Beriá, Yetzirá y Asiá.',
'Descent is not presented as a purposeless loss: it makes revelation receivable by created beings. The online text includes בבי״ע, an abbreviation absent from the example guide. It is preserved here and translated as Beriah, Yetzirah and Asiyah.',
'¿Por qué la capacidad del receptor importa para una revelación?', 'Why does the recipient’s capacity matter for revelation?', 'right',3,'right',5),
('Revelación y vínculo', 'Revelation and connection',
'''וזהו ענין חסד אתגלי בפומא דאמה להיות גילוי ההשפעה בבחי' התקשרות והוא יושב פתח האהל כו'.''',
'Este es el sentido de «el jésed se revela en la abertura del órgano [del pacto]»: que la influencia se revele como vinculación; «y él estaba sentado a la entrada de la tienda».',
'This is the meaning of “chesed is revealed at the opening of the organ [of the covenant]”: the influence is revealed as a connection; “and he was sitting at the entrance of the tent.”',
'La expresión aramea דאמה se conserva tal como aparece. No la sustituimos por דאימא ni la traducimos como «de Imá». El pasaje usa el lenguaje cabalístico del pacto y la transmisión para hablar de una influencia que establece vínculo. Esta aclaración editorial corrige la traducción problemática de la guía de apoyo.',
'The Aramaic דאמה is retained as printed. It is not replaced with דאימא or translated as “of Imma.” The passage uses the Kabbalistic language of covenant and transmission for an influence that establishes connection. This editorial clarification addresses the problematic rendering in the supporting guide.',
'¿Qué añade la idea de vínculo a la de transmisión?', 'What does connection add to the idea of transmission?', 'right',5,'right',6),
('Un mundo que existe y se anula', 'A world that exists and yields',
'''אך גילוי זה הוא ע"י צמצומים והעלם בחי' חשך דיצחק ויהי ערב ויהי בקר יום א' כדי להיות בחי' יש ובו יהיה יום אחד המשכת אחד שיהיה היש בטל דהיינו שיהיה בחי' יש ובטל כו'.''',
'Pero esta revelación ocurre mediante contracciones y ocultamiento, el aspecto de oscuridad de Yitzjak. «Y fue tarde y fue mañana, día uno»: para que exista el yesh y en él se extienda la unidad, de modo que el yesh esté anulado; que sea yesh y, a la vez, esté anulado.',
'But this revelation comes through contractions and concealment, the aspect of darkness associated with Yitzchak. “There was evening and there was morning, one day”: so that yesh exists, and unity extends within it, making that yesh nullified—existent, yet yielding.',
'Yesh designa aquí la existencia creada percibida como algo. Bitul no significa destruir físicamente el mundo: el texto mantiene ambos términos, «yesh y batel». La idea es que exista un receptor y, dentro de su existencia, pueda reconocerse la unidad divina.',
'Here yesh denotes created existence perceived as something. Bitul does not mean physically destroying the world: the text retains both terms, “yesh and batel.” A recipient exists, and divine unity can be recognized within that existence.',
'¿Cómo puede haber existencia y bitul a la vez?', 'How can existence and bitul coexist?', 'right',6,'right',9),
('Retirar lo que obstruye', 'Removing what obstructs',
'''והנה להיות גילוי זה צ"ל מצות מילה להסיר ערלה היא קליפת נוגה החופפת כו' שלא יהיה לה יניקה שא"א להמשיך בחי' גילוי בעודה שם כ"א כשיעור חיותה כו'.''',
'Para que tenga lugar esta revelación es necesaria la mitzvá de milá: retirar la orlá, que es la kelipat noga que recubre, para que no tenga de dónde nutrirse; mientras permanezca allí no puede extenderse esa revelación, salvo en la medida de su vitalidad.',
'For this revelation, the mitzvah of milah is necessary: removing the orlah, identified with the covering kelipat nogah, so that it cannot draw sustenance. While it remains, that revelation cannot be extended except to the measure of its vitality.',
'El maamar vincula una mitzvá concreta con el lenguaje de ocultamiento y revelación. No debemos reducir la mitzvá a una metáfora ni convertir esta lectura en una instrucción práctica o un fallo halájico. Aquí estudiamos la explicación conceptual del pasaje.',
'The discourse connects a concrete mitzvah with concealment and revelation. The mitzvah should not be reduced to a metaphor, nor should this reading become practical instruction or a halachic ruling. Our focus is the conceptual explanation of the passage.',
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
'La imagen ayuda a pensar una inclusión, no sólo una imposición externa. La llama menor no deja de ser luz, pero ante la mayor ya no se distingue como una presencia independiente. Esa es la analogía que utiliza el pasaje; no toda propiedad de una llama debe trasladarse a lo espiritual.',
'The image suggests inclusion, rather than merely external force. The smaller flame remains light, but before the greater flame it is no longer distinct as an independent presence. This is the passage’s analogy; not every physical property of a flame should be projected onto the spiritual.',
'¿Qué diferencia hay entre ser suprimido y quedar incluido?', 'What is the difference between being suppressed and becoming included?', 'right',13,'right',15),
('Las chispas y el refinamiento', 'Sparks and refinement',
'''ואמרו גלו לאדום כו' כי לא גלו אלא כדי שיתוסף עליהם גרים והן הניצוצות שבק"נ שבמאכלים ומשקים שמתעלים להתכלל בקדושה מפני גילוי שכינה שעי"ז הם בטלים ונכללים כנר בפני אבוקה כו'.''',
'Y dijeron que fueron exiliados a Edom, pues el exilio tiene como propósito que se les añadan conversos. En esta lectura, son las chispas de kelipat noga presentes en alimentos y bebidas, que ascienden para incorporarse a la santidad por la revelación de la Shejiná: se anulan y quedan incluidas como una vela ante una gran llama.',
'It is said that they were exiled to Edom so that converts would be added to them. In this reading, these are the sparks of kelipat nogah within food and drink, which ascend to become included in holiness through the revelation of the Shechinah, yielding and becoming included like a candle before a great flame.',
'El texto aplica la imagen anterior al birur de lo cotidiano. Distingue la lectura jasídica de «conversos» como chispas de su sentido humano ordinario; este pasaje no autoriza a borrar ese sentido ni a hacer afirmaciones sobre personas concretas. La frase cruza de la columna derecha a la izquierda y por eso conservamos ambas ubicaciones.',
'The passage applies the preceding image to the refinement of everyday life. Its Chassidic reading of “converts” as sparks should be distinguished from the ordinary human meaning of the word; it does not erase that meaning or justify claims about particular people. The sentence crosses from the right column to the left, so both locations are preserved.',
'¿Cómo continúa aquí la imagen de la vela?', 'How does the candle image continue here?', 'right',15,'left',3),
('Del ocultamiento al tikún', 'From concealment to tikkun',
'''וזהו ענין פ' זו ויאמר ה' אל אברם א"ב ר"ם שיהא יורד ומשתלשל בבחי' גילוי כדי להיות תיקון ובירור כי עד אברם הי' שבה"כ דור המבול כו'.''',
'Este es el sentido de este pasaje: «Y dijo Hashem a Avram», Av Ram: que descendiera y se desplegara como revelación para que hubiera reparación y refinamiento; hasta Avram estaba el aspecto de la ruptura de los recipientes, la generación del Diluvio.',
'This is the meaning of this passage: “Hashem said to Avram,” Av Ram—that he should descend and unfold into revelation, bringing repair and refinement; before Avram there was the aspect of the shattering of the vessels, the generation of the Flood.',
'El maamar vuelve al versículo después de desarrollar su vocabulario. Ahora el viaje puede leerse como un movimiento desde lo oculto hacia una revelación capaz de refinar. La referencia al Diluvio pertenece al argumento espiritual del texto; no es una explicación histórica exhaustiva.',
'The discourse returns to the verse after developing its vocabulary. The journey can now be read as a movement from concealment toward a revelation capable of refinement. The Flood reference belongs to the text’s spiritual argument, rather than an exhaustive historical explanation.',
'¿Cómo cambió tu lectura de «Lej Lejá» tras las unidades anteriores?', 'How has your reading of “Lech Lecha” changed after the preceding units?', 'left',3,'left',5),
('La tierra que te mostraré', 'The land that I will show you',
'''ומאברם מתחיל עולם התיקון לך לך יציאת שם מ"ה המתקן ומברר כו'. וצ"ל ירידה אחר ירידה מא"ב ר"ם בחי' יסוד אבא עד אל הארץ בחי' מל'. אשר אראך. פי' אראה ואגלה אותך בעצמך כלומר שאתה תבא לידי התגלות במצות מילה. והיה שמך אברהם אב המון גוים כו':''',
'Y con Avram comienza el mundo del tikún: «Lej Lejá», la salida del Nombre Mah que repara y refina. Debe haber descenso tras descenso desde Av Ram, el aspecto de Yesod Abba, hasta «la tierra», el aspecto de Maljut. «Que te mostraré»: te mostraré y te revelaré a ti mismo; llegarás a revelarte mediante la mitzvá de milá. «Y será tu nombre Abraham», padre de multitud de naciones.',
'With Avram begins the world of tikkun: “Lech Lecha,” the emergence of the Name Mah that repairs and refines. There must be descent after descent from Av Ram, the aspect of Yesod Abba, to “the land,” the aspect of Malchut. “That I will show you”: I will show and reveal you to yourself; you will come into revelation through the mitzvah of milah. “Your name shall be Abraham,” father of a multitude of nations.',
'La primera idea extensa del maamar concluye enlazando el descenso con la revelación de Abraham mismo. El siguiente párrafo pregunta cómo ese descenso constituye una elevación y qué significa la letra hei añadida. Nos detenemos aquí: esta entrega cubre la apertura, no las seis hojas completas.',
'The discourse’s first extended idea concludes by connecting descent with Abraham’s own revelation. The following paragraph asks how that descent constitutes elevation and what the added letter hei means. We pause here: this installment covers the opening passage, not all six scanned pages.',
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
    print('Instalada una lección: Lej Lejá, diez unidades bilingües, seis hojas de consulta.')

if __name__ == '__main__':
    seed()
