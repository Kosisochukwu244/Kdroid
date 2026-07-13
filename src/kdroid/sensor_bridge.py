"""
Relays ESP32 soil moisture / temperature / humidity readings into Cyberwave
telemetry, so environmental data lives on the same timeline as
camera-triggered plant assessments.

Assumes the ESP32 sub-controller already publishes readings over its
existing serial link to the Pi host (same pattern the Beast uses for
motor/IMU data) — this module just needs a local MQTT broker in between
and a Cyberwave-side telemetry push.

Phase 3 item — not needed until Phase 1/2 (movement + vision) are working.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass

import paho.mqtt.client as mqtt

from kdroid.config import config


@dataclass
class SensorReading:
    timestamp: float
    soil_moisture_pct: float
    temperature_c: float
    humidity_pct: float


class SensorBridge:
    def __init__(self, on_reading=None):
        """
        on_reading: optional callback(SensorReading) -> None, called each
        time a new reading arrives. Wire this to the fusion step in Phase 3.
        """
        self._on_reading = on_reading
        self._client = mqtt.Client()
        self._client.on_connect = self._handle_connect
        self._client.on_message = self._handle_message
        self.latest: SensorReading | None = None

    def _handle_connect(self, client, userdata, flags, rc):
        client.subscribe(config.mqtt_sensor_topic)

    def _handle_message(self, client, userdata, msg):
        # Expected ESP32 payload shape — adjust to match your actual
        # firmware's JSON output.
        payload = json.loads(msg.payload.decode())
        reading = SensorReading(
            timestamp=time.time(),
            soil_moisture_pct=payload["soil_moisture_pct"],
            temperature_c=payload["temperature_c"],
            humidity_pct=payload["humidity_pct"],
        )
        self.latest = reading
        if self._on_reading:
            self._on_reading(reading)

        # TODO: push `reading` to Cyberwave twin telemetry here once the
        # SDK's telemetry-publish call is confirmed (docs mention MQTT-based
        # streaming; wire this up once the twin is provisioned).

    def start(self) -> None:
        self._client.connect(config.mqtt_broker_host, config.mqtt_broker_port)
        self._client.loop_start()

    def stop(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()


if __name__ == "__main__":
    bridge = SensorBridge(on_reading=lambda r: print(r))
    bridge.start()
    print(f"Listening on {config.mqtt_sensor_topic}... Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        bridge.stop()
