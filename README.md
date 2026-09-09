<p align="center">
  <img src="icon.jpg" alt="Kehua Tech Logo" width="200"/>
</p>

<h1 align="center">Kehua WiseSolar – Home Assistant Integration</h1>

<p align="center">
  <a href="https://github.com/lazarojpr/kehua_wisesolar/releases"><img src="https://img.shields.io/github/v/release/lazarojpr/kehua_wisesolar?style=flat-square" alt="Release"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/lazarojpr/kehua_wisesolar?style=flat-square" alt="License"/></a>
  <a href="https://github.com/lazarojpr/kehua_wisesolar/stargazers"><img src="https://img.shields.io/github/stars/lazarojpr/kehua_wisesolar?style=flat-square" alt="Stars"/></a>
  <img src="https://img.shields.io/badge/HACS-Custom-orange?style=flat-square" alt="HACS"/>
</p>

<p align="center">
  A custom <a href="https://www.home-assistant.io/">Home Assistant</a> integration for <strong>Kehua Tech</strong> solar inverters using the <strong>WiseSolar+ / Energy Cloud</strong> API.
</p>

---

## ✨ Features

- ☀️ **PV Power** – Real-time solar generation (W)
- ⚡ **Grid Power** – Power flowing to/from the grid (W)
- 🏠 **Load Power** – Household consumption (W)
- 🔋 **Battery Power** – Battery charge/discharge (W)
- 📊 **Daily Generation** – Energy produced today (kWh)
- 📈 **Total Generation** – Lifetime energy produced (kWh)
- 🟢 **Inverter Status** – Online / Offline / Abnormal

## 📋 Requirements

- Home Assistant **2024.1.0** or newer
- A Kehua inverter registered in the **WiseSolar+** mobile app
- Valid WiseSolar+ account credentials (phone number or email + password)

## 🚀 Installation

### HACS (Recommended)

1. Open **HACS** in Home Assistant
2. Click the **⋮** menu → **Custom repositories**
3. Add this repository URL: `https://github.com/lazarojpr/kehua_wisesolar`
4. Select category: **Integration**
5. Click **Download**
6. Restart Home Assistant

### Manual

1. Copy the `kehua_wisesolar` folder to your `custom_components` directory:
   ```
   /config/custom_components/kehua_wisesolar/
   ```
2. Restart Home Assistant

## ⚙️ Configuration

1. Go to **Settings → Devices & Services**
2. Click **+ Add Integration**
3. Search for **Kehua WiseSolar**
4. Enter your credentials:

| Field | Description |
|---|---|
| **Username** | Your WiseSolar+ phone number or email |
| **Password** | Your WiseSolar+ password |
| **Plant ID** | *(Optional)* Leave blank for auto-discovery |

> **Note:** These are the same credentials you use in the WiseSolar+ mobile app.

## 📡 Sensors

Once configured, the integration creates the following sensor entities:

| Sensor | Unit | Description |
|---|---|---|
| `sensor.pv_power` | W | Current solar panel output |
| `sensor.grid_power` | W | Power from/to the electrical grid |
| `sensor.load_power` | W | Current household consumption |
| `sensor.battery_power` | W | Battery charge (+) or discharge (−) |
| `sensor.day_energy` | kWh | Energy generated today |
| `sensor.total_energy` | kWh | Total lifetime energy generated |
| `sensor.status` | — | Inverter status (Normal / Offline / Abnormal) |

## 🔧 How It Works

This integration communicates with the **Kehua Energy Cloud** API (`energy.kehua.com`) — the same backend used by the official WiseSolar+ mobile app. Data is polled every **60 seconds** by default.

**Authentication flow:**
1. Credentials are AES-encrypted and sent to the login endpoint
2. A JWT token is returned and used for subsequent API calls
3. The integration auto-discovers your power plant (station) if no Plant ID is provided

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Some areas where help is appreciated:
- Support for multiple stations/plants
- Additional sensor types (string-level data, daily consumption, revenue)
- Improved error handling and retry logic
- Translations for other languages
- Energy dashboard integration improvements

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## ⚠️ Disclaimer

This integration is **not affiliated with or endorsed by Kehua Tech**. It is an unofficial community project created by reverse-engineering the public WiseSolar+ mobile app API. Use at your own risk.
