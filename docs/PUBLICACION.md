# Virtual Rabbi · Publicación / Deployment

## Español

La aplicación privada sigue en 127.0.0.1:8790. La biblioteca pública usa otro proceso,
127.0.0.1:8791, y recibe tráfico exclusivamente desde el túnel Cloudflare
`virtualrabbi-mac`. No se abre un puerto entrante en el router.

El catálogo público es una copia seleccionada de las lecciones revisadas. No incluye
el progreso, notas o conversaciones del propietario. Cada navegador recibe una
identidad aleatoria firmada en una cookie Secure/HttpOnly. No es todavía una cuenta:
al borrar cookies o cambiar de dispositivo no se recupera el progreso anterior.
Los endpoints de llamadas, chat IA y cobros están cerrados en el servidor público.

- Actualizar catálogo: `python3 scripts/publish_catalog.py`.
- Instalar servicio público: `python3 scripts/install_public.py`.
- Instalar también el conector autorizado: `python3 scripts/install_public.py --tunnel`.
- Credencial: `.runtime/deploy/tunnel-token`, permisos 0600, nunca en GitHub.
- Estado privado de visitantes: `.runtime/public/readers/`, nunca en GitHub.
- Secreto de firmas: `.runtime/public/cookie-secret`; conservar al respaldar los avances.
- Agentes: `net.virtualrabbi.public` y `net.virtualrabbi.tunnel`, al iniciar sesión en macOS.
- La Mac necesita permanecer encendida, despierta y conectada a Internet.

DNS: Cloudflare administra el dominio con virginia.ns.cloudflare.com y
zeus.ns.cloudflare.com. Conservar MX, SPF, DKIM, DMARC y autodiscover de IONOS.
El túnel tiene ID `0121a8d0-1bbf-49ba-bef8-639f2889f13e`.

Para activar aportaciones, guardar `.runtime/public/support-links.json` con enlaces públicos
`https://buy.stripe.com/...` para las claves `5`, `18`, `52`, `100`, `260`,
`450`, `1800` y `other`. El enlace `other` debe exigir mínimo US$5.01 en Stripe. No contiene claves. Sin ese enlace no aparece un botón
de pago. Las aportaciones son voluntarias y no compran minutos ni habilitan voz.
Antes de habilitar voz pública: identidad de usuario persistente, límites globales
aplicados por el servidor, registro fiable de consumo y cierre de sesiones desde el
servidor. Un contador modificable desde el navegador no sirve para limitar gastos.

## English

The owner's local application remains on port 8790. A separate public reader runs
on loopback port 8791 behind the `virtualrabbi-mac` Cloudflare Tunnel. Only reviewed
teaching content is published. Owner progress, notes, transcripts and credentials
are excluded. Signed Secure/HttpOnly cookies isolate visitor data by browser; these
are not cross-device accounts. Clearing cookies loses access to that browser's
previous progress. Public AI calls and checkout remain disabled.

Run `scripts/publish_catalog.py` to refresh the curated catalog, then
`scripts/install_public.py --tunnel` using the project's Python environment to install
both user LaunchAgents. Keep tunnel credentials, the signing secret and visitor
state out of Git. The Mac must stay awake, online and logged in. Preserve IONOS mail
records when updating web DNS.

Optional `.runtime/public/support-links.json` maps the seven approved amounts
and `other` to public Stripe Payment Links on `https://buy.stripe.com/`.
The custom amount link must enforce a US$5.01 minimum in Stripe. Contributions do not purchase voice access. Public voice
requires server-enforced usage budgets and session termination before activation.
