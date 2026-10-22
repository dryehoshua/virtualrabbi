# Virtual Rabbi · virtualrabbi.net

Jabrutá virtual local para Torá Or del Alter Rebbe, con enfoque Jabad ortodoxo. Local virtual chavruta for the Alter Rebbe’s Torah Or within Orthodox Chabad tradition.

## Abrir / Open

Doble clic en **Virtual Rabbi.app**, en el escritorio, o visita http://127.0.0.1:8790. / Double-click **Virtual Rabbi.app** on the desktop, or visit http://127.0.0.1:8790.

Una lección precargada: Lej Lejá, entrega 01. Las seis hojas escaneadas sirven de consulta humana; diez unidades del primer párrafo están preparadas en hebreo, español e inglés. / One preloaded lesson: Lech Lecha, installment 01. Six scanned sheets are available for human reference; ten units of the opening paragraph are prepared in Hebrew, Spanish and English.

## Estudiar / Study

- **Comenzar llamada** inicia el estudio en la misma landing, con retrato generado por IA y conversación. / **Start call** begins study on the landing page, with an AI-generated portrait and conversation.
- La aplicación conduce hebreo → traducción → explicación breve → siguiente idea. / The application conducts Hebrew → translation → short explanation → next idea.
- Una pregunta conserva el punto. **Retomar texto** repite la etapa interrumpida; tras la pausa sin preguntas continúa automáticamente hasta el final de la entrega; una pausa explícita detiene el avance. / A question preserves the checkpoint. **Resume text** repeats the interrupted stage; study resumes automatically after the question window, until the installment ends; an explicit pause stops progression.
- **Ubicarme** guarda página PDF, columna y línea. Si no hay texto preparado ahí, la aplicación lo indica en lugar de inventarlo. / Saves PDF page, column and line. Unprepared locations are identified rather than invented.
- El progreso se guarda localmente; esta versión usa un perfil de estudio en este Mac. / Progress is stored locally; this version has one study profile on this Mac.

## Archivos importantes / Important files

`Estudio/` contiene los Markdown de cada parashá; `Instrucciones/` conserva el comportamiento del agente en español e inglés. `Biblioteca/` contiene el índice operativo, las conversaciones, las notas, el progreso y los facsímiles opcionales. / `Estudio/` contains each parashah’s Markdown; `Instrucciones/` stores the Spanish and English agent protocol. `Biblioteca/` contains the runtime index, conversations, notes, checkpoints and optional facsimiles.

Los cambios de contenido conservan versiones en `.historial/`. Las preguntas no mueven el cursor. No hay almacenamiento ni publicación en internet. Las funciones de IA envían el material necesario a OpenAI. / Content changes retain versions under `.historial/`. Questions do not move the cursor. The app is not publicly hosted. AI functions send the required material to OpenAI.

## Configurar IA / Configure AI

La configuración es responsabilidad del operador: define `VIRTUALRABBI_OPENAI_API_KEY` en el entorno del servidor, o usa la credencial existente en el llavero de macOS (`virtualrabbi.net.openai`, cuenta `virtualrabbi.net`). No hay ajustes ni formulario de claves para visitantes. / The operator configures `VIRTUALRABBI_OPENAI_API_KEY` on the server, or uses the existing macOS Keychain credential. Visitors have no settings or key form.

La interfaz está orientada a usuarios, pero esta instalación sigue siendo local y de un solo perfil. Antes de alojarla para varios usuarios hay que separar progreso, notas y conversaciones por usuario y proteger los endpoints de administración. / The interface is visitor-facing, but this installation remains local with one profile. Multi-user hosting requires isolated progress, notes and conversations, plus protected administration endpoints.

ChatGPT y la API tienen facturación separada. Se requiere acceso a los modelos configurados en `config.json` y permiso de micrófono. / ChatGPT and the API have separate billing. Access to the models in `config.json` and browser microphone permission are required.

## Incorporar nuevas hojas / Add sheets

El flujo principal es compartir las hojas en este chat y conservar la edición Markdown aquí. La aplicación conserva también un cargador local opcional: con clave configurada ejecuta OCR por página, revisión conservadora, validación de correspondencia de líneas y generación de hojas en ambos idiomas. Las ubicaciones inferidas por IA están identificadas como tales y pueden revisarse; los bloques grandes pueden requerir revisión de continuidad. / The main workflow is to supply sheets in this chat and maintain the Markdown edition here. An optional local uploader runs per-page OCR, conservative review, line/text consistency checks and bilingual study-guide generation when a key is configured. AI-inferred locations are labeled and reviewable; large blocks may require continuity review.

## Desarrollo / Development

```sh
./run.sh
```

Usa Python con `pypdf` y Poppler (`pdftoppm`) del runtime local de Codex. Interfaz HTML/CSS/JavaScript sin compilación. Escucha sólo en `127.0.0.1:8790`. / Uses Python with `pypdf` and Poppler (`pdftoppm`) from the local Codex runtime. Buildless HTML/CSS/JavaScript. Listens only on `127.0.0.1:8790`.

```sh
/Users/dabbabot/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests -v
```

La secuencia de voz tiene además una prueba de eventos sin llamadas pagadas: `node tests/voice-flow.mjs`. / Voice sequencing also has an event simulation without paid calls: `node tests/voice-flow.mjs`.

Inspirado en el patrón de Kim Live (WebRTC, transcripción y memoria local), con servidor independiente y sin sus herramientas ajenas al estudio. / Based on Kim Live’s WebRTC, transcription and local-memory pattern, with an independent server and no unrelated tools.

API references: [OpenAI WebRTC](https://developers.openai.com/api/docs/guides/realtime-webrtc), [file inputs](https://developers.openai.com/api/docs/guides/file-inputs).

## Sincronización / Synchronization

Repositorio: https://github.com/dryehoshua/virtualrabbi. Se versionan código, retrato IA y Markdown de estudio. Claves, logs, PDFs locales, conversaciones y progreso personal quedan fuera de Git. / Code, AI portrait and study Markdown are versioned. Keys, logs, local PDFs, conversations and personal progress stay outside Git.

## Voz únicamente / Voice-only spending

`voice_only: true` bloquea todas las solicitudes salientes salvo `/v1/realtime/calls`, antes de leer la credencial o abrir la conexión. Se deshabilitan las búsquedas web y el chat independiente. La clave se lee exclusivamente del llavero de Virtual Rabbi o `VIRTUALRABBI_OPENAI_API_KEY`; no se reutiliza Kim ni una clave genérica. / Outbound requests other than Realtime calls are blocked before credential access or network activity. Web search and standalone chat are disabled. Only this project's credential is used.

`input_transcription: true` activa, a petición del usuario, la transcripción de las preguntas habladas en la pestaña Chat; tiene un cargo separado de transcripción de voz. Se conservan las transcripciones de ambos participantes, no grabaciones de audio. Realtime sigue facturando los tokens de audio y texto del contexto de la llamada. / Student microphone transcription is enabled at the user’s request and carries its separate audio transcription charge. Both participants’ transcripts are saved, not audio recordings. Realtime still bills audio and text context tokens within the call.

El operador crea una clave en un proyecto dedicado de OpenAI Platform y ejecuta `python3 scripts/configure_voice_key.py` en Terminal. La entrada se oculta y la clave se guarda en el llavero de macOS, sin archivos ni argumentos de proceso que contengan el secreto. Recargar la web después. / The operator creates a dedicated project key and runs the setup script in Terminal; hidden input is stored in macOS Keychain. Reload the app afterward.

Ritmo de voz / Voice pace: `voice_speed: 1.25`, con entonación hebrea solicitada por instrucciones, sin garantía de canto. / Hebrew study cadence is prompted, not guaranteed singing. [Realtime speed configuration](https://developers.openai.com/api/reference/resources/realtime/client-events#session.update).

## Mesa de lectura / Reading desk

Retrato compacto, controles, facsímil resaltado y texto legible en la misma vista. Chat en una pestaña aparte. La llamada comienza leyendo el hebreo de la unidad guardada. Las lecturas usan `conversation: none` con el fragmento como entrada explícita, sin herramientas, para que el historial de preguntas no sustituya el texto por promesas de continuar. Una comprobación de longitud de hebreo detecta respuestas vacías o sin lectura, reintenta una vez y conserva el marcador si vuelve a fallar; no equivale a verificación palabra por palabra. / Compact portrait, controls, highlighted facsimile and readable text share the view. Chat has its own tab. Calls start with the saved unit’s Hebrew. Isolated reading responses contain the explicit passage and disable tools. A Hebrew-length check catches empty/non-reading output, retries once and preserves the checkpoint on repeated failure; it is not word-level verification.

Sólo se pregunta por dudas al completar una sección álef/bet con límites verificados en los datos; las diez unidades iniciales no tienen ese marcado y avanzan sin preguntas rutinarias. / Questions are invited only at verified aleph/bet section boundaries; the ten initial units have no such markers and proceed without routine questions.

## Ampliar y desplazar la hoja / Zoom and pan

Usa + y − para ampliar de 100% a 500%; pulsa el porcentaje para ajustar la hoja. Desplázate con las barras, el trackpad o arrastrando la hoja ampliada. El resaltado escala junto al escaneo. / Use + and − for 100–500% zoom; click the percentage to fit the page. Scroll with scrollbars, a trackpad, or drag the enlarged sheet. Highlights scale with the scan.

El corpus contiene 28 unidades bilingües: el maamar de la primera hoja y la segunda hoja completa (página impresa 22). Las continuaciones cotejadas están en `Estudio/lej-leja/09-continuacion.json` y `10-hoja-2.json`; `python3 scripts/extend_lej_leja.py` las añade sin sobrescribir unidades anteriores ni el progreso. La unidad 28 empieza un párrafo que continúa en la hoja 3, pendiente de preparación. Las bandas nuevas señalan líneas completas, con solapamiento cuando dos unidades comparten una línea. Las notas registran variantes y distinguen las traducciones editoriales de la fuente Chabad/Kehot.

The corpus contains 28 bilingual units: the discourse on sheet 1 and the complete second sheet (printed page 22). The extension script installs the reviewed continuations without overwriting earlier units or progress. Unit 28 begins a paragraph continuing onto sheet 3, still awaiting preparation. New highlights cover whole lines, overlapping where two units share a line. Source notes record variants and distinguish editorial translations from the Chabad/Kehot source.
