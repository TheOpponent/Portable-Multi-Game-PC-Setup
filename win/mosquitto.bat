:: This file is a workaround to start Mosquitto on startup rather than use the service, which is unreliable with a custom config file.
:: Place this file in the Startup folder in your Start Menu.
nircmd exec hide "C:\Program Files\Mosquitto\mosquitto.exe" -c "C:\Program Files\Mosquitto\mosquitto.conf"