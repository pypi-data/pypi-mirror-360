# VoiceBot

VoiceBot is a lightweight Discord bot that posts a message in the first text channel it can write to whenever someone joins a voice channel. Idea and code originally from/heavily inspired by [Dan Petrolito's article](https://blog.danpetrolito.xyz/i-built-something-that-changed-my-friend-gro-social-fabric/).

---

## ✨ Features

| Feature | Details |
|---------|---------|
| Voice‑join announcements | Sends one of several random phrases (e.g., *“Mitchell jumped into General”*) whenever a member joins a voice channel. |
| Auto‑delete | Messages disappear after 5 minutes to keep channels tidy. |
| Private by default | Designed to run only on **your** server (toggleable in Discord Dev Portal). |
| Zero database required | Fully functional without a database (hooks included if you want to log joins). |
| Runs anywhere | Tested on Ubuntu 24.04 in an LXC container on Proxmox, but any system with Python ≥ 3.11 works. |

---

## 📝 Setup Guide

This guide utilizes [uv](https://docs.astral.sh/uv/) to manage Python and run the bot for simplicity.

### 1 ‒ Create & Configure the Bot in Discord

1. **Open the Developer Portal:** <https://discord.com/developers/applications>  
2. **New Application** → give it a name (e.g. *VoiceBot*).  
3. **Installation → Install Link → *None***
4. **Bot → Add Bot → Yes, do it!**  
5. **Copy the Token** — you’ll need this for the `.env` file.  
6. **Privileged Gateway Intents:** toggle **Server Members Intent** **ON**.  
7. **Public Bot:** *OFF* (keeps your bot private).  
8. **OAuth2 → URL Generator**  
   - Scopes: **bot**  
   - Bot Permissions: **View Channels**, **Send Messages**, **Embed Links**  
   Copy the generated URL, visit it, and invite the bot to your server.

### 2 ‒ Install Python & uv

```bash
# Install uv (one‑liner)
# WARNING: Installs to /usr/local/bin so that all users can access uv
curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="/usr/local/bin" sh
```

> **Why uv?** It’s a drop‑in replacement for `pip`/`venv` that installs dependencies in lightning‑fast Rust.

### 3 ‒ Run with UVX

> Using the uvx command with the "--refresh" flag will download dependencies on each run, so updates are automatic.

```bash
uvx --refresh discord-voicebot --token=<your_discord_token_here>
```

### 4 ‒ Running 24 × 7 with systemd (Ubuntu/Debian)

> This creates a service that will run the bot in the background. The bot will automatically start at boot. Be sure to replace <your_discord_token_here> with your actual token.

```bash
# 4.1  Create service user (optional but recommended)
sudo useradd -r -m -s /usr/sbin/nologin discord-voicebot

# 4.2  Create working directory
sudo mkdir -p /opt/discord-voicebot
sudo chown discord-voicebot:discord-voicebot /opt/discord-voicebot

# 4.3  Create the systemd unit file
sudo tee /etc/systemd/system/discord-voicebot.service > /dev/null <<EOF
[Unit]
Description=Discord VoiceBot instance
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=discord-voicebot
WorkingDirectory=/opt/discord-voicebot
EnvironmentFile=/etc/discord-voicebot/bot.env
ExecStart=/usr/local/bin/uvx --refresh discord-voicebot
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 4.4 Create an environment file with your token
sudo install -Dm600 /dev/null /etc/discord-voicebot/bot.env
echo "DISCORD_TOKEN=<your_discord_token_here>" | sudo tee /etc/discord-voicebot/bot.env > /dev/null

# 4.5 Fire it up (using "bot" as the instance name)
sudo systemctl daemon-reload
sudo systemctl enable --now discord-voicebot
sudo journalctl -u discord-voicebot -f   # live logs
```

---

## Managing the Discord Token

VoiceBot supports multiple ways to provide your Discord token, checked in this priority order:

### 1. Command Line
Provide the token as an argument when launching the script:
```bash
uvx discord-voicebot --token=<your_discord_token_here>
```
This sets the `_VOICEBOT_TOKEN_CLI` environment variable internally.

### 2. Environment Variable
Set the `DISCORD_TOKEN` environment variable:
```bash
export DISCORD_TOKEN=<your_discord_token_here>
uvx discord-voicebot
```

### 3. Configuration File (.env)
Create a `.env` file in your XDG config directory:
```bash
# Create the config directory
mkdir -p ~/.config/voicebot

# Add your token
echo "DISCORD_TOKEN=<your_discord_token_here>" > ~/.config/voicebot/.env
```

> **⚠️ Security Note:** Never commit `.env` files containing tokens to version control. Add `.env` to your `.gitignore`.

### For systemd Service
The systemd template service reads the token from an environment file:
```bash
sudo systemctl enable --now discord-voicebot
```
This expects `/etc/discord-voicebot/bot.env` to contain your token.

---

## Optional Health Checks

Pass a URL to `--ping-url` to periodically ping a health check service. The
interval in seconds can be adjusted with `--ping-interval` (defaults to 300).
You can also set the environment variables `VOICEBOT_PING_URL` and
`VOICEBOT_PING_INTERVAL` (or define them in the config `.env` file) instead of
command line options:

```bash
uvx discord-voicebot --ping-url=https://hc-ping.com/YOUR-UUID --ping-interval=600
```

---

## 🧪 Development & Testing

| Task | Command |
|------|---------|
| Add a new dependency | `uv add --script voicebot.py PACKAGE_NAME` |
| Lint (optional) | `uv pip install ruff && ruff check .` |

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org).

---

## 🛠 Troubleshooting

| Symptom | Fix |
|---------|-----|
| *Bot prints “TOKEN not set” and exits* | Ensure `.env` exists and `DISCORD_TOKEN` is correct. |
| *No message appears when someone joins voice* | 1) Verify the bot has **View Channels** & **Send Messages** perms in at least one text channel. 2) Make sure **Server Members Intent** is enabled and the bot was restarted afterward. |
| *systemd service keeps restarting* | `sudo journalctl -u voicebot -xe` for detailed logs. Most issues are missing token or bad Python path. |

---

## ❤️ Contributing

1. Fork → Branch → PR.  
2. Follow the commit style.  
3. All code must pass `ruff`.  
