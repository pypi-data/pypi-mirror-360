import sdb_connector as sdb_conn
import time
import pandas as pd

#RUN_ID = "run_info:01JKG9806ABN68BXD7MW2Y8SPP"
RUN_ID = "run_info:01JKG94MFR38A4RAB68WQZ7MF7"
#RUN_ID = "run_info:01JKG9D3G88RNH3V8E03DZ6CZW"
# PROJECT_ID = "project_info:01JKG94AKGTX28RSZC1Y17K4NJ"
IP = "192.168.2.63"

def main():
    start = time.time()
    result = sdb_conn.select_additional_info_data(IP, "8000", 
                "root", "root","main", "data", "amv_tag_49", RUN_ID, "additional_info.xlsx", 0)
    df = pd.DataFrame(result, columns=['run_counter', 'len_trigger', 'channel', 'peak', 'peak_positon', \
                                       'positon_over', 'positon_under', 'offset_after', 'offset_before', 'timestamp']).sort_values(by=['run_counter', 'channel'])
    print(df)
    end = time.time()
    print("Time taken result: ", end - start)
    
    start = time.time()
    result = sdb_conn.select_measurement_data(IP, "8000", 
                "root", "root","main", "data", "amv_tag_41", RUN_ID, "measurement.xlsx", 0)
    df = pd.DataFrame(result, columns=['run_counter', 'channel', 'integral', 'mass',"offset", "offset1", "offset2", "tolerance_bottom",\
                                       "tolerance_top", "project", "timestamp", "status"]).sort_values(by=['run_counter', 'channel'])
    print(df)
    end = time.time()
    print("Time taken result: ", end - start)
    
    start = time.time()
    result = sdb_conn.select_raw_data(IP, "8000", 
                "root", "root","main", "data", "amv_raw_data", RUN_ID)
    df = pd.DataFrame(result, columns=['run_counter', 'channel', 'data', 'datetime']).sort_values(by=['run_counter', 'channel'])
    df["run_id"] = RUN_ID
    print(df)
    end = time.time()
    print("Time taken result: ", end - start)

if __name__ == "__main__":
    main()