# Quothed

Quothed is a small Flask application used to demonstrate a production-style
deployment on Ubuntu. It displays one randomly selected quote from a text
file. The deployment will later use Gunicorn, Systemd, nginx, and HTTPS.

This is a learning exercise. Certificates used later are intended for
controlled testing, not for a public certificate deployment.

## Requirements

The guide targets Ubuntu 24.04 LTS or newer, Python 3.12 or newer, and uv.
One quote is stored on each line in `src/quothed/quotes.txt`.

## Install uv system-wide

Install `uv` and `uvx` system-wide so they are available independently of a
developer's home directory:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sudo env UV_INSTALL_DIR=/usr/local/bin UV_NO_MODIFY_PATH=1 sh
```

Verify that both commands are installed in `/usr/local/bin`:

```sh
command -v uv
command -v uvx
uv --version
uvx --version
```

## Install the project

Change into the project directory and install the project and development
dependencies:

```sh
cd quothed
uv sync --dev
```

This creates the project virtual environment and installs Flask and pytest.

## Run the Flask application directly

```sh
uv run quothed
```

The Flask development server starts at `http://127.0.0.1:5000/`.

Stop the server with `Ctrl-C`.

## Run the tests

```sh
uv run pytest -q
```

The tests verify quote loading, the root route, HTML rendering, and stylesheet
delivery.

## Run the application with Gunicorn

Gunicorn is the WSGI server used for the production-style deployment. Install
the updated dependencies if needed:

```sh
uv sync --dev
```

Start Gunicorn with the Flask application object:

```sh
uv run gunicorn quothed:app
```

Gunicorn listens on `127.0.0.1:8000` by default. Verify the application from
the Ubuntu machine:

```sh
curl http://127.0.0.1:8000/
```

The response should contain one of the quotes and the page markup. Stop
Gunicorn with `Ctrl-C`.

## Run Gunicorn with Systemd

Run the application as a dedicated system user. The user has no login shell
and owns the application directory at `/var/lib/quothed`.

The commands in this section are run as an administrator with `sudo`.

### Create the system user

Create the user, group, and home directory:

```sh
sudo useradd --system --user-group --home-dir /var/lib/quothed --create-home --shell /usr/sbin/nologin quothed
```

The command is intentionally explicit about the home directory. This is the
directory used as the application's deployment directory, not a human user's
home directory.

### Install the application

Copy the project into the deployment directory. From the project directory,
one simple approach is:

```sh
sudo cp -a . /var/lib/quothed/
```

Set ownership before creating the virtual environment:

```sh
sudo chown -R quothed:quothed /var/lib/quothed
```

Install only runtime dependencies using the system-wide `uv` installation:

```sh
sudo uv sync --no-dev --directory /var/lib/quothed
```

The command creates `/var/lib/quothed/.venv`. The systemd service uses the
Gunicorn executable from that virtual environment directly.

### Install the service file

The repository contains the service definition in
`deploy/quothed.service`. Copy it into systemd's local unit directory:

```sh
sudo cp deploy/quothed.service /etc/systemd/system/quothed.service
```

Reload systemd, enable the service at boot, and start it now:

```sh
sudo systemctl daemon-reload
sudo systemctl enable quothed.service
sudo systemctl start quothed.service
```

Check the service status:

```sh
sudo systemctl status quothed.service
```

Verify the application through Gunicorn:

```sh
curl http://127.0.0.1:8000/
```

If the service fails, inspect its recent journal entries:

```sh
sudo journalctl --unit quothed.service --since today
```

## Install nginx and configure the HTTP reverse proxy

Put nginx in front of the Systemd-managed Gunicorn process. This configuration
uses plain HTTP.

### Install nginx

Install nginx from the Ubuntu package repository:

```sh
sudo apt update
sudo apt install nginx
```

Verify that nginx is running:

```sh
sudo systemctl status nginx
```

### Install the Quothed site configuration

The repository contains the version 1 nginx configuration in
`deploy/nginx/quothed.conf`. It listens on port 80 and forwards requests to
Gunicorn on `127.0.0.1:8000`.

Copy the configuration into nginx's available-sites directory:

```sh
sudo cp deploy/nginx/quothed.conf /etc/nginx/sites-available/quothed
```

Enable the site with a symbolic link:

```sh
sudo ln -s /etc/nginx/sites-available/quothed /etc/nginx/sites-enabled/quothed
```

If the default nginx site is enabled, remove only its enabled-site link so it
does not handle the test request before the Quothed site:

```sh
sudo rm /etc/nginx/sites-enabled/default
```

Test the configuration before reloading nginx:

```sh
sudo nginx -t
```

Reload nginx after the configuration test succeeds:

```sh
sudo systemctl reload nginx
```

### Verify the HTTP reverse proxy

Verify the response through nginx:

```sh
curl --header 'Host: quothed.example.com' http://127.0.0.1/
```

The response should contain the Quothed page. At this point the request path
is:

```text
client -> nginx:80 -> Gunicorn:8000 -> Flask
```

## Generate certificates for HTTPS

The HTTPS setup uses a local root CA and a server certificate signed by that
CA. This models the certificate chain used in production while keeping the
exercise self-contained. These certificates are for the Ubuntu VM and learning
environment; they are not public production certificates.

The repository contains a script at
`scripts/generate-certificates.sh`. Make it executable and run it:

```sh
chmod +x scripts/generate-certificates.sh
./scripts/generate-certificates.sh
```

The script writes the generated files to `certificates/`:

```text
certificates/root-ca.crt
certificates/root-ca.key
certificates/server.crt
certificates/server.key
```

The server certificate contains `quothed.example.com` as a Subject Alternative
Name. The private keys must be kept private. Do not commit the `certificates/`
directory to source control.

The script accepts an output directory and hostname when needed:

```sh
./scripts/generate-certificates.sh /tmp/quothed-certs quothed.example.com
```

## Install the HTTPS files

Create a private directory for the nginx certificate files:

```sh
sudo install -d -m 0750 /etc/quothed/ssl
```

Install the server certificate and private key:

```sh
sudo install -m 0644 certificates/server.crt /etc/quothed/ssl/server.crt
sudo install -m 0600 certificates/server.key /etc/quothed/ssl/server.key
```

The root CA certificate is not required by nginx. Keep it available for
importing into clients such as Firefox:

```sh
install -m 0644 certificates/root-ca.crt /tmp/quothed-root-ca.crt
```

## Install the nginx HTTPS configuration

Version 2 of the nginx configuration is in
`deploy/nginx/quothed-ssl.conf`. It redirects HTTP to HTTPS and proxies HTTPS
requests to Gunicorn.

Replace the version 1 site configuration:

```sh
sudo cp deploy/nginx/quothed-ssl.conf /etc/nginx/sites-available/quothed
sudo nginx -t
sudo systemctl reload nginx
```

Verify that HTTPS responds:

```sh
curl --cacert certificates/root-ca.crt \
    --header 'Host: quothed.example.com' \
    https://quothed.example.com/
```

The HTTP endpoint should redirect to HTTPS:

```sh
curl --header 'Host: quothed.example.com' --head http://127.0.0.1/
```

The request path is now:

```text
client -> nginx:443 -> Gunicorn:8000 -> Flask
```

## Trust the root CA in Firefox

Firefox has its own certificate store. Importing the root CA into Ubuntu's
system certificate store does not automatically make Firefox trust it.

1. Open Firefox Settings.
2. Open Privacy & Security.
3. Find the Certificates section and click View Certificates.
4. Select the Authorities tab.
5. Click Import and select `certificates/root-ca.crt`.
6. Enable the option to trust this CA to identify websites.
7. Confirm the import and restart Firefox if necessary.

Open `https://quothed.example.com/` in Firefox. The browser should accept the
server certificate when the hostname resolves to the Ubuntu VM. The root CA
must be imported on each browser profile that should trust this learning CA.

## Project structure

```text
src/quothed/
    __init__.py       Flask application and quote loading
    quotes.txt        One quote, including attribution, per line
    templates/
        index.html     HTML page for the selected quote
    static/
        style.css      Page layout and typography
deploy/
    quothed.service   Systemd service for Gunicorn
    nginx/
        quothed.conf   Version 1 HTTP reverse proxy configuration
        quothed-ssl.conf Version 2 HTTPS reverse proxy configuration
scripts/
    generate-certificates.sh  Generate the local CA and server certificate
tests/
    test_app.py       Application tests
goal.md              Project goal and scope
pyproject.toml       Project metadata and dependencies
```

