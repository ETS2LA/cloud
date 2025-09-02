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