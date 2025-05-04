# Running AI Hedge Fund in Production

This guide explains how to run the AI Hedge Fund application in a production environment using a WSGI server.

## Prerequisites

Before deploying to production, ensure you have installed the project with Poetry including production dependencies:

```bash
# Install Poetry if you haven't already
# curl -sSL https://install.python-poetry.org | python3 -

# Install all dependencies including production ones
poetry install
```

## Running with Built-in Production Mode

The application includes a built-in production mode that uses Gunicorn as the WSGI server. To use it:

```bash
poetry run python webui.py --production --host 0.0.0.0 --api-port 5000 --workers 4
```

Options:
- `--host`: The host address to bind to (default: localhost)
- `--api-port`: The port to run the API server on (default: 5000)
- `--workers`: Number of worker processes (default: 4)

## Running with External WSGI Server

Alternatively, you can use an external WSGI server like Gunicorn directly:

### Using Gunicorn

```bash
poetry run gunicorn -w 4 -b 0.0.0.0:5000 --worker-class gevent --timeout 120 wsgi:app
```

Options:
- `-w 4`: Run 4 worker processes
- `-b 0.0.0.0:5000`: Bind to all interfaces on port 5000
- `--worker-class gevent`: Use gevent worker class for better performance
- `--timeout 120`: Set worker timeout to 120 seconds

### Using Supervisor for Process Management

For production deployments, it's recommended to use a process manager like Supervisor:

1. Install Supervisor: `poetry add --group dev supervisor`

2. Create a configuration file `/etc/supervisor/conf.d/ai-hedge-fund.conf`:

```ini
[program:ai-hedge-fund]
command=/path/to/poetry run gunicorn -w 4 -b 0.0.0.0:5000 --worker-class gevent --timeout 120 wsgi:app
directory=/path/to/ai-hedge-fund
user=www-data
autostart=true
autorestart=true
stdout_logfile=/var/log/ai-hedge-fund/gunicorn.log
stderr_logfile=/var/log/ai-hedge-fund/gunicorn.err.log
environment=PYTHONPATH="/path/to/ai-hedge-fund"
```

3. Create log directory: `mkdir -p /var/log/ai-hedge-fund`

4. Update Supervisor: `supervisorctl update`

## Nginx Configuration

For production deployments, it's recommended to use Nginx as a reverse proxy in front of the WSGI server:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Environment Variables

Ensure all required environment variables are set in your production environment. You can use a `.env` file or set them directly in your environment.

## Security Considerations

1. Never run the application as root
2. Set appropriate file permissions
3. Use HTTPS in production
4. Restrict access to the API endpoints if needed
5. Consider using environment-specific configuration files