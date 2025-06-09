# LightGrid
LightGrid s a smart, battery-powered mesh networking and lighting management system for highways and smart infrastructure. It combines energy monitoring, mesh WiFi, and adaptive lighting to provide sustainable, resilient, and secure connectivity and illumination for motorists and city services.

Features
Battery & Energy Monitoring: Real-time tracking and analytics of battery charge, energy harvesting, and consumption.
Smart Lighting Control: Adaptive lighting with ON/DIM/OFF/EMERGENCY modes, emergency lighting for low power.
Mesh Network Management: Dynamic mesh topology, node throttling, and reliability analytics.
Web Dashboard: Real-time control, advanced analytics, and visualizations.
REST API: Secure, remote control and monitoring endpoints.
Event Logging & Alerts: Persistent event log, health checks, and email alerts.
Security: Hashed passwords, session management, API key rotation, HTTPS support.

[Battery/Energy] <--> [Power Management] <--> [Lighting Controller]
         |                        |
         v                        v
   [Mesh Node] <------------> [Mesh Network]
         |
         v
 [Web Dashboard & API]

Analytics & Visualization
Battery trend and forecast
Mesh uptime and reliability
Lighting ON hours
Event log

Security
All passwords are hashed (bcrypt).
API access requires a key (can be rotated by admin).
HTTPS enabled by default (self-signed for development).
Health checks and email alerts for failures.

Contribution Guidelines
Fork the repo and create a feature branch.
Add tests for new features.
Submit a pull request with a clear description.

License
MIT License
