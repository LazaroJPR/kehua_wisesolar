<p align="center">
  <img src="icon.png" alt="Kehua Tech Logo" width="200"/>
</p>

<h1 align="center">Kehua WiseSolar – Home Assistant Integration</h1>

<p align="center">
  <a href="https://github.com/lazarojpr/kehua_wisesolar/releases"><img src="https://img.shields.io/github/v/release/lazarojpr/kehua_wisesolar?style=flat-square" alt="Release"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/lazarojpr/kehua_wisesolar?style=flat-square" alt="License"/></a>
  <a href="https://github.com/lazarojpr/kehua_wisesolar/stargazers"><img src="https://img.shields.io/github/stars/lazarojpr/kehua_wisesolar?style=flat-square" alt="Stars"/></a>
  <img src="https://img.shields.io/badge/HACS-Custom-orange?style=flat-square" alt="HACS"/>
  <img src="https://img.shields.io/badge/Energy%20Dashboard-Compatible-success?style=flat-square" alt="Energy Dashboard"/>
</p>

<p align="center">
  A custom <a href="https://www.home-assistant.io/">Home Assistant</a> integration for <strong>Kehua Tech</strong> solar inverters using the <strong>WiseSolar+ / Energy Cloud</strong> API.
</p>

---

## ✨ Features

- ☀️ **Real-time Solar & Grid Monitoring** – PV power, grid net power, household load power.
- ⚡ **Energy Dashboard Native** – Full compatibility with Home Assistant Energy Dashboard (`state_class: total_increasing`, `device_class: energy`).
- 🔌 **PV String-Level Data** – Individual string voltage, current, and wattage (PV1, PV2).
- 🌐 **AC Grid Metrics** – Grid voltage, grid current, grid frequency, power factor.
- 📊 **Consumption & Generation Tracking** – Daily & lifetime generation and household consumption.
- 💰 **Financial Savings / Revenue** – Daily and total estimated economic savings.
- 🔋 **Battery & Hybrid Support** – Battery power, State of Charge (SOC), daily/total charge & discharge.
- 🌡️ **Inverter Diagnostics** – Internal temperature, heatsink temperature, operating hours, inverter status.
- 🔍 **Zero-Config Auto Discovery** – Automatically discovers your power plant ID and inverter serial number.

---

## 📋 Requirements

- Home Assistant **2024.1.0** or newer
- A Kehua inverter registered in the **WiseSolar+** mobile app
- Valid WiseSolar+ account credentials (phone number or email + password)

---

## 🚀 Installation

### HACS (Recommended)

1. Open **HACS** in Home Assistant.
2. Click the **⋮** menu (top right) → **Custom repositories**.
3. Add this repository URL: `https://github.com/lazarojpr/kehua_wisesolar`
4. Select category: **Integration**.
5. Click **Add**, then find **Kehua WiseSolar** and click **Download**.
6. Restart Home Assistant.

### Manual

1. Copy the `kehua_wisesolar` folder to your Home Assistant `custom_components` directory:
   ```bash
   /config/custom_components/kehua_wisesolar/
   ```
2. Restart Home Assistant.

---

## ⚙️ Configuration

1. Go to **Settings → Devices & Services**.
2. Click **+ Add Integration**.
3. Search for **Kehua WiseSolar**.
4. Enter your credentials:

| Field | Description |
|---|---|
| **Username** | Your WiseSolar+ phone number (e.g. `27996145888`) or email |
| **Password** | Your WiseSolar+ password |
| **Plant ID** | *(Optional)* Leave blank for automatic discovery |

---

## ⚡ Home Assistant Energy Dashboard Setup

This integration is designed to work seamlessly out-of-the-box with the Home Assistant **Energy Dashboard**:

1. Go to **Settings → Dashboards → Energy**.
2. **Solar Panels**:
   - Click **Add Solar Production**.
   - Select `sensor.geracao_total_acumulada` (or `sensor.total_energy`).
3. **Home Battery Storage** *(if using a hybrid inverter with battery)*:
   - Click **Add Battery System**.
   - Energy going into battery: `sensor.carga_da_bateria_no_dia` (or total charge).
   - Energy coming out of battery: `sensor.descarga_da_bateria_no_dia` (or total discharge).
4. **Energy Consumption**:
   - Select `sensor.consumo_total_acumulado` (or `sensor.total_consumption`).

---

## 📡 Sensor Entities

### ☀️ Solar & Power
| Sensor | Unit | Device Class | State Class | Description |
|---|---|---|---|---|
| `sensor.potencia_solar` | W | `power` | `measurement` | Current solar panel generation |
| `sensor.geracao_do_dia` | kWh | `energy` | `total_increasing` | Solar energy generated today |
| `sensor.geracao_total_acumulada` | kWh | `energy` | `total_increasing` | Total lifetime solar energy generated |
| `sensor.consumo_da_residencia` | W | `power` | `measurement` | Current household load power |
| `sensor.consumo_do_dia` | kWh | `energy` | `total_increasing` | Household electricity consumed today |
| `sensor.consumo_total_acumulado` | kWh | `energy` | `total_increasing` | Total lifetime household electricity consumed |

### 🔌 PV String Details (Branch Data)
| Sensor | Unit | Device Class | State Class | Description |
|---|---|---|---|---|
| `sensor.string_1_tensao` | V | `voltage` | `measurement` | PV String 1 DC voltage |
| `sensor.string_1_corrente` | A | `current` | `measurement` | PV String 1 DC current |
| `sensor.string_1_potencia` | W | `power` | `measurement` | PV String 1 calculated power |
| `sensor.string_2_tensao` | V | `voltage` | `measurement` | PV String 2 DC voltage |
| `sensor.string_2_corrente` | A | `current` | `measurement` | PV String 2 DC current |
| `sensor.string_2_potencia` | W | `power` | `measurement` | PV String 2 calculated power |

### 🌐 Electrical Grid
| Sensor | Unit | Device Class | State Class | Description |
|---|---|---|---|---|
| `sensor.potencia_da_rede` | W | `power` | `measurement` | Grid net power (import / export) |
| `sensor.tensao_da_rede` | V | `voltage` | `measurement` | AC grid voltage |
| `sensor.corrente_da_rede` | A | `current` | `measurement` | AC grid current |
| `sensor.frequencia_da_rede` | Hz | `frequency` | `measurement` | Grid AC frequency |
| `sensor.fator_de_potencia` | — | `power_factor` | `measurement` | Inverter power factor |

### 💰 Financial / Savings
| Sensor | Unit | Device Class | Description |
|---|---|---|---|
| `sensor.economia_do_dia` | R$ / currency | `monetary` | Estimated economic savings today |
| `sensor.economia_total` | R$ / currency | `monetary` | Total lifetime economic savings |

### 🔋 Battery (Hybrid Inverters)
| Sensor | Unit | Device Class | State Class | Description |
|---|---|---|---|---|
| `sensor.potencia_da_bateria` | W | `power` | `measurement` | Battery charge/discharge power |
| `sensor.bateria_soc` | % | `battery` | `measurement` | Battery State of Charge (SOC) |
| `sensor.carga_da_bateria_no_dia` | kWh | `energy` | `total_increasing` | Battery energy charged today |
| `sensor.descarga_da_bateria_no_dia` | kWh | `energy` | `total_increasing` | Battery energy discharged today |

### 🌡️ Inverter Health & Diagnostics
| Sensor | Unit | Device Class | Description |
|---|---|---|---|
| `sensor.temperatura_interna` | °C | `temperature` | Inverter internal temperature |
| `sensor.temperatura_do_dissipador` | °C | `temperature` | Inverter heatsink/radiator temperature |
| `sensor.horas_de_operacao` | h | `duration` | Total inverter operational hours |
| `sensor.status_do_inversor` | — | — | Status (Normal / Offline / Abnormal) |
| `sensor.alerta_ativo` | — | — | Active alarm name (or "Nenhum") with cause attributes |
| `sensor.quantidade_de_alertas` | — | — | Total count of active unsolved alarms |

---

## 🔔 Setting Up Notifications for Inverter Alerts

You can easily configure Home Assistant to send a push notification to your phone whenever the inverter status changes from `Normal` to `Abnormal` or `Offline`:

```yaml
alias: "Kehua Solar: Alerta no Inversor"
trigger:
  - platform: state
    entity_id: sensor.status_do_inversor
    from: "Normal"
condition: []
action:
  - service: notify.notify
    data:
      title: "⚠️ Alerta no Inversor Solar"
      message: >
        O inversor Kehua mudou de status para {{ states('sensor.status_do_inversor') }}.
        Motivo: {{ state_attr('sensor.alerta_ativo', 'motivo_alerta') }} (Código: {{ state_attr('sensor.alerta_ativo', 'codigo_evento') }}).
        Horário: {{ state_attr('sensor.alerta_ativo', 'horario_evento') }}.
```

## 🔧 How It Works

This integration communicates with the official **Kehua Energy Cloud** backend (`energy.kehua.com/necp`) used by the **WiseSolar+** mobile app:

1. **Authentication**: Credentials are encrypted using AES-128-ECB and signed with MD5+timestamp request signatures. A JWT token is obtained via `/v2/login/appLogin2`.
2. **Station Discovery**: Automatically discovers plants registered to your account using `/app/station/listPowerStationByPage`.
3. **Device Discovery**: Locates inverter serial number and model using `/app/device/listDevice`.
4. **Data Polling**: Polls every **60 seconds** via `/app/Plant/getEmsPlantDetailInfo`, `/app/Plant/getPlantDetailConciseInfo`, and `/app/device/getDeviceRunData2`.

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Ideas for future contributions:
- Support for multiple stations on a single account
- Inverter control & configuration switches (export limit, charging modes)
- Additional language translations

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## ⚠️ Disclaimer

This integration is **not affiliated with or endorsed by Kehua Tech**. It is an unofficial community project created by reverse-engineering the WiseSolar+ mobile application API.
