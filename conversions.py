"""
This file contains various conversions between old and new formats. It's only meant to be run
automatically from main.py before the server itself starts.
"""

def check_for_conversion() -> None:
    import logging
    import os
    
    # log to console
    logging.basicConfig(level=logging.INFO)
    
    if not os.path.exists("data/tracking.pkl") and os.path.exists("data/tracking"):
        from classes import TrackingData
        logging.info("Old .txt tracking data found, converting to new format...")
        txt_to_class()
        tracking_data = TrackingData()
        tracking_data.load_from_pickle("data/tracking.pkl")
        print(f"Tracking data loaded, {len(tracking_data.users)} users tracked.")

# convert from old .txt tracking to classes
def txt_to_class() -> bool:
    from classes import UserSessionData, SessionData, TrackingData
    import logging
    import pickle
    import os
    
    data: dict[str, UserSessionData] = {}
    users = os.listdir("data/tracking")
    for i, user in enumerate(users):
        if not os.path.exists(f"data/tracking/{user}/ping.txt"):
            continue
        
        sessions: list[SessionData] = []
        with open(f"data/tracking/{user}/ping.txt", "r") as f:
            lines = f.readlines()
            start = float(lines[0].strip())
            end = start
            for line in lines[1:]:
                timestamp = float(line.strip())
                if timestamp - end > 180: # 3 minutes
                    sessions.append(SessionData(start, end))
                    start = timestamp
                
                end = timestamp
                
            sessions.append(SessionData(start, end))
            
        tracking = UserSessionData()
        tracking.sessions = sessions
        tracking.latest = sessions[-1].end
        tracking.total = sum(s.end - s.start for s in sessions)
        data[user] = tracking
        if i % 100 == 0:
            logging.info(f"Converted {i}/{len(users)} users...    ")
        
    tracking_data = TrackingData()
    tracking_data.users = data
    tracking_data.last_1h = 0
    tracking_data.last_1d = 0
    tracking_data.last_7d = 0
    tracking_data.last_30d = 0
    
    with open("data/tracking.pkl", "wb") as f:
        pickle.dump(tracking_data, f)
        
    logging.info("Converted old .txt tracking data to classes.")
    return True

if __name__ == "__main__":
    txt_to_class()