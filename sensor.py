"""Sensors for Kehua WiseSolar integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    # --- Solar Generation (Energy Dashboard Ready) ---
    SensorEntityDescription(
        key="pv_power",
        name="Potência Solar",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-power",
    ),
    SensorEntityDescription(
        key="day_energy",
        name="Geração do Dia",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power-variant",
    ),
    SensorEntityDescription(
        key="total_energy",
        name="Geração Total Acumulada",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:counter",
    ),

    # --- Home Consumption (Energy Dashboard Ready) ---
    SensorEntityDescription(
        key="load_power",
        name="Consumo da Residência",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-lightning-bolt",
    ),
    SensorEntityDescription(
        key="day_consumption",
        name="Consumo do Dia",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:calendar-today",
    ),
    SensorEntityDescription(
        key="total_consumption",
        name="Consumo Total Acumulado",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:chart-line",
    ),

    # --- Electrical Grid ---
    SensorEntityDescription(
        key="grid_power",
        name="Potência da Rede",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower",
    ),
    SensorEntityDescription(
        key="grid_voltage",
        name="Tensão da Rede",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sine-wave",
    ),
    SensorEntityDescription(
        key="grid_current",
        name="Corrente da Rede",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-ac",
    ),
    SensorEntityDescription(
        key="grid_frequency",
        name="Frequência da Rede",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:chart-bell-curve",
    ),
    SensorEntityDescription(
        key="power_factor",
        name="Fator de Potência",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:angle-acute",
    ),

    # --- PV Strings (Branch Data) ---
    SensorEntityDescription(
        key="pv1_voltage",
        name="String 1 Tensão",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="pv1_current",
        name="String 1 Corrente",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-dc",
    ),
    SensorEntityDescription(
        key="pv1_power",
        name="String 1 Potência",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash-outline",
    ),
    SensorEntityDescription(
        key="pv2_voltage",
        name="String 2 Tensão",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="pv2_current",
        name="String 2 Corrente",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-dc",
    ),
    SensorEntityDescription(
        key="pv2_power",
        name="String 2 Potência",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash-outline",
    ),

    # --- Financial / Revenue ---
    SensorEntityDescription(
        key="today_revenue",
        name="Economia do Dia",
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:cash-clock",
    ),
    SensorEntityDescription(
        key="total_revenue",
        name="Economia Total",
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:cash-multiple",
    ),

    # --- Battery (Hybrid Systems) ---
    SensorEntityDescription(
        key="battery_power",
        name="Potência da Bateria",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-charging",
    ),
    SensorEntityDescription(
        key="battery_soc",
        name="Bateria SOC",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="day_charge",
        name="Carga da Bateria no Dia",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:battery-arrow-up",
    ),
    SensorEntityDescription(
        key="day_discharge",
        name="Descarga da Bateria no Dia",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:battery-arrow-down",
    ),

    # --- Inverter Health & Diagnostics ---
    SensorEntityDescription(
        key="inverter_temperature",
        name="Temperatura Interna",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
    ),
    SensorEntityDescription(
        key="radiator_temperature",
        name="Temperatura do Dissipador",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:heat-wave",
    ),
    SensorEntityDescription(
        key="operating_hours",
        name="Horas de Operação",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:clock-check-outline",
    ),
    SensorEntityDescription(
        key="status",
        name="Status do Inversor",
        icon="mdi:information-outline",
    ),
    SensorEntityDescription(
        key="active_alarm",
        name="Alerta Ativo",
        icon="mdi:alert-circle-outline",
    ),
    SensorEntityDescription(
        key="alarm_count",
        name="Quantidade de Alertas",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:bell-alert-outline",
    ),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up the WiseSolar sensors."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    client = data["client"]

    entities = [
        WiseSolarSensor(coordinator, description, entry.entry_id, client.station_id or "default")
        for description in SENSOR_DESCRIPTIONS
    ]
    async_add_entities(entities)


class WiseSolarSensor(CoordinatorEntity, SensorEntity):
    """Representation of a WiseSolar sensor."""

    def __init__(self, coordinator, description: SensorEntityDescription, entry_id: str, station_id: str) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._attr_has_entity_name = True

        data = coordinator.data or {}
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, station_id)},
            name=data.get("station_name") or "Inversor Kehua",
            manufacturer="Kehua Tech",
            model=data.get("device_model") or "SPI-B2 Series",
            sw_version=data.get("device_version"),
            serial_number=data.get("device_sn"),
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.entity_description.key)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement, supporting dynamic currency."""
        if self.entity_description.key in ("today_revenue", "total_revenue"):
            if self.coordinator.data:
                return self.coordinator.data.get("revenue_unit", "R$")
            return "R$"
        return self.entity_description.native_unit_of_measurement

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return rich diagnostics and alarm details for cards and automations."""
        if not self.coordinator.data:
            return None
        data = self.coordinator.data
        if self.entity_description.key in ("status", "active_alarm"):
            return {
                "motivo_alerta": data.get("active_alarm"),
                "codigo_evento": data.get("alarm_code"),
                "nivel_gravidade": data.get("alarm_level"),
                "horario_evento": data.get("alarm_time"),
                "total_alertas": data.get("alarm_count", 0),
                "lista_eventos": data.get("alarm_list", []),
                "modelo_inversor": data.get("device_model"),
                "numero_serie": data.get("device_sn"),
            }
        return None

