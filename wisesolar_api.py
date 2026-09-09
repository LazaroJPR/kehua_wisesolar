"""WiseSolar API Client for Home Assistant."""
from __future__ import annotations

import base64
import hashlib
import json
import logging
import time
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

PWD_KEY = b"clxslychxyl11988"
SIGN_KEY = b"%vSBtRMV4F8mr#dYofsG3lJOBv5vw*fZ"
BASE_URL = "https://energy.kehua.com/necp"


def _aes_encrypt(plaintext: str, key: bytes) -> str:
    """Encrypt plaintext using AES-ECB with PKCS7 padding."""
    data = plaintext.encode("utf-8")
    pad_len = 16 - (len(data) % 16)
    padded = data + bytes([pad_len] * pad_len)

    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend

        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded) + encryptor.finalize()
    except Exception:
        import pyaes

        aes = pyaes.AESModeOfOperationECB(key)
        encrypted = b"".join(aes.encrypt(padded[i : i + 16]) for i in range(0, len(padded), 16))

    return base64.b64encode(encrypted).decode("ascii")


def _sign(params: dict[str, Any]) -> str:
    """Generate WiseSolar request signature."""
    sorted_str = ",".join(f"{k}={params[k]}" for k in sorted(params.keys()) if params[k] is not None and params[k] != "")
    md5 = hashlib.md5(sorted_str.encode("utf-8")).hexdigest().lower()
    timestamp = str(int(time.time() * 1000))
    digest = f"{md5},{timestamp}"
    if digest.startswith(","):
        digest = digest[1:]
    return _aes_encrypt(digest, SIGN_KEY)


class WiseSolarApiClient:
    """WiseSolar Cloud API client."""

    def __init__(self, session: aiohttp.ClientSession, username: str, password: str, station_id: str | None = None) -> None:
        self._session = session
        self.username = username
        self.password = password
        self.station_id = station_id
        self.token: str | None = None
        self.customer_id: str | None = None
        self.plant_name: str | None = None
        self.device_id: str | None = None
        self.device_sn: str | None = None
        self.device_model: str | None = None
        self.device_version: str | None = None

    async def async_api_call(self, path: str, params: dict[str, Any], use_token: bool = True) -> dict[str, Any]:
        """Perform API POST call with signature."""
        url = f"{BASE_URL}{path}"
        body_params = {k: str(v) for k, v in params.items() if v is not None}
        sign = _sign(body_params)

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "sign": sign,
            "version": "6.2.1",
            "channelType": "2",
            "os": "android",
            "clientType": "Android",
            "locale": "pt",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 14)",
        }
        if use_token and self.token:
            headers["authorization"] = self.token
            headers["token"] = self.token

        async with self._session.post(url, data=body_params, headers=headers, ssl=False) as resp:
            text = await resp.text()
            try:
                data = json.loads(text)
            except Exception:
                _LOGGER.error("Falha ao processar resposta do WiseSolar: %s", text)
                return {"code": "-1", "message": text}
            return data

    async def async_login(self) -> bool:
        """Authenticate with WiseSolar."""
        encrypted_pwd = _aes_encrypt(self.password, PWD_KEY)
        resp = await self.async_api_call("/v2/login/appLogin2", {"username": self.username, "password": encrypted_pwd}, use_token=False)
        code = str(resp.get("code"))
        if code != "0":
            msg = resp.get("message") or resp.get("msg") or f"Erro {code}"
            _LOGGER.error("Falha no login do WiseSolar: %s", msg)
            raise ValueError(f"Falha no login: {msg}")

        data = resp.get("data", {})
        self.token = data.get("token") or data.get("authorization")
        self.customer_id = str(data.get("customerId") or "")

        if not self.station_id:
            await self.async_discover_station()
        elif not self.device_id:
            await self.async_discover_device()

        return True

    async def async_discover_station(self) -> None:
        """Discover first station/plant associated with account."""
        resp = await self.async_api_call("/app/station/listPowerStationByPage", {
            "customerId": self.customer_id or "",
            "pageNum": "1",
            "pageSize": "20",
        })
        if str(resp.get("code")) == "0" and resp.get("data"):
            results = resp["data"].get("result", [])
            if results:
                self.station_id = str(results[0].get("stationId") or results[0].get("id"))
                self.plant_name = results[0].get("stationName") or results[0].get("name")
                await self.async_discover_device()
                return

        resp = await self.async_api_call("/app/station/listStationForOm", {"customerId": self.customer_id or ""})
        if str(resp.get("code")) == "0" and resp.get("data"):
            rows = resp["data"] if isinstance(resp["data"], list) else []
            if rows:
                self.station_id = str(rows[0].get("stationId") or rows[0].get("id"))
                self.plant_name = rows[0].get("stationName") or rows[0].get("name")
                await self.async_discover_device()
                return

    async def async_discover_device(self) -> None:
        """Discover inverter device ID and serial number."""
        if not self.station_id:
            return
        resp = await self.async_api_call("/app/device/listDevice", {"stationId": self.station_id})
        if str(resp.get("code")) == "0" and resp.get("data"):
            devices = resp["data"] if isinstance(resp["data"], list) else []
            if devices:
                self.device_id = str(devices[0].get("deviceId") or "")
                self.device_sn = str(devices[0].get("sn") or "")

    async def async_get_data(self) -> dict[str, Any]:
        """Fetch real-time, concise stats, and string/inverter diagnostics."""
        if not self.token:
            await self.async_login()

        if not self.station_id:
            await self.async_discover_station()
            if not self.station_id:
                raise ValueError("Nenhuma usina encontrada na conta WiseSolar.")

        if not self.device_id:
            await self.async_discover_device()

        rt_resp = await self.async_api_call("/app/Plant/getEmsPlantDetailInfo", {"stationId": self.station_id})
        if str(rt_resp.get("code")) in ("900", "901", "902", "903", "999", "111005"):
            await self.async_login()
            rt_resp = await self.async_api_call("/app/Plant/getEmsPlantDetailInfo", {"stationId": self.station_id})

        stats_resp = await self.async_api_call("/app/Plant/getPlantDetailConciseInfo", {"stationId": self.station_id})

        result: dict[str, Any] = {
            "pv_power": 0.0,
            "grid_power": 0.0,
            "load_power": 0.0,
            "battery_power": 0.0,
            "battery_soc": 0.0,
            "day_energy": 0.0,
            "total_energy": 0.0,
            "day_consumption": 0.0,
            "total_consumption": 0.0,
            "today_revenue": 0.0,
            "total_revenue": 0.0,
            "revenue_unit": "R$",
            "day_charge": 0.0,
            "day_discharge": 0.0,
            "total_charge": 0.0,
            "total_discharge": 0.0,
            "pv1_voltage": 0.0,
            "pv1_current": 0.0,
            "pv1_power": 0.0,
            "pv2_voltage": 0.0,
            "pv2_current": 0.0,
            "pv2_power": 0.0,
            "grid_voltage": 0.0,
            "grid_current": 0.0,
            "grid_frequency": 0.0,
            "power_factor": 0.0,
            "inverter_temperature": 0.0,
            "radiator_temperature": 0.0,
            "operating_hours": 0.0,
            "alarm_count": 0,
            "active_alarm": "Nenhum",
            "alarm_code": "",
            "alarm_level": "Normal",
            "alarm_time": "",
            "alarm_list": [],
            "device_model": self.device_model or "SPI6000-B2",
            "device_version": self.device_version or "V1.0",
            "device_sn": self.device_sn or "",
            "status": "Unknown",
            "station_name": self.plant_name or f"Kehua Inverter ({self.station_id})",
        }

        # 1. Real-time plant & EMS data
        if str(rt_resp.get("code")) == "0" and rt_resp.get("data"):
            data = rt_resp["data"]
            rt = data.get("plantRealTimeData", {})
            si = data.get("stationInfo", {})
            ems = data.get("emsPlantInfoOutPut", {})

            if not self.plant_name and si.get("stationName"):
                self.plant_name = si["stationName"]
                result["station_name"] = self.plant_name

            result["pv_power"] = round(float(rt.get("pvPower") or 0) * 1000, 1)
            result["grid_power"] = round(float(rt.get("gridPower") or 0) * 1000, 1)
            result["load_power"] = round(float(rt.get("loadPower") or 0) * 1000, 1)
            result["battery_power"] = round(float(rt.get("batteryPower") or 0) * 1000, 1)
            result["battery_soc"] = round(float(rt.get("soc") or 0), 1)

            st = int(si.get("stationStatus") or 1)
            status_map = {1: "Normal", 2: "Offline", 3: "Abnormal"}
            result["status"] = status_map.get(st, f"Status ({st})")

            result["day_charge"] = round(float(ems.get("dayCharge") or 0), 2)
            result["day_discharge"] = round(float(ems.get("dayDischarge") or 0), 2)
            result["total_charge"] = round(float(ems.get("totalCharge") or 0), 2)
            result["total_discharge"] = round(float(ems.get("totalDischarge") or 0), 2)

        # 2. Key statistics & Revenue
        if str(stats_resp.get("code")) == "0" and stats_resp.get("data"):
            kd = stats_resp["data"].get("keyData", {})
            result["day_energy"] = round(float(kd.get("dayElec") or 0), 2)

            total_elec = float(kd.get("totalElec") or 0)
            total_unit = (kd.get("totalElecUnit") or "kWh").strip()
            if total_unit == "MWh":
                total_elec *= 1000
            result["total_energy"] = round(total_elec, 2)

            result["day_consumption"] = round(float(kd.get("dayConsum") or 0), 2)

            total_consum = float(kd.get("totalConsum") or 0)
            total_consum_unit = (kd.get("totalConsumUnit") or "kWh").strip()
            if total_consum_unit == "MWh":
                total_consum *= 1000
            result["total_consumption"] = round(total_consum, 2)

            result["today_revenue"] = round(float(kd.get("todayRevenue") or 0), 2)
            result["total_revenue"] = round(float(kd.get("totalRevenue") or 0), 2)
            unit = kd.get("todayRevenueUnit") or kd.get("totalRevenueUnit")
            if unit:
                result["revenue_unit"] = str(unit).strip()

        # 3. String-level & detailed inverter diagnostics
        if self.device_id and self.device_sn:
            try:
                dev_run_resp = await self.async_api_call(
                    "/app/device/getDeviceRunData2",
                    {"deviceId": self.device_id, "sn": self.device_sn},
                )
                if str(dev_run_resp.get("code")) == "0" and dev_run_resp.get("data"):
                    tables = dev_run_resp["data"].get("tableYcInfos", [])
                    for group in tables:
                        gname = group.get("groupName")
                        dp = group.get("dataPoint")

                        # String / branch data (showType 2)
                        if gname == "Branch data" and isinstance(dp, dict):
                            for key, points in dp.items():
                                k_lower = key.lower()
                                prefix = "pv1" if "pv1" in k_lower else "pv2" if "pv2" in k_lower else "pv3" if "pv3" in k_lower else "pv4"
                                if isinstance(points, list):
                                    for pt in points:
                                        pname = (pt.get("name") or "").lower()
                                        val = float(pt.get("val") or 0)
                                        if "voltage" in pname:
                                            result[f"{prefix}_voltage"] = round(val, 1)
                                        elif "current" in pname:
                                            result[f"{prefix}_current"] = round(val, 2)
                                        elif "power" in pname:
                                            result[f"{prefix}_power"] = round(val, 1)

                        # Single point list groups
                        elif isinstance(dp, list):
                            for pt in dp:
                                prop = pt.get("property")
                                val = pt.get("val")
                                if not val:
                                    continue
                                if prop == "YC4502":  # Grid voltage
                                    result["grid_voltage"] = round(float(val), 1)
                                elif prop == "YC4503":  # Grid current
                                    result["grid_current"] = round(float(val), 2)
                                elif prop == "YC4504":  # Grid frequency
                                    result["grid_frequency"] = round(float(val), 2)
                                elif prop == "YC4519":  # Power factor
                                    result["power_factor"] = round(float(val), 2)
                                elif prop == "YC4534":  # Internal temperature
                                    result["inverter_temperature"] = round(float(val), 1)
                                elif prop == "YC5504":  # Radiator temperature
                                    result["radiator_temperature"] = round(float(val), 1)
                                elif prop == "YC4542":  # Operating hours
                                    result["operating_hours"] = round(float(val), 1)
                                elif prop == "deviceModel":
                                    self.device_model = str(val)
                                    result["device_model"] = str(val)
                                elif prop == "YC4853":
                                    self.device_version = str(val)
                                    result["device_version"] = str(val)
            except Exception as err:
                _LOGGER.warning("Não foi possível carregar diagnóstico detalhado do inversor: %s", err)

        # 4. Active alarms & event log (Unsolved Events)
        try:
            alarm_resp = await self.async_api_call(
                "/app/eventlog/listUnsolvedEventLog",
                {"stationId": self.station_id, "pageNum": "1", "pageSize": "10"},
            )
            if str(alarm_resp.get("code")) == "0" and alarm_resp.get("data"):
                adata = alarm_resp["data"]
                events = adata.get("eventList") or []
                result["alarm_count"] = int(adata.get("total") or len(events))
                if events:
                    first_event = events[0]
                    result["active_alarm"] = first_event.get("eventName") or "Alerta Ativo"
                    result["alarm_code"] = first_event.get("eventCode") or ""
                    result["alarm_level"] = first_event.get("levelName") or ""
                    result["alarm_time"] = first_event.get("creatTime") or ""
                    result["alarm_list"] = [
                        f"[{e.get('levelName', 'Alerta')}] {e.get('eventName')} ({e.get('creatTime')})"
                        for e in events
                    ]
                else:
                    result["active_alarm"] = "Nenhum"
                    result["alarm_code"] = ""
                    result["alarm_level"] = "Normal"
                    result["alarm_time"] = ""
                    result["alarm_list"] = []
        except Exception as err:
            _LOGGER.debug("Erro ao consultar alertas ativos: %s", err)

        return result
