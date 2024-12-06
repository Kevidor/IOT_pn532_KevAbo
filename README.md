# IOT2 - Raspberry Pie
## Teaching Factory mit AutoID (RFID-Chip)
### Station 1: Flaschen ID schreiben

-   Flasche mit `Flaschen_ID` beschreiben (RFID-Tag) bevor die Flasche in die Abfüllstation kommt
-   Wählen Sie hierzu das erste Byte im zweiten Block aus, um die `Flaschen_ID` zu speichern
-   Hierbei soll die erste Flasche in der Datenbank Tabelle `Flasche` gewählt werden, welche noch einne `0` in `Tagged_Date` hat
-   Nach dem Schreiben der ID soll die Flaschen-ID in der Datenbank getagged werden (indem `Tagged_Date` mit dem aktuellen Unix-Time-Stamp befüllt wird.)
![enter image description here](https://jhumci.github.io/2023_WiSe_IoT2/images/Bottle_DB.png)
### UML-Diagramm von Station 1
```mermaid
stateDiagram
[*]  -->  State1
State1: Warte auf Karte
State1  -->  State2: Karte erkannt
State2: Schreibe auf Karte
State2  -->  State1: Schreiben nicht erfolgreich
State2  -->  State3: Schreiben erfolgreich
State3: Speichere ID und Datum in Datenbank
State3  -->  State5: DB schreiben nicht erfolgreich
State3  -->  State4: DB schreiben erfolgreich
State1  -->  State5: Timeout
State4: Erstelle Bestätigung
State5: Erstelle Fehlermeldung
State4  -->  [*]: Sende Nachricht
State5  -->  [*]: Sende Nachricht
```
