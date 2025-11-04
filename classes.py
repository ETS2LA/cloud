from pydantic import BaseModel
from typing import Literal

class Response:
    def __init__(self, data: dict, status: int) -> None:
        self.data = data
        self.status = status

# MARK: Jobs

class CancelledJob(BaseModel):
    timestamp: float = 0
    special: bool = False
    started_time: int = 0
    cancelled_time: int = 0
    cancelled_penalty: int = 0
    
    def json(self):
        return self.model_dump()

class FinishedJob(BaseModel):
    timestamp: float = 0
    special: bool = False
    cargo: str = ""
    cargo_id: str = ""
    unit_mass: float = 0
    unit_count: int = 0
    starting_time: int = 0
    finished_time: int = 0
    delivered_delivery_time: int = 0
    delivered_autoload_used: bool = False
    delivered_autopark_used: bool = False
    delivered_cargo_damage: float = 0
    delivered_distance_km: float = 0
    delivered_revenue: int = 0
    
    def json(self):
        return self.model_dump()
    
class Job(BaseModel):
    timestamp: float = 0
    special: bool = False
    cargo: str = ""
    cargo_id: str = ""
    unit_mass: float = 0
    unit_count: int = 0
    delivered_delivery_time: int = 0
    starting_time: int = 0
    finished_time: int = 0
    delivered_cargo_damage: float = 0
    delivered_distance_km: float = 0
    delivered_autopark_used: bool = False
    delivered_autoload_used: bool = False
    income: int = 0
    delivered_revenue: int = 0
    cancelled_penalty: int = 0
    event_type: Literal["delivered", "cancelled", "loaded"] = "loaded"
    
    def json(self):
        return self.model_dump()
    
def IsFinishedJobSameAsStartedJob(started_job: Job, finished_job: FinishedJob) -> bool:
    return started_job.special == finished_job.special\
        and started_job.cargo == finished_job.cargo\
        and started_job.cargo_id == finished_job.cargo_id\
        and started_job.unit_mass == finished_job.unit_mass
        
        
# MARK: Commits

class UpdatedCommits(BaseModel):
    commits: list[str] = []
    
    def json(self):
        return self.model_dump()
    
# MARK: Discord Integration

class CrashReport(BaseModel):
    timestamp: float
    source: str
    source_description: str
    fields: dict[str, str] = {}

class Feedback(BaseModel):
    timestamp: float
    message: str
    user: str
    fields: dict[str, str] = {}
    
# MARK: Ko-fi Integration

class ShopItem(BaseModel):
    direct_link_code: str
    variation_name: str
    quantity: int

class Shipping(BaseModel):
    full_name: str
    street_address: str
    city: str
    state_or_province: str
    postal_code: str
    country: str
    country_code: str
    telephone: str
    
class KofiData(BaseModel):
    verification_token: str
    message_id: str
    timestamp: str
    type: Literal["Donation", "Subscription", "Shop Order"]
    is_public: bool
    from_name: str
    message: str | None
    amount: str
    url: str
    email: str
    currency: str
    is_subscription_payment: bool
    is_first_subscription_payment: bool
    kofi_transaction_id: str
    discord_username: str | None
    discord_userid: str | None
    
# MARK: Tracking

class SessionData():
    start: float
    end: float
    
    def __init__(self, start: float, end: float) -> None:
        self.start = start
        self.end = end
        
    def json(self) -> dict:
        return {
            "start": self.start,
            "end": self.end
        }

class UserSessionData():
    sessions: list[SessionData] = []
    latest: float = 0
    total: float = 0
    
class TrackingData():
    users: dict[str, UserSessionData] = {}
    """Dictionary of user ID to their session data."""
    
    total: float = 0
    last_1h: int = 0
    last_1d: int = 0
    last_7d: int = 0
    last_30d: int = 0
    last_updated: float = 0
    last_written: float = 0
    
    last_180s: int = 0
    last_current_updated: float = 0
    
    def update_stats(self) -> None:
        import time
        now = time.time()
        
        if self.last_updated > now - 3600: # updated within the last hour
            return
        
        self.last_1h = sum(1 for u in self.users.values() if u.latest > now - 3600)
        self.last_1d = sum(1 for u in self.users.values() if u.latest > now - 86400)
        self.last_7d = sum(1 for u in self.users.values() if u.latest > now - 604800)
        self.last_30d = sum(1 for u in self.users.values() if u.latest > now - 2592000)
        self.total = sum(u.total for u in self.users.values())
        self.last_updated = now
        
    def update_current_users(self) -> None:
        import time
        now = time.time()
        if self.last_current_updated > now - 120: # updated within the last two minutes
            return
        
        self.last_180s = sum(1 for u in self.users.values() if u.latest > now - 180)
        self.last_current_updated = now
    
    def load_from_pickle(self, path: str) -> None:
        import pickle
        with open(path, "rb") as f:
            data = pickle.load(f)
            self.users = data.users
            self.last_1d = data.last_1d
            self.last_7d = data.last_7d
            self.last_30d = data.last_30d
            self.last_updated = data.last_updated
            
    def save_to_pickle(self, path: str) -> None:
        import logging
        import pickle
        import time
        import os
        
        now = time.time()
        if self.last_written > now - 43200: # saved within the last 12 hours
            return
        
        # There's a chance of a race condition here, but it's *very* unlikely.
        # You'd have to have two calls within some nanoseconds, basically impossible (right?) :copege:
        self.last_written = now
        
        # backup old file
        backup_filename = path + f".{round(now)}.bak"
        if os.path.exists(path):
            os.rename(path, backup_filename)

        # and write new one
        try:
            with open(path, "wb") as f:
                pickle.dump(self, f)
        except Exception as e:
            logging.error(f"Failed to save tracking data to {path}: {e}")
            data = os.read(backup_filename)
            with open(path, "wb") as f:
                f.write(data)