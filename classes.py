from pydantic import BaseModel
from typing import Literal

class CancelledJob(BaseModel):
    timestamp: int = 0
    special: bool = False
    started_time: int = 0
    cancelled_time: int = 0
    cancelled_penalty: int = 0
    
    def json(self):
        return self.model_dump()

class FinishedJob(BaseModel):
    timestamp: int = 0
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
    timestamp: int = 0
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