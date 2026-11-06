# Aportaciones voluntarias / Voluntary support

**Actualización posterior / Later update:** el titular eligió US$5 por clase de hasta 30 minutos, sin suscripción. Ese enlace está preparado y pausado hasta recargar OpenAI. Los otros importes siguen siendo apoyo voluntario sin minutos. / The owner subsequently chose US$5 per class up to 30 minutes, no subscription. That link is prepared and paused pending OpenAI funding; other amounts remain voluntary support without minutes. Ver / See [PUBLICACION.md](PUBLICACION.md). Las decisiones iniciales y estimaciones siguientes se conservan como referencia histórica. / Earlier decisions and estimates below are historical context.

Consulta de precios: 2026-11-05. Modelo instalado: `gpt-realtime` (sin cambiarlo).

## Español

Importes habilitados: US$5, US$18, US$52, US$100, US$260, US$450 y US$1,800; otro importe debe ser mayor a US$5 (mínimo US$5.01), pago único y voluntario. Mensaje:
«Si este estudio te ayudó, ayúdanos a seguir difundiendo la Torá».
No vincular el aporte con minutos garantizados ni llamarlo un plan. No anunciar
recibos deducibles sin una entidad fiscal que los respalde.

Chabad.org combina importes sugeridos, importe libre y frecuencia única o mensual.
Su mensaje se centra en difundir Torá. Sefaria también invita a apoyar el aprendizaje.
Estas referencias orientan la presentación; Virtual Rabbi es un proyecto independiente.

### Costo estimado de voz

Por millón de tokens: audio de entrada US$32; audio de salida US$64;
texto de entrada US$4; texto de salida US$16. Entrada en caché US$0.40.
El audio nuevo del alumno produce aproximadamente 600 tokens/minuto y el generado
por el rabino 1,200 tokens/minuto: US$0.0192/min y US$0.0768/min respectivamente.

Ejemplo de estudio con 80% del tiempo hablando el rabino y 20% el alumno:

| Duración | Solo audio nuevo | Audio × 1.52 |
| --- | ---: | ---: |
| 15 minutos | US$0.98 | US$1.49 |
| 30 minutos | US$1.96 | US$2.98 |
| 60 minutos | US$3.92 | US$5.95 |

Estas cifras NO son el costo completo ni un presupuesto garantizado: faltan el
texto, historial procesado de nuevo (o en caché), transcripción adicional, herramientas,
comisiones Stripe e impuestos aplicables. Una sesión real debe medirse con los
registros de uso del proveedor. El silencio y las interrupciones cambian la mezcla.
El 52% es un incremento sobre el costo, no un margen neto de 52%.
Fórmula interna: costo medido × 1.52; para sostenibilidad financiera también hay que
cubrir comisiones y otros gastos. Las aportaciones abiertas pueden no cubrir el uso.

## English

Suggested voluntary, one-time amounts: US$5, US$18, US$52, US$100, US$260, US$450 and US$1,800; custom amounts must exceed US$5 (minimum US$5.01).
Copy: “If this study helped you, help us keep sharing Torah.” Contributions do not
buy voice minutes. The current `gpt-realtime` model costs US$32/million input audio
tokens and US$64/million output audio tokens. New speech is roughly US$0.0192 per
learner minute and US$0.0768 per teacher minute. At an 80/20 teacher/learner split,
30 minutes costs about US$1.96 for new audio alone, or US$2.98 after a 52% markup.
Text, reused context, transcription, tools, payment fees and taxes are additional.
Measure actual provider usage before setting budgets; voluntary support is not a
reliable per-session payment. A 52% markup is not a 52% profit margin.

## Fuentes / Sources

- https://developers.openai.com/api/docs/models/gpt-realtime
- https://developers.openai.com/api/docs/guides/voice-latency-cost?voice-api=realtime
- https://www.chabad.org/tools/donate/donate_cdo/aid/161548/jewish/Donate.htm
- https://www.sefaria.org/ways-to-give

## Publicación / Publication — 2026-11-05

Los ocho enlaces de pago están en `config/support-links.json`. Son enlaces públicos,
no credenciales. `.runtime/public/support-links.json` permite sustituirlos por
instalación. Cobros a través de AI PEOPLE LEGACY Inc, con categoría AIaaS y cálculo
fiscal automático, según autorización del titular. Los impuestos no están incluidos
en el importe base. El importe libre tiene mínimo US$5.01 y sugerido US$18.
No se realizó ningún cargo de prueba. Las llamadas públicas siguen desactivadas;
las aportaciones no habilitan minutos ni suscripciones.

All eight public payment links are tracked in `config/support-links.json`; an
installation may override them in `.runtime/public/support-links.json`. One-time
payments use the owner-approved AI PEOPLE LEGACY Inc account and existing AIaaS
tax configuration. Applicable taxes are added by Stripe. Custom support starts at
US$5.01, with US$18 suggested. No test charge was made. Public voice remains
disabled, and contributions do not purchase minutes or subscriptions.
