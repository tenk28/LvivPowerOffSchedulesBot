# Energy Schedule Telegram Bot

This project downloads an image from a website and sends it to a Telegram chat when the image changes.  
It runs continuously and is designed to be started automatically using systemd.

---

## Requirements

- Python 3.10+
- Linux (Ubuntu recommended)
- Telegram bot token and chat ID
- Playwright dependencies

---

##  Set up virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install
```

## Configure .env
```bash
vim .env
```

## Systemd service (auto start on boot)

### 1. Configure service file
```bash
vim energy_schedule.service
```

### 2. Copy the service file
```bash
sudo cp energy_schedule.service /etc/systemd/system/
```

### 3. Start the service
```bash
sudo systemctl daemon-reload
sudo systemctl enable energy_schedule.service
sudo systemctl start energy_schedule.service
```

### 4. Check status
```bash
sudo systemctl status energy_schedule.service
journalctl -u energy_schedule.service -f
```
