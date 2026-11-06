# Virtual Rabbi · Publicación / Deployment

## Estado / Status — 2026-11-06

Voz pública y enlace Stripe de la clase **activados** tras la recarga. Se creó el
proyecto OpenAI **Virtual Rabbi** y su cuenta de servicio `virtualrabbi-voice`.
La prueba real con la nueva clave conectó, recibió 46 cuadros de audio, completó
la respuesta y cerró la llamada remotamente, sin errores (costo estimado US$0.001972).
Se verificó la apertura del formulario Stripe de US$5. No se realizó un cobro real;
la entrega de minutos y sus protecciones se comprobaron mediante pruebas aisladas.
Una compra real seguida de una clase completa por el navegador sigue pendiente.

Public voice and the class Stripe link are **enabled** after funding. The dedicated
OpenAI **Virtual Rabbi** project and `virtualrabbi-voice` service account are active.
An actual call with the new key connected, received 46 audio frames, completed its
response and was remotely closed without errors (estimated cost US$0.001972).
The US$5 Stripe checkout opens. No real payment was made; fulfillment and its
protections were checked with isolated tests. A real purchase followed by a full
browser study session remains to be verified.

## OpenAI: proyecto y saldo / Project and balance

- Proyecto / Project: `Virtual Rabbi`, `proj_HktAxy5owCe8AoAGGxavlap7`.
- Organización / Organization: `Personal`. Es el nombre de la organización,
  no una indicación de que la aplicación use una clave personal.
- Cuenta de servicio / Service account: `virtualrabbi-voice`.
- Clave sólo en el llavero macOS / Key only in macOS Keychain:
  servicio `virtualrabbi.net.openai`, cuenta `virtualrabbi.net`.
- La clave anterior se conserva en el llavero como `virtualrabbi.net.previous`;
  no fue revocada, porque podría tener otros usos. The previous key was retained
  locally and not revoked, since other applications may still use it.
- Sin límite mensual de proyecto, por decisión del titular. Los límites de clase
  y los de la organización siguen vigentes. No project monthly spend limit,
  as requested; per-class and organization limits still apply.
- El saldo se recarga por organización; cada proyecto separa claves y consumo.
  Prepaid credit belongs to the organization; projects separate keys and usage.
  [OpenAI: spend limits](https://developers.openai.com/api/docs/guides/spend-limits).
- La aplicación mantiene `voice_only`: esta clave se usa para llamadas de voz,
  no para preparar documentos. The application retains its voice-only API mode.

## Infraestructura / Infrastructure

- Local privado / Private local: `127.0.0.1:8790`.
- Público / Public: `127.0.0.1:8791`, Cloudflare Tunnel `virtualrabbi-mac`.
- Inicio / Landing: https://virtualrabbi.net/ ; lector / reader: `/study`.
- Servicios / Services: `net.virtualrabbi.public`, `net.virtualrabbi.tunnel`.
- Instalar dependencias públicas / Install public dependencies:
  `python3 -m pip install -r requirements-public.txt`.
- Publicar catálogo / Publish curated content: `python3 scripts/publish_catalog.py`.
- Instalar servicios / Install services: `python3 scripts/install_public.py --tunnel`.
- La Mac debe estar encendida, despierta, conectada y con sesión iniciada.
  The Mac must remain awake, online and logged in.
- DNS Cloudflare: `virginia.ns.cloudflare.com`, `zeus.ns.cloudflare.com`.
  Conservar correo IONOS / Preserve IONOS mail records.
- Tunnel ID: `0121a8d0-1bbf-49ba-bef8-639f2889f13e`.

## Cuentas y privacidad / Accounts and privacy

Registro con nombre, correo y contraseña; scrypt con sal única, sesiones opacas
revocables de siete días, cookies Secure/HttpOnly. El avance y la conversación se
separan por cuenta. El modo invitado conserva una identidad por navegador.
No hay recuperación de contraseña ni verificación de correo todavía. El avance
anónimo no se combina automáticamente al registrarse. Las transcripciones de voz
se guardan; no se guardan grabaciones de audio.

Signup captures a display name, email and password. Passwords use salted scrypt;
revocable seven-day sessions use Secure/HttpOnly cookies. Progress and transcripts
are account-specific. Guest identities remain browser-specific. Email verification,
password recovery and automatic guest-progress migration are not implemented.
Audio recordings are not stored; voice transcripts are saved.

Cuenta y agradecimiento disponibles en inglés, español, ruso, francés, hebreo y
portugués, con detección del idioma del navegador y selector manual. El resto de
la interfaz y las hojas preparadas son español/inglés; la voz recibe instrucciones
para explicar en el idioma seleccionado, conservando el original hebreo.

Account and thank-you flows support EN/ES/RU/FR/HE/PT using browser language and a
manual selector. Remaining UI and prepared study sheets are Spanish/English;
voice is instructed to explain in the selected language and preserve Hebrew.

## Pago por clase / One-time class payment

US$5 más impuestos aplicables por hasta 30 minutos, sin suscripción. El tiempo no
utilizado permanece en la cuenta. La clase también tiene un límite de consumo
estimado de IA de US$4; puede terminar antes, como se informa antes del pago.
No garantiza un margen del 52%. El consumo se calcula con eventos del proveedor;
puede haber sobrepaso durante una respuesta o retraso al cerrar. Validar costos
reales antes de ampliar el lanzamiento.

US$5 plus applicable tax for up to 30 minutes, no subscription. Unused time stays
in the account. A US$4 estimated AI allowance can end a class earlier, disclosed
before checkout. This does not guarantee a 52% markup or profit. Provider usage
events drive estimates; an in-flight response or delayed hangup may overshoot.
Measure actual usage before expanding the launch.

- Stripe: AI PEOPLE LEGACY Inc, configuración fiscal AIaaS autorizada.
- Producto / Product: `Virtual Rabbi · Torah Or · 30 min`.
- Payment Link: `plink_1UYZ5C1fJ8c9bLD8jeDbdnDv`, **activo / active**.
- Return: `https://virtualrabbi.net/study?payment=return`.
- Webhook: `https://virtualrabbi.net/api/stripe/webhook`.
- Destination: `we_1UYZmV1fJ8c9bLD8hcV60vqr`, enabled.
- Events: `checkout.session.completed`, `checkout.session.async_payment_succeeded`,
  `charge.refunded`, `charge.dispute.created`.
- Firma Stripe obligatoria; reintentos idempotentes; cuenta enlazada por una
  referencia aleatoria generada en el servidor. La URL de retorno no otorga saldo.
  Signed events only; idempotent retries; server-generated order references bind
  payments to accounts. Returning from checkout does not itself grant access.
- Reembolsos y disputas revocan acceso. Una llamada simultánea por cuenta, cuatro
  globales; cierre en el servidor por tiempo, consumo o pérdida de conexión.
  Refunds/disputes revoke grants. One concurrent call per account, four globally;
  server-enforced time, estimated spend and connection-loss termination.
- Los otros importes son apoyo voluntario y no añaden minutos.
  Other amounts are voluntary support and do not add class minutes.

## Activación posterior a la recarga / Activation after funding

1. Recargar la organización de OpenAI asociada a la clave del proyecto.
   Fund the OpenAI organization associated with this project's key.
2. Probar conexión real, recepción de audio, monitor del servidor y cierre remoto
   usando un estado aislado; no emitir créditos ficticios en producción.
   Verify actual audio, server monitoring and provider hangup with isolated state.
3. Verificar la entrega con eventos firmados en pruebas aisladas; comprobar que
   el usuario correcto recibe 1,800 segundos una sola vez. Esta prueba no equivale
   a un pago real de extremo a extremo. Verify signed-event fulfillment in isolated
   tests; this does not replace an actual end-to-end payment.
4. Reactivar el Payment Link anterior y crear `.runtime/public/voice-enabled`
   únicamente después de estas verificaciones. Reiniciar el servicio público.
   Reactivate the link and create the local activation flag only after verification.
5. Comprobar `/api/status`, llamada autenticada, interrupción, reanudación y tiempo.
   Check status, authenticated calls, interruption, resume and elapsed time.

Para cerrar admisiones, eliminar el archivo `voice-enabled` y desactivar el enlace
Stripe. Un error de saldo OpenAI elimina automáticamente el archivo local.
To stop admissions, remove the activation flag and deactivate the Stripe link.
An OpenAI insufficient-credit response automatically removes the local flag.

## Respaldo / Backups

Guardar juntos, fuera de GitHub / Back up together outside GitHub:
`.runtime/public/accounts.sqlite3`, `classes.sqlite3`, `readers/`, `cookie-secret`,
`stripe-webhook-secret` y `.runtime/deploy/tunnel-token`.
Secretos con permisos 0600. Nunca poner claves, contraseñas, conversaciones o
bases privadas en Git. / Secrets use mode 0600; never commit secrets or user data.

## Validación / Validation

`python3 -m unittest discover -s tests -q` y `node tests/voice-flow.mjs` prueban
identidad, aislamiento, firmas falsas, duplicados, reembolsos, bloqueo sin pago,
contabilidad, límites, interrupciones y reanudación. No sustituyen una prueba
real de voz ni un pago de extremo a extremo.

These automated tests cover identity, isolation, forged signatures, retries,
refunds, unpaid access, accounting, limits, interruption and resume. They do not
replace real voice and end-to-end payment verification.

## Jayé Sará y continuidad — 2026-11-06

Dos parashot publicadas: Lej Lejá (62 unidades) y Jayé Sará (cinco unidades,
cuatro facsímiles). No se modificó el progreso de Lej Lejá. Selector de parashá
visible y enlaces directos por `?lesson=ID`.

Two published portions: Lech Lecha (62 units) and Chayei Sarah (five units,
four facsimiles). Existing Lech Lecha progress is preserved. A visible portion
selector and `?lesson=ID` links open either collection.

Las lecturas largas se envían en fragmentos internos conservando todas las
palabras: primero todo el hebreo, después la traducción y la explicación. No se
avanza con una respuesta incompleta; se reintenta una vez, después de terminar
el audio, y se conserva el marcador si persiste el error. Una pausa o pregunta
invalida las lecturas pendientes. La entrega termina después de la lección 5.

Long readings use internal fragments preserving every word: all Hebrew first,
then translation and explanation. An incomplete response cannot advance the
cursor; one retry follows playback, and persistent errors retain the bookmark.
A pause or question invalidates pending readings. This installment stops after
lesson five.

Validación: 32 pruebas Python, simulación previa de preguntas/pausas y simulación
de las cinco lecciones reales en ES y EN. La prueba de audio real completó dos
fragmentos hebreos y el siguiente fragmento español: 949 cuadros de audio,
sin errores, cierre remoto confirmado, costo estimado US$0.035316. Esto no
sustituye una sesión completa con preguntas habladas desde un navegador.

Validation: 32 Python tests, existing question/pause simulations and all five
actual lessons simulated in ES and EN. A real voice test completed two Hebrew
fragments followed by a Spanish fragment: 949 audio frames, no errors, confirmed
remote hangup, estimated US$0.035316. This does not replace a complete browser
session with spoken student questions.

Reinstalar desde el PDF aportado / Reinstall from the supplied PDF (requires
`pymupdf` for facsimile rendering):

```sh
python3 scripts/seed_jaye_sara.py /path/to/original.pdf
python3 scripts/publish_catalog.py --id 1e7e1e7a202611070000000000000002
node tests/voice-five-lessons.mjs
STUDY_LANGUAGE=en node tests/voice-five-lessons.mjs
```
