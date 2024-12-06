import logging
import nfc_reader as nfc
import sqlite3 as sql
from time import time

# Initialize logger, NFCREADER and Databasepath
logging.basicConfig(level=logging.DEBUG)
nfc_reader = None
SQL_PATH = "/home/uwe/IOT_pn532_KevAbo/data/flaschen_database.db"

class StateMachine:
    def __init__(self, reader):
        self.current_state = 'State0'
        self.reader = reader
        self.SQL_counter = None
        self.states = {
            'State0': State0(self),
            'State1': State1(self),
            'State2': State2(self),
            'State3': State3(self),
            'State4': State4(self),
            'State5': State5(self)
        }

    def run(self):
        while self.current_state not in ['State5']:
            state = self.states[self.current_state]
            state.run()  # Run the current state

class State:
    def __init__(self, machine):
        self.machine = machine

    def run(self):
        raise NotImplementedError("State must implement 'run' method.")

class State0(State):
    def run(self):
        logging.info("Initializing RFID reader...")
        init_successful = False
        self.machine.SQL_counter = 1

        # Simulate RFID reader initialization (replace with actual initialization code)
        self.machine.reader = nfc.NFCReader()
        if self.machine.reader: 
            init_successful = True
        
        if init_successful:
            logging.info("RFID reader initialized successfully.")
            self.machine.current_state = 'State1'  # Transition to State1
        else:
            logging.error("Failed to initialize RFID reader.")
            self.machine.current_state = 'State5'  # Transition to State5

class State1(State):
    def run(self):
        logging.info("Waiting for RFID card...")
        
        #uid = [45, 162, 193, 56]  # Placeholder for RFID detection
        while True:
            self.machine.reader.uid = self.machine.reader.read_passive_target(timeout=0.5)
            print(".", end="")
            if self.machine.reader.uid is None:
                continue
            #logging.info("Found card with UID: %s", [hex(i) for i in self.machine.reader.uid])
            break

        if self.machine.reader.uid is None:
            logging.warning("No card detected. Retrying...")
            self.machine.current_state = 'State1'  # Wait again
        else:
            logging.info(f"Found card with UID: {[hex(i) for i in self.machine.reader.uid]}") 
            self.machine.current_state = 'State2'  # Transition to State2

class State2(State):
    def run(self):
        logging.info("Writing Bottle ID to card...")
        write_successful = False

        # Simulate writing logic
        write_successful = self.machine.reader.write_block(self.machine.reader.uid, 4, nfc.str_to_hex_block('B16B00B5')) # type: ignore
        
        if write_successful:
            logging.info("Successfully wrote to card.")
            self.machine.current_state = 'State3'  # Transition to State3
        else:
            logging.error("Failed to write to card. Waiting for a new card.")
            self.machine.current_state = 'State1'  # Transition back to State1

class State3(State):
    def run(self):
        logging.info("Saving Bottle ID and timestamp to database...")
        
        # Simulate database write (replace with actual database code)
        db_write_successful = False

        # Simulate database write (replace with actual database code)
        #db_write_successful = True  # Simulate success
        conn = sql.connect(SQL_PATH)
        cursor = conn.cursor()

        cursor.execute("UPDATE Flasche SET Tagged_Date = ? WHERE Flaschen_ID = ?", (69, self.machine.SQL_counter))
        conn.commit()

        cursor.execute("SELECT Tagged_Date FROM Flasche WHERE Flaschen_ID = ?", (self.machine.SQL_counter,))
        cell_data = cursor.fetchone()
        if cell_data[0] == 69: db_write_successful = True

        self.machine.SQL_counter += 1

        # Close the connection
        conn.close()
        
        if db_write_successful:
            logging.info("Successfully saved to database.")
            self.machine.current_state = 'State4'  # Transition to State4
        else:
            logging.error("Failed to save data to database.")
            self.machine.current_state = 'State5'  # Transition to State5

class State4(State):
    def run(self):
        logging.info("Successfully completed the process! Returning to State1.")
        
        # Transition back to State1 - probably not hepful while debugging
        #self.machine.current_state = 'State1'  

class State5(State):
    def run(self):
        logging.error("Process failed at some point. Please check the logs.")
        self.machine.current_state = 'State5'  # End of process

# Main execution
if __name__ == '__main__':
    machine = StateMachine(nfc_reader)
    machine.run()
    logging.info("Stopped Execution. Please rerun the program to start again.")