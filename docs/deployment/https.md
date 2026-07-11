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

## Forwarded headers

Both examples above set `X-Forwarded-Proto`, `X-Forwarded-For`, and `Host`
on the proxied request, which is the standard way to tell the app it's
being served over HTTPS even though the connection to it is plain HTTP.

!!! warning "Unverified against application code"
    Whether the frontend and backend containers currently *read and act on*
    these headers — for example, generating `https://` URLs, treating the
    connection as secure for cookie flags, or trusting `X-Forwarded-For`
    for logging — has not been verified against the `chores-web-frontend`
    and `chores-web-backend` source. If you hit mixed-content warnings,
    incorrect redirects, or cookies not being marked `Secure` once you're
    behind TLS, that's the first place to look; please open an issue in the
    relevant repository if you find gaps.

## Updating CORS

If the backend is reachable directly (not only through the frontend's
`/api/` proxy) or you're serving the frontend from a different origin than
the backend, update `allow_origins` to your HTTPS origin — see
[Operations → CORS](operations.md#cors).
