from abc import ABC, abstractmethod
import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.spi import PN532_SPI
import logging


# Configure logging
LOG_PATH = "/home/uwe/IOT_pn532_KevAbo/log/nfc_reader.log"
logging.basicConfig(
    level=logging.INFO,
    filename=LOG_PATH,
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Constants
DEFAULT_KEY_A = bytes([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
BLOCK_COUNT = 64

class NFCReaderInterface(ABC):

    @abstractmethod
    def config(self):
        pass

    @abstractmethod
    def read_block(self, uid, block_number):
        pass

    @abstractmethod
    def read_all_blocks(self, uid):
        pass
    @abstractmethod
    def write_block(self, uid, block_number, data):
        pass



class NFCReader(NFCReaderInterface):
    def __init__(self):
        self._pn532 = self.config()
        self.uid = None

    def __getattr__(self, name):
        """
        Delegate any call to PN532_SPI if it's not explicitly defined in NFCReader.
        """
        return getattr(self._pn532, name)

    def config(self):
        try:
            spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
            cs_pin = DigitalInOut(board.D8)
            pn532 = PN532_SPI(spi, cs_pin, debug=False)

            ic, ver, rev, support = pn532.firmware_version
            logger.info("Found PN532 with firmware version: %d.%d", ver, rev)

            # Configure PN532 to communicate with MiFare cards
            pn532.SAM_configuration()
            return pn532
        except Exception as e:
            logger.error("Failed to configure PN532: %s", e)
            raise

    def read_block(self, uid, block_number):
        try:
            authenticated = self._pn532.mifare_classic_authenticate_block(
                uid, block_number, 0x60, key=DEFAULT_KEY_A
            )
            if not authenticated:
                logger.error("Failed to authenticate block %d", block_number)
                return None

            block_data = self._pn532.mifare_classic_read_block(block_number)
            if block_data is None:
                logger.error("Failed to read block %d", block_number)
                return None

            return block_data
        except Exception as e:
            logger.exception("Error reading block %d: %s", block_number, e)
            return None

    def read_all_blocks(self, uid):
        blocks_data = []
        for block_number in range(BLOCK_COUNT):
            block_data = self.read_block(uid, block_number)
            if block_data:
                blocks_data.append(block_data)
            else:
                logger.warning("No data read from Block %d", block_number)
        return blocks_data

    def write_block(self, uid, block_number, data):
        try:
            authenticated = self._pn532.mifare_classic_authenticate_block(
                uid, block_number, 0x60, key=DEFAULT_KEY_A
            )
            if not authenticated:
                logger.error("Failed to authenticate block %d for writing", block_number)
                return False

            success = self._pn532.mifare_classic_write_block(block_number, data)
            if not success:
                logger.error("Failed to write to block %d", block_number)
                return False

            logger.info("Successfully wrote data to block %d", block_number)
            return True
        except Exception as e:
            logger.exception("Error writing block %d: %s", block_number, e)
            return False

def strint_to_hex_block(hex_string) -> bytes:
    if isinstance(hex_string, int): hex_string = hex(hex_string)[2:]
    if len(hex_string) % 2 != 0:
        hex_string = '0' + hex_string  # Pad with leading zero if necessary

    data = bytes(int(hex_string[i:i+2], 16) for i in range(0, len(hex_string), 2))
    padded_data = data + b'\x00' * (16 - len(data))

    return padded_data

def hex_block_to_strint(padded_data: bytes, to_int: bool = True):
    unpadded_data = padded_data.rstrip(b'\x00')
    
    hex_string = ''.join(f'{byte:02X}' for byte in unpadded_data)
    if to_int: hex_string = int(hex_string, 16)

    return hex_string

if __name__ == "__main__":

    nfc_reader = NFCReader()

    logger.info("Waiting for RFID/NFC card...")
    while True:
        uid = nfc_reader.read_passive_target(timeout=0.5)
        print(".", end="")
        if uid is None:
            continue
        logger.info("Found card with UID: %s", [hex(i) for i in uid])
        break

    
    #for i in range(4,7):
    #nfc_reader.write_block(uid, 4, strint_to_hex_block(1))

    #blocks_data = nfc_reader.read_all_blocks(uid)
    #for block_number, block_data in enumerate(blocks_data):
    #    hex_values = ' '.join([f'{byte:02x}' for byte in block_data])
    #    logger.info("Data in Block %d: %s", block_number, hex_values)

    flaschen_id = nfc_reader.read_block(uid, 4)
    print(flaschen_id)