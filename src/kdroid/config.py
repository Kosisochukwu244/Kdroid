"""
Central config for Kdroid. Loads from environment variables (see
.env.example) so nothing sensitive is hardcoded.
"""
import os
from dataclasses import dataclass


@dataclass
class KdroidConfig:
    # Cyberwave — the SDK's cw.twin() call needs all three of these.
    # Get them via `cyberwave twin show <your-twin-uuid>`:
    #   Asset:       -> CYBERWAVE_ASSET_ID
    #   UUID:        -> CYBERWAVE_TWIN_ID
    #   Environment: -> CYBERWAVE_ENVIRONMENT_ID
    cyberwave_api_key: str = os.getenv("CYBERWAVE_API_KEY", "")
    cyberwave_asset_id: str = os.getenv("CYBERWAVE_ASSET_ID", "")
    cyberwave_twin_id: str = os.getenv("CYBERWAVE_TWIN_ID", "")
    cyberwave_environment_id: str = os.getenv("CYBERWAVE_ENVIRONMENT_ID", "")
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

    # Target crop for this build. Prompt is pepper-specific for now — see
    # workflows/plant_health_workflow.md for the full structured schema.
    crop_name: str = os.getenv("CROP_NAME", "pepper")
    default_prompt: str = os.getenv(
        "DEFAULT_PROMPT",
        "You are inspecting a pepper plant/fruit for a farmer. Respond with "
        "ONLY a JSON object, no other text, matching this schema: "
        '{"status": "healthy" | "diseased", '
        '"disease_guess": string or null (name the most likely disease/pest '
        "if status is diseased, else null), "
        '"ripeness": "ripe" | "unripe" | "not_applicable" (use '
        "not_applicable if no fruit is visible, only leaves/stem), "
        '"confidence": "high" | "medium" | "low", '
        '"notes": short plain-language explanation, 1 sentence max}',
    )

    # Local-first data — SD-card storage on the Pi. Every capture + result
    # is written here regardless of whether the Cyberwave sync succeeds,
    # so nothing is lost if connectivity drops mid-scout.
    local_data_dir: str = os.getenv("LOCAL_DATA_DIR", os.path.expanduser("~/kdroid_data"))
    local_db_path: str = os.getenv("LOCAL_DB_PATH", "kdroid_local.sqlite3")


config = KdroidConfig()
