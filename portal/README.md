# MedDemo portal (static homepage)

Static landing page for **https://meddemo.org/** — separate from the Django BRPI app at `/brpi/`.

## Files

```text
portal/
├── index.html
└── css/
    └── portal.css
```

## Deploy on the VPS

### 1. Upload to the server

Upload the `portal/` folder contents to e.g.:

```text
/var/www/meddemo-portal/
├── index.html
└── css/
    └── portal.css
```

WinSCP: create `/var/www/meddemo-portal/` and upload `index.html` + `css/portal.css`.

### 2. Update Apache site config

Edit `/etc/apache2/sites-available/meddemo.org.conf` so the **root** serves the portal and `/brpi/` still proxies to Gunicorn:

```apache
<VirtualHost *:80>
    ServerName meddemo.org
    ServerAlias www.meddemo.org

    DocumentRoot /var/www/meddemo-portal

    <Directory /var/www/meddemo-portal>
        Options -Indexes +FollowSymLinks
        AllowOverride None
        Require all granted
        DirectoryIndex index.html
    </Directory>

    Alias /brpi/static/ /var/www/brpi/staticfiles/
    <Directory /var/www/brpi/staticfiles/>
        Require all granted
    </Directory>

    ProxyPass /brpi/static/ !
    ProxyPreserveHost On
    RequestHeader set X-Forwarded-Proto "http"
    ProxyPass /brpi/ http://127.0.0.1:8001/
    ProxyPassReverse /brpi/ http://127.0.0.1:8001/
</VirtualHost>
```

If certbot already created a `:443` block, add the same `DocumentRoot` and `<Directory>` there too (certbot usually keeps existing directives).

### 3. Permissions and reload

```bash
sudo chown -R www-data:www-data /var/www/meddemo-portal
sudo apache2ctl configtest
sudo systemctl reload apache2
```

### 4. Verify

- https://meddemo.org/ → portal homepage
- https://meddemo.org/brpi/ → BRPI demonstrator

## Adding future demos

1. Deploy each demo under its own path (`/demo-name/`).
2. Add a new card in `portal/index.html` linking to that path.
3. Re-upload `index.html` only — no Django restart needed for portal changes.

## Optional: subdomain later

If a demo grows large, move it to e.g. `brpi.meddemo.org` and keep the portal card updated. Subdirectories remain the simplest default for a research demo hub.
