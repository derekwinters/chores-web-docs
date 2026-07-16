# HTTPS / TLS

The bundled stack serves plain HTTP. For anything reachable outside your own
machine, put a TLS-terminating reverse proxy in front of it and get a
certificate from [Let's Encrypt](https://letsencrypt.org/).

## Architecture

The proxy sits at the edge and forwards plaintext HTTP to the `frontend`
container over the compose network; `frontend`'s own Nginx keeps proxying
`/api/` to `backend` exactly as it does today. Nothing in the app needs to
know TLS is involved — it terminates entirely at the edge.

```
client --HTTPS--> [reverse proxy :443] --HTTP--> frontend:80 --HTTP--> backend:8000
```

## Prerequisites

- A domain name with a DNS **A** (and/or **AAAA**) record pointing at this
  host's public IP.
- Ports **80** and **443** reachable from the internet. Port 80 is required
  for the ACME HTTP-01 challenge that both options below use, and is also
  used to redirect HTTP → HTTPS.

## Recommended: Caddy

[Caddy](https://caddyserver.com/) requests and renews the Let's Encrypt
certificate automatically — there's no certbot container, cron job, or
renewal hook to maintain. This is the path documented and smoke-tested
here.

1. **Download the overlay files** alongside your `docker-compose.yml`:

   ```bash
   curl -fsSLO https://raw.githubusercontent.com/derekwinters/chores-web-docs/main/docs/deployment/docker-compose.https.yml
   curl -fsSLO https://raw.githubusercontent.com/derekwinters/chores-web-docs/main/docs/deployment/Caddyfile
   ```

2. **Set your domain** in `.env` (alongside `JWT_SECRET`, see
   [Setup](setup.md)):

   ```bash
   echo "DOMAIN=chores.example.com" >> .env
   ```

3. **Start the stack with the HTTPS overlay:**

   ```bash
   docker compose -f docker-compose.yml -f docker-compose.https.yml up -d
   ```

   Caddy listens on 80/443, obtains a certificate for `DOMAIN` on first
   request, and reverse-proxies to `frontend:80`.

The overlay file and Caddyfile:

```yaml title="docker-compose.https.yml"
--8<-- "docs/deployment/docker-compose.https.yml"
```

```caddyfile title="Caddyfile"
--8<-- "docs/deployment/Caddyfile"
```

### Verifying renewal

Caddy renews certificates automatically in the background well before
expiry — there's nothing to schedule. To confirm it's working, check the
logs:

```bash
docker compose logs caddy | grep -i certificate
```

## Alternative: nginx + certbot

If you're already standardized on nginx at the edge, terminate TLS there
instead. This requires more manual wiring than Caddy: you own certificate
acquisition, renewal, and reloading nginx after each renewal.

1. **Obtain a certificate** with [certbot](https://certbot.eff.org/), e.g.
   via the webroot method (adjust paths to wherever nginx serves the ACME
   challenge from):

   ```bash
   certbot certonly --webroot -w /var/www/certbot -d chores.example.com
   ```

2. **Mount the certificate** into the nginx container:

   ```yaml
   volumes:
     - /etc/letsencrypt/live/chores.example.com:/etc/ssl/certs:ro
   ```

3. **Configure nginx** to terminate TLS and proxy to the frontend
   container, forwarding the standard headers:

   ```nginx
   server {
     listen 443 ssl;
     server_name chores.example.com;
     ssl_certificate     /etc/ssl/certs/fullchain.pem;
     ssl_certificate_key /etc/ssl/certs/privkey.pem;

     location / {
       proxy_pass http://frontend:80;
       proxy_set_header Host $host;
       proxy_set_header X-Forwarded-Proto $scheme;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
     }
   }

   server {
     listen 80;
     server_name chores.example.com;
     location /.well-known/acme-challenge/ {
       root /var/www/certbot;
     }
     location / {
       return 301 https://$host$request_uri;
     }
   }
   ```

4. **Automate renewal.** Certificates from Let's Encrypt expire every 90
   days. Run `certbot renew` on a schedule (systemd timer or cron) and
   reload nginx afterward so it picks up the renewed certificate:

   ```bash
   certbot renew --quiet --deploy-hook "docker compose exec nginx nginx -s reload"
   ```

   Verify the renewal path works without waiting 90 days:

   ```bash
   certbot renew --dry-run
   ```

## Alternative: Traefik

If you already run [Traefik](https://traefik.io/) as your cluster or host
edge, it can terminate TLS and acquire Let's Encrypt certificates
automatically via its ACME resolver — no certbot and no manual renewal, like
Caddy. This path is not smoke-tested here, so treat the snippet below as a
starting point rather than a drop-in overlay.

Point a router at the `frontend` service with an ACME (Let's Encrypt)
certificate resolver and let Traefik handle 80 → 443 redirection. Using
container labels on the `frontend` service:

```yaml title="docker-compose.https.yml (Traefik variant)"
services:
  traefik:
    image: traefik:v3
    command:
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.le.acme.httpchallenge=true"
      - "--certificatesresolvers.le.acme.httpchallenge.entrypoint=web"
      - "--certificatesresolvers.le.acme.email=you@example.com"
      - "--certificatesresolvers.le.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - chores-traefik-acme:/letsencrypt

  frontend:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.chores.rule=Host(`chores.example.com`)"
      - "traefik.http.routers.chores.entrypoints=websecure"
      - "traefik.http.routers.chores.tls.certresolver=le"
      - "traefik.http.services.chores.loadbalancer.server.port=80"

volumes:
  chores-traefik-acme:
```

Traefik sets `X-Forwarded-Proto` / `X-Forwarded-For` on the proxied request
by default, so the forwarded-header behaviour matches the Caddy and nginx
examples above.

## Forwarded headers

All three examples above set `X-Forwarded-Proto`, `X-Forwarded-For`, and
`Host` on the proxied request, which is the standard way to tell an upstream
it's being served over HTTPS even though the connection to it is plain HTTP.

## Are application changes required?

**No.** Edge TLS termination is fully transparent to the current stack — you
can put any of the proxies above in front of it without changing the
`frontend` or `backend` images:

- **No mixed content.** The frontend talks to the API over the relative path
  `/api/v1` (never an absolute `http://` URL), so every API call inherits the
  page's `https://` scheme automatically once the proxy is in front.
- **No `Secure`-cookie concern.** Authentication uses a bearer token sent in
  the `Authorization` header and held in the browser's `localStorage`, not a
  session cookie — so there are no cookie `Secure` / `SameSite` flags that
  need the app to know it's behind TLS.
- **The backend is origin-agnostic.** It is reached only through the
  frontend's same-origin `/api/` proxy, and it neither emits absolute URLs
  nor sets cookies, so it needs no `X-Forwarded-*` awareness to work
  correctly behind the proxy.

!!! note "Optional backend hardening (a separate, not-yet-filed follow-up)"
    The backend runs `uvicorn` **without** `--proxy-headers`, so it currently
    *ignores* `X-Forwarded-Proto` / `X-Forwarded-For`: from its point of view
    every request arrives as plain HTTP from the frontend container, and the
    "client" IP is the proxy, not the real caller. Nothing in the app depends
    on that today, so it is not a blocker. It would only matter if a future
    feature needs the real client scheme or IP (for example, recording the
    caller's address in the authentication log). If that day comes, enabling
    `--proxy-headers` (and trusting the proxy) is a **`chores-web-backend`**
    change, and any frontend-side URL/scheme handling would be a
    **`chores-web-frontend`** change — both out of scope for this
    user-facing docs repo, and each should be filed as its own issue in the
    respective code repository rather than fixed here.

## Updating CORS

If the backend is reachable directly (not only through the frontend's
`/api/` proxy) or you're serving the frontend from a different origin than
the backend, update `allow_origins` to your HTTPS origin — see
[Operations → CORS](operations.md#cors).
