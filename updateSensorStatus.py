import Adafruit_DHT as dht
from google.cloud import firestore
from google.oauth2 import service_account
from datetime import datetime, timedelta
from lib.SerialDevice import SerialDevice

# Credentials JSON key file
cred = service_account.Credentials.from_service_account_file('db/hortilite-test-firebase-adminsdk-w9s0u-6fdaaf3ee5.json')

# Database init
db = firestore.Client(credentials=cred)

# Sensor 'active' field
active_ref = None

# addresses
camera_ip_range = ("192.168.1.205", "192.168.1.206", "192.168.1.207", "192.168.1.208")
soil_id = dht_id = (5, 6, 7, 8)

# Soil Sensors #
def checkSoilStatus(sensor_ids):
    serial_device = None

    for sensor_id in sensor_ids:
        try:
            serial_device = SerialDevice.init_port(port_name="/dev/ttyUSB0", baudRate=9600, timeOut=2, verbose=False)
            active_ref = db.collection("Soil").document("soil" + '_' + str(sensor_id))
            if serial_device:
                active_ref.update({'active': True,})
            else:
                active_ref.update({'active': False,})
                
        except Exception as e:
            print(f"An error occurred: {e}")
        
# DHT22 Sensors #
def checkDHTStatus(addr_range):
    for dev_id in addr_range:
        active_ref = db.collection("DHT22").document("dht22" + '_' + str(dev_id))
        h, t = dht.read_retry(dht.DHT22, dev_id)
        if h is None and t is None:
            active_ref.update({'active': False,})
        else:
            active_ref.update({'active': True,})
            
            
def checkCamStatus(ip_addr_range):
    camera = None
    for cam_ip in ip_addr_range:
        active_ref = db.collection("Camera").document(str(cam_ip))
        try:
            camera = HIKROBOTCamera(ip_addr=camera_ip, load_settings=True)
            camera.connect()
            active_ref.update({'active': True,})
            
            if not camera.connected():
                active_ref.update({'active': False,})
                print("Failed to connect to the camera.")
                
                
checkSoilStatus(soil_id)
checkDHTStatus(dht_id)
checkCamStatus(camera_ip_range)