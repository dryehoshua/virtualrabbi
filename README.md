# Virtual Rabbi · virtualrabbi.net

Jabrutá virtual local para Torá Or del Alter Rebbe, con enfoque Jabad ortodoxo. Local virtual chavruta for the Alter Rebbe’s Torah Or within Orthodox Chabad tradition.

## Abrir / Open

Doble clic en **Virtual Rabbi.app**, en el escritorio, o visita http://127.0.0.1:8790. / Double-click **Virtual Rabbi.app** on the desktop, or visit http://127.0.0.1:8790.

Una lección precargada: Lej Lejá, entrega 01. Las seis hojas escaneadas sirven de consulta humana; diez unidades del primer párrafo están preparadas en hebreo, español e inglés. / One preloaded lesson: Lech Lecha, installment 01. Six scanned sheets are available for human reference; ten units of the opening paragraph are prepared in Hebrew, Spanish and English.

## Estudiar / Study

- **Comenzar llamada** inicia el estudio en la misma landing, con retrato generado por IA, orbe y conversación. / **Start call** begins study on the landing page, with an AI-generated portrait, orb and conversation.
- La aplicación conduce introducción → hebreo → traducción → explicación → pausa. / The application conducts introduction → Hebrew → translation → explanation → pause.
- Una pregunta conserva el punto. **Retomar texto** repite la etapa interrumpida; después de una idea terminada pasa a la siguiente sólo por solicitud. / A question preserves the checkpoint. **Resume text** repeats the interrupted stage; the next idea starts only on request.
- **Ubicarme** guarda página PDF, columna y línea. Si no hay texto preparado ahí, la aplicación lo indica en lugar de inventarlo. / Saves PDF page, column and line. Unprepared locations are identified rather than invented.
- El progreso se guarda localmente; esta versión usa un perfil de estudio en este Mac. / Progress is stored locally; this version has one study profile on this Mac.

## Archivos importantes / Important files

`Estudio/` contiene los Markdown de cada parashá; `Instrucciones/` conserva el comportamiento del agente en español e inglés. `Biblioteca/` contiene el índice operativo, las conversaciones, las notas, el progreso y los facsímiles opcionales. / `Estudio/` contains each parashah’s Markdown; `Instrucciones/` stores the Spanish and English agent protocol. `Biblioteca/` contains the runtime index, conversations, notes, checkpoints and optional facsimiles.

Los cambios de contenido conservan versiones en `.historial/`. Las preguntas no mueven el cursor. No hay almacenamiento ni publicación en internet. Las funciones de IA envían el material necesario a OpenAI. / Content changes retain versions under `.historial/`. Questions do not move the cursor. The app is not publicly hosted. AI functions send the required material to OpenAI.

## Configurar IA / Configure AI

La configuración es responsabilidad del operador: define `OPENAI_API_KEY` en el entorno del servidor, o usa la credencial existente en el llavero de macOS (`virtualrabbi.net.openai`, cuenta `virtualrabbi.net`). No hay ajustes ni formulario de claves para visitantes. / The operator configures `OPENAI_API_KEY` on the server, or uses the existing macOS Keychain credential. Visitors have no settings or key form.

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
