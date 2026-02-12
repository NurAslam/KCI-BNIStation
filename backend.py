

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import random
import numpy as np

app = FastAPI(
    title="KCI Stasiun BNI City",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TrafficHourData(BaseModel):
    hour: int
    count: int
    period: str 

class GateUtilizationData(BaseModel):
    gate_id: str
    zone: str
    count: int
    utilization_rate: float

class TrafficZoneData(BaseModel):
    zone: str
    count: int
    percentage: float

class DirectionBalanceData(BaseModel):
    zone: str
    direction: str
    count: int
    percentage: float

class OperationalEfficiencyResponse(BaseModel):
    date: str
    total_transactions: int
    traffic_per_hour: List[TrafficHourData]
    gate_utilization: List[GateUtilizationData]
    traffic_by_zone: List[TrafficZoneData]
    balance_direction: List[DirectionBalanceData]
    summary: Dict

class AgeDistributionData(BaseModel):
    age_range: str
    count: int
    percentage: float

class OccupationDistributionData(BaseModel):
    occupation: str
    count: int
    percentage: float

class GenderDistributionData(BaseModel):
    gender: str
    count: int
    percentage: float

class OriginStationData(BaseModel):
    station: str
    count: int
    percentage: float

class DemografiResponse(BaseModel):
    date: str
    total_passengers: int
    age_distribution: List[AgeDistributionData]
    occupation_distribution: List[OccupationDistributionData]
    gender_distribution: List[GenderDistributionData]
    origin_station_distribution: List[OriginStationData]
    summary: Dict

class OriginDistributionData(BaseModel):
    station: str
    count: int
    percentage: float

class DirectionDistributionData(BaseModel):
    direction: str
    count: int
    percentage: float

class TimeTravelData(BaseModel):
    time_segment: str
    count: int
    percentage: float

class SegmentasiPerjalananResponse(BaseModel):
    date: str
    total_transactions: int
    origin_distribution: List[OriginDistributionData]
    direction_distribution: List[DirectionDistributionData]
    time_travel_distribution: List[TimeTravelData]
    summary: Dict

class LoyaltySegmentData(BaseModel):
    segment: str
    count: int
    percentage: float
    min_freq: int
    max_freq: int

class LoyaltyByOccupationData(BaseModel):
    occupation: str
    avg_frequency: float
    count: int

class SegmentasiLoyaltasResponse(BaseModel):
    date: str
    total_passengers: int
    loyalty_segments: List[LoyaltySegmentData]
    loyalty_by_occupation: List[LoyaltyByOccupationData]
    summary: Dict


class AgeLoyaltyCorrelationData(BaseModel):
    age: int
    avg_loyalty_frequency: float
    count: int

class HourGenderData(BaseModel):
    hour: int
    pria_count: int
    wanita_count: int
    pria_percentage: float
    wanita_percentage: float

class OccupationZonePreferenceData(BaseModel):
    occupation: str
    north_count: int
    west_count: int
    preference: str  # 'North' or 'West'

class BehaviorCorrelationResponse(BaseModel):
    date: str
    age_loyalty_correlation: List[AgeLoyaltyCorrelationData]
    hour_gender_distribution: List[HourGenderData]
    occupation_zone_preference: List[OccupationZonePreferenceData]
    summary: Dict

# ==========================
# DATA GENERATION HELPERS
# ==========================

def generate_daily_data(base_value: int, variance: float = 0.2) -> int:
    """Generate random daily data with variance"""
    return int(base_value * (1 + random.uniform(-variance, variance)))

def get_date() -> str:
    """Get current date string"""
    return datetime.now().strftime("%Y-%m-%d")

# ==========================
# ENDPOINTS - KATEGORI 1: OPERATIONAL EFFICIENCY
# ==========================

@app.get("/api/v1/operational-efficiency", response_model=OperationalEfficiencyResponse, include_in_schema=False)
async def get_operational_efficiency(date: Optional[str] = None):
    """
    Kategori 1: Operational Efficiency
    - 1.1 Traffic per Jam
    - 1.2 Gate Utilization
    - 1.3 Traffic by Zone
    - 1.4 Balance Direction
    """
    target_date = date or get_date()

    # Random daily total transactions (4000-6000)
    total_transactions = random.randint(4000, 6000)


    traffic_per_hour = []
    for hour in range(6, 23):
        # Morning peak (7-9) higher, Evening peak (16-19) higher, Off-peak tanpa label
        if 7 <= hour <= 9:
            base_count = random.randint(400, 600)
            period = "Morning Peak"
        elif 16 <= hour <= 19:
            base_count = random.randint(400, 600)
            period = "Evening Peak"
        else:
            base_count = random.randint(50, 200)
            period = ""  # Empty label untuk off-peak (tidak ditampilkan)

        count = generate_daily_data(base_count, 0.15)
        traffic_per_hour.append(TrafficHourData(
            hour=hour,
            count=count,
            period=period
        ))

    # 1.2 Gate Utilization (8 gates: 4 North, 4 West)
    gate_utilization = []
    zones = ['North', 'West']
    for zone in zones:
        for i in range(1, 5):
            gate_id = f"TAP-{zone.upper()}-00{i}"
            base_count = random.randint(450, 650) if zone == 'North' else random.randint(400, 600)
            count = generate_daily_data(base_count, 0.2)
            utilization_rate = (count / total_transactions) * 100
            gate_utilization.append(GateUtilizationData(
                gate_id=gate_id,
                zone=zone,
                count=count,
                utilization_rate=round(utilization_rate, 2)
            ))

    # 1.3 Traffic by Zone
    north_count = sum(g.count for g in gate_utilization if g.zone == 'North')
    west_count = sum(g.count for g in gate_utilization if g.zone == 'West')
    traffic_by_zone = [
        TrafficZoneData(
            zone='TAP-NORTH',
            count=north_count,
            percentage=round((north_count / total_transactions) * 100, 1)
        ),
        TrafficZoneData(
            zone='TAP-WEST',
            count=west_count,
            percentage=round((west_count / total_transactions) * 100, 1)
        )
    ]

    # 1.4 Balance Direction per Zone
    balance_direction = []
    for zone_data in traffic_by_zone:
        zone_name = zone_data.zone.replace('TAP-', '')
        for direction in ['IN', 'OUT']:
            count = int(zone_data.count * random.uniform(0.45, 0.55))
            percentage = round((count / zone_data.count) * 100, 1)
            balance_direction.append(DirectionBalanceData(
                zone=zone_name,
                direction=direction,
                count=count,
                percentage=percentage
            ))

    # Summary
    morning_peak = sum(t.count for t in traffic_per_hour if 7 <= t.hour <= 9)
    evening_peak = sum(t.count for t in traffic_per_hour if 16 <= t.hour <= 19)
    avg_gate_util = sum(g.utilization_rate for g in gate_utilization) / len(gate_utilization)

    summary = {
        "morning_peak_transactions": morning_peak,
        "morning_peak_percentage": round((morning_peak / total_transactions) * 100, 1),
        "evening_peak_transactions": evening_peak,
        "evening_peak_percentage": round((evening_peak / total_transactions) * 100, 1),
        "avg_gate_utilization_rate": round(avg_gate_util, 2),
        "busiest_gate": max(gate_utilization, key=lambda x: x.count).gate_id,
        "busiest_zone": max(traffic_by_zone, key=lambda x: x.count).zone
    }

    return OperationalEfficiencyResponse(
        date=target_date,
        total_transactions=total_transactions,
        traffic_per_hour=traffic_per_hour,
        gate_utilization=gate_utilization,
        traffic_by_zone=traffic_by_zone,
        balance_direction=balance_direction,
        summary=summary
    )


# ==========================
# ENDPOINTS - KATEGORI 3: PROFIL DEMOGRAFI PENUMPANG
# ==========================

@app.get("/api/v1/demografi", response_model=DemografiResponse, include_in_schema=False)
async def get_demografi(date: Optional[str] = None):
    """
    Kategori 3: Profil Demografi Penumpang
    - 3.1 Distribusi Usia
    - 3.2 Distribusi Pekerjaan
    - 3.3 Distribusi Jenis Kelamin
    - 3.4 Distribusi Stasiun Asal
    """
    target_date = date or get_date()

    # Random daily total passengers
    total_passengers = random.randint(3500, 5000)

    # 3.1 Distribusi Usia
    age_ranges = [
        ('18-24', random.randint(300, 500)),
        ('25-34', random.randint(800, 1200)),
        ('35-44', random.randint(1000, 1500)),
        ('45-54', random.randint(700, 1000)),
        ('55+', random.randint(200, 400))
    ]
    age_distribution = []
    for age_range, base_count in age_ranges:
        count = generate_daily_data(base_count, 0.1)
        age_distribution.append(AgeDistributionData(
            age_range=age_range,
            count=count,
            percentage=round((count / total_passengers) * 100, 1)
        ))

    # 3.2 Distribusi Pekerjaan
    occupations = [
        ('Karyawan Swasta', random.randint(1500, 2200)),
        ('PNS/BUMN', random.randint(600, 900)),
        ('Pelajar/Mahasiswa', random.randint(400, 700)),
        ('Wiraswasta', random.randint(500, 800)),
        ('Wisatawan', random.randint(100, 300))
    ]
    occupation_distribution = []
    for occupation, base_count in occupations:
        count = generate_daily_data(base_count, 0.15)
        occupation_distribution.append(OccupationDistributionData(
            occupation=occupation,
            count=count,
            percentage=round((count / total_passengers) * 100, 1)
        ))

    # 3.3 Distribusi Jenis Kelamin
    pria_count = generate_daily_data(int(total_passengers * 0.52), 0.05)
    wanita_count = total_passengers - pria_count
    gender_distribution = [
        GenderDistributionData(
            gender='Pria',
            count=pria_count,
            percentage=round((pria_count / total_passengers) * 100, 1)
        ),
        GenderDistributionData(
            gender='Wanita',
            count=wanita_count,
            percentage=round((wanita_count / total_passengers) * 100, 1)
        )
    ]

    # 3.4 Distribusi Stasiun Asal
    stations = [
        ('Bekasi', random.randint(700, 1000)),
        ('Cikarang', random.randint(400, 600)),
        ('Depok', random.randint(500, 700)),
        ('Bogor', random.randint(400, 600)),
        ('Tangerang', random.randint(300, 500)),
        ('Sudirman', random.randint(300, 500)),
        ('Karet', random.randint(300, 500)),
        ('Pasar Minggu', random.randint(100, 300)),
        ('Tanah Abang', random.randint(200, 400))
    ]
    origin_station_distribution = []
    for station, base_count in stations:
        count = generate_daily_data(base_count, 0.2)
        origin_station_distribution.append(OriginStationData(
            station=station,
            count=count,
            percentage=round((count / total_passengers) * 100, 1)
        ))

    # Summary
    avg_age = sum(
        (int(age_range.split('-')[0]) + int(age_range.split('-')[1])) / 2
        if '-' in age_range else 60
        for age_range, _ in age_ranges
    ) / len(age_ranges)

    productive_age = sum(a.count for a in age_distribution if a.age_range in ['25-34', '35-44'])
    workers = sum(o.count for o in occupation_distribution if o.occupation in ['Karyawan Swasta', 'PNS/BUMN'])

    summary = {
        "average_age": round(avg_age, 1),
        "productive_age_passengers": productive_age,
        "productive_age_percentage": round((productive_age / total_passengers) * 100, 1),
        "worker_passengers": workers,
        "worker_percentage": round((workers / total_passengers) * 100, 1),
        "dominant_origin_station": max(origin_station_distribution, key=lambda x: x.count).station
    }

    return DemografiResponse(
        date=target_date,
        total_passengers=total_passengers,
        age_distribution=age_distribution,
        occupation_distribution=occupation_distribution,
        gender_distribution=gender_distribution,
        origin_station_distribution=origin_station_distribution,
        summary=summary
    )


# ==========================
# ENDPOINTS - KATEGORI 4: SEGMENTASI PERJALANAN
# ==========================

@app.get("/api/v1/segmentasi-perjalanan", response_model=SegmentasiPerjalananResponse, include_in_schema=False)
async def get_segmentasi_perjalanan(date: Optional[str] = None):
    """
    Kategori 4: Segmentasi Perjalanan
    - 4.1 Distribusi Stasiun Awal
    - 4.2 Direction Distribution
    - 4.3 Waktu Perjalanan
    """
    target_date = date or get_date()

    # Random daily total transactions
    total_transactions = random.randint(4000, 6000)

    # 4.1 Distribusi Stasiun Awal
    stations = [
        ('Bekasi', random.randint(700, 1000)),
        ('Cikarang', random.randint(400, 600)),
        ('Depok', random.randint(500, 700)),
        ('Bogor', random.randint(400, 600)),
        ('Tangerang', random.randint(300, 500)),
        ('Sudirman', random.randint(300, 500)),
        ('Karet', random.randint(300, 500)),
        ('Pasar Minggu', random.randint(100, 300)),
        ('Tanah Abang', random.randint(200, 400))
    ]
    origin_distribution = []
    for station, base_count in stations:
        count = generate_daily_data(base_count, 0.2)
        origin_distribution.append(OriginDistributionData(
            station=station,
            count=count,
            percentage=round((count / total_transactions) * 100, 1)
        ))

    # 4.2 Direction Distribution (IN vs OUT)
    in_count = generate_daily_data(int(total_transactions * 0.51), 0.03)
    out_count = total_transactions - in_count
    direction_distribution = [
        DirectionDistributionData(
            direction='IN',
            count=in_count,
            percentage=round((in_count / total_transactions) * 100, 1)
        ),
        DirectionDistributionData(
            direction='OUT',
            count=out_count,
            percentage=round((out_count / total_transactions) * 100, 1)
        )
    ]

    # 4.3 Waktu Perjalanan (Morning vs Evening vs Off-Peak)
    morning_base = random.randint(1200, 1800)
    evening_base = random.randint(1200, 1800)
    off_peak_base = random.randint(600, 1000)

    time_travel_distribution = [
        TimeTravelData(
            time_segment='Morning (07:00-09:00)',
            count=generate_daily_data(morning_base, 0.15),
            percentage=0
        ),
        TimeTravelData(
            time_segment='Evening (16:00-19:00)',
            count=generate_daily_data(evening_base, 0.15),
            percentage=0
        ),
        TimeTravelData(
            time_segment='Off-Peak',
            count=generate_daily_data(off_peak_base, 0.2),
            percentage=0
        )
    ]

    # Calculate percentages
    for tt in time_travel_distribution:
        tt.percentage = round((tt.count / total_transactions) * 100, 1)

    # Summary
    top_origin = max(origin_distribution, key=lambda x: x.count)
    dominant_direction = max(direction_distribution, key=lambda x: x.count)
    dominant_time = max(time_travel_distribution, key=lambda x: x.count)

    summary = {
        "top_origin_station": top_origin.station,
        "top_origin_count": top_origin.count,
        "top_origin_percentage": top_origin.percentage,
        "dominant_direction": dominant_direction.direction,
        "dominant_time_segment": dominant_time.time_segment,
        "dominant_time_percentage": dominant_time.percentage
    }

    return SegmentasiPerjalananResponse(
        date=target_date,
        total_transactions=total_transactions,
        origin_distribution=origin_distribution,
        direction_distribution=direction_distribution,
        time_travel_distribution=time_travel_distribution,
        summary=summary
    )


# ==========================
# ENDPOINTS - KATEGORI 5: SEGMENTASI LOYALITAS
# ==========================

@app.get("/api/v1/segmentasi-loyaltas", response_model=SegmentasiLoyaltasResponse, include_in_schema=False)
async def get_segmentasi_loyaltas(date: Optional[str] = None):
    """
    Kategori 5: Segmentasi Loyaltas
    - 5.2 Segmentasi Loyaltas
    - 5.3 Loyaltas berdasarkan Pekerjaan
    """
    target_date = date or get_date()

    # Random daily total passengers
    total_passengers = random.randint(3500, 5000)

    # 5.2 Segmentasi Loyaltas
    high_base = random.randint(1200, 1800)
    medium_base = random.randint(1000, 1500)
    low_base = random.randint(800, 1200)

    loyalty_segments = [
        LoyaltySegmentData(
            segment='High Loyalty (≥12x)',
            count=generate_daily_data(high_base, 0.15),
            percentage=0,
            min_freq=12,
            max_freq=14
        ),
        LoyaltySegmentData(
            segment='Medium Loyalty (7-11x)',
            count=generate_daily_data(medium_base, 0.15),
            percentage=0,
            min_freq=7,
            max_freq=11
        ),
        LoyaltySegmentData(
            segment='Low Loyalty (<7x)',
            count=generate_daily_data(low_base, 0.2),
            percentage=0,
            min_freq=1,
            max_freq=6
        )
    ]

    # Calculate percentages
    total_loyalty = sum(ls.count for ls in loyalty_segments)
    for ls in loyalty_segments:
        ls.percentage = round((ls.count / total_loyalty) * 100, 1)

    # 5.3 Loyaltas berdasarkan Pekerjaan
    # Gunakan random.uniform untuk float (avg_frequency)
    occupations_base = [
        ('Karyawan Swasta', round(random.uniform(8.0, 10.0), 1), random.randint(1500, 2200)),
        ('PNS/BUMN', round(random.uniform(8.5, 10.5), 1), random.randint(600, 900)),
        ('Pelajar/Mahasiswa', round(random.uniform(5.0, 7.0), 1), random.randint(400, 700)),
        ('Wiraswasta', round(random.uniform(6.0, 8.0), 1), random.randint(500, 800)),
        ('Wisatawan', round(random.uniform(2.0, 4.0), 1), random.randint(100, 300))
    ]
    loyalty_by_occupation = []
    for occupation, avg_freq, count in occupations_base:
        loyalty_by_occupation.append(LoyaltyByOccupationData(
            occupation=occupation,
            avg_frequency=round(avg_freq + random.uniform(-0.5, 0.5), 1),
            count=generate_daily_data(count, 0.1)
        ))

    # Summary
    high_loyalty = next(ls for ls in loyalty_segments if 'High' in ls.segment)
    loyal_workers = sum(lo.count for lo in loyalty_by_occupation if lo.occupation in ['Karyawan Swasta', 'PNS/BUMN'])
    most_loyal_occupation = max(loyalty_by_occupation, key=lambda x: x.avg_frequency)

    summary = {
        "high_loyalty_count": high_loyalty.count,
        "high_loyalty_percentage": high_loyalty.percentage,
        "loyal_workers_count": loyal_workers,
        "loyal_workers_percentage": round((loyal_workers / total_passengers) * 100, 1),
        "most_loyal_occupation": most_loyal_occupation.occupation,
        "most_loyal_occupation_avg_freq": most_loyal_occupation.avg_frequency
    }

    return SegmentasiLoyaltasResponse(
        date=target_date,
        total_passengers=total_passengers,
        loyalty_segments=loyalty_segments,
        loyalty_by_occupation=loyalty_by_occupation,
        summary=summary
    )


# ==========================
# ENDPOINTS - KATEGORI KORELASI BEHAVIOR
# ==========================

@app.get("/api/v1/behavior-correlation", response_model=BehaviorCorrelationResponse, include_in_schema=False)
async def get_behavior_correlation(date: Optional[str] = None):
    """
    Kategori Korelasi Behavior - Analisis hubungan antar variabel
    - 6.1 Usia vs Frekuensi Loyalty
    - 6.2 Distribusi Gender per Jam
    - 6.3 Preferensi Zone berdasarkan Pekerjaan
    """
    target_date = date or get_date()

    # 6.1 Usia vs Frekuensi Loyalty
    # Pola: usia lebih tinggi cenderung lebih loyal
    age_loyalty_correlation = []
    age_groups = [
        (22, 6.5),  # Usia muda (22-28)
        (28, 7.2),  # Young adult (29-35)
        (35, 8.5),  # Mid adult (36-45)
        (45, 9.0),  # Mature (46-55)
        (55, 7.0)   # Senior (56+)
    ]
    for age, base_freq in age_groups:
        count = generate_daily_data(random.randint(400, 800), 0.2)
        avg_freq = round(base_freq + random.uniform(-1.0, 1.0), 1)
        age_loyalty_correlation.append(AgeLoyaltyCorrelationData(
            age=age,
            avg_loyalty_frequency=avg_freq,
            count=count
        ))

    
    hour_gender_distribution = []
    for hour in range(6, 23):
    
        base_count = random.randint(50, 600)
        if 6 <= hour <= 11:
            pria_pct = 0.55 + random.uniform(-0.05, 0.05)  # 50-60%
        elif 16 <= hour <= 19:
            pria_pct = 0.45 + random.uniform(-0.05, 0.05)  # 40-50%
        else:
            pria_pct = 0.50 + random.uniform(-0.05, 0.05)  # ~50%

        total = generate_daily_data(base_count, 0.15)
        pria_count = int(total * pria_pct)
        wanita_count = total - pria_count

        hour_gender_distribution.append(HourGenderData(
            hour=hour,
            pria_count=pria_count,
            wanita_count=wanita_count,
            pria_percentage=round((pria_count / total) * 100, 1),
            wanita_percentage=round((wanita_count / total) * 100, 1)
        ))

    # 6.3 Preferensi Zone berdasarkan Pekerjaan
    # Pola: PNS/BUMN prefer North (dekat kantor), Wisatawan prefer West (dekat area komersial)
    occupation_zone_base = [
        ('Karyawan Swasta', 0.52, 0.48),   # Sedikit prefer North
        ('PNS/BUMN', 0.60, 0.40),        # Jelas prefer North
        ('Pelajar/Mahasiswa', 0.48, 0.52),  # Sedikit prefer West
        ('Wiraswasta', 0.50, 0.50),        # Seimbang
        ('Wisatawan', 0.35, 0.65)         # Prefer West (area komersial)
    ]

    occupation_zone_preference = []
    for occupation, north_ratio, west_ratio in occupation_zone_base:
        total = generate_daily_data(random.randint(200, 1000), 0.2)
        north_count = int(total * north_ratio)
        west_count = total - north_count

        # Tentukan preference
        if north_ratio > 0.55:
            pref = 'North'
        elif west_ratio > 0.55:
            pref = 'West'
        else:
            pref = 'Neutral'

        occupation_zone_preference.append(OccupationZonePreferenceData(
            occupation=occupation,
            north_count=north_count,
            west_count=west_count,
            preference=pref
        ))

    # Summary
    # Hitung korelasi usia vs loyalty
    avg_young_loyalty = sum(item.avg_loyalty_frequency * item.count for item in age_loyalty_correlation[:2])
    avg_young_count = sum(item.count for item in age_loyalty_correlation[:2])
    young_avg = avg_young_loyalty / avg_young_count if avg_young_count > 0 else 0

    avg_senior_loyalty = sum(item.avg_loyalty_frequency * item.count for item in age_loyalty_correlation[3:])
    avg_senior_count = sum(item.count for item in age_loyalty_correlation[3:])
    senior_avg = avg_senior_loyalty / avg_senior_count if avg_senior_count > 0 else 0

    summary = {
        "age_loyalty_insight": "Positif" if senior_avg > young_avg else "Negatif/Netral",
        "young_avg_loyalty": round(young_avg, 1),
        "senior_avg_loyalty": round(senior_avg, 1),
        "dominant_gender_morning": "Pria" if hour_gender_distribution[1].pria_percentage > 50 else "Wanita",
        "dominant_gender_evening": "Pria" if hour_gender_distribution[14].pria_percentage > 50 else "Wanita",
        "strong_zone_preference_count": sum(1 for item in occupation_zone_preference if item.preference != 'Neutral')
    }

    return BehaviorCorrelationResponse(
        date=target_date,
        age_loyalty_correlation=age_loyalty_correlation,
        hour_gender_distribution=hour_gender_distribution,
        occupation_zone_preference=occupation_zone_preference,
        summary=summary
    )


# ==========================
# ENDPOINTS - COMBINED DATA
# ==========================

@app.get("/api/v1/all-data")
async def get_all_data(date: Optional[str] = None):
    """
    Get all analysis data in one request
    Struktur JSON diorganisir agar mudah dibaca frontend
    Semua keys sudah diubah ke Bahasa Indonesia
    """
    target_date = date or get_date()

    # Fetch semua data
    ops_eff_raw = await get_operational_efficiency(target_date)
    demog_raw = await get_demografi(target_date)
    seg_perj_raw = await get_segmentasi_perjalanan(target_date)
    seg_loy_raw = await get_segmentasi_loyaltas(target_date)
    beh_corr_raw = await get_behavior_correlation(target_date)

    # Convert ke dict lalu transform keys ke bahasa Indonesia
    ops_eff = ops_eff_raw.model_dump()
    demog = demog_raw.model_dump()
    seg_perj = seg_perj_raw.model_dump()
    seg_loy = seg_loy_raw.model_dump()
    beh_corr = beh_corr_raw.model_dump()

    
    def transform_ops_eff_keys(data):
        
        total_transaksi = data["total_transactions"]
        morning_pct = data["summary"]["morning_peak_percentage"]
        evening_pct = data["summary"]["evening_peak_percentage"]
        avg_util = data["summary"]["avg_gate_utilization_rate"]

        # Identify traffic pattern
        if morning_pct > 35:
            pola_trafik = "morning_peak"
        elif evening_pct > 35:
            pola_trafik = "evening_peak"
        else:
            pola_trafik = "neutral"

        # Gate balance analysis
        gate_utils = [g["utilization_rate"] for g in data["gate_utilization"]]
        min_util = min(gate_utils)
        max_util = max(gate_utils)
        selisih_util = max_util - min_util

        if selisih_util > 15:
            keseimbangan_gate = "tidak_seimbang"
            rekomendasi_gate = "Re-allocate petugas dari gate sepi ke gate sibuk"
        else:
            keseimbangan_gate = "seimbang"
            rekomendasi_gate = "Distribusi petugas sudah optimal"

        # Peak hours insight
        total_peak = morning_pct + evening_pct
        if total_peak > 65:
            intensitas_peak = "sangat_tinggi"
        elif total_peak > 50:
            intensitas_peak = "tinggi"
        else:
            intensitas_peak = "sedang"

        return {
            "tanggal": data["date"],
            "total_transaksi": data["total_transactions"],
            "trafik_per_jam": [
                {"jam": t["hour"], "jumlah": t["count"], "periode": t["period"]}
                for t in data["traffic_per_hour"]
            ],
            "penggunaan_gate": [
                {"gate_id": g["gate_id"], "zona": g["zone"], "jumlah": g["count"],
                 "tingkat_utilisasi": g["utilization_rate"]}
                for g in data["gate_utilization"]
            ],
            "trafik_per_zona": [
                {"zona": z["zone"], "jumlah": z["count"], "persentase": z["percentage"]}
                for z in data["traffic_by_zone"]
            ],
            "keseimbangan_arah": [
                {"zona": b["zone"], "arah": b["direction"], "jumlah": b["count"],
                 "persentase": b["percentage"]}
                for b in data["balance_direction"]
            ],
            "ringkasan": {
                "transaksi_pagi": data["summary"]["morning_peak_transactions"],
                "persentase_pagi": data["summary"]["morning_peak_percentage"],
                "transaksi_sore": data["summary"]["evening_peak_transactions"],
                "persentase_sore": data["summary"]["evening_peak_percentage"],
                "rata_utilisasi_gate": data["summary"]["avg_gate_utilization_rate"],
                "gate_tertersibuk": data["summary"]["busiest_gate"],
                "zona_tertersibuk": data["summary"]["busiest_zone"]
            },
            "insight_ai": {
                "pola_trafik": pola_trafik,
                "intensitas_peak": intensitas_peak,
                "keseimbangan_gate": keseimbangan_gate,
                "rekomendasi_optimalisasi": rekomendasi_gate,
                "analisis_detail": f"Trafik pagi {morning_pct:.1f}% dan sore {evening_pct:.1f}% dari total transaksi. Rata-rata utilisasi gate {avg_util:.1f}%. {rekomendasi_gate}"
            },
            "rekomendasi_operasi": [
                f"1. Shift petugas dari gate sepi (jam off-peak) ke gate sibuk untuk optimalisasi",
                f"2. Tambah gate darurat saat peak hours untuk mengurangi antrean",
                f"3. Implement queue system baris dengan kapasitas maksimal 200 orang per baris"
            ],
            "rekomendasi_strategis": [
                f"Morning: Prioritaskan penangan cepat (coffee grab, breakfast set) untuk komuter pagi",
                f"Evening: Focus ke retail & family services (makan malam, grocery) untuk komuter sore",
                f"Off-Peak: Gunakan flash sale & special promo untuk menarik trafik di jam sepi"
            ]
        }

    def transform_demog_keys(data):
        # AI Insights: Analisis demografi penumpang yang lebih actionable
        productive_pct = data["summary"]["productive_age_percentage"]
        worker_pct = data["summary"]["worker_percentage"]

        # Segmentasi pasar utama
        if productive_pct > 60:
            segmen_pasar_utama = "Usia Produktif Dominan"
        elif worker_pct > 70:
            segmen_pasar_utama = "Pekerja Dominan"
        else:
            segmen_pasar_utama = "Campuran Beragam"

        # Rasio gender
        gender_data = data["gender_distribution"]
        pria_pct = next(g["percentage"] for g in gender_data if g["gender"] == "Pria")
        wanita_pct = next(g["percentage"] for g in gender_data if g["gender"] == "Wanita")
        rasio_gender = "Seimbang" if abs(pria_pct - wanita_pct) < 10 else ("Pria Dominan" if pria_pct > wanita_pct else "Wanita Dominan")

        # Stasiun asal utama
        origin_stations = data["origin_station_distribution"]
        top_3_stations = sorted(origin_stations, key=lambda x: x["count"], reverse=True)[:3]
        stasiun_prioritas = ", ".join([s["station"] for s in top_3_stations])

        # Rasio usia produktif vs non-produktif
        productive_count = data["summary"]["productive_age_passengers"]
        non_productive = data["total_passengers"] - productive_count
        rasio_usia = (productive_count / non_productive * 100) if non_productive > 0 else 0

        return {
            "tanggal": data["date"],
            "total_penumpang": data["total_passengers"],
            "distribusi_usia": [
                {"rentang_usia": a["age_range"], "jumlah": a["count"], "persentase": a["percentage"]}
                for a in data["age_distribution"]
            ],
            "distribusi_pekerjaan": [
                {"pekerjaan": o["occupation"], "jumlah": o["count"], "persentase": o["percentage"]}
                for o in data["occupation_distribution"]
            ],
            "distribusi_gender": [
                {"gender": g["gender"], "jumlah": g["count"], "persentase": g["percentage"]}
                for g in data["gender_distribution"]
            ],
            "distribusi_stasiun_asal": [
                {"stasiun": s["station"], "jumlah": s["count"], "persentase": s["percentage"]}
                for s in data["origin_station_distribution"]
            ],
            "ringkasan": {
                "rata_usia": data["summary"]["average_age"],
                "penumpang_usia_produktif": data["summary"]["productive_age_passengers"],
                "persentase_usia_produktif": data["summary"]["productive_age_percentage"],
                "penumpang_pekerja": data["summary"]["worker_passengers"],
                "persentase_pekerja": data["summary"]["worker_percentage"],
                "stasiun_asal_dominan": data["summary"]["dominant_origin_station"]
            },
            "insight_ai": {
                "profil_penumpang": f"Rata-rata {data['summary']['average_age']:.1f} tahun dengan {productive_pct:.0f}% usia produktif (25-45 tahun)",
                "rasio_demografi": f"{rasio_gender} - {pria_pct:.0f}% pria vs {wanita_pct:.0f}% wanita",
                "stasiun_prioritas": stasiun_prioritas,
                "analisis_peluang": f"Rasio usia produktif vs non-produktif {rasio_usia:.0f}% menunjukkan potensi revenue yang tinggi",
                "target_promosi_utama": f"1. F&B: {wanita_pct:.0f}% (target: wanita pekerja & keluarga), 2. Retail: {pria_pct:.0f}% (target: pria pekerja), 3. Services: {worker_pct:.0f}% (target: PNS/BUMN)",
                "fasilitas_prioritas": f"Toilet/musholla perlu dialokasi berdasarkan dominasi gender di setiap zona"
            },
            "rekomendasi_operasional": [
                "1. Zone-based advertising: Promosikan F&B di area NORTH (wanita), retail di area WEST (pria)",
                "2. Partnership dengan perusahaan di 3 stasiun teratas: Bekasi, Cikarang, Depok",
                "3. Employee shuttle service untuk penumpang usia produktif pagi-sore",
                "4. Digital signage berbahasa Indonesia di zona utama"
            ]
        }

    def transform_seg_perj_keys(data):
        # AI Insights: Analisis pola perjalanan penumpang yang lebih actionable
        dir_data = data["direction_distribution"]
        in_pct = next(d["percentage"] for d in dir_data if d["direction"] == "IN")
        out_pct = next(d["percentage"] for d in dir_data if d["direction"] == "OUT")

        time_data = data["time_travel_distribution"]
        morning_pct = next(t["percentage"] for t in time_data if "Morning" in t["time_segment"])
        evening_pct = next(t["percentage"] for t in time_data if "Evening" in t["time_segment"])

        # Rekomendasi stasiun
        origin_stations = data["origin_distribution"]
        top_stations = sorted(origin_stations, key=lambda x: x["count"], reverse=True)[:3]

        return {
            "tanggal": data["date"],
            "total_transaksi": data["total_transactions"],
            "distribusi_stasiun_awal": [
                {"stasiun": s["station"], "jumlah": s["count"], "persentase": s["percentage"]}
                for s in data["origin_distribution"]
            ],
            "distribusi_arah": [
                {"arah": d["direction"], "jumlah": d["count"], "persentase": d["percentage"]}
                for d in data["direction_distribution"]
            ],
            "distribusi_waktu_perjalanan": [
                {"segmen_waktu": t["time_segment"], "jumlah": t["count"], "persentase": t["percentage"]}
                for t in data["time_travel_distribution"]
            ],
            "ringkasan": {
                "stasiun_asal_terbanyak": data["summary"]["top_origin_station"],
                "jumlah_stasiun_asal": data["summary"]["top_origin_count"],
                "persentase_stasiun_asal": data["summary"]["top_origin_percentage"],
                "arah_dominan": data["summary"]["dominant_direction"],
                "segmen_waktu_dominan": data["summary"]["dominant_time_segment"],
                "persentase_waktu_dominan": data["summary"]["dominant_time_percentage"]
            },
            "insight_ai": {
                "pola_perjalanan": f"Pola perjalanan: {in_pct:.1f}% IN, {out_pct:.1f}% OUT. Waktu dominan: {time_data[0]['time_segment'] if time_data else 'N/A'}",
                "tipe_penumpang": "Komuter harian (2-way)" if in_pct > 40 and out_pct > 40 else "Pengguna sekali jalan",
                "rekomendasi_kapasitas": f"Kapasitas KRL saat peak: ~200-250 penumpang per 5 menit. Pertimbangkan tambah 1-2 KRL saat peak hours",
                "analisis_origin": f"Top 3 stasiun asal: {', '.join([s['station'] for s in top_stations])} menyumbang {sum(s['count'] for s in top_stations)} transaksi"
            },
            "rekomendasi_operasional": [
                f"1. Increase KRL frequency saat peak hours (07:00-09:00 dan 16:00-19:00)",
                f"2. Single-journey ticket promo untuk off-peak riders (10:00-16:00 dan 19:00-22:00)",
                f"3. Coordinate dengan stasiun asal untuk thru-ticket promo",
                f"4. Real-time crowding indicator di area tap-in untuk distribusi penumpang"
            ],
            "rekomendasi_strategis": [
                f"Morning: Prioritaskan penangan cepat (coffee grab, breakfast set) untuk komuter pagi",
                f"Evening: Focus ke retail & family services (makan malam, grocery) untuk komuter sore",
                f"Off-Peak: Gunakan flash sale & special promo untuk menarik trafik di jam sepi"
            ]
        }

    def transform_seg_loy_keys(data):
        # AI Insights: Analisis segmentasi loyalitas penumpang
        seg_data = data["loyalty_segments"]
        high_seg = next(s for s in seg_data if "High" in s["segment"])
        med_seg = next(s for s in seg_data if "Medium" in s["segment"])
        low_seg = next(s for s in seg_data if "Low" in s["segment"])

        high_loy = high_seg["percentage"]
        med_loy = med_seg["percentage"]
        low_loy = low_seg["percentage"]
        high_count = high_seg["count"]
        med_count = med_seg["count"]
        low_count = low_seg["count"]

        # Analisis strategi loyalitas
        if high_loy > 40:
            strategi_loyal = "Fokus retensi penumpang high loyalty"
            rekomendasi_high = "Tiered membership program dengan exclusive benefits (priority access, discount)"
        elif high_loy > 30:
            strategi_loyal = "Kombinasi retensi & akuisisi"
            rekomendasi_high = "Loyalty rewards + first-time promo untuk low loyalty"
        else:
            strategi_loyal = "Fokus akuisisi & upgrade"
            rekomendasi_high = "Agresive acquisition campaign + upgrade program medium ke high"

        # Occupasi paling loyal
        occ_loy = data["loyalty_by_occupation"]
        most_loyal = max(occ_loy, key=lambda x: x["avg_frequency"])
        most_loyal_occ = most_loyal["occupation"]
        most_loyal_freq = most_loyal["avg_frequency"]

        total_penumpang = data["total_passengers"]

        return {
            "tanggal": data["date"],
            "total_penumpang": data["total_passengers"],
            "segmentasi_loyal": [
                {"segmen": s["segment"], "jumlah": s["count"], "persentase": s["percentage"],
                 "frekuensi_min": s["min_freq"], "frekuensi_max": s["max_freq"]}
                for s in data["loyalty_segments"]
            ],
            "loyal_berdasarkan_pekerjaan": [
                {"pekerjaan": o["occupation"], "jumlah_penumpang": o["count"],
                 "rata_frekuensi": o["avg_frequency"], "persentase_dari_total": round((o["count"] / total_penumpang) * 100, 1)}
                for o in data["loyalty_by_occupation"]
            ],
            "ringkasan": {
                "persentase_loyal_tinggi": high_loy,
                "persentase_loyal_sedang": med_loy,
                "persentase_loyal_rendah": low_loy,
                "jumlah_loyal_tinggi": high_count,
                "jumlah_loyal_sedang": med_count,
                "jumlah_loyal_rendah": low_count,
                "pekerjaan_paling_loyal": data["summary"]["most_loyal_occupation"],
                "frekuensi_loyal_tertinggi": data["summary"]["most_loyal_occupation_avg_freq"]
            },
            "insight_ai": {
                "strategi_loyal": strategi_loyal,
                "profil_loyal": f"High: {high_loy:.1f}% ({high_count} penumpang), Medium: {med_loy:.1f}% ({med_count} penumpang), Low: {low_loy:.1f}% ({low_count} penumpang)",
                "pekerjaan_tertinggi": f"{most_loyal_occ} dengan rata-rata {most_loyal_freq:.1f}x/minggu",
                "rekomendasi_high": rekomendasi_high,
                "rekomendasi_medium": f"Upgrade program: Target {med_count} penumpang Medium untuk naik ke High tier",
                "rekomendasi_low": f"Acquisition campaign: Target {low_count} penumpang Low dengan first-time promo & welcome discount"
            },
            "rekomendasi_operasional": [
                f"1. Implement tiered membership: Bronze (Low), Silver (Medium), Gold (High)",
                f"2. Gold members: Priority access, lounge access, 20% retail discount",
                f"3. Silver members: 10% discount, double points promo",
                f"4. Bronze members: Welcome discount, first 3 rides promo points"
            ],
            "rekomendasi_strategis": [
                f"Partnership B2B dengan perusahaan dominan ({most_loyal_occ}) untuk bulk loyalty program",
                f"Loyalty points redemption di station facilities (F&B, retail)",
                f"Referral bonus: High loyalty members yang berhasil ajak teman dapat bonus points",
                f"Seasonal campaign: Double points pada off-peak hours untuk mengurangi crowd peak"
            ]
        }

    def transform_beh_corr_keys(data):
        # AI Insights: Analisis korelasi perilaku penumpang
        age_data = data["age_loyalty_correlation"]
        young_avg = sum(a["avg_loyalty_frequency"] for a in age_data if a["age"] < 30) / len([a for a in age_data if a["age"] < 30])
        senior_avg = sum(a["avg_loyalty_frequency"] for a in age_data if a["age"] >= 45) / len([a for a in age_data if a["age"] >= 45])
        korelasi_usia = "Positif" if senior_avg > young_avg else ("Negatif" if abs(senior_avg - young_avg) > 0.5 else "Netral")

        # Gender pattern per jam
        hour_gender = data["hour_gender_distribution"]
        morning_hours = [h for h in hour_gender if 6 <= h["hour"] <= 11]
        evening_hours = [h for h in hour_gender if 16 <= h["hour"] <= 19]

        morning_pria = sum(h["pria_count"] for h in morning_hours)
        morning_wanita = sum(h["wanita_count"] for h in morning_hours)
        morning_gender_dom = "Pria" if morning_pria > morning_wanita else "Wanita"

        evening_pria = sum(h["pria_count"] for h in evening_hours)
        evening_wanita = sum(h["wanita_count"] for h in evening_hours)
        evening_gender_dom = "Wanita" if evening_wanita > evening_pria else "Pria"

        # Zone preference analysis
        zone_prefs = data["occupation_zone_preference"]
        strong_prefs = [z for z in zone_prefs if z["preference"] != "Neutral"]
        jumlah_preferensi_kuat = len(strong_prefs)

        return {
            "tanggal": data["date"],
            "korelasi_usia_loyal": [
                {"usia": a["age"], "rata_loyal": a["avg_loyalty_frequency"],
                 "jumlah": a["count"]}
                for a in data["age_loyalty_correlation"]
            ],
            "distribusi_gender_per_jam": [
                {"jam": h["hour"], "jumlah_pria": h["pria_count"],
                 "jumlah_wanita": h["wanita_count"],
                 "persentase_pria": h["pria_percentage"],
                 "persentase_wanita": h["wanita_percentage"]}
                for h in data["hour_gender_distribution"]
            ],
            "preferensi_zona_pekerjaan": [
                {"pekerjaan": o["occupation"], "jumlah_utara": o["north_count"],
                 "jumlah_barat": o["west_count"], "preferensi": o["preference"]}
                for o in data["occupation_zone_preference"]
            ],
            "ringkasan": {
                "insight_korelasi_usia_loyal": data["summary"]["age_loyalty_insight"],
                "rata_loyal_muda": data["summary"]["young_avg_loyalty"],
                "rata_loyal_senior": data["summary"]["senior_avg_loyalty"],
                "gender_dominan_pagi": data["summary"]["dominant_gender_morning"],
                "gender_dominan_sore": data["summary"]["dominant_gender_evening"],
                "jumlah_preferensi_zona_kuat": data["summary"]["strong_zone_preference_count"]
            },
            "insight_ai": {
                "korelasi_usia": korelasi_usia,
                "pola_gender_waktu": f"Pagi dominan {morning_gender_dom}, sore dominan {evening_gender_dom}",
                "fasilitas_waktu": {
                    "pagi": "Quick service (coffee, breakfast grab)",
                    "sore": "Retail & family-oriented (F&B, pharmacy, kids zone)"
                },
                "analisis_zona": {
                    "pola": f"{jumlah_preferensi_kuat} pekerjaan menunjukkan preferensi zona kuat",
                    "rekomendasi": "PNS/BUMN → North Zone (office services), Wisatawan → West Zone (retail & tourism)"
                },
                "rekomendasi_promosi": {
                    "morning": f"Target {morning_gender_dom} dengan quick breakfast & coffee promo",
                    "sore": f"Target {evening_gender_dom} dengan family meal deals & retail discount"
                }
            }
        }

    # Transform semua data ke bahasa Indonesia
    ops_eff_indo = transform_ops_eff_keys(ops_eff)
    demog_indo = transform_demog_keys(demog)
    seg_perj_indo = transform_seg_perj_keys(seg_perj)
    seg_loy_indo = transform_seg_loy_keys(seg_loy)
    beh_corr_indo = transform_beh_corr_keys(beh_corr)

    # Dashboard Summary - Key metrics untuk Dashboard Utama
    dashboard_summary = {
        "total_transaksi": {
            "nilai": ops_eff_indo['total_transaksi'],
            "label": "Total Transaksi",
            "deskripsi": "Total tap-in dan tap-out hari ini",
            "delta": "Harian"
        },
        "total_penumpang_unik": {
            "nilai": demog_indo['total_penumpang'],
            "label": "Total Penumpang Unik",
            "deskripsi": "Jumlah penumpang unik hari ini",
            "delta": "Unik"
        },
        "high_loyalty_penumpang": {
            "nilai": f"{seg_loy_indo['ringkasan']['persentase_loyal_tinggi']}%",
            "label": "High Loyalty Penumpang",
            "deskripsi": "Persentase penumpang loyal (frekuensi ≥12x/minggu)",
            "delta": "≥12x/minggu",
            "persentase": seg_loy_indo['ringkasan']['persentase_loyal_tinggi']
        },
        "gate_tersibuk": {
            "nilai": ops_eff_indo['ringkasan']['gate_tertersibuk'].replace('TAP-', ''),
            "label": "Gate Tersibuk",
            "deskripsi": "Gate dengan penggunaan tertinggi hari ini",
            "delta": "Highest Utilization",
            "gate_id_full": ops_eff_indo['ringkasan']['gate_tertersibuk']
        },
        "morning_peak_traffic": {
            "nilai": f"{ops_eff_indo['ringkasan']['persentase_pagi']}%",
            "label": "Morning Peak Traffic",
            "deskripsi": "Persentase trafik jam sibuk pagi",
            "delta": "07:00-09:00",
            "persentase": ops_eff_indo['ringkasan']['persentase_pagi']
        },
        "evening_peak_traffic": {
            "nilai": f"{ops_eff_indo['ringkasan']['persentase_sore']}%",
            "label": "Evening Peak Traffic",
            "deskripsi": "Persentase trafik jam sibuk sore",
            "delta": "16:00-19:00",
            "persentase": ops_eff_indo['ringkasan']['persentase_sore']
        },
        "rata_rata_usia": {
            "nilai": f"{demog_indo['ringkasan']['rata_usia']} tahun",
            "label": "Rata-rata Usia",
            "deskripsi": "Usia rata-rata penumpang",
            "delta": "Demografi",
            "usia": demog_indo['ringkasan']['rata_usia']
        },
        "stasiun_asal_dominan": {
            "nilai": seg_perj_indo['ringkasan']['stasiun_asal_terbanyak'],
            "label": "Stasiun Asal Dominan",
            "deskripsi": "Stasiun asal dengan penumpang terbanyak",
            "delta": f"{seg_perj_indo['ringkasan']['persentase_stasiun_asal']}% dari total",
            "persentase": seg_perj_indo['ringkasan']['persentase_stasiun_asal'],
            "stasiun": seg_perj_indo['ringkasan']['stasiun_asal_terbanyak']
        }
    }

    return {
        "tanggal": target_date,
        "dashboard_summary": dashboard_summary,
        "kategori": {
            "efisiensi_operasional": "1️⃣ Operational Efficiency",
            "demografi": "2️⃣ Profil Demografi",
            "segmentasi_perjalanan": "3️⃣ Segmentasi Perjalanan",
            "segmentasi_loyaltas": "4️⃣ Segmentasi Loyaltas",
            "korelasi_perilaku": "5️⃣ Behavior Correlation"
        },
        "data": {
            "efisiensi_operasional": ops_eff_indo,
            "demografi": demog_indo,
            "segmentasi_perjalanan": seg_perj_indo,
            "segmentasi_loyaltas": seg_loy_indo,
            "korelasi_perilaku": beh_corr_indo
        }
    }



@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "aman cuyy",
        "service": "KCI i love you",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8004)
