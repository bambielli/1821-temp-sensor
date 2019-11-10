import os
from airtable import Airtable
import temp_readings
from time import sleep
from datetime import datetime

# Env Vars and Constants
AIRTABLE_API_KEY = os.environ['AIRTABLE_API_KEY']
AIRTABLE_BASE_KEY = os.environ['AIRTABLE_BASE_KEY']
AIRTABLE_TABLE_NAME = os.environ['AIRTABLE_TABLE_NAME']
TIME_BETWEEN_PUBLISH = 0.5 # in seconds
TEMP_THRESHOLD = 80 # in Farenheit

airtable_client = Airtable(AIRTABLE_BASE_KEY, AIRTABLE_TABLE_NAME, api_key=AIRTABLE_API_KEY)
record_id = airtable_client.get_all(view="Readings")[0]["id"]



sensor_name = temp_readings.get_sensor_name()

# Airtable free tier gives you 1200 records per table.
# instead of keeping historical data around, I'm just going to 
# overwrite the same record's value every time the publish action runs.

# Thought about using zapier to connect airtable and slack... fortunately I didn't need to, since airtable had its own slack integration already.


def create_record(date_time, farenheit):
    return {'Date': date_time, 'Temp': farenheit}

def cold_enough_to_publish(current_temp):
    return current_temp <= TEMP_THRESHOLD

def within_24_hours(last_alert_datetime):
    print(f"last_alert_date: {last_alert_datetime}")
    last_alert_datetime_parsed = datetime.strptime(last_alert_datetime, "%Y-%m-%dT%H:%M:%S.%fZ")
    now = datetime.now()
    # if the days property of the resulting datetime after subtracting the two is 0, then we are within 24 hours.
    return (now - last_alert_datetime_parsed).days == 0

def publish_cold_record(cold_record):
    """
    If temperature drops below a certain threeshold this funciton is called
    We publish to a different view in airtable that publishes to a different slack channel
    """
    cold_record_airtable = airtable_client.get_all(view="Cold Temperature Alerts")[0]
    print(cold_record_airtable)
    if not within_24_hours(cold_record_airtable["fields"]["Date"]):
        print ("last record was not within 24 hours")
        cold_record_id = cold_record_airtable["id"]
        cold_record["isColdAlert"] = True
        airtable_client.replace(cold_record_id, cold_record)

def publish_record_to_airtable():
    
    # get a reading from the sensor
    _ , farenheit, date_time = temp_readings.read(sensor_name)
    print(farenheit, date_time)
        
    # publish to airtable
    record = create_record(date_time, farenheit)
    airtable_client.replace(record_id, record)
    
    if cold_enough_to_publish(farenheit):
        print("publishing cold alert")
        publish_cold_record(record)
    

def loop():
    """
    This is just used for testing
    """
    if sensor_name != None and record_id != None:
        while True:
            publish_reading_to_airtable()
        
            # sleep for a while then publish again
            sleep(TIME_BETWEEN_PUBLISH)

def main():
    """
    run via crontab every hour to publish record to airtable
    """
    publish_record_to_airtable()

if __name__ == '__main__':
    main()
elif __name__ == 'loop':
    loop()
