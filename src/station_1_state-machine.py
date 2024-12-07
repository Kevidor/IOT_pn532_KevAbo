import logging
import nfc_reader as nfc
import sqlite3 as sql
from time import time

# Initialize logger, NFCREADER and Databasepath
nfc_reader = None
SQL_PATH = "/home/uwe/IOT_pn532_KevAbo/data/flaschen_database.db"
logger1 = logging.getLogger("station1_logger")
logger1.setLevel(logging.DEBUG)
file_handler_station1 = logging.FileHandler("/home/uwe/IOT_pn532_KevAbo/log/station1.log", mode="a")
file_handler_station1.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger1.addHandler(file_handler_station1)

class StateMachine:
    def __init__(self, reader):
        self.current_state = 'State0'
        self.reader = reader
        self.SQL_counter = None
        self.unix_time = None
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
            logger1.info("RFID reader initialized successfully.")
            self.machine.current_state = 'State1'  # Transition to State1
        else:
            logger1.error("Failed to initialize RFID reader.")
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
            logger1.warning("No card detected. Retrying...")
            self.machine.current_state = 'State1'  # Wait again
        else:
            logger1.info(f"Found card with UID: {[hex(i) for i in self.machine.reader.uid]}") 
            self.machine.current_state = 'State2'  # Transition to State2

class State2(State):
    def run(self):
        logging.info("Writing Bottle ID to card...")
        write_successful = False

        # Simulate writing logic
        write_successful = self.machine.reader.write_block(self.machine.reader.uid, 4, nfc.strint_to_hex_block('B16B00B5')) # type: ignore
        
        if write_successful:
            logger1.info("Successfully wrote to card.")
            self.machine.unix_time = int(time())
            self.machine.current_state = 'State3'  # Transition to State3
        else:
            logger1.error("Failed to write to card. Waiting for a new card.")
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

        cursor.execute("UPDATE Flasche SET Tagged_Date = ? WHERE Flaschen_ID = ?", (self.machine.unix_time, self.machine.SQL_counter))
        conn.commit()

        cursor.execute("SELECT Tagged_Date FROM Flasche WHERE Flaschen_ID = ?", (self.machine.SQL_counter,))
        cell_data = cursor.fetchone()
        if cell_data[0] == self.machine.unix_time: db_write_successful = True

        # Close the connection
        conn.close()
        
        if db_write_successful:
            logger1.info("Successfully saved to database.")
            self.machine.SQL_counter += 1
            self.machine.current_state = 'State4'  # Transition to State4
        else:
            logger1.error("Failed to save data to database.")
            self.machine.current_state = 'State5'  # Transition to State5

class State4(State):
    def run(self):
        temp_uid = None
        while True:
            temp_uid = self.machine.reader.read_passive_target(timeout=0.5)
            print(".", end="")
            if temp_uid is None:
                continue
            break
        
        if temp_uid != self.machine.reader.uid:
            logger1.info("New card detected. Returning to State1")
            self.machine.current_state = 'State1' 

class State5(State):
    def run(self):
        logger1.error("Process failed at some point. Please check the logs.")
        self.machine.current_state = 'State5'  # End of process

# Main execution
if __name__ == '__main__':
    machine = StateMachine(nfc_reader)
    machine.run()
    logger1.info("Stopped Execution. Please rerun the program to start again.")