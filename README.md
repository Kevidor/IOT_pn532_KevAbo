
# IOT2 - Raspberry Pie

## Teaching Factory mit AutoID (RFID-Chip)

### Station 1: Flaschen ID schreiben

- Flasche mit `Flaschen_ID` beschreiben (RFID-Tag) bevor die Flasche in die Abfüllstation kommt
- Wählen Sie hierzu das erste Byte im zweiten Block aus, um die `Flaschen_ID` zu speichern
- Hierbei soll die erste Flasche in der Datenbank Tabelle `Flasche` gewählt werden, welche noch einne `0` in `Tagged_Date` hat
- Nach dem Schreiben der ID soll die Flaschen-ID in der Datenbank getagged werden (indem `Tagged_Date` mit dem aktuellen Unix-Time-Stamp befüllt wird.)
![flaschen_datenbank](https://jhumci.github.io/2023_WiSe_IoT2/images/Bottle_DB.png)

### UML-Diagramm von Station 1

```mermaid
stateDiagram
State1: State 1
State1: Warte auf RFID
State2: State 2
State2: Schreibe Flaschen_ID auf RFID
State3: State 3
State3: Speichere ID und Datum in Datenbank
State4: State 4
State4: Warte auf neue RFID
State5: State 5
State5: Fehlermeldung

[*]  -->  State1
State1  -->  State2: Karte erkannt
State2  -->  State1: Schreiben nicht erfolgreich
State2  -->  State3: Schreiben erfolgreich
State3  -->  State5: DB schreiben nicht erfolgreich
State3  -->  State4: DB schreiben erfolgreich
State1  -->  State5: Timeout
State4  -->  State1: Warte auf neue RFID
State5  -->  State1: Fehler quittiert
State4  -->  [*]: Sende Nachricht
State5  -->  [*]: Sende Nachricht
```

---

### Station 2: Abfüllen

- Die Station dient dazu die Rezepte zu einer Flasche abrufen bevor die Flasche an einem Dispenser ankommt
- Die Flaschen und Rezepte für die Flaschen liegen in der bereitgestellten Datenbank unter der Tabelle `Rezept_besteht_aus_Granulat`
- Geben Sie die `Flaschen_ID` und die Menge der relevanten Granulate als Sinnvolle Meldung in der Kommandozeile aus
![flaschen_datenbank_2](https://jhumci.github.io/2023_WiSe_IoT2/images/DATABSENFC.png)

### UML-Diagramm von Station 2

```mermaid
stateDiagram
State1: State 1
State1: Karte einlesen und Flaschen_ID auslesen
State2: State 2
State2: Lese Rezept (Menge von Granulat) durch Flaschen_ID aus
State3: State 3
State3: Erstelle ein QR-Code
State4: State 4
State4: Warte auf den nächsten RFID
State5: State 5
State5: Fehlermeldung

[*]  -->  State1
State1  -->  State2: Karte erkannt
State1  -->  State5: Karte konnte nicht erkannt werden
State2  -->  State3: Daten auslesen erfolgreich
State2  -->  State5: Daten auslesen nicht erfolgreich
State3  -->  State4: QR-Code erfolgreich erstellt
State3  -->  State5: QR-Code konnte nicht erstellt werden
State4  -->  State1: Warte auf neue RFID
State5  -->  State1: Fehler quittiert
State4  -->  [*]: Sende Nachricht
State5  -->  [*]: Sende Nachricht
```

#### Abgabe

- Geben Sie einen Link zu einem Öffentlichen **Git-Repository** ab, in dem Sie die beiden Stationen implementiert haben
- 5pt: Station 1: Schreiben Sie ein Python-Modul `station1.py`, das den RFID-Tag der Flaschen-ID mit der ersten noch nicht vergebenen Flaschen-ID beschreibt. Geben Sie ein Log-File `station1.log` ab, das das Starten der Station und das Schreiben der Flaschen-ID dokumentiert (im erfolgreichen und nicht erfolgreichen Fall)
- 5pt: Station 2: Schreiben Sie ein Python-Modul `station2.py`, das anhand der RFID-Tags der Flaschen-ID die richtige Menge ermittelt. Geben Sie ein Log-File `station2.log` ab, das for Füllmengen für zwei verschiedene Flaschen dokumentiert
- 2pt: Zeichnen Sie ein Zustandsübergangsdiagramm für beide Stationen, für ein funktionierendes Fehlermanagement und fügen Sie dieses in die `README.md` des Repositories ein
- 2pt: Bauen sie die beiden Module in je ein eine sinnvolle State-Machine für ein Fehlermanagement ein, damit z.B. wenn der RFID Tag zu früh entfernt wird

---

**Hinweis**: - Es ist einfacher erst kleine Test-Programme zu Interaktion mit der Datenbank und den RFID-Reader zu schreiben, bevor Sie die Module in die State-Machine einbauen - Warten Sie hiervor ggf. die Vorlesung in Software Engineering ab

---

#### Abgabe Bonus (2pt)

- 2pt: Für alle korrekt abgefüllten Flaschen wird ein QR-Code erstellt, welche die ID und den Rezept-Nummer und das Datum enthält

### QR-Codes

![flaschen_datenbank_2](qr_code/QR_Code1.png)
![flaschen_datenbank_2](qr_code/QR_Code2.png)