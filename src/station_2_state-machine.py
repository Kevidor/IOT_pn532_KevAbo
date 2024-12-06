import logging
import nfc_reader as nfc
import sqlite3 as sql
import qrcode
from PIL import Image

# Initialize logger, NFCREADER and Databasepath
logging.basicConfig(level=logging.DEBUG)
nfc_reader = None
SQL_PATH = "/home/uwe/IOT_pn532_KevAbo/data/flaschen_database.db"

class StateMachine:
    def __init__(self, reader):
        self.current_state = 'State0'
        self.reader = reader
        self.flaschen_id = None
        self.states = {
            'State0': State0(self),
            'State1': State1(self),
            'State2': State2(self),
            'State3': State3(self),
            'State4': State4(self)
        }

    def run(self):
        while self.current_state not in ['State5']:
            state = self.states[self.current_state]
            state.run()

class State:
    def __init__(self, machine):
        self.machine = machine

    def run(self):
        raise NotImplementedError("State must implement 'run' method.")
    
# Init State
class State0(State):
    def run(self):
        logging.info("Initializing RFID reader...")
        init_successful = False

        self.machine.reader = nfc.NFCReader()
        if self.machine.reader: 
            init_successful = True
        
        if init_successful:
            logging.info("RFID reader initialized successfully.")
            self.machine.current_state = 'State1'
        else:
            logging.error("Failed to initialize RFID reader.")
            self.machine.current_state = 'State5'

# Read RFID Tag State
class State1(State):
    def run(self):
        logging.info("Waiting for RFID card...")
        
        while True:
            self.machine.reader.uid = self.machine.reader.read_passive_target(timeout=0.5)
            print(".", end="")
            if self.machine.reader.uid is None:
                continue
            break
        
        self.machine.flaschen_id = nfc.hex_block_to_strint(self.machine.reader.read_block(self.machine.reader.uid, 4))

        if self.machine.reader.uid is None:
            logging.warning("No card detected. Retrying...")
            self.machine.current_state = 'State1'
        else:
            logging.info(f"Found card with UID: {[hex(i) for i in self.machine.reader.uid]}") 
            self.machine.current_state = 'State2'

# Read from Database State
class State2(State):
    def run(self):
        logging.info("Reading from Database...")
        db_read_successful = False

        rezept_id, granulat_id, menge = None, None, None

        conn = sql.connect(SQL_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT Rezept_ID FROM Flasche WHERE Flaschen_ID = ?", (self.machine.flaschen_id,))
        rezept_id = cursor.fetchone()[0]
        cursor.execute("SELECT Granulat_ID FROM Rezept_besteht_aus_Granulat WHERE Rezept_ID = ?", (rezept_id,))
        granulat_id = cursor.fetchone()[0]
        cursor.execute("SELECT Menge FROM Rezept_besteht_aus_Granulat WHERE Rezept_ID = ?", (rezept_id,))
        menge = cursor.fetchone()[0]

        conn.close()

        if rezept_id != None and granulat_id != None and menge != None:
            db_read_successful = True
        
        if db_read_successful:
            logging.info(f"Flasche mit ID {self.machine.flaschen_id} hat Rezept_ID: {rezept_id}, Granulat_ID: {granulat_id} und Menge: {menge}")
            logging.info("Successfully read from database.")
            self.machine.current_state = 'State3'
        else:
            logging.error("Failed to read data from database.")
            self.machine.current_state = 'State5'

# Create QR-Code State
class State3(State):
    def run(self):
        qr_creation_successful = False

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(self.machine.flaschen_id)
        qr_img = qr.make_image(fill_color='black', back_color='white')

        logo = Image.open("MCI-negative_Print.png").resize((75, 75), Image.LANCZOS)
        offset = ((qr_img.size[0] - 75) // 2, (qr_img.size[1] - 75) // 2)
        qr_img.paste(logo, offset, mask=logo.split()[3] if logo.mode == 'RGBA' else None)
        
        qr_img.save(f"../src/QR_Code{self.machine.flaschen_id}.png")

        if qr_creation_successful:
            logging.info("Successfully created QR-Code.")
            self.machine.current_state = 'State3'
        else:
            logging.error("Failed to create QR-Code.")
            self.machine.current_state = 'State5'

class State4(State):
    def run(self):
        logging.info("Successfully completed the process! Returning to State1.")
        
        # Transition back to State1 - probably not hepful while debugging
        #self.machine.current_state = 'State1'  

class State5(State):
    def run(self):
        logging.error("Process failed at some point. Please check the logs.")
        self.machine.current_state = 'State5'


# Main execution
if __name__ == '__main__':
    machine = StateMachine(nfc_reader)
    machine.run()
    logging.info("Stopped Execution. Please rerun the program to start again.")