# Virtual Rabbi · Publicación / Deployment

## Estado / Status — 2026-11-05

Registro público, acceso por cuenta, Stripe y control de clases implementados.
Las llamadas y la compra de clases están **pausadas**: la prueba real de OpenAI
respondió `429 credit_balance_exhausted`. El titular decidió recargar después.
No se ha verificado todavía una llamada pública completa ni un cobro real.

Public signup, account access, Stripe fulfillment and class controls are implemented.
Voice and class checkout are **paused** because the actual OpenAI call attempt
returned `429 credit_balance_exhausted`. The owner will fund the API later.
A complete public voice call and a real payment have not yet been verified.

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
- Payment Link: `plink_1UYZ5C1fJ8c9bLD8jeDbdnDv`, **desactivado / deactivated**.
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
3. Verificar pago y entrega Stripe en un entorno de prueba aislado antes de abrir
   ventas; comprobar que el usuario correcto recibe 1,800 segundos una sola vez.
   Verify sandbox payment fulfillment to the correct account exactly once.
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
