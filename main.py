import asyncio
from bleak import BleakScanner, BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
import logging
import motion_pb2
import logging
from datetime import datetime, timezone
import aiofiles
from tqdm import tqdm
import time

#todo: keep track of tracker ID's read to prevent reading multiple times due to adress changes
#todo: format data in coloms?

logger = logging.getLogger(__name__)
#logging.basicConfig(level=logging.DEBUG)

#IO_DATA_CHAR_UUID = "d97b1503-a25c-4295-bd21-f96823d91552"
BT_DEVICE_ID = "56a332cc-0379-497e-bd2d-e778c69badd6"
BT_MEM_POS = "84b45135-170b-4d03-92b6-386d7bff160d"
BT_DATA_NOTIFY = "6f2648ed-e73f-4b9f-a809-b1686d18676c"
BT_DATA_REQ = "4e10fd71-6cc1-4fa7-aa91-82021582ca54" 
BATTERY_LEVEL_UUID = "00002a19-0000-1000-8000-00805f9b34fb"

class uutrack_reader:
    
    def __init__(self):
        self.id = 0
        self.counter = 0
        self.received_ble = bytearray()
        self.semaphore = asyncio.Semaphore(1)
        self.storage = []         
        self.amountBytes = 0    

    async def notification_handler(self, sender, data : bytearray):        

        self.counter +=1
        self.received_ble.extend(data)
        if(self.counter == 0):
            self.amountBytes = int.from_bytes(data[0:2], "little")
 
        if len(self.received_ble) >= self.amountBytes:
            server2 = motion_pb2.HourlyResult()            
            server2.ParseFromString(self.received_ble[2:self.amountBytes+2])
            self.storage.append(datetime.fromtimestamp(server2.UnixTime, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))
            self.storage.extend([str(item) for item in server2.AvgMinuteList])
            self.counter = 0
            self.received_ble.clear()
            self.semaphore.release()
            
    async def makeconnectiontodevice(self, device):
        client = BleakClient(device.address, timeout=30)
        
        try:
            await client.connect()
            device_id_bytes = await client.read_gatt_char(BT_DEVICE_ID)
            stored_amount_bytes = await client.read_gatt_char(BT_MEM_POS)
            battery_level_byte = await client.read_gatt_char(BATTERY_LEVEL_UUID)
                
            #await client.pair()
            #password_bytes = await client.read_gatt_char(IO_DATA_CHAR_UUID)

            self.id = int.from_bytes(device_id_bytes, "little")
            stored_amount = int.from_bytes(stored_amount_bytes, "little")
            
            print(f'device_id {self.id}')            
            print(f'storage amount {stored_amount}')
            print(f'battery level {int.from_bytes(battery_level_byte, byteorder="little")}')
                        
            await client.start_notify(BT_DATA_NOTIFY, self.notification_handler)
            
            for storage_position in tqdm(range(stored_amount-1), desc="BLE Data"): #replace with# range(stored_amount):                    
                storage_position_bytes = int.to_bytes(storage_position, byteorder="little", length=2)
                await client.write_gatt_char(BT_DATA_REQ, storage_position_bytes)
                await self.semaphore.acquire()
            
            
            async with aiofiles.open(f'data/UU_Track{self.id}', mode="w") as localfile:
                await localfile.writelines([str(item) + "\n" for item in self.storage])
                print(f'wrote to {localfile.name}')
                
        except Exception as e:
            print(e)
        finally:
            await client.disconnect()
            print(f'disconnected {self.id}')
    

class datacollector:
    async def app(self):
        devices = await BleakScanner.discover()
        for d in devices:
            #print(d)
            if(d.name == "UU_tracker_DEBUG" or d.name == "UU_tracker"):            
                print(f'device found:{d}')
                the_reader = uutrack_reader()
                await the_reader.makeconnectiontodevice(d)
                

def main(): 
    collectior = datacollector()
    asyncio.run(collectior.app())

if __name__ == "__main__":
    main()
