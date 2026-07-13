"""
Central config for Kdroid. Loads from environment variables (see
.env.example) so nothing sensitive is hardcoded.
"""
import os
from dataclasses import dataclass


@dataclass
class KdroidConfig:
    # Cyberwave
    cyberwave_api_key: str = os.getenv("CYBERWAVE_API_KEY", "")
    cyberwave_twin_id: str = os.getenv("CYBERWAVE_TWIN_ID", "")
    # TODO: confirm the correct catalog slug once the Beast twin is
    # provisioned in your Cyberwave account. It may not be a public catalog
    # entry yet and could need custom registration.
    cyberwave_twin_slug: str = os.getenv("CYBERWAVE_TWIN_SLUG", "waveshare/ugv-beast")
    cyberwave_workflow_id: str = os.getenv("CYBERWAVE_WORKFLOW_ID", "")

    # Robot / networking
    raspi_ip: str = os.getenv("RASPI_IP", "")

    # Sensor bridge (ESP32 -> MQTT)
    mqtt_broker_host: str = os.getenv("MQTT_BROKER_HOST", "localhost")
    mqtt_broker_port: int = int(os.getenv("MQTT_BROKER_PORT", "1883"))
    mqtt_sensor_topic: str = os.getenv("MQTT_SENSOR_TOPIC", "kdroid/esp32/sensors")

    # Waypoint behaviour
    waypoint_trigger_radius_m: float = float(os.getenv("WAYPOINT_TRIGGER_RADIUS_M", "0.5"))
    waypoint_cooldown_s: float = float(os.getenv("WAYPOINT_COOLDOWN_S", "60"))
    default_prompt: str = os.getenv(
        "DEFAULT_PROMPT",
        "Assess this plant's health. Note any visible signs of disease, "
        "pest damage, wilting, discoloration, or nutrient deficiency.",
    )

    # Local-first data
    local_db_path: str = os.getenv("LOCAL_DB_PATH", "kdroid_local.sqlite3")


config = KdroidConfig()
