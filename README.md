# Deployment einer ToDo-List-Web-Applikation: Dokumentation
> **Fach:** Lernfeld 9 (LF9) | **Klasse:** IFA43 | **Schüler:** Alex Kowert
---
# 1. IP-Adresskonfiguration
1.1 Aktuelle IP-Adresse ermitteln

![alt text](Doc-Images/image-01.png)

1.2 IP-Konfigurationsdatei aufrufen

![alt text](Doc-Images/image-02.png)

1.3 Änderungen konfigurieren

![alt text](Doc-Images/image-03.png)
<br>Speichern mit Strg+O

1.4 Änderungen prüfen und umsetzen

![alt text](Doc-Images/image-04.png)

1.5 Kontrolle, ob Einstellungen übernommen wurden

![alt text](Doc-Images/image-05.png)

1.6 Anpassungen der Einstellung für privates Netzwerk (zu Hause)

![alt text](Doc-Images/image-06.png)

1.7 Separate Konfiguration eingepflegt (zum schnellen Wechseln)

![alt text](Doc-Images/image-07.png)

---
# 2. Nutzer anlegen

2.1 Nutzer "willi" anlegen

![alt text](Doc-Images/image-08.png)

2.2 Nutzer "fernzugriff" anlegen

![alt text](Doc-Images/image-09.png)

2.3 Nutzer "fernzugriff" Sudo-Rechte geben

![alt text](Doc-Images/image-10.png)

2.4 SSH-Key in Windows anzeigen lassen

![alt text](Doc-Images/image-11.png)

2.5 SSH-Key in Linux Ubuntu hinterlegen

![alt text](Doc-Images/image-12.png)

2.6 Besitzrechte und restriktive Zugriffsrechte für das SSH-Verzeichnis konfigurieren

![alt text](Doc-Images/image-13.png)
---
# 3. SSH-Verbindung verwenden

3.1 SSH-Schlüssel-Authentifizierung für "fernzugriff" testen

![alt text](Doc-Images/image-14.png)

3.2 Zugriff vom Windows-PC auf Linux Ubuntu

![alt text](Doc-Images/image-15.png)
---
# 4. Docker konfigurieren

4.1 Docker installieren

Konsolen-Befehl: sudo apt update && sudo apt install -y docker.io

4.2 Docker-Installation überprüfen

![alt text](Doc-Images/image-16.png)

4.3 User "fernzugriff" zu Docker-Gruppe hinzufügen

Konsolen-Befehl: sudo usermod -aG docker fernzugriff

4.4 Gruppenrechte für aktuelle Sitzung übernehmen

Konsolen-Befehl: newgrp docker
---
# 5. To-Do-Liste im Docker-Container einrichten

5.1 SSH-Verbindung schließen und in den Projektordner wechseln

![alt text](Doc-Images/image-17.png)

5.2 Docker-Kontext in Windows erstellen

Konsolen-Befehl: docker context create ubuntu-live --docker "host=ssh://fernzugriff@192.168.0.112"

5.3 Docker-Kontext in Windows aktivieren

Konsolen-Befehl: docker context use ubuntu-live

5.4 Überprüfung des korrekten Build-Verzeichnisses

![alt text](Doc-Images/image-18.png)
<br>Die ".dockerignore" definiert nicht benötigte Dateien für den Build

---
# 6. Deployment der ToDo-List-App

6.1 Deplyoment ausführen

Konsolen-Befehl: docker-compose up -d --build

6.2 Docker-Container anzeigen zur Überprüfung

![alt text](Doc-Images/image-19.png)

6.3 ToDo-Liste im Browser mittels SwaggerUI ansteuern

    Browser-Eingabe: http://192.168.0.112:8080/swagger/
---
# 7. Firewall einrichten

7.1 Whitelist-Prinzip aktivieren

Konsolen-Befehl 1: sudo ufw default deny incoming

Konsolen-Befehl 2: sudo ufw default allow outgoing

7.2 Ausnahmen definieren (SSH-Port und Web-App-Port)

Konsolen-Befehl 1: sudo ufw allow 22/tcp

Konsolen-Befehl 2: sudo ufw allow 8080/tcp

7.3 Firewall aktiviren

Konsolen-Befehl: sudo ufw enable

7.4 Überprüfung auf korrekte Konfiguration

![alt text](Doc-Images/image-20.png)
---
# 8. Caddy Reverse-Proxy einrichten, um den Docker-Container vom Internet zu isolieren

8.1 docker-compose.yml anpassen:

Auszug:

    ports:
      - "127.0.0.1:8080:5000"

8.2 Firewall-Regeln anpassen

Konsolen-Befehl 1: sudo ufw delete allow 8080/tcp

Konsolen-Befehl 2: sudo ufw allow 80/tcp

Konsolen-Befehl 3: sudo ufw reload

8.3 Überprüfung auf korrekte Konfiguration

![alt text](Doc-Images/image-21.png)

8.4 Installation des Caddy Reverse-Proxys

Konsolen-Befehl 1: sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl

Konsolen-Befehl 2: curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg

Konsolen-Befehl 3: echo "deb [signed-by=/usr/share/keyrings/caddy-stable-archive-keyring.gpg] https://cloudsmith.io any main" | sudo tee /etc/apt/sources.list.d/caddy-stable.list

Konsolen-Befehl 4: sudo apt update

Konsolen-Befehl 5: sudo apt install -y caddy

8.5 Caddy starten und Status überprüfen

Konsolen-Befehl 1: sudo systemctl start caddy

Konsolen-Befehl 2: sudo systemctl status caddy

![alt text](Doc-Images/image-22.png)

8.6 Konfiguration des Reverse-Proxys (Caddyfile)

Konsolen-Befehl 1: sudo nano /etc/caddy/Caddyfile

Eingefügter Text: 

    :80 {
        reverse_proxy 127.0.0.1:8080
    }

Konsolen-Befehl 2: sudo systemctl reload caddy

8.7 Funktionstest des Caddy Reverse-Proxys

    Browser-Eingabe: http://192.168.0.112/swagger/

8.8 Überprüfung der internen Port-Bindung auf Server-Ebene

Konsolen-Befehl: sudo ss -tulpn | grep :8080

Ausgabe: 

    tcp   LISTEN 0      4096                           127.0.0.1:8080       0.0.0.0:*    users:(("docker-proxy",pid=231573,fd=7))

8.9 Lokale Gegenprobe der Schnittstellen-Isolierung

Konsolen-Befehl: curl -I --connect-timeout 3 http://192.168.0.112:8080

Ausgabe: 

    curl: (7) Failed to connect to 192.168.0.112 port 8080 after 0 ms: Could not connect to server
---
# 9. Server-Monitoring mit Grafana

9.1 Erstellen eines Accounts auf grafana.com

9.2 Grafana-Instanz erstellen

![alt text](Doc-Images/image-23.png)
<br>"Monitor infrastructure" auswählen

![alt text](Doc-Images/image-24.png)
<br>"Monitor your OS" auswählen

![alt text](Doc-Images/image-25.png)
<br>"Linux" auswählen

![alt text](Doc-Images/image-26.png)
<br>Token-Erstellung vorbereiten und auf "Create token" klicken

9.3 Grafana Alloy installieren

![alt text](Doc-Images/image-27.png)
<br>Installationsskript auf Linux Ubuntu ausführen

9.4 Verbindung testen

![alt text](Doc-Images/image-28.png)
<br>Auf "Test connection" klicken

![alt text](Doc-Images/image-29.png)

9.5 Dashboard konfigurieren

![alt text](Doc-Images/image-30.png)
<br>Auf "Select and visualize a dashboard" klicken

![alt text](Doc-Images/image-31.png)
<br>Dashboard-Typ auswählen: "Overview" ausgewählt

9.6 Dashboard auslesen

![alt text](Doc-Images/image-32.png)
<br>Prozessor- und Arbeitsspeicherauslastung sind im Normalbereich"# Release v1.0.0" 
"# Release v1.0.0" 
