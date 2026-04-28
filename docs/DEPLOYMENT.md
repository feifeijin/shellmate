# Deployment (Linux VPS + systemd + Caddy)

## 1. Install

```bash
git clone https://github.com/yourorg/your-private-bot /opt/mybot
cd /opt/mybot
python3 -m venv .venv
source .venv/bin/activate
pip install shellmate            # public package
pip install -r requirements.txt  # your private deps
cp .env.example .env
# Fill in .env — never commit it
```

## 2. systemd service

```ini
# /etc/systemd/system/mybot.service
[Unit]
Description=ShellMate Bot
After=network.target

[Service]
User=runner
WorkingDirectory=/opt/mybot
EnvironmentFile=/opt/mybot/.env
ExecStart=/opt/mybot/.venv/bin/python main.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable --now mybot
journalctl -fu mybot
```

## 3. Caddy (HTTPS for webhook mode)

```
# /etc/caddy/Caddyfile
bot.example.com {
    reverse_proxy localhost:8080
}
```

Set `WEBHOOK_BASE_URL=https://bot.example.com` in `.env`.

## 4. Polling mode (no domain needed)

Leave `WEBHOOK_BASE_URL` empty — the bot falls back to polling automatically.
