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
                return

        resp = await self.async_api_call("/app/station/listStationForOm", {"customerId": self.customer_id or ""})
        if str(resp.get("code")) == "0" and resp.get("data"):
            rows = resp["data"] if isinstance(resp["data"], list) else []
            if rows:
                self.station_id = str(rows[0].get("stationId") or rows[0].get("id"))
                self.plant_name = rows[0].get("stationName") or rows[0].get("name")
                return

    async def async_get_data(self) -> dict[str, Any]:
        """Fetch real-time and concise stats."""
        if not self.token:
            await self.async_login()

        if not self.station_id:
            await self.async_discover_station()
            if not self.station_id:
                raise ValueError("Nenhuma usina encontrada na conta WiseSolar.")

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
            "day_energy": 0.0,
            "total_energy": 0.0,
            "status": "Desconhecido",
            "station_name": self.plant_name or f"Inversor Kehua ({self.station_id})",
        }

        if str(rt_resp.get("code")) == "0" and rt_resp.get("data"):
            data = rt_resp["data"]
            rt = data.get("plantRealTimeData", {})
            si = data.get("stationInfo", {})
            if not self.plant_name and si.get("stationName"):
                self.plant_name = si["stationName"]
                result["station_name"] = self.plant_name

            result["pv_power"] = round(float(rt.get("pvPower") or 0) * 1000, 1)
            result["grid_power"] = round(float(rt.get("gridPower") or 0) * 1000, 1)
            result["load_power"] = round(float(rt.get("loadPower") or 0) * 1000, 1)
            result["battery_power"] = round(float(rt.get("batteryPower") or 0) * 1000, 1)

            st = int(si.get("stationStatus") or 1)
            status_map = {1: "Normal", 2: "Offline", 3: "Anormal"}
            result["status"] = status_map.get(st, f"Status ({st})")

        if str(stats_resp.get("code")) == "0" and stats_resp.get("data"):
            kd = stats_resp["data"].get("keyData", {})
            result["day_energy"] = round(float(kd.get("dayElec") or 0), 2)
            result["total_energy"] = round(float(kd.get("totalElec") or 0), 2)
            result["day_consumption"] = round(float(kd.get("dayConsum") or 0), 2)

        return result
