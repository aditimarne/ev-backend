from pydantic import BaseModel

class OlaInput(BaseModel):
    Year_of_purchase: float
    Month_of_purchase: float
    Charge_times: float
    Charge_duration: float
    Avg_charging_percentage: float
    Total_distance_travelled_daily: float
    Travel_time_daily: float
    Avg_speed_daily: float
    Eco_mode_distance: float
    Normal_mode_distance: float
    Sport_mode_distance: float
    Hyper_mode_distance: float


class RevoltInput(BaseModel):
    Distance_Travelled: float
    RideTime: float
    Average_Speed: float
    Max_Speed: float
    Eco_Mode: float
    Normal_Mode: float
    Sport_Mode: float
    SOC_Consumed: float
    Year_of_purchase: float
    Month_of_purchase: float
