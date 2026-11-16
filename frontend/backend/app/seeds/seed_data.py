from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.models.station import Station
from backend.app.models.train import Train
from backend.app.models.stop import Stop
from backend.app.models.alert import ServiceAlert
from backend.app.services.auth import get_password_hash

STATIONS_DATA = [
    {"code": "NDLS", "name": "New Delhi", "division": "Delhi", "zone": "NR", "state": "Delhi", "latitude": 28.6429, "longitude": 77.2195, "platforms_count": 16},
    {"code": "MMCT", "name": "Mumbai Central", "division": "Mumbai", "zone": "WR", "state": "Maharashtra", "latitude": 18.9696, "longitude": 72.8194, "platforms_count": 5},
    {"code": "CSMT", "name": "Chhatrapati Shivaji Maharaj Terminus", "division": "Mumbai", "zone": "CR", "state": "Maharashtra", "latitude": 18.9402, "longitude": 72.8358, "platforms_count": 18},
    {"code": "HWH", "name": "Howrah Junction", "division": "Howrah", "zone": "ER", "state": "West Bengal", "latitude": 22.5839, "longitude": 88.3426, "platforms_count": 23},
    {"code": "MAS", "name": "MGR Chennai Central", "division": "Chennai", "zone": "SR", "state": "Tamil Nadu", "latitude": 13.0827, "longitude": 80.2754, "platforms_count": 17},
    {"code": "SBC", "name": "KSR Bengaluru City", "division": "Bengaluru", "zone": "SWR", "state": "Karnataka", "latitude": 12.9781, "longitude": 77.5696, "platforms_count": 10},
    {"code": "PNBE", "name": "Patna Junction", "division": "Danapur", "zone": "ECR", "state": "Bihar", "latitude": 25.6022, "longitude": 85.1376, "platforms_count": 10},
    {"code": "GKP", "name": "Gorakhpur Junction", "division": "Lucknow", "zone": "NER", "state": "Uttar Pradesh", "latitude": 26.7588, "longitude": 83.3853, "platforms_count": 10},
    {"code": "BSB", "name": "Varanasi Junction", "division": "Varanasi", "zone": "NR", "state": "Uttar Pradesh", "latitude": 25.3283, "longitude": 82.9868, "platforms_count": 9},
    {"code": "CNB", "name": "Kanpur Central", "division": "Prayagraj", "zone": "NCR", "state": "Uttar Pradesh", "latitude": 26.4547, "longitude": 80.3507, "platforms_count": 10},
    {"code": "AGC", "name": "Agra Cantt", "division": "Agra", "zone": "NCR", "state": "Uttar Pradesh", "latitude": 27.1593, "longitude": 78.0081, "platforms_count": 6},
    {"code": "GWL", "name": "Gwalior Junction", "division": "Jhansi", "zone": "NCR", "state": "Madhya Pradesh", "latitude": 26.2183, "longitude": 78.1828, "platforms_count": 5},
    {"code": "VGLJ", "name": "Virangana Lakshmibai Jhansi", "division": "Jhansi", "zone": "NCR", "state": "Uttar Pradesh", "latitude": 25.4484, "longitude": 78.5685, "platforms_count": 8},
    {"code": "BPL", "name": "Bhopal Junction", "division": "Bhopal", "zone": "WCR", "state": "Madhya Pradesh", "latitude": 23.2684, "longitude": 77.4126, "platforms_count": 6},
    {"code": "RKMP", "name": "Rani Kamlapati", "division": "Bhopal", "zone": "WCR", "state": "Madhya Pradesh", "latitude": 23.2163, "longitude": 77.4384, "platforms_count": 5},
    {"code": "BRC", "name": "Vadodara Junction", "division": "Vadodara", "zone": "WR", "state": "Gujarat", "latitude": 22.3107, "longitude": 73.1812, "platforms_count": 7},
    {"code": "ST", "name": "Surat", "division": "Mumbai WR", "zone": "WR", "state": "Gujarat", "latitude": 21.2049, "longitude": 72.8407, "platforms_count": 4},
    {"code": "BVI", "name": "Borivali", "division": "Mumbai WR", "zone": "WR", "state": "Maharashtra", "latitude": 19.2288, "longitude": 72.8569, "platforms_count": 10},
    {"code": "KOTA", "name": "Kota Junction", "division": "Kota", "zone": "WCR", "state": "Rajasthan", "latitude": 25.2198, "longitude": 75.8648, "platforms_count": 6},
    {"code": "RTM", "name": "Ratlam Junction", "division": "Ratlam", "zone": "WR", "state": "Madhya Pradesh", "latitude": 23.3441, "longitude": 75.0352, "platforms_count": 7},
    {"code": "ADI", "name": "Ahmedabad Junction", "division": "Ahmedabad", "zone": "WR", "state": "Gujarat", "latitude": 23.0232, "longitude": 72.6009, "platforms_count": 12},
    {"code": "PRYJ", "name": "Prayagraj Junction", "division": "Prayagraj", "zone": "NCR", "state": "Uttar Pradesh", "latitude": 25.4439, "longitude": 81.8252, "platforms_count": 10},
    {"code": "DDU", "name": "Pt. Deen Dayal Upadhyaya Jn", "division": "Danapur", "zone": "ECR", "state": "Uttar Pradesh", "latitude": 25.2818, "longitude": 83.1189, "platforms_count": 8},
    {"code": "MYS", "name": "Mysuru Junction", "division": "Mysuru", "zone": "SWR", "state": "Karnataka", "latitude": 12.3164, "longitude": 76.6437, "platforms_count": 6},
    {"code": "TVC", "name": "Thiruvananthapuram Central", "division": "Thiruvananthapuram", "zone": "SR", "state": "Kerala", "latitude": 8.4875, "longitude": 76.9532, "platforms_count": 5},
    # Western Railway Main Line Stations (Mumbai Central - Ahmedabad Route)
    {"code": "VAPI", "name": "Vapi", "division": "Mumbai WR", "zone": "WR", "state": "Gujarat", "latitude": 20.3714, "longitude": 72.9043, "platforms_count": 3},
    {"code": "BL", "name": "Valsad", "division": "Mumbai WR", "zone": "WR", "state": "Gujarat", "latitude": 20.6101, "longitude": 72.9272, "platforms_count": 5},
    {"code": "BH", "name": "Bharuch Junction", "division": "Vadodara", "zone": "WR", "state": "Gujarat", "latitude": 21.7051, "longitude": 72.9959, "platforms_count": 6},
    {"code": "ANND", "name": "Anand Junction", "division": "Vadodara", "zone": "WR", "state": "Gujarat", "latitude": 22.5645, "longitude": 72.9289, "platforms_count": 5},
    {"code": "ND", "name": "Nadiad Junction", "division": "Vadodara", "zone": "WR", "state": "Gujarat", "latitude": 22.6916, "longitude": 72.8634, "platforms_count": 4},
    {"code": "DDR", "name": "Dadar Western", "division": "Mumbai WR", "zone": "WR", "state": "Maharashtra", "latitude": 19.0178, "longitude": 72.8478, "platforms_count": 7},
    {"code": "PLG", "name": "Palghar", "division": "Mumbai WR", "zone": "WR", "state": "Maharashtra", "latitude": 19.6967, "longitude": 72.7655, "platforms_count": 3},
    {"code": "NVS", "name": "Navsari", "division": "Mumbai WR", "zone": "WR", "state": "Gujarat", "latitude": 20.9467, "longitude": 72.9282, "platforms_count": 3},
    {"code": "AKV", "name": "Ankleshwar Junction", "division": "Vadodara", "zone": "WR", "state": "Gujarat", "latitude": 21.6264, "longitude": 73.0019, "platforms_count": 4},
    {"code": "MAN", "name": "Maninagar", "division": "Ahmedabad", "zone": "WR", "state": "Gujarat", "latitude": 22.9981, "longitude": 72.6033, "platforms_count": 2},
    {"code": "MHD", "name": "Mahemdavad Kheda Road", "division": "Vadodara", "zone": "WR", "state": "Gujarat", "latitude": 22.8258, "longitude": 72.7712, "platforms_count": 2},
    {"code": "MYG", "name": "Miyagam Karjan Junction", "division": "Vadodara", "zone": "WR", "state": "Gujarat", "latitude": 22.0461, "longitude": 73.1235, "platforms_count": 3},
    {"code": "PLJ", "name": "Palej", "division": "Vadodara", "zone": "WR", "state": "Gujarat", "latitude": 21.8492, "longitude": 73.0722, "platforms_count": 2},
    {"code": "KSB", "name": "Kosamba Junction", "division": "Mumbai WR", "zone": "WR", "state": "Gujarat", "latitude": 21.4729, "longitude": 72.9568, "platforms_count": 3},
    {"code": "KIM", "name": "Kim", "division": "Mumbai WR", "zone": "WR", "state": "Gujarat", "latitude": 21.4011, "longitude": 72.9328, "platforms_count": 2},
    {"code": "BIM", "name": "Bilimora Junction", "division": "Mumbai WR", "zone": "WR", "state": "Gujarat", "latitude": 20.7634, "longitude": 72.9641, "platforms_count": 5},
    {"code": "UVD", "name": "Udvada", "division": "Mumbai WR", "zone": "WR", "state": "Gujarat", "latitude": 20.4722, "longitude": 72.9248, "platforms_count": 2},
    {"code": "BLD", "name": "Bhilad", "division": "Mumbai WR", "zone": "WR", "state": "Gujarat", "latitude": 20.2783, "longitude": 72.8808, "platforms_count": 2},
    {"code": "UBR", "name": "Umbergaon Road", "division": "Mumbai WR", "zone": "WR", "state": "Gujarat", "latitude": 20.1836, "longitude": 72.8202, "platforms_count": 2},
    {"code": "DRD", "name": "Dahanu Road", "division": "Mumbai WR", "zone": "WR", "state": "Maharashtra", "latitude": 19.9734, "longitude": 72.7384, "platforms_count": 3},
    {"code": "BOR", "name": "Boisar", "division": "Mumbai WR", "zone": "WR", "state": "Maharashtra", "latitude": 19.8005, "longitude": 72.7561, "platforms_count": 3}
]

TRAINS_DATA = [
    {
        "train_number": "12951",
        "train_name": "Mumbai Tejas Rajdhani Express",
        "train_type": "Rajdhani",
        "source_station_code": "MMCT",
        "destination_station_code": "NDLS",
        "running_days": "1111111",
        "total_distance_km": 1384.0,
        "duration_minutes": 932,
        "classes": ["1A", "2A", "3A"],
        "pantry_car": True,
        "return_train_number": "12952",
        "stops": [
            {"station_code": "MMCT", "seq": 1, "arr": None, "dep": "17:00", "halt": 0, "dist": 0.0, "day": 1, "plat": "1"},
            {"station_code": "BVI", "seq": 2, "arr": "17:22", "dep": "17:24", "halt": 2, "dist": 30.0, "day": 1, "plat": "6"},
            {"station_code": "ST", "seq": 3, "arr": "19:43", "dep": "19:48", "halt": 5, "dist": 263.0, "day": 1, "plat": "1"},
            {"station_code": "BRC", "seq": 4, "arr": "21:14", "dep": "21:27", "halt": 13, "dist": 392.0, "day": 1, "plat": "2"},
            {"station_code": "RTM", "seq": 5, "arr": "00:25", "dep": "00:28", "halt": 3, "dist": 653.0, "day": 2, "plat": "5"},
            {"station_code": "KOTA", "seq": 6, "arr": "03:15", "dep": "03:20", "halt": 5, "dist": 920.0, "day": 2, "plat": "1"},
            {"station_code": "NDLS", "seq": 7, "arr": "08:32", "dep": None, "halt": 0, "dist": 1384.0, "day": 2, "plat": "1"}
        ]
    },
    {
        "train_number": "12952",
        "train_name": "New Delhi - Mumbai Tejas Rajdhani Express",
        "train_type": "Rajdhani",
        "source_station_code": "NDLS",
        "destination_station_code": "MMCT",
        "running_days": "1111111",
        "total_distance_km": 1384.0,
        "duration_minutes": 935,
        "classes": ["1A", "2A", "3A"],
        "pantry_car": True,
        "return_train_number": "12951",
        "stops": [
            {"station_code": "NDLS", "seq": 1, "arr": None, "dep": "16:55", "halt": 0, "dist": 0.0, "day": 1, "plat": "3"},
            {"station_code": "KOTA", "seq": 2, "arr": "21:30", "dep": "21:40", "halt": 10, "dist": 465.0, "day": 1, "plat": "1"},
            {"station_code": "RTM", "seq": 3, "arr": "00:30", "dep": "00:33", "halt": 3, "dist": 732.0, "day": 2, "plat": "4"},
            {"station_code": "BRC", "seq": 4, "arr": "03:45", "dep": "03:55", "halt": 10, "dist": 992.0, "day": 2, "plat": "3"},
            {"station_code": "ST", "seq": 5, "arr": "05:13", "dep": "05:18", "halt": 5, "dist": 1122.0, "day": 2, "plat": "2"},
            {"station_code": "BVI", "seq": 6, "arr": "07:40", "dep": "07:42", "halt": 2, "dist": 1354.0, "day": 2, "plat": "7"},
            {"station_code": "MMCT", "seq": 7, "arr": "08:35", "dep": None, "halt": 0, "dist": 1384.0, "day": 2, "plat": "1"}
        ]
    },
    # 22961: Mumbai Central - Ahmedabad Vande Bharat Express
    {
        "train_number": "22961",
        "train_name": "Mumbai Central - Ahmedabad Vande Bharat Express",
        "train_type": "Vande Bharat",
        "source_station_code": "MMCT",
        "destination_station_code": "ADI",
        "running_days": "1111110",  # Monday to Saturday (except Sunday)
        "total_distance_km": 491.0,
        "duration_minutes": 330,  # 5h 30m
        "classes": ["EC", "CC"],
        "pantry_car": True,
        "return_train_number": "22962",
        "stops": [
            {"station_code": "MMCT", "seq": 1, "arr": None, "dep": "15:45", "halt": 0, "dist": 0.0, "day": 1, "plat": "5"},
            {"station_code": "BVI", "seq": 2, "arr": "16:10", "dep": "16:13", "halt": 3, "dist": 30.0, "day": 1, "plat": "6"},
            {"station_code": "VAPI", "seq": 3, "arr": "17:40", "dep": "17:42", "halt": 2, "dist": 168.0, "day": 1, "plat": "1"},
            {"station_code": "ST", "seq": 4, "arr": "18:38", "dep": "18:43", "halt": 5, "dist": 263.0, "day": 1, "plat": "1"},
            {"station_code": "BRC", "seq": 5, "arr": "20:07", "dep": "20:10", "halt": 3, "dist": 392.0, "day": 1, "plat": "2"},
            {"station_code": "ADI", "seq": 6, "arr": "21:15", "dep": None, "halt": 0, "dist": 491.0, "day": 1, "plat": "1"}
        ]
    },
    # 22962: Ahmedabad - Mumbai Central Vande Bharat Express
    {
        "train_number": "22962",
        "train_name": "Ahmedabad - Mumbai Central Vande Bharat Express",
        "train_type": "Vande Bharat",
        "source_station_code": "ADI",
        "destination_station_code": "MMCT",
        "running_days": "1111110",  # Monday to Saturday (except Sunday)
        "total_distance_km": 491.0,
        "duration_minutes": 340,  # 5h 40m
        "classes": ["EC", "CC"],
        "pantry_car": True,
        "return_train_number": "22961",
        "stops": [
            {"station_code": "ADI", "seq": 1, "arr": None, "dep": "06:05", "halt": 0, "dist": 0.0, "day": 1, "plat": "1"},
            {"station_code": "BRC", "seq": 2, "arr": "06:55", "dep": "06:58", "halt": 3, "dist": 99.0, "day": 1, "plat": "2"},
            {"station_code": "ST", "seq": 3, "arr": "08:15", "dep": "08:20", "halt": 5, "dist": 228.0, "day": 1, "plat": "1"},
            {"station_code": "VAPI", "seq": 4, "arr": "09:13", "dep": "09:15", "halt": 2, "dist": 323.0, "day": 1, "plat": "2"},
            {"station_code": "BVI", "seq": 5, "arr": "10:43", "dep": "10:45", "halt": 2, "dist": 461.0, "day": 1, "plat": "7"},
            {"station_code": "MMCT", "seq": 6, "arr": "11:45", "dep": None, "halt": 0, "dist": 491.0, "day": 1, "plat": "5"}
        ]
    },
    # 22954: Gujarat Superfast Express (ADI -> MMCT)
    {
        "train_number": "22954",
        "train_name": "Gujarat Superfast Express",
        "train_type": "Superfast",
        "source_station_code": "ADI",
        "destination_station_code": "MMCT",
        "running_days": "1111111",  # Daily
        "total_distance_km": 491.0,
        "duration_minutes": 534,  # 8h 54m
        "classes": ["CC", "2S", "SL"],
        "pantry_car": False,
        "return_train_number": "22953",
        "stops": [
            {"station_code": "ADI", "seq": 1, "arr": None, "dep": "07:10", "halt": 0, "dist": 0.0, "day": 1, "plat": "3"},
            {"station_code": "MAN", "seq": 2, "arr": "07:20", "dep": "07:22", "halt": 2, "dist": 3.0, "day": 1, "plat": "2"},
            {"station_code": "MHD", "seq": 3, "arr": "07:42", "dep": "07:44", "halt": 2, "dist": 28.0, "day": 1, "plat": "1"},
            {"station_code": "ND", "seq": 4, "arr": "07:58", "dep": "08:00", "halt": 2, "dist": 46.0, "day": 1, "plat": "1"},
            {"station_code": "ANND", "seq": 5, "arr": "08:16", "dep": "08:18", "halt": 2, "dist": 65.0, "day": 1, "plat": "4"},
            {"station_code": "BRC", "seq": 6, "arr": "08:58", "dep": "09:03", "halt": 5, "dist": 100.0, "day": 1, "plat": "3"},
            {"station_code": "MYG", "seq": 7, "arr": "09:28", "dep": "09:30", "halt": 2, "dist": 130.0, "day": 1, "plat": "1"},
            {"station_code": "PLJ", "seq": 8, "arr": "09:42", "dep": "09:44", "halt": 2, "dist": 145.0, "day": 1, "plat": "1"},
            {"station_code": "BH", "seq": 9, "arr": "10:07", "dep": "10:09", "halt": 2, "dist": 171.0, "day": 1, "plat": "4"},
            {"station_code": "AKV", "seq": 10, "arr": "10:20", "dep": "10:22", "halt": 2, "dist": 180.0, "day": 1, "plat": "2"},
            {"station_code": "KSB", "seq": 11, "arr": "10:38", "dep": "10:40", "halt": 2, "dist": 198.0, "day": 1, "plat": "2"},
            {"station_code": "KIM", "seq": 12, "arr": "10:50", "dep": "10:52", "halt": 2, "dist": 206.0, "day": 1, "plat": "2"},
            {"station_code": "ST", "seq": 13, "arr": "11:27", "dep": "11:32", "halt": 5, "dist": 230.0, "day": 1, "plat": "2"},
            {"station_code": "NVS", "seq": 14, "arr": "11:58", "dep": "12:00", "halt": 2, "dist": 259.0, "day": 1, "plat": "2"},
            {"station_code": "BIM", "seq": 15, "arr": "12:20", "dep": "12:22", "halt": 2, "dist": 280.0, "day": 1, "plat": "2"},
            {"station_code": "BL", "seq": 16, "arr": "12:45", "dep": "12:50", "halt": 5, "dist": 298.0, "day": 1, "plat": "3"},
            {"station_code": "UVD", "seq": 17, "arr": "13:06", "dep": "13:08", "halt": 2, "dist": 314.0, "day": 1, "plat": "2"},
            {"station_code": "VAPI", "seq": 18, "arr": "13:20", "dep": "13:22", "halt": 2, "dist": 324.0, "day": 1, "plat": "2"},
            {"station_code": "BLD", "seq": 19, "arr": "13:34", "dep": "13:36", "halt": 2, "dist": 336.0, "day": 1, "plat": "2"},
            {"station_code": "UBR", "seq": 20, "arr": "13:50", "dep": "13:52", "halt": 2, "dist": 353.0, "day": 1, "plat": "2"},
            {"station_code": "DRD", "seq": 21, "arr": "14:15", "dep": "14:17", "halt": 2, "dist": 373.0, "day": 1, "plat": "2"},
            {"station_code": "BOR", "seq": 22, "arr": "14:31", "dep": "14:33", "halt": 2, "dist": 388.0, "day": 1, "plat": "3"},
            {"station_code": "PLG", "seq": 23, "arr": "14:45", "dep": "14:47", "halt": 2, "dist": 399.0, "day": 1, "plat": "2"},
            {"station_code": "BVI", "seq": 24, "arr": "15:27", "dep": "15:29", "halt": 2, "dist": 457.0, "day": 1, "plat": "7"},
            {"station_code": "DDR", "seq": 25, "arr": "15:52", "dep": "15:54", "halt": 2, "dist": 485.0, "day": 1, "plat": "6"},
            {"station_code": "MMCT", "seq": 26, "arr": "16:04", "dep": None, "halt": 0, "dist": 491.0, "day": 1, "plat": "2"}
        ]
    },
    # 22953: Gujarat Superfast Express (MMCT -> ADI)
    {
        "train_number": "22953",
        "train_name": "Gujarat Superfast Express",
        "train_type": "Superfast",
        "source_station_code": "MMCT",
        "destination_station_code": "ADI",
        "running_days": "1111111",  # Daily
        "total_distance_km": 491.0,
        "duration_minutes": 540,  # 9h 00m
        "classes": ["CC", "2S", "SL"],
        "pantry_car": False,
        "return_train_number": "22954",
        "stops": [
            {"station_code": "MMCT", "seq": 1, "arr": None, "dep": "05:40", "halt": 0, "dist": 0.0, "day": 1, "plat": "2"},
            {"station_code": "DDR", "seq": 2, "arr": "05:49", "dep": "05:52", "halt": 3, "dist": 6.0, "day": 1, "plat": "5"},
            {"station_code": "BVI", "seq": 3, "arr": "06:14", "dep": "06:16", "halt": 2, "dist": 34.0, "day": 1, "plat": "6"},
            {"station_code": "PLG", "seq": 4, "arr": "06:58", "dep": "07:00", "halt": 2, "dist": 92.0, "day": 1, "plat": "1"},
            {"station_code": "BOR", "seq": 5, "arr": "07:11", "dep": "07:13", "halt": 2, "dist": 103.0, "day": 1, "plat": "2"},
            {"station_code": "DRD", "seq": 6, "arr": "07:31", "dep": "07:33", "halt": 2, "dist": 118.0, "day": 1, "plat": "1"},
            {"station_code": "UBR", "seq": 7, "arr": "07:54", "dep": "07:56", "halt": 2, "dist": 138.0, "day": 1, "plat": "1"},
            {"station_code": "BLD", "seq": 8, "arr": "08:10", "dep": "08:12", "halt": 2, "dist": 155.0, "day": 1, "plat": "1"},
            {"station_code": "VAPI", "seq": 9, "arr": "08:24", "dep": "08:26", "halt": 2, "dist": 167.0, "day": 1, "plat": "1"},
            {"station_code": "UVD", "seq": 10, "arr": "08:38", "dep": "08:40", "halt": 2, "dist": 177.0, "day": 1, "plat": "1"},
            {"station_code": "BL", "seq": 11, "arr": "08:58", "dep": "09:03", "halt": 5, "dist": 193.0, "day": 1, "plat": "2"},
            {"station_code": "BIM", "seq": 12, "arr": "09:20", "dep": "09:22", "halt": 2, "dist": 211.0, "day": 1, "plat": "1"},
            {"station_code": "NVS", "seq": 13, "arr": "09:40", "dep": "09:42", "halt": 2, "dist": 232.0, "day": 1, "plat": "1"},
            {"station_code": "ST", "seq": 14, "arr": "10:20", "dep": "10:25", "halt": 5, "dist": 261.0, "day": 1, "plat": "1"},
            {"station_code": "KIM", "seq": 15, "arr": "10:48", "dep": "10:50", "halt": 2, "dist": 285.0, "day": 1, "plat": "1"},
            {"station_code": "KSB", "seq": 16, "arr": "11:00", "dep": "11:02", "halt": 2, "dist": 293.0, "day": 1, "plat": "1"},
            {"station_code": "AKV", "seq": 17, "arr": "11:18", "dep": "11:20", "halt": 2, "dist": 311.0, "day": 1, "plat": "1"},
            {"station_code": "BH", "seq": 18, "arr": "11:32", "dep": "11:34", "halt": 2, "dist": 320.0, "day": 1, "plat": "3"},
            {"station_code": "PLJ", "seq": 19, "arr": "11:58", "dep": "12:00", "halt": 2, "dist": 346.0, "day": 1, "plat": "2"},
            {"station_code": "MYG", "seq": 20, "arr": "12:13", "dep": "12:15", "halt": 2, "dist": 361.0, "day": 1, "plat": "3"},
            {"station_code": "BRC", "seq": 21, "arr": "12:45", "dep": "12:50", "halt": 5, "dist": 391.0, "day": 1, "plat": "2"},
            {"station_code": "ANND", "seq": 22, "arr": "13:28", "dep": "13:30", "halt": 2, "dist": 426.0, "day": 1, "plat": "3"},
            {"station_code": "ND", "seq": 23, "arr": "13:46", "dep": "13:48", "halt": 2, "dist": 445.0, "day": 1, "plat": "2"},
            {"station_code": "MHD", "seq": 24, "arr": "14:03", "dep": "14:05", "halt": 2, "dist": 463.0, "day": 1, "plat": "2"},
            {"station_code": "MAN", "seq": 25, "arr": "14:26", "dep": "14:28", "halt": 2, "dist": 488.0, "day": 1, "plat": "1"},
            {"station_code": "ADI", "seq": 26, "arr": "14:40", "dep": None, "halt": 0, "dist": 491.0, "day": 1, "plat": "3"}
        ]
    },
    {
        "train_number": "22436",
        "train_name": "Vande Bharat Express",
        "train_type": "Vande Bharat",
        "source_station_code": "NDLS",
        "destination_station_code": "BSB",
        "running_days": "1101111",  # Operates 6 days a week (except Thursday)
        "total_distance_km": 759.0,
        "duration_minutes": 480,
        "classes": ["EC", "CC"],
        "pantry_car": True,
        "return_train_number": "22435",
        "stops": [
            {"station_code": "NDLS", "seq": 1, "arr": None, "dep": "06:00", "halt": 0, "dist": 0.0, "day": 1, "plat": "16"},
            {"station_code": "CNB", "seq": 2, "arr": "10:08", "dep": "10:10", "halt": 2, "dist": 440.0, "day": 1, "plat": "1"},
            {"station_code": "PRYJ", "seq": 3, "arr": "12:08", "dep": "12:10", "halt": 2, "dist": 635.0, "day": 1, "plat": "6"},
            {"station_code": "BSB", "seq": 4, "arr": "14:00", "dep": None, "halt": 0, "dist": 759.0, "day": 1, "plat": "1"}
        ]
    },
    {
        "train_number": "22435",
        "train_name": "Varanasi - New Delhi Vande Bharat Express",
        "train_type": "Vande Bharat",
        "source_station_code": "BSB",
        "destination_station_code": "NDLS",
        "running_days": "1101111",
        "total_distance_km": 759.0,
        "duration_minutes": 480,
        "classes": ["EC", "CC"],
        "pantry_car": True,
        "return_train_number": "22436",
        "stops": [
            {"station_code": "BSB", "seq": 1, "arr": None, "dep": "15:00", "halt": 0, "dist": 0.0, "day": 1, "plat": "1"},
            {"station_code": "PRYJ", "seq": 2, "arr": "16:30", "dep": "16:32", "halt": 2, "dist": 124.0, "day": 1, "plat": "6"},
            {"station_code": "CNB", "seq": 3, "arr": "18:30", "dep": "18:32", "halt": 2, "dist": 319.0, "day": 1, "plat": "1"},
            {"station_code": "NDLS", "seq": 4, "arr": "23:00", "dep": None, "halt": 0, "dist": 759.0, "day": 1, "plat": "16"}
        ]
    },
    {
        "train_number": "12002",
        "train_name": "New Delhi - Rani Kamlapati Shatabdi Express",
        "train_type": "Shatabdi",
        "source_station_code": "NDLS",
        "destination_station_code": "RKMP",
        "running_days": "1111111",
        "total_distance_km": 707.0,
        "duration_minutes": 510,
        "classes": ["EC", "CC"],
        "pantry_car": True,
        "return_train_number": "12001",
        "stops": [
            {"station_code": "NDLS", "seq": 1, "arr": None, "dep": "06:00", "halt": 0, "dist": 0.0, "day": 1, "plat": "1"},
            {"station_code": "AGC", "seq": 2, "arr": "07:50", "dep": "07:55", "halt": 5, "dist": 195.0, "day": 1, "plat": "1"},
            {"station_code": "GWL", "seq": 3, "arr": "09:23", "dep": "09:28", "halt": 5, "dist": 313.0, "day": 1, "plat": "1"},
            {"station_code": "VGLJ", "seq": 4, "arr": "10:45", "dep": "10:50", "halt": 5, "dist": 411.0, "day": 1, "plat": "2"},
            {"station_code": "BPL", "seq": 5, "arr": "14:05", "dep": "14:10", "halt": 5, "dist": 701.0, "day": 1, "plat": "1"},
            {"station_code": "RKMP", "seq": 6, "arr": "14:30", "dep": None, "halt": 0, "dist": 707.0, "day": 1, "plat": "1"}
        ]
    },
    {
        "train_number": "12301",
        "train_name": "Howrah - New Delhi Rajdhani Express (via Gaya)",
        "train_type": "Rajdhani",
        "source_station_code": "HWH",
        "destination_station_code": "NDLS",
        "running_days": "1111110",
        "total_distance_km": 1451.0,
        "duration_minutes": 1025,
        "classes": ["1A", "2A", "3A"],
        "pantry_car": True,
        "return_train_number": "12302",
        "stops": [
            {"station_code": "HWH", "seq": 1, "arr": None, "dep": "16:50", "halt": 0, "dist": 0.0, "day": 1, "plat": "9"},
            {"station_code": "DDU", "seq": 2, "arr": "00:45", "dep": "00:55", "halt": 10, "dist": 668.0, "day": 2, "plat": "2"},
            {"station_code": "PRYJ", "seq": 3, "arr": "02:43", "dep": "02:45", "halt": 2, "dist": 820.0, "day": 2, "plat": "1"},
            {"station_code": "CNB", "seq": 4, "arr": "04:50", "dep": "04:55", "halt": 5, "dist": 1015.0, "day": 2, "plat": "1"},
            {"station_code": "NDLS", "seq": 5, "arr": "10:05", "dep": None, "halt": 0, "dist": 1451.0, "day": 2, "plat": "14"}
        ]
    },
    {
        "train_number": "20607",
        "train_name": "Chennai - Mysuru Vande Bharat Express",
        "train_type": "Vande Bharat",
        "source_station_code": "MAS",
        "destination_station_code": "MYS",
        "running_days": "1101111",
        "total_distance_km": 497.0,
        "duration_minutes": 390,
        "classes": ["EC", "CC"],
        "pantry_car": True,
        "return_train_number": "20608",
        "stops": [
            {"station_code": "MAS", "seq": 1, "arr": None, "dep": "05:50", "halt": 0, "dist": 0.0, "day": 1, "plat": "2A"},
            {"station_code": "SBC", "seq": 2, "arr": "10:20", "dep": "10:25", "halt": 5, "dist": 359.0, "day": 1, "plat": "7"},
            {"station_code": "MYS", "seq": 3, "arr": "12:20", "dep": None, "halt": 0, "dist": 497.0, "day": 1, "plat": "1"}
        ]
    },
    {
        "train_number": "12009",
        "train_name": "Mumbai - Ahmedabad Shatabdi Express",
        "train_type": "Shatabdi",
        "source_station_code": "MMCT",
        "destination_station_code": "ADI",
        "running_days": "1111110",
        "total_distance_km": 493.0,
        "duration_minutes": 385,
        "classes": ["EC", "CC"],
        "pantry_car": True,
        "return_train_number": "12010",
        "stops": [
            {"station_code": "MMCT", "seq": 1, "arr": None, "dep": "06:20", "halt": 0, "dist": 0.0, "day": 1, "plat": "1"},
            {"station_code": "BVI", "seq": 2, "arr": "06:43", "dep": "06:45", "halt": 2, "dist": 30.0, "day": 1, "plat": "6"},
            {"station_code": "ST", "seq": 3, "arr": "09:30", "dep": "09:35", "halt": 5, "dist": 263.0, "day": 1, "plat": "1"},
            {"station_code": "BRC", "seq": 4, "arr": "11:00", "dep": "11:05", "halt": 5, "dist": 392.0, "day": 1, "plat": "2"},
            {"station_code": "ADI", "seq": 5, "arr": "12:45", "dep": None, "halt": 0, "dist": 493.0, "day": 1, "plat": "1"}
        ]
    }
]

ALERTS_DATA = [
    {
        "title": "Winter Fog Precautionary Speed Restriction (Northern Railway)",
        "alert_type": "weather",
        "severity": "warning",
        "description": "Due to dense fog conditions in Delhi-NCR, Uttar Pradesh and Bihar sections, maximum speed is regulated to 75 km/h for safety. Rajdhani and Shatabdi trains may experience moderate delays of 15 to 45 minutes.",
        "affected_train_numbers": ["12951", "12952", "22436", "22435", "12301"],
        "affected_station_codes": ["NDLS", "CNB", "PRYJ", "BSB"]
    },
    {
        "title": "Non-Interlocking Electronic Signaling Work at Kanpur Central (CNB)",
        "alert_type": "maintenance",
        "severity": "critical",
        "description": "Electronic interlocking upgrade on Platform 1 and 2 at Kanpur Central. Platform re-assignments in effect for passing trains.",
        "affected_train_numbers": ["22436", "12301"],
        "affected_station_codes": ["CNB"]
    },
    {
        "title": "Special Holiday Frequency Enhancement for Vande Bharat",
        "alert_type": "special",
        "severity": "info",
        "description": "Additional rake inducted to ensure 99.8% punctuality during festive rush on Western Railway and Northern Railway sectors.",
        "affected_train_numbers": ["22436", "20607", "22961", "22962"],
        "affected_station_codes": ["NDLS", "BSB", "MMCT", "ADI"]
    }
]

def seed_database(db: Session):
    # 1. Seed Admin & Passenger Users
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@railtrack.gov.in",
            hashed_password=get_password_hash("RailAdmin@2026"),
            role="admin",
            is_active=True
        )
        db.add(admin_user)

    pass_user = db.query(User).filter(User.username == "passenger").first()
    if not pass_user:
        pass_user = User(
            username="passenger",
            email="passenger@railtrack.gov.in",
            hashed_password=get_password_hash("Passenger@2026"),
            role="passenger",
            is_active=True
        )
        db.add(pass_user)

    db.commit()

    # 2. Seed Stations
    for s_data in STATIONS_DATA:
        existing = db.query(Station).filter(Station.code == s_data["code"]).first()
        if not existing:
            st = Station(**s_data)
            db.add(st)
    db.commit()

    # 3. Seed Trains & Timetable Stops
    for t_data_raw in TRAINS_DATA:
        t_data = dict(t_data_raw)
        stops_info = t_data.pop("stops", [])
        existing = db.query(Train).filter(Train.train_number == t_data["train_number"]).first()
        if not existing:
            train = Train(**t_data)
            db.add(train)
            db.flush()

            for s in stops_info:
                stop = Stop(
                    train_id=train.id,
                    station_code=s["station_code"],
                    stop_sequence=s["seq"],
                    arrival_time=s["arr"],
                    departure_time=s["dep"],
                    halt_minutes=s["halt"],
                    distance_km=s["dist"],
                    day_number=s["day"],
                    platform=s["plat"]
                )
                db.add(stop)
    db.commit()

    # 4. Seed Service Alerts
    for a_data in ALERTS_DATA:
        existing = db.query(ServiceAlert).filter(ServiceAlert.title == a_data["title"]).first()
        if not existing:
            alert = ServiceAlert(
                title=a_data["title"],
                alert_type=a_data["alert_type"],
                severity=a_data["severity"],
                description=a_data["description"],
                affected_train_numbers=a_data["affected_train_numbers"],
                affected_station_codes=a_data["affected_station_codes"],
                active_from=datetime.utcnow() - timedelta(hours=2),
                active_to=datetime.utcnow() + timedelta(days=14),
                is_active=True
            )
            db.add(alert)
    db.commit()
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    from backend.app.database import SessionLocal, Base, engine
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db)
    db.close()
