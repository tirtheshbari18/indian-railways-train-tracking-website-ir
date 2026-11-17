from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.models.station import Station
from backend.app.models.train import Train
from backend.app.models.stop import Stop
from backend.app.models.alert import ServiceAlert
from backend.app.services.auth import get_password_hash

# ==============================================================================
# 1. COMPREHENSIVE INDIAN RAILWAYS STATION DATABASE (ALL 18 ZONES)
# Covers Terminals, Major Junctions, Regular, Suburban, and Rural Halt Stations
# ==============================================================================

STATIONS_DATA = [
    # --- WESTERN RAILWAY (WR) - Mumbai Suburban & Mainline Corridor ---
    {"code": "CCG", "name": "Churchgate", "state": "Maharashtra", "district": "Mumbai City", "division": "Mumbai WR", "zone": "WR", "latitude": 18.9322, "longitude": 72.8264, "category": "Terminal", "platforms_count": 4, "facilities": ["Waiting Room", "Wi-Fi", "Suburban Concourse", "ATVMs"], "operational_status": "Operational"},
    {"code": "BCL", "name": "Mumbai Central (Local)", "state": "Maharashtra", "district": "Mumbai City", "division": "Mumbai WR", "zone": "WR", "latitude": 18.9696, "longitude": 72.8194, "category": "Suburban", "platforms_count": 4, "facilities": ["Suburban Concourse", "ATVMs", "FoB"], "operational_status": "Operational"},
    {"code": "MMCT", "name": "Mumbai Central (Main)", "state": "Maharashtra", "district": "Mumbai City", "division": "Mumbai WR", "zone": "WR", "latitude": 18.9696, "longitude": 72.8194, "category": "Terminal", "platforms_count": 5, "facilities": ["AC Waiting Hall", "Executive Lounge", "Wi-Fi", "Food Plaza", "Cloak Room", "Retiring Rooms", "Escalator"], "operational_status": "Operational"},
    {"code": "MX", "name": "Mahalakshmi", "state": "Maharashtra", "district": "Mumbai City", "division": "Mumbai WR", "zone": "WR", "latitude": 18.9827, "longitude": 72.8236, "category": "Suburban", "platforms_count": 3, "facilities": ["ATVMs", "FoB"], "operational_status": "Operational"},
    {"code": "PL", "name": "Lower Parel", "state": "Maharashtra", "district": "Mumbai City", "division": "Mumbai WR", "zone": "WR", "latitude": 18.9953, "longitude": 72.8306, "category": "Suburban", "platforms_count": 3, "facilities": ["ATVMs", "FoB"], "operational_status": "Operational"},
    {"code": "PBHD", "name": "Prabhadevi", "state": "Maharashtra", "district": "Mumbai City", "division": "Mumbai WR", "zone": "WR", "latitude": 19.0084, "longitude": 72.8354, "category": "Suburban", "platforms_count": 2, "facilities": ["ATVMs", "FoB to Parel CR"], "operational_status": "Operational"},
    {"code": "DDR", "name": "Dadar Western", "state": "Maharashtra", "district": "Mumbai City", "division": "Mumbai WR", "zone": "WR", "latitude": 19.0178, "longitude": 72.8478, "category": "Junction", "platforms_count": 7, "facilities": ["Waiting Hall", "Wi-Fi", "Food Stalls", "Interchange to CR", "Escalator"], "operational_status": "Operational"},
    {"code": "MRU", "name": "Matunga Road", "state": "Maharashtra", "district": "Mumbai City", "division": "Mumbai WR", "zone": "WR", "latitude": 19.0275, "longitude": 72.8447, "category": "Suburban", "platforms_count": 2, "facilities": ["ATVMs", "FoB"], "operational_status": "Operational"},
    {"code": "MM", "name": "Mahim Junction", "state": "Maharashtra", "district": "Mumbai City", "division": "Mumbai WR", "zone": "WR", "latitude": 19.0406, "longitude": 72.8436, "category": "Junction", "platforms_count": 6, "facilities": ["Harbour Line Interchange", "ATVMs", "FoB"], "operational_status": "Operational"},
    {"code": "BA", "name": "Bandra Local", "state": "Maharashtra", "district": "Mumbai Suburban", "division": "Mumbai WR", "zone": "WR", "latitude": 19.0553, "longitude": 72.8406, "category": "Suburban", "platforms_count": 7, "facilities": ["Heritage Station", "ATVMs", "Harbour Line Interchange"], "operational_status": "Operational"},
    {"code": "BDTS", "name": "Bandra Terminus", "state": "Maharashtra", "district": "Mumbai Suburban", "division": "Mumbai WR", "zone": "WR", "latitude": 19.0624, "longitude": 72.8415, "category": "Terminal", "platforms_count": 7, "facilities": ["Waiting Hall", "AC Lounge", "Cloak Room", "Wi-Fi", "Food Plaza", "Prepaid Taxi"], "operational_status": "Operational"},
    {"code": "KHAR", "name": "Khar Road", "state": "Maharashtra", "district": "Mumbai Suburban", "division": "Mumbai WR", "zone": "WR", "latitude": 19.0694, "longitude": 72.8378, "category": "Suburban", "platforms_count": 4, "facilities": ["ATVMs", "FoB"], "operational_status": "Operational"},
    {"code": "STC", "name": "Santa Cruz", "state": "Maharashtra", "district": "Mumbai Suburban", "division": "Mumbai WR", "zone": "WR", "latitude": 19.0817, "longitude": 72.8403, "category": "Suburban", "platforms_count": 4, "facilities": ["ATVMs", "FoB"], "operational_status": "Operational"},
    {"code": "VLP", "name": "Vile Parle", "state": "Maharashtra", "district": "Mumbai Suburban", "division": "Mumbai WR", "zone": "WR", "latitude": 19.0989, "longitude": 72.8439, "category": "Suburban", "platforms_count": 4, "facilities": ["ATVMs", "FoB"], "operational_status": "Operational"},
    {"code": "ADH", "name": "Andheri", "state": "Maharashtra", "district": "Mumbai Suburban", "division": "Mumbai WR", "zone": "WR", "latitude": 19.1197, "longitude": 72.8464, "category": "Junction", "platforms_count": 9, "facilities": ["Metro Line 1 Interchange", "AC Waiting Hall", "Wi-Fi", "Escalators", "ATVMs", "Food Stalls"], "operational_status": "Operational"},
    {"code": "JOS", "name": "Jogeshwari", "state": "Maharashtra", "district": "Mumbai Suburban", "division": "Mumbai WR", "zone": "WR", "latitude": 19.1350, "longitude": 72.8492, "category": "Suburban", "platforms_count": 4, "facilities": ["ATVMs", "FoB"], "operational_status": "Operational"},
    {"code": "RMAR", "name": "Ram Mandir", "state": "Maharashtra", "district": "Mumbai Suburban", "division": "Mumbai WR", "zone": "WR", "latitude": 19.1486, "longitude": 72.8508, "category": "Suburban", "platforms_count": 4, "facilities": ["ATVMs", "Elevated FoB"], "operational_status": "Operational"},
    {"code": "GMN", "name": "Goregaon", "state": "Maharashtra", "district": "Mumbai Suburban", "division": "Mumbai WR", "zone": "WR", "latitude": 19.1644, "longitude": 72.8497, "category": "Suburban", "platforms_count": 7, "facilities": ["Harbour Line Terminus", "ATVMs", "Wi-Fi", "Escalator"], "operational_status": "Operational"},
    {"code": "MDD", "name": "Malad", "state": "Maharashtra", "district": "Mumbai Suburban", "division": "Mumbai WR", "zone": "WR", "latitude": 19.1864, "longitude": 72.8486, "category": "Suburban", "platforms_count": 4, "facilities": ["ATVMs", "FoB"], "operational_status": "Operational"},
    {"code": "KILE", "name": "Kandivali", "state": "Maharashtra", "district": "Mumbai Suburban", "division": "Mumbai WR", "zone": "WR", "latitude": 19.2047, "longitude": 72.8522, "category": "Suburban", "platforms_count": 4, "facilities": ["ATVMs", "FoB"], "operational_status": "Operational"},
    {"code": "BVI", "name": "Borivali", "state": "Maharashtra", "district": "Mumbai Suburban", "division": "Mumbai WR", "zone": "WR", "latitude": 19.2288, "longitude": 72.8569, "category": "Junction", "platforms_count": 10, "facilities": ["Major Terminal & Junction", "AC Waiting Hall", "Executive Lounge", "Food Stalls", "Wi-Fi", "Escalators", "Suburban & Express Stop"], "operational_status": "Operational"},
    {"code": "DIC", "name": "Dahisar", "state": "Maharashtra", "district": "Mumbai Suburban", "division": "Mumbai WR", "zone": "WR", "latitude": 19.2556, "longitude": 72.8594, "category": "Suburban", "platforms_count": 4, "facilities": ["ATVMs", "FoB"], "operational_status": "Operational"},
    {"code": "MIRA", "name": "Mira Road", "state": "Maharashtra", "district": "Thane", "division": "Mumbai WR", "zone": "WR", "latitude": 19.2814, "longitude": 72.8572, "category": "Suburban", "platforms_count": 4, "facilities": ["ATVMs", "Wi-Fi", "FoB"], "operational_status": "Operational"},
    {"code": "BYR", "name": "Bhayandar", "state": "Maharashtra", "district": "Thane", "division": "Mumbai WR", "zone": "WR", "latitude": 19.3014, "longitude": 72.8519, "category": "Suburban", "platforms_count": 6, "facilities": ["Local Train Terminus", "ATVMs", "FoB"], "operational_status": "Operational"},
    {"code": "NIG", "name": "Naigaon", "state": "Maharashtra", "district": "Palghar", "division": "Mumbai WR", "zone": "WR", "latitude": 19.3497, "longitude": 72.8469, "category": "Suburban", "platforms_count": 4, "facilities": ["ATVMs", "FoB"], "operational_status": "Operational"},
    {"code": "BSR", "name": "Vasai Road", "state": "Maharashtra", "district": "Palghar", "division": "Mumbai WR", "zone": "WR", "latitude": 19.3814, "longitude": 72.8331, "category": "Junction", "platforms_count": 8, "facilities": ["CR-WR Chord Interchange", "Waiting Room", "Wi-Fi", "Food Stalls", "MEMU/DEMU Stop"], "operational_status": "Operational"},
    {"code": "NSP", "name": "Nallasopara", "state": "Maharashtra", "district": "Palghar", "division": "Mumbai WR", "zone": "WR", "latitude": 19.4181, "longitude": 72.8183, "category": "Suburban", "platforms_count": 4, "facilities": ["ATVMs", "FoB"], "operational_status": "Operational"},
    {"code": "VR", "name": "Virar", "state": "Maharashtra", "district": "Palghar", "division": "Mumbai WR", "zone": "WR", "latitude": 19.4533, "longitude": 72.8094, "category": "Terminal", "platforms_count": 8, "facilities": ["Major Suburban Terminus", "Car Shed", "Waiting Hall", "Wi-Fi", "Food Court", "ATVMs"], "operational_status": "Operational"},
    {"code": "VTN", "name": "Vaitarna", "state": "Maharashtra", "district": "Palghar", "division": "Mumbai WR", "zone": "WR", "latitude": 19.5256, "longitude": 72.8272, "category": "Halt", "platforms_count": 2, "facilities": ["Suburban Halt", "Ticket Window"], "operational_status": "Operational"},
    {"code": "SAH", "name": "Saphale", "state": "Maharashtra", "district": "Palghar", "division": "Mumbai WR", "zone": "WR", "latitude": 19.5764, "longitude": 72.8219, "category": "Regular", "platforms_count": 3, "facilities": ["Waiting Hall", "Ticket Window", "Local/MEMU Stop"], "operational_status": "Operational"},
    {"code": "KLV", "name": "Kelve Road", "state": "Maharashtra", "district": "Palghar", "division": "Mumbai WR", "zone": "WR", "latitude": 19.6264, "longitude": 72.7847, "category": "Regular", "platforms_count": 3, "facilities": ["Tourist Beach Access", "Waiting Hall", "Ticket Window"], "operational_status": "Operational"},
    {"code": "PLG", "name": "Palghar", "state": "Maharashtra", "district": "Palghar", "division": "Mumbai WR", "zone": "WR", "latitude": 19.6967, "longitude": 72.7655, "category": "Regular", "platforms_count": 3, "facilities": ["District Headquarters", "Waiting Hall", "Wi-Fi", "Express/Local Stop"], "operational_status": "Operational"},
    {"code": "UOI", "name": "Umroli", "state": "Maharashtra", "district": "Palghar", "division": "Mumbai WR", "zone": "WR", "latitude": 19.7422, "longitude": 72.7608, "category": "Halt", "platforms_count": 2, "facilities": ["Local Train Halt", "Ticket Window"], "operational_status": "Operational"},
    {"code": "BOR", "name": "Boisar", "state": "Maharashtra", "district": "Palghar", "division": "Mumbai WR", "zone": "WR", "latitude": 19.8005, "longitude": 72.7561, "category": "Regular", "platforms_count": 3, "facilities": ["MIDC Industrial Hub", "Waiting Hall", "Wi-Fi", "Express/MEMU/Local Stop", "ATVMs"], "operational_status": "Operational"},
    {"code": "VGN", "name": "Vangaon", "state": "Maharashtra", "district": "Palghar", "division": "Mumbai WR", "zone": "WR", "latitude": 19.8786, "longitude": 72.7483, "category": "Regular", "platforms_count": 2, "facilities": ["Local Train Stop", "Ticket Window"], "operational_status": "Operational"},
    {"code": "DRD", "name": "Dahanu Road", "state": "Maharashtra", "district": "Palghar", "division": "Mumbai WR", "zone": "WR", "latitude": 19.9734, "longitude": 72.7384, "category": "Terminal", "platforms_count": 3, "facilities": ["Suburban Terminus of Western Railway", "Waiting Hall", "Wi-Fi", "Food Stalls", "Express & Local Stop"], "operational_status": "Operational"},
    {"code": "GVD", "name": "Gholvad", "state": "Maharashtra", "district": "Palghar", "division": "Mumbai WR", "zone": "WR", "latitude": 20.0811, "longitude": 72.7381, "category": "Regular", "platforms_count": 2, "facilities": ["Waiting Hall", "Ticket Counter"], "operational_status": "Operational"},
    {"code": "BRRD", "name": "Bordi Road", "state": "Maharashtra", "district": "Palghar", "division": "Mumbai WR", "zone": "WR", "latitude": 20.1264, "longitude": 72.7594, "category": "Halt", "platforms_count": 2, "facilities": ["Border Station", "Ticket Window"], "operational_status": "Operational"},
    {"code": "UBR", "name": "Umbergaon Road", "state": "Gujarat", "district": "Valsad", "division": "Mumbai WR", "zone": "WR", "latitude": 20.1836, "longitude": 72.8202, "category": "Regular", "platforms_count": 2, "facilities": ["Waiting Hall", "Express/MEMU Stop"], "operational_status": "Operational"},
    {"code": "SJN", "name": "Sanjan", "state": "Gujarat", "district": "Valsad", "division": "Mumbai WR", "zone": "WR", "latitude": 20.2017, "longitude": 72.8614, "category": "Regular", "platforms_count": 2, "facilities": ["Historical Station", "Ticket Counter"], "operational_status": "Operational"},
    {"code": "BLD", "name": "Bhilad", "state": "Gujarat", "district": "Valsad", "division": "Mumbai WR", "zone": "WR", "latitude": 20.2783, "longitude": 72.8808, "category": "Regular", "platforms_count": 2, "facilities": ["Industrial Area", "Waiting Hall"], "operational_status": "Operational"},
    {"code": "KEB", "name": "Karambeli", "state": "Gujarat", "district": "Valsad", "division": "Mumbai WR", "zone": "WR", "latitude": 20.3206, "longitude": 72.8944, "category": "Halt", "platforms_count": 2, "facilities": ["Passenger Halt"], "operational_status": "Operational"},
    {"code": "VAPI", "name": "Vapi", "state": "Gujarat", "district": "Valsad", "division": "Mumbai WR", "zone": "WR", "latitude": 20.3714, "longitude": 72.9043, "category": "Regular", "platforms_count": 3, "facilities": ["Chemical Hub", "AC Waiting Hall", "Wi-Fi", "Vande Bharat Stop", "Food Plaza", "Cloak Room"], "operational_status": "Operational"},
    {"code": "UVD", "name": "Udvada", "state": "Gujarat", "district": "Valsad", "division": "Mumbai WR", "zone": "WR", "latitude": 20.4722, "longitude": 72.9248, "category": "Regular", "platforms_count": 2, "facilities": ["Parsi Pilgrim Hub", "Waiting Hall"], "operational_status": "Operational"},
    {"code": "BL", "name": "Valsad", "state": "Gujarat", "district": "Valsad", "division": "Mumbai WR", "zone": "WR", "latitude": 20.6101, "longitude": 72.9272, "category": "Junction", "platforms_count": 5, "facilities": ["Major Junction & Locomotive Shed", "AC Waiting Hall", "Wi-Fi", "Food Plaza", "Retiring Rooms"], "operational_status": "Operational"},
    {"code": "BIM", "name": "Bilimora Junction", "state": "Gujarat", "district": "Navsari", "division": "Mumbai WR", "zone": "WR", "latitude": 20.7634, "longitude": 72.9641, "category": "Junction", "platforms_count": 5, "facilities": ["Heritage Narrow Gauge Junction", "Waiting Hall", "Express Stop"], "operational_status": "Operational"},
    {"code": "AML", "name": "Amalsad", "state": "Gujarat", "district": "Navsari", "division": "Mumbai WR", "zone": "WR", "latitude": 20.8253, "longitude": 72.9511, "category": "Regular", "platforms_count": 2, "facilities": ["Fruit Hub", "Waiting Hall"], "operational_status": "Operational"},
    {"code": "NVS", "name": "Navsari", "state": "Gujarat", "district": "Navsari", "division": "Mumbai WR", "zone": "WR", "latitude": 20.9467, "longitude": 72.9282, "category": "Regular", "platforms_count": 3, "facilities": ["Diamond & Textile Hub", "Waiting Hall", "Wi-Fi", "Express Stop"], "operational_status": "Operational"},
    {"code": "MRL", "name": "Maroli", "state": "Gujarat", "district": "Navsari", "division": "Mumbai WR", "zone": "WR", "latitude": 21.0361, "longitude": 72.8944, "category": "Regular", "platforms_count": 2, "facilities": ["Waiting Hall", "Ticket Counter"], "operational_status": "Operational"},
    {"code": "URN", "name": "Udhna Junction", "state": "Gujarat", "district": "Surat", "division": "Mumbai WR", "zone": "WR", "latitude": 21.1603, "longitude": 72.8467, "category": "Junction", "platforms_count": 5, "facilities": ["Jalgaon Line Junction", "Waiting Hall", "Wi-Fi", "Satellite Station"], "operational_status": "Operational"},
    {"code": "ST", "name": "Surat", "state": "Gujarat", "district": "Surat", "division": "Mumbai WR", "zone": "WR", "latitude": 21.2049, "longitude": 72.8407, "category": "Junction", "platforms_count": 4, "facilities": ["A1 Category Station", "AC Executive Lounge", "Wi-Fi", "Food Plaza", "Multi-Level Parking", "Escalators", "Cloak Room"], "operational_status": "Operational"},
    {"code": "KIM", "name": "Kim", "state": "Gujarat", "district": "Surat", "division": "Mumbai WR", "zone": "WR", "latitude": 21.4011, "longitude": 72.9328, "category": "Regular", "platforms_count": 2, "facilities": ["Waiting Hall", "Ticket Counter"], "operational_status": "Operational"},
    {"code": "KSB", "name": "Kosamba Junction", "state": "Gujarat", "district": "Surat", "division": "Mumbai WR", "zone": "WR", "latitude": 21.4729, "longitude": 72.9568, "category": "Junction", "platforms_count": 3, "facilities": ["Umarpada Line Junction", "Waiting Hall"], "operational_status": "Operational"},
    {"code": "AKV", "name": "Ankleshwar Junction", "state": "Gujarat", "district": "Bharuch", "division": "Vadodara", "zone": "WR", "latitude": 21.6264, "longitude": 73.0019, "category": "Junction", "platforms_count": 4, "facilities": ["Chemical Estate Junction", "Waiting Hall", "Wi-Fi", "Express Stop"], "operational_status": "Operational"},
    {"code": "BH", "name": "Bharuch Junction", "state": "Gujarat", "district": "Bharuch", "division": "Vadodara", "zone": "WR", "latitude": 21.7051, "longitude": 72.9959, "category": "Junction", "platforms_count": 6, "facilities": ["Narmada River Rail Hub", "Waiting Hall", "Wi-Fi", "Retiring Rooms", "Express Stop"], "operational_status": "Operational"},
    {"code": "PLJ", "name": "Palej", "state": "Gujarat", "district": "Bharuch", "division": "Vadodara", "zone": "WR", "latitude": 21.8492, "longitude": 73.0722, "category": "Regular", "platforms_count": 2, "facilities": ["Waiting Hall", "Ticket Counter"], "operational_status": "Operational"},
    {"code": "MYG", "name": "Miyagam Karjan Junction", "state": "Gujarat", "district": "Vadodara", "division": "Vadodara", "zone": "WR", "latitude": 22.0461, "longitude": 73.1235, "category": "Junction", "platforms_count": 3, "facilities": ["Moti Koral Branch Junction", "Waiting Hall"], "operational_status": "Operational"},
    {"code": "BRC", "name": "Vadodara Junction", "state": "Gujarat", "district": "Vadodara", "division": "Vadodara", "zone": "WR", "latitude": 22.3107, "longitude": 73.1812, "category": "Junction", "platforms_count": 7, "facilities": ["Premier A1 Junction", "Electric Loco Shed", "AC Lounge", "Food Plazas", "Cloak Room", "Wi-Fi", "Escalators"], "operational_status": "Operational"},
    {"code": "ANND", "name": "Anand Junction", "state": "Gujarat", "district": "Anand", "division": "Vadodara", "zone": "WR", "latitude": 22.5645, "longitude": 72.9289, "category": "Junction", "platforms_count": 5, "facilities": ["Milk Capital of India (Amul)", "Waiting Hall", "Wi-Fi", "Express/MEMU Hub"], "operational_status": "Operational"},
    {"code": "ND", "name": "Nadiad Junction", "state": "Gujarat", "district": "Kheda", "division": "Vadodara", "zone": "WR", "latitude": 22.6916, "longitude": 72.8634, "category": "Junction", "platforms_count": 4, "facilities": ["Modasa Line Junction", "Waiting Hall", "Wi-Fi", "Express Stop"], "operational_status": "Operational"},
    {"code": "MHD", "name": "Mahemdavad Kheda Road", "state": "Gujarat", "district": "Kheda", "division": "Vadodara", "zone": "WR", "latitude": 22.8258, "longitude": 72.7712, "category": "Regular", "platforms_count": 2, "facilities": ["Waiting Hall", "Ticket Counter"], "operational_status": "Operational"},
    {"code": "BJD", "name": "Barejadi Nandej", "state": "Gujarat", "district": "Ahmedabad", "division": "Ahmedabad", "zone": "WR", "latitude": 22.9064, "longitude": 72.6719, "category": "Suburban", "platforms_count": 2, "facilities": ["Suburban Halt", "Ticket Counter"], "operational_status": "Operational"},
    {"code": "MAN", "name": "Maninagar", "state": "Gujarat", "district": "Ahmedabad", "division": "Ahmedabad", "zone": "WR", "latitude": 22.9981, "longitude": 72.6033, "category": "Suburban", "platforms_count": 2, "facilities": ["Satellite Station to Ahmedabad", "Waiting Hall", "Wi-Fi", "Express Stop"], "operational_status": "Operational"},
    {"code": "ADI", "name": "Ahmedabad Junction", "state": "Gujarat", "district": "Ahmedabad", "division": "Ahmedabad", "zone": "WR", "latitude": 23.0232, "longitude": 72.6009, "category": "Terminal", "platforms_count": 12, "facilities": ["Premier Terminus (Kalupur)", "AC VIP Lounge", "Wi-Fi", "Metro Line Interchange", "Food Plazas", "Cloak Room", "Retiring Rooms"], "operational_status": "Operational"},
    {"code": "RTM", "name": "Ratlam Junction", "state": "Madhya Pradesh", "district": "Ratlam", "division": "Ratlam", "zone": "WR", "latitude": 23.3441, "longitude": 75.0352, "category": "Junction", "platforms_count": 7, "facilities": ["Major Crew Changing Junction", "AC Lounge", "Wi-Fi", "Food Court", "Retiring Rooms"], "operational_status": "Operational"},

    # --- CENTRAL RAILWAY (CR) - Mumbai Suburban & Mainline ---
    {"code": "CSMT", "name": "Chhatrapati Shivaji Maharaj Terminus", "state": "Maharashtra", "district": "Mumbai City", "division": "Mumbai CR", "zone": "CR", "latitude": 18.9402, "longitude": 72.8358, "category": "Terminal", "platforms_count": 18, "facilities": ["UNESCO World Heritage Monument", "Executive Lounge", "Wi-Fi", "Food Plazas", "Pod Hotel", "Cloak Room", "Prepaid Taxi"], "operational_status": "Operational"},
    {"code": "BY", "name": "Byculla", "state": "Maharashtra", "district": "Mumbai City", "division": "Mumbai CR", "zone": "CR", "latitude": 18.9774, "longitude": 72.8339, "category": "Suburban", "platforms_count": 4, "facilities": ["Heritage Station", "ATVMs", "FoB"], "operational_status": "Operational"},
    {"code": "DR", "name": "Dadar Central", "state": "Maharashtra", "district": "Mumbai City", "division": "Mumbai CR", "zone": "CR", "latitude": 19.0178, "longitude": 72.8478, "category": "Junction", "platforms_count": 8, "facilities": ["Interchange with WR", "Waiting Hall", "Wi-Fi", "Food Stalls", "Escalators"], "operational_status": "Operational"},
    {"code": "CLA", "name": "Kurla Junction", "state": "Maharashtra", "district": "Mumbai Suburban", "division": "Mumbai CR", "zone": "CR", "latitude": 19.0653, "longitude": 72.8794, "category": "Junction", "platforms_count": 8, "facilities": ["Harbour & Mainline Interchange", "ATVMs", "FoB", "Suburban Hub"], "operational_status": "Operational"},
    {"code": "GC", "name": "Ghatkopar", "state": "Maharashtra", "district": "Mumbai Suburban", "division": "Mumbai CR", "zone": "CR", "latitude": 19.0864, "longitude": 72.9081, "category": "Suburban", "platforms_count": 4, "facilities": ["Metro Line 1 Elevated Interchange", "ATVMs", "Wi-Fi", "Heavy Suburban Footfall"], "operational_status": "Operational"},
    {"code": "TNA", "name": "Thane", "state": "Maharashtra", "district": "Thane", "division": "Mumbai CR", "zone": "CR", "latitude": 19.1861, "longitude": 72.9758, "category": "Junction", "platforms_count": 10, "facilities": ["Historic First Railway Station in India (1853)", "Trans-Harbour Interchange", "AC Waiting Hall", "Food Plaza", "Wi-Fi"], "operational_status": "Operational"},
    {"code": "DI", "name": "Diva Junction", "state": "Maharashtra", "district": "Thane", "division": "Mumbai CR", "zone": "CR", "latitude": 19.1889, "longitude": 73.0428, "category": "Junction", "platforms_count": 8, "facilities": ["Vasai-Panvel-Roha Chord Junction", "DEMU/MEMU Hub", "ATVMs"], "operational_status": "Operational"},
    {"code": "KYN", "name": "Kalyan Junction", "state": "Maharashtra", "district": "Thane", "division": "Mumbai CR", "zone": "CR", "latitude": 19.2356, "longitude": 73.1306, "category": "Junction", "platforms_count": 8, "facilities": ["North-East & South-East Bifurcation", "AC Waiting Hall", "Wi-Fi", "Food Court", "Major Crew Base"], "operational_status": "Operational"},
    {"code": "KSRA", "name": "Kasara", "state": "Maharashtra", "district": "Thane", "division": "Mumbai CR", "zone": "CR", "latitude": 19.6467, "longitude": 73.4833, "category": "Terminal", "platforms_count": 4, "facilities": ["Suburban North-East Terminus", "Banker Locomotive Attachment Base (Thal Ghat)"], "operational_status": "Operational"},
    {"code": "KJT", "name": "Karjat Junction", "state": "Maharashtra", "district": "Raigad", "division": "Mumbai CR", "zone": "CR", "latitude": 18.9108, "longitude": 73.3217, "category": "Junction", "platforms_count": 3, "facilities": ["Suburban South-East Terminus", "Banker Base (Bhor Ghat)", "Khopoli Branch Junction"], "operational_status": "Operational"},
    {"code": "PNVL", "name": "Panvel Junction", "state": "Maharashtra", "district": "Raigad", "division": "Mumbai CR", "zone": "CR", "latitude": 18.9894, "longitude": 73.1219, "category": "Junction", "platforms_count": 7, "facilities": ["Harbour Line Terminus", "Konkan Railway Gateway", "AC Lounge", "Wi-Fi", "Express Halt"], "operational_status": "Operational"},
    {"code": "PUNE", "name": "Pune Junction", "state": "Maharashtra", "district": "Pune", "division": "Pune", "zone": "CR", "latitude": 18.5289, "longitude": 73.8744, "category": "Junction", "platforms_count": 6, "facilities": ["Major Intercity Terminal", "AC Executive Lounge", "Food Plazas", "Cloak Room", "Wi-Fi", "Retiring Rooms"], "operational_status": "Operational"},
    {"code": "LNL", "name": "Lonavala", "state": "Maharashtra", "district": "Pune", "division": "Mumbai CR", "zone": "CR", "latitude": 18.7533, "longitude": 73.4072, "category": "Regular", "platforms_count": 3, "facilities": ["Hill Station Hub", "Suburban Terminus of Pune EMU", "Waiting Hall"], "operational_status": "Operational"},
    {"code": "BSL", "name": "Bhusaval Junction", "state": "Maharashtra", "district": "Jalgaon", "division": "Bhusaval", "zone": "CR", "latitude": 21.0506, "longitude": 75.7975, "category": "Junction", "platforms_count": 8, "facilities": ["Premier Locomotive Hub", "AC Lounge", "Wi-Fi", "Retiring Rooms"], "operational_status": "Operational"},
    {"code": "NGP", "name": "Nagpur Junction", "state": "Maharashtra", "district": "Nagpur", "division": "Nagpur CR", "zone": "CR", "latitude": 21.1522, "longitude": 79.0886, "category": "Junction", "platforms_count": 8, "facilities": ["Diamond Crossing Geographical Center of India", "AC Lounge", "Wi-Fi", "Food Court"], "operational_status": "Operational"},

    # --- NORTHERN RAILWAY (NR) ---
    {"code": "NDLS", "name": "New Delhi", "state": "Delhi", "district": "Central Delhi", "division": "Delhi", "zone": "NR", "latitude": 28.6429, "longitude": 77.2195, "category": "Terminal", "platforms_count": 16, "facilities": ["Flagship A1 Terminal", "Airport Express Metro Interchange", "Executive Lounges", "Multi-Cuisine Food Court", "Retiring Rooms", "Wi-Fi", "Escalators"], "operational_status": "Operational"},
    {"code": "DLI", "name": "Old Delhi Junction", "state": "Delhi", "district": "North Delhi", "division": "Delhi", "zone": "NR", "latitude": 28.6617, "longitude": 77.2289, "category": "Junction", "platforms_count": 16, "facilities": ["Historic Terminal", "Metro Interchange", "Retiring Rooms", "Cloak Room", "Wi-Fi"], "operational_status": "Operational"},
    {"code": "NZM", "name": "Hazrat Nizamuddin", "state": "Delhi", "district": "South East Delhi", "division": "Delhi", "zone": "NR", "latitude": 28.5886, "longitude": 77.2536, "category": "Terminal", "platforms_count": 9, "facilities": ["Major Rajdhani/Express Terminal", "AC Waiting Hall", "Wi-Fi", "Food Plaza", "Prepaid Taxi"], "operational_status": "Operational"},
    {"code": "ANVT", "name": "Anand Vihar Terminal", "state": "Delhi", "district": "East Delhi", "division": "Delhi", "zone": "NR", "latitude": 28.6506, "longitude": 77.3153, "category": "Terminal", "platforms_count": 7, "facilities": ["Modern Satellite Terminal", "ISBT Interchange", "Metro Interchange", "AC Lounges"], "operational_status": "Operational"},
    {"code": "GZB", "name": "Ghaziabad Junction", "state": "Uttar Pradesh", "district": "Ghaziabad", "division": "Delhi", "zone": "NR", "latitude": 28.6675, "longitude": 77.4344, "category": "Junction", "platforms_count": 6, "facilities": ["EMU/MEMU Hub", "Waiting Hall", "Wi-Fi", "Express Stop"], "operational_status": "Operational"},
    {"code": "ASR", "name": "Amritsar Junction", "state": "Punjab", "district": "Amritsar", "division": "Firozpur", "zone": "NR", "latitude": 31.6339, "longitude": 74.8656, "category": "Terminal", "platforms_count": 8, "facilities": ["Golden Temple Gateway", "AC Waiting Lounge", "Wi-Fi", "Retiring Rooms"], "operational_status": "Operational"},
    {"code": "SVDK", "name": "Shri Mata Vaishno Devi Katra", "state": "Jammu & Kashmir", "district": "Reasi", "division": "Firozpur", "zone": "NR", "latitude": 32.9903, "longitude": 74.9317, "category": "Terminal", "platforms_count": 3, "facilities": ["Pilgrim World-Class Station", "AC Lounges", "Yatri Nivas", "Solar Powered", "Wi-Fi"], "operational_status": "Operational"},
    {"code": "BSB", "name": "Varanasi Junction", "state": "Uttar Pradesh", "district": "Varanasi", "division": "Lucknow NR", "zone": "NR", "latitude": 25.3283, "longitude": 82.9868, "category": "Junction", "platforms_count": 9, "facilities": ["Spiritual Capital Terminal", "AC Waiting Hall", "Wi-Fi", "Vande Bharat Hub", "Food Plaza"], "operational_status": "Operational"},

    # --- NORTH CENTRAL RAILWAY (NCR) ---
    {"code": "CNB", "name": "Kanpur Central", "state": "Uttar Pradesh", "district": "Kanpur Nagar", "division": "Prayagraj", "zone": "NCR", "latitude": 26.4547, "longitude": 80.3507, "category": "Junction", "platforms_count": 10, "facilities": ["Major Quadruple Line Junction", "AC Lounge", "Wi-Fi", "Food Plazas", "Retiring Rooms", "Escalators"], "operational_status": "Operational"},
    {"code": "PRYJ", "name": "Prayagraj Junction", "state": "Uttar Pradesh", "district": "Prayagraj", "division": "Prayagraj", "zone": "NCR", "latitude": 25.4439, "longitude": 81.8252, "category": "Junction", "platforms_count": 10, "facilities": ["Kumbh Mela Gateway", "AC Waiting Hall", "Wi-Fi", "Retiring Rooms", "Cloak Room"], "operational_status": "Operational"},
    {"code": "AGC", "name": "Agra Cantt", "state": "Uttar Pradesh", "district": "Agra", "division": "Agra", "zone": "NCR", "latitude": 27.1593, "longitude": 78.0081, "category": "Junction", "platforms_count": 6, "facilities": ["Taj Mahal Gateway", "AC Tourist Lounge", "Prepaid Taxi", "Wi-Fi", "Food Plaza"], "operational_status": "Operational"},
    {"code": "GWL", "name": "Gwalior Junction", "state": "Madhya Pradesh", "district": "Gwalior", "division": "Jhansi", "zone": "NCR", "latitude": 26.2183, "longitude": 78.1828, "category": "Junction", "platforms_count": 5, "facilities": ["Heritage Station", "Waiting Hall", "Wi-Fi", "Express Stop"], "operational_status": "Operational"},
    {"code": "VGLJ", "name": "Virangana Lakshmibai Jhansi", "state": "Uttar Pradesh", "district": "Jhansi", "division": "Jhansi", "zone": "NCR", "latitude": 25.4484, "longitude": 78.5685, "category": "Junction", "platforms_count": 8, "facilities": ["Grand Trunk Interchange", "AC Waiting Hall", "Wi-Fi", "Food Court"], "operational_status": "Operational"},

    # --- WEST CENTRAL RAILWAY (WCR) ---
    {"code": "BPL", "name": "Bhopal Junction", "state": "Madhya Pradesh", "district": "Bhopal", "division": "Bhopal", "zone": "WCR", "latitude": 23.2684, "longitude": 77.4126, "category": "Junction", "platforms_count": 6, "facilities": ["Capital Junction", "AC Lounge", "Wi-Fi", "Food Stalls", "Retiring Rooms"], "operational_status": "Operational"},
    {"code": "RKMP", "name": "Rani Kamlapati", "state": "Madhya Pradesh", "district": "Bhopal", "division": "Bhopal", "zone": "WCR", "latitude": 23.2163, "longitude": 77.4384, "category": "Terminal", "platforms_count": 5, "facilities": ["India's First Airport-Standard World-Class Station (PPP)", "Air Concourse", "Segregated Arrival/Departure", "Multi-Brand Food Court", "Wi-Fi"], "operational_status": "Operational"},
    {"code": "KOTA", "name": "Kota Junction", "state": "Rajasthan", "district": "Kota", "division": "Kota", "zone": "WCR", "latitude": 25.2198, "longitude": 75.8648, "category": "Junction", "platforms_count": 6, "facilities": ["Education Hub", "AC Waiting Hall", "Wi-Fi", "Rajdhani Crew Base"], "operational_status": "Operational"},

    # --- EASTERN & SOUTH EASTERN RAILWAY (ER / SER) ---
    {"code": "HWH", "name": "Howrah Junction", "state": "West Bengal", "district": "Howrah", "division": "Howrah", "zone": "ER", "latitude": 22.5839, "longitude": 88.3426, "category": "Terminal", "platforms_count": 23, "facilities": ["India's Busiest & Largest 23-Platform Terminus", "Yatri Niwas", "AC Lounges", "Suburban Concourse", "Metro Interchange", "Wi-Fi"], "operational_status": "Operational"},
    {"code": "SDAH", "name": "Sealdah", "state": "West Bengal", "district": "Kolkata", "division": "Sealdah", "zone": "ER", "latitude": 22.5675, "longitude": 88.3711, "category": "Terminal", "platforms_count": 21, "facilities": ["High-Density Suburban Terminus", "Metro Line 2 Interchange", "AC Lounges", "Wi-Fi"], "operational_status": "Operational"},

    # --- EAST CENTRAL RAILWAY (ECR) ---
    {"code": "PNBE", "name": "Patna Junction", "state": "Bihar", "district": "Patna", "division": "Danapur", "zone": "ECR", "latitude": 25.6022, "longitude": 85.1376, "category": "Junction", "platforms_count": 10, "facilities": ["Capital Junction", "AC Lounge", "Wi-Fi", "Retiring Rooms", "Escalators"], "operational_status": "Operational"},
    {"code": "DDU", "name": "Pt. Deen Dayal Upadhyaya Jn", "state": "Uttar Pradesh", "district": "Chandauli", "division": "Pt Deen Dayal Upadhyaya", "zone": "ECR", "latitude": 25.2818, "longitude": 83.1189, "category": "Junction", "platforms_count": 8, "facilities": ["Asia's Largest Railway Marshalling Yard", "AC Lounge", "Wi-Fi", "Grand Trunk Hub"], "operational_status": "Operational"},

    # --- NORTH EASTERN & NORTHEAST FRONTIER (NER / NFR) ---
    {"code": "GKP", "name": "Gorakhpur Junction", "state": "Uttar Pradesh", "district": "Gorakhpur", "division": "Lucknow NER", "zone": "NER", "latitude": 26.7588, "longitude": 83.3853, "category": "Junction", "platforms_count": 10, "facilities": ["World-Record 1366-meter Platform", "AC Lounge", "Wi-Fi", "Retiring Rooms"], "operational_status": "Operational"},
    {"code": "GHY", "name": "Guwahati", "state": "Assam", "district": "Kamrup Metropolitan", "division": "Lumding", "zone": "NFR", "latitude": 26.1822, "longitude": 91.7511, "category": "Terminal", "platforms_count": 7, "facilities": ["Gateway to North-East India", "100% Solar-Powered Terminal", "AC Lounges", "Wi-Fi"], "operational_status": "Operational"},

    # --- SOUTHERN & SOUTH WESTERN RAILWAY (SR / SWR) ---
    {"code": "MAS", "name": "MGR Chennai Central", "state": "Tamil Nadu", "district": "Chennai", "division": "Chennai", "zone": "SR", "latitude": 13.0827, "longitude": 80.2754, "category": "Terminal", "platforms_count": 17, "facilities": ["Premier Southern Terminal", "AC Executive Lounges", "Metro Interchange", "Suburban Concourse (Moore Market)", "Wi-Fi"], "operational_status": "Operational"},
    {"code": "SBC", "name": "KSR Bengaluru City", "state": "Karnataka", "district": "Bengaluru Urban", "division": "Bengaluru", "zone": "SWR", "latitude": 12.9781, "longitude": 77.5696, "category": "Terminal", "platforms_count": 10, "facilities": ["Tech Capital Terminal", "Namma Metro Interchange", "AC Lounges", "Wi-Fi", "Food Court"], "operational_status": "Operational"},
    {"code": "MYS", "name": "Mysuru Junction", "state": "Karnataka", "district": "Mysuru", "division": "Mysuru", "zone": "SWR", "latitude": 12.3164, "longitude": 76.6437, "category": "Junction", "platforms_count": 6, "facilities": ["Heritage Clean Terminal", "Tourist Hub", "Wi-Fi", "Vande Bharat Stop"], "operational_status": "Operational"},
    {"code": "TVC", "name": "Thiruvananthapuram Central", "state": "Kerala", "district": "Thiruvananthapuram", "division": "Thiruvananthapuram", "zone": "SR", "latitude": 8.4875, "longitude": 76.9532, "category": "Terminal", "platforms_count": 5, "facilities": ["Kerala Capital Terminal", "AC Waiting Hall", "Wi-Fi", "Food Plaza"], "operational_status": "Operational"},

    # --- NORTH WESTERN & SOUTH CENTRAL (NWR / SCR) ---
    {"code": "JP", "name": "Jaipur Junction", "state": "Rajasthan", "district": "Jaipur", "division": "Jaipur", "zone": "NWR", "latitude": 26.9208, "longitude": 75.7875, "category": "Junction", "platforms_count": 8, "facilities": ["Pink City Heritage Terminal", "AC Lounges", "Metro Interchange", "Wi-Fi"], "operational_status": "Operational"},
    {"code": "BKN", "name": "Bikaner Junction", "state": "Rajasthan", "district": "Bikaner", "division": "Bikaner", "zone": "NWR", "latitude": 28.0167, "longitude": 73.3119, "category": "Junction", "platforms_count": 6, "facilities": ["Heritage Station", "Waiting Hall", "Wi-Fi"], "operational_status": "Operational"},
    {"code": "SC", "name": "Secunderabad Junction", "state": "Telangana", "district": "Hyderabad", "division": "Secunderabad", "zone": "SCR", "latitude": 17.4339, "longitude": 78.5042, "category": "Junction", "platforms_count": 10, "facilities": ["Twin City Hub", "AC Lounges", "Metro Interchange", "MMTS Suburban Hub", "Wi-Fi"], "operational_status": "Operational"},

    # --- ADDITIONAL STRATEGIC JUNCTIONS & INTERCHANGES ---
    {"code": "SWM", "name": "Sawai Madhopur Junction", "state": "Rajasthan", "district": "Sawai Madhopur", "division": "Kota", "zone": "WCR", "latitude": 25.9928, "longitude": 76.3686, "category": "Junction", "platforms_count": 4, "facilities": ["Ranthambore National Park Gateway", "Waiting Hall", "Wi-Fi", "Rajdhani Stop"], "operational_status": "Operational"},
    {"code": "MTJ", "name": "Mathura Junction", "state": "Uttar Pradesh", "district": "Mathura", "division": "Agra", "zone": "NCR", "latitude": 27.4924, "longitude": 77.6737, "category": "Junction", "platforms_count": 10, "facilities": ["Major 7-Route Junction", "AC Waiting Hall", "Wi-Fi", "Food Plaza", "Express & Rajdhani Stop"], "operational_status": "Operational"},
    {"code": "LKO", "name": "Lucknow Charbagh", "state": "Uttar Pradesh", "district": "Lucknow", "division": "Lucknow NR", "zone": "NR", "latitude": 26.8317, "longitude": 80.9234, "category": "Terminal", "platforms_count": 9, "facilities": ["Heritage Architecture", "AC Lounge", "Wi-Fi", "Tejas Express Hub"], "operational_status": "Operational"},
    {"code": "MAO", "name": "Madgaon Junction", "state": "Goa", "district": "South Goa", "division": "Karwar", "zone": "KR", "latitude": 15.2736, "longitude": 73.9792, "category": "Junction", "platforms_count": 4, "facilities": ["Goa Main Terminus", "AC Lounge", "Wi-Fi", "Prepaid Taxi", "Jan Shatabdi Stop"], "operational_status": "Operational"},
    {"code": "KRMI", "name": "Karmali", "state": "Goa", "district": "North Goa", "division": "Karwar", "zone": "KR", "latitude": 15.4989, "longitude": 73.9214, "category": "Regular", "platforms_count": 2, "facilities": ["Panaji Gateway", "Waiting Hall", "Tejas Express Stop"], "operational_status": "Operational"},
    {"code": "DBG", "name": "Darbhanga Junction", "state": "Bihar", "district": "Darbhanga", "division": "Samastipur", "zone": "ECR", "latitude": 26.1522, "longitude": 85.8978, "category": "Junction", "platforms_count": 5, "facilities": ["Mithila Hub", "Amrit Bharat Terminus", "Wi-Fi"], "operational_status": "Operational"},
    {"code": "GNC", "name": "Gandhinagar Capital", "state": "Gujarat", "district": "Gandhinagar", "division": "Ahmedabad", "zone": "WR", "latitude": 23.2356, "longitude": 72.6394, "category": "Terminal", "platforms_count": 3, "facilities": ["Modern 5-Star Hotel Station", "Vande Bharat Terminus", "Wi-Fi"], "operational_status": "Operational"},
    {"code": "HAPA", "name": "Hapa", "state": "Gujarat", "district": "Jamnagar", "division": "Rajkot", "zone": "WR", "latitude": 22.4833, "longitude": 70.1333, "category": "Regular", "platforms_count": 3, "facilities": ["Jamnagar Industrial Terminal", "Duronto Stop", "Waiting Room"], "operational_status": "Operational"},
    {"code": "YPR", "name": "Yesvantpur Junction", "state": "Karnataka", "district": "Bengaluru Urban", "division": "Bengaluru", "zone": "SWR", "latitude": 13.0236, "longitude": 77.5503, "category": "Terminal", "platforms_count": 6, "facilities": ["Satellite Metro Terminal", "AC Lounges", "Duronto/Sampark Kranti Hub", "Wi-Fi"], "operational_status": "Operational"},
    {"code": "DEE", "name": "Delhi Sarai Rohilla", "state": "Delhi", "district": "Central Delhi", "division": "Delhi", "zone": "NR", "latitude": 28.6664, "longitude": 77.1819, "category": "Terminal", "platforms_count": 7, "facilities": ["Duronto/AC Express Terminus", "AC Waiting Hall", "Wi-Fi"], "operational_status": "Operational"}
]

# ==============================================================================
# 2. COMPREHENSIVE TRAIN MASTER DATABASE (ALL REQUIRED CATEGORIES)
# Covers MEMU, DEMU, Suburban EMU Locals, Superfast, Express, Passenger,
# Mail Express, Weekly/Biweekly, and Festival/Special Trains.
# ==============================================================================

TRAINS_DATA = [
    # --------------------------------------------------------------------------
    # CATEGORY A: MEMU TRAINS (Mainline Electric Multiple Unit)
    # --------------------------------------------------------------------------
    {
        "train_number": "09159",
        "train_name": "Bandra Terminus - Vapi MEMU Special",
        "train_category": "MEMU",
        "train_type": "MEMU",
        "source_station_code": "BDTS",
        "destination_station_code": "VAPI",
        "running_days": "1111111",
        "total_distance_km": 159.0,
        "duration_minutes": 210,
        "classes": ["2S"],
        "pantry_car": False,
        "return_train_number": "09160",
        "is_special": False,
        "source_of_data": "WR Official Timetable",
        "stops": [
            {"station_code": "BDTS", "seq": 1, "arr": None, "dep": "09:30", "halt": 0, "dist": 0.0, "day": 1, "plat": "4"},
            {"station_code": "BVI", "seq": 2, "arr": "09:58", "dep": "10:00", "halt": 2, "dist": 19.0, "day": 1, "plat": "8"},
            {"station_code": "BSR", "seq": 3, "arr": "10:25", "dep": "10:27", "halt": 2, "dist": 37.0, "day": 1, "plat": "6"},
            {"station_code": "VR", "seq": 4, "arr": "10:38", "dep": "10:40", "halt": 2, "dist": 45.0, "day": 1, "plat": "5"},
            {"station_code": "SAH", "seq": 5, "arr": "10:58", "dep": "11:00", "halt": 2, "dist": 61.0, "day": 1, "plat": "2"},
            {"station_code": "PLG", "seq": 6, "arr": "11:15", "dep": "11:17", "halt": 2, "dist": 76.0, "day": 1, "plat": "1"},
            {"station_code": "BOR", "seq": 7, "arr": "11:30", "dep": "11:32", "halt": 2, "dist": 87.0, "day": 1, "plat": "2"},
            {"station_code": "DRD", "seq": 8, "arr": "11:58", "dep": "12:00", "halt": 2, "dist": 109.0, "day": 1, "plat": "1"},
            {"station_code": "UBR", "seq": 9, "arr": "12:20", "dep": "12:22", "halt": 2, "dist": 130.0, "day": 1, "plat": "1"},
            {"station_code": "BLD", "seq": 10, "arr": "12:40", "dep": "12:42", "halt": 2, "dist": 147.0, "day": 1, "plat": "1"},
            {"station_code": "VAPI", "seq": 11, "arr": "13:00", "dep": None, "halt": 0, "dist": 159.0, "day": 1, "plat": "1"}
        ]
    },
    {
        "train_number": "09160",
        "train_name": "Vapi - Bandra Terminus MEMU Special",
        "train_category": "MEMU",
        "train_type": "MEMU",
        "source_station_code": "VAPI",
        "destination_station_code": "BDTS",
        "running_days": "1111111",
        "total_distance_km": 159.0,
        "duration_minutes": 205,
        "classes": ["2S"],
        "pantry_car": False,
        "return_train_number": "09159",
        "is_special": False,
        "source_of_data": "WR Official Timetable",
        "stops": [
            {"station_code": "VAPI", "seq": 1, "arr": None, "dep": "13:40", "halt": 0, "dist": 0.0, "day": 1, "plat": "2"},
            {"station_code": "BLD", "seq": 2, "arr": "13:54", "dep": "13:56", "halt": 2, "dist": 12.0, "day": 1, "plat": "2"},
            {"station_code": "UBR", "seq": 3, "arr": "14:12", "dep": "14:14", "halt": 2, "dist": 29.0, "day": 1, "plat": "2"},
            {"station_code": "DRD", "seq": 4, "arr": "14:35", "dep": "14:37", "halt": 2, "dist": 50.0, "day": 1, "plat": "2"},
            {"station_code": "BOR", "seq": 5, "arr": "14:55", "dep": "14:57", "halt": 2, "dist": 72.0, "day": 1, "plat": "1"},
            {"station_code": "PLG", "seq": 6, "arr": "15:10", "dep": "15:12", "halt": 2, "dist": 83.0, "day": 1, "plat": "2"},
            {"station_code": "SAH", "seq": 7, "arr": "15:28", "dep": "15:30", "halt": 2, "dist": 98.0, "day": 1, "plat": "1"},
            {"station_code": "VR", "seq": 8, "arr": "15:52", "dep": "15:54", "halt": 2, "dist": 114.0, "day": 1, "plat": "4"},
            {"station_code": "BSR", "seq": 9, "arr": "16:04", "dep": "16:06", "halt": 2, "dist": 122.0, "day": 1, "plat": "5"},
            {"station_code": "BVI", "seq": 10, "arr": "16:32", "dep": "16:34", "halt": 2, "dist": 140.0, "day": 1, "plat": "7"},
            {"station_code": "BDTS", "seq": 11, "arr": "17:05", "dep": None, "halt": 0, "dist": 159.0, "day": 1, "plat": "3"}
        ]
    },
    {
        "train_number": "09101",
        "train_name": "Virar - Bharuch MEMU",
        "train_category": "MEMU",
        "train_type": "MEMU",
        "source_station_code": "VR",
        "destination_station_code": "BH",
        "running_days": "1111111",
        "total_distance_km": 268.0,
        "duration_minutes": 330,
        "classes": ["2S"],
        "pantry_car": False,
        "return_train_number": "09102",
        "is_special": False,
        "source_of_data": "WR Official Timetable",
        "stops": [
            {"station_code": "VR", "seq": 1, "arr": None, "dep": "04:35", "halt": 0, "dist": 0.0, "day": 1, "plat": "5"},
            {"station_code": "SAH", "seq": 2, "arr": "04:54", "dep": "04:56", "halt": 2, "dist": 16.0, "day": 1, "plat": "2"},
            {"station_code": "KLV", "seq": 3, "arr": "05:04", "dep": "05:05", "halt": 1, "dist": 22.0, "day": 1, "plat": "1"},
            {"station_code": "PLG", "seq": 4, "arr": "05:15", "dep": "05:17", "halt": 2, "dist": 31.0, "day": 1, "plat": "1"},
            {"station_code": "BOR", "seq": 5, "arr": "05:30", "dep": "05:32", "halt": 2, "dist": 42.0, "day": 1, "plat": "2"},
            {"station_code": "DRD", "seq": 6, "arr": "05:58", "dep": "06:00", "halt": 2, "dist": 64.0, "day": 1, "plat": "1"},
            {"station_code": "UBR", "seq": 7, "arr": "06:21", "dep": "06:23", "halt": 2, "dist": 85.0, "day": 1, "plat": "1"},
            {"station_code": "VAPI", "seq": 8, "arr": "07:05", "dep": "07:07", "halt": 2, "dist": 114.0, "day": 1, "plat": "1"},
            {"station_code": "BL", "seq": 9, "arr": "07:45", "dep": "07:50", "halt": 5, "dist": 140.0, "day": 1, "plat": "3"},
            {"station_code": "BIM", "seq": 10, "arr": "08:08", "dep": "08:10", "halt": 2, "dist": 158.0, "day": 1, "plat": "1"},
            {"station_code": "NVS", "seq": 11, "arr": "08:30", "dep": "08:32", "halt": 2, "dist": 179.0, "day": 1, "plat": "1"},
            {"station_code": "ST", "seq": 12, "arr": "09:15", "dep": "09:20", "halt": 5, "dist": 208.0, "day": 1, "plat": "1"},
            {"station_code": "KIM", "seq": 13, "arr": "09:44", "dep": "09:46", "halt": 2, "dist": 232.0, "day": 1, "plat": "1"},
            {"station_code": "KSB", "seq": 14, "arr": "09:56", "dep": "09:58", "halt": 2, "dist": 240.0, "day": 1, "plat": "1"},
            {"station_code": "AKV", "seq": 15, "arr": "10:14", "dep": "10:16", "halt": 2, "dist": 259.0, "day": 1, "plat": "1"},
            {"station_code": "BH", "seq": 16, "arr": "10:35", "dep": None, "halt": 0, "dist": 268.0, "day": 1, "plat": "2"}
        ]
    },
    {
        "train_number": "69165",
        "train_name": "Ahmedabad - Anand MEMU",
        "train_category": "MEMU",
        "train_type": "MEMU",
        "source_station_code": "ADI",
        "destination_station_code": "ANND",
        "running_days": "1111111",
        "total_distance_km": 65.0,
        "duration_minutes": 90,
        "classes": ["2S"],
        "pantry_car": False,
        "return_train_number": "69166",
        "is_special": False,
        "source_of_data": "WR Official Timetable",
        "stops": [
            {"station_code": "ADI", "seq": 1, "arr": None, "dep": "07:30", "halt": 0, "dist": 0.0, "day": 1, "plat": "6"},
            {"station_code": "MAN", "seq": 2, "arr": "07:38", "dep": "07:40", "halt": 2, "dist": 3.0, "day": 1, "plat": "2"},
            {"station_code": "BJD", "seq": 3, "arr": "07:54", "dep": "07:55", "halt": 1, "dist": 17.0, "day": 1, "plat": "1"},
            {"station_code": "MHD", "seq": 4, "arr": "08:08", "dep": "08:10", "halt": 2, "dist": 28.0, "day": 1, "plat": "1"},
            {"station_code": "ND", "seq": 5, "arr": "08:26", "dep": "08:28", "halt": 2, "dist": 46.0, "day": 1, "plat": "1"},
            {"station_code": "ANND", "seq": 6, "arr": "09:00", "dep": None, "halt": 0, "dist": 65.0, "day": 1, "plat": "3"}
        ]
    },

    # --------------------------------------------------------------------------
    # CATEGORY B: DEMU TRAINS (Diesel Electric Multiple Unit)
    # --------------------------------------------------------------------------
    {
        "train_number": "71089",
        "train_name": "Diva - Roha DEMU",
        "train_category": "DEMU",
        "train_type": "DEMU",
        "source_station_code": "DI",
        "destination_station_code": "PNVL",
        "running_days": "1111111",
        "total_distance_km": 39.0,
        "duration_minutes": 50,
        "classes": ["2S"],
        "pantry_car": False,
        "return_train_number": "71090",
        "is_special": False,
        "source_of_data": "CR Official Timetable",
        "stops": [
            {"station_code": "DI", "seq": 1, "arr": None, "dep": "08:45", "halt": 0, "dist": 0.0, "day": 1, "plat": "7"},
            {"station_code": "PNVL", "seq": 2, "arr": "09:35", "dep": None, "halt": 0, "dist": 39.0, "day": 1, "plat": "5"}
        ]
    },

    # --------------------------------------------------------------------------
    # CATEGORY C & D: SUBURBAN LOCAL TRAINS (Western & Central Lines)
    # Includes Churchgate - Dahanu, Boisar - Dahanu, Virar - Dahanu, CSMT - Kalyan
    # --------------------------------------------------------------------------
    {
        "train_number": "93005",
        "train_name": "Churchgate - Dahanu Road Fast Local",
        "train_category": "Local",
        "train_type": "Suburban Local",
        "source_station_code": "CCG",
        "destination_station_code": "DRD",
        "running_days": "1111111",
        "total_distance_km": 124.0,
        "duration_minutes": 140,
        "classes": ["FC", "2S"],
        "pantry_car": False,
        "return_train_number": "93006",
        "is_special": False,
        "source_of_data": "WR Suburban Official Schedule",
        "stops": [
            {"station_code": "CCG", "seq": 1, "arr": None, "dep": "05:15", "halt": 0, "dist": 0.0, "day": 1, "plat": "3"},
            {"station_code": "BCL", "seq": 2, "arr": "05:24", "dep": "05:25", "halt": 1, "dist": 5.0, "day": 1, "plat": "3"},
            {"station_code": "DDR", "seq": 3, "arr": "05:32", "dep": "05:33", "halt": 1, "dist": 11.0, "day": 1, "plat": "4"},
            {"station_code": "BA", "seq": 4, "arr": "05:39", "dep": "05:40", "halt": 1, "dist": 16.0, "day": 1, "plat": "4"},
            {"station_code": "ADH", "seq": 5, "arr": "05:49", "dep": "05:50", "halt": 1, "dist": 23.0, "day": 1, "plat": "5"},
            {"station_code": "BVI", "seq": 6, "arr": "06:05", "dep": "06:07", "halt": 2, "dist": 35.0, "day": 1, "plat": "7"},
            {"station_code": "BYR", "seq": 7, "arr": "06:19", "dep": "06:20", "halt": 1, "dist": 44.0, "day": 1, "plat": "4"},
            {"station_code": "BSR", "seq": 8, "arr": "06:29", "dep": "06:30", "halt": 1, "dist": 52.0, "day": 1, "plat": "5"},
            {"station_code": "VR", "seq": 9, "arr": "06:39", "dep": "06:41", "halt": 2, "dist": 60.0, "day": 1, "plat": "4"},
            {"station_code": "VTN", "seq": 10, "arr": "06:50", "dep": "06:51", "halt": 1, "dist": 69.0, "day": 1, "plat": "1"},
            {"station_code": "SAH", "seq": 11, "arr": "06:59", "dep": "07:00", "halt": 1, "dist": 76.0, "day": 1, "plat": "1"},
            {"station_code": "KLV", "seq": 12, "arr": "07:08", "dep": "07:09", "halt": 1, "dist": 82.0, "day": 1, "plat": "1"},
            {"station_code": "PLG", "seq": 13, "arr": "07:18", "dep": "07:19", "halt": 1, "dist": 91.0, "day": 1, "plat": "1"},
            {"station_code": "UOI", "seq": 14, "arr": "07:25", "dep": "07:26", "halt": 1, "dist": 97.0, "day": 1, "plat": "1"},
            {"station_code": "BOR", "seq": 15, "arr": "07:32", "dep": "07:34", "halt": 2, "dist": 103.0, "day": 1, "plat": "2"},
            {"station_code": "VGN", "seq": 16, "arr": "07:43", "dep": "07:44", "halt": 1, "dist": 112.0, "day": 1, "plat": "1"},
            {"station_code": "DRD", "seq": 17, "arr": "07:58", "dep": None, "halt": 0, "dist": 124.0, "day": 1, "plat": "2"}
        ]
    },
    {
        "train_number": "93006",
        "train_name": "Dahanu Road - Churchgate Fast Local",
        "train_category": "Local",
        "train_type": "Suburban Local",
        "source_station_code": "DRD",
        "destination_station_code": "CCG",
        "running_days": "1111111",
        "total_distance_km": 124.0,
        "duration_minutes": 138,
        "classes": ["FC", "2S"],
        "pantry_car": False,
        "return_train_number": "93005",
        "is_special": False,
        "source_of_data": "WR Suburban Official Schedule",
        "stops": [
            {"station_code": "DRD", "seq": 1, "arr": None, "dep": "08:15", "halt": 0, "dist": 0.0, "day": 1, "plat": "1"},
            {"station_code": "VGN", "seq": 2, "arr": "08:26", "dep": "08:27", "halt": 1, "dist": 12.0, "day": 1, "plat": "2"},
            {"station_code": "BOR", "seq": 3, "arr": "08:35", "dep": "08:37", "halt": 2, "dist": 21.0, "day": 1, "plat": "1"},
            {"station_code": "UOI", "seq": 4, "arr": "08:44", "dep": "08:45", "halt": 1, "dist": 27.0, "day": 1, "plat": "2"},
            {"station_code": "PLG", "seq": 5, "arr": "08:52", "dep": "08:53", "halt": 1, "dist": 33.0, "day": 1, "plat": "2"},
            {"station_code": "KLV", "seq": 6, "arr": "09:02", "dep": "09:03", "halt": 1, "dist": 42.0, "day": 1, "plat": "2"},
            {"station_code": "SAH", "seq": 7, "arr": "09:12", "dep": "09:13", "halt": 1, "dist": 48.0, "day": 1, "plat": "2"},
            {"station_code": "VTN", "seq": 8, "arr": "09:21", "dep": "09:22", "halt": 1, "dist": 55.0, "day": 1, "plat": "2"},
            {"station_code": "VR", "seq": 9, "arr": "09:33", "dep": "09:35", "halt": 2, "dist": 64.0, "day": 1, "plat": "3"},
            {"station_code": "BSR", "seq": 10, "arr": "09:44", "dep": "09:45", "halt": 1, "dist": 72.0, "day": 1, "plat": "4"},
            {"station_code": "BYR", "seq": 11, "arr": "09:54", "dep": "09:55", "halt": 1, "dist": 80.0, "day": 1, "plat": "3"},
            {"station_code": "BVI", "seq": 12, "arr": "10:08", "dep": "10:10", "halt": 2, "dist": 89.0, "day": 1, "plat": "6"},
            {"station_code": "ADH", "seq": 13, "arr": "10:25", "dep": "10:26", "halt": 1, "dist": 101.0, "day": 1, "plat": "4"},
            {"station_code": "BA", "seq": 14, "arr": "10:35", "dep": "10:36", "halt": 1, "dist": 108.0, "day": 1, "plat": "3"},
            {"station_code": "DDR", "seq": 15, "arr": "10:42", "dep": "10:43", "halt": 1, "dist": 113.0, "day": 1, "plat": "3"},
            {"station_code": "BCL", "seq": 16, "arr": "10:50", "dep": "10:51", "halt": 1, "dist": 119.0, "day": 1, "plat": "2"},
            {"station_code": "CCG", "seq": 17, "arr": "11:00", "dep": None, "halt": 0, "dist": 124.0, "day": 1, "plat": "2"}
        ]
    },
    {
        "train_number": "93025",
        "train_name": "Boisar - Dahanu Road Shuttle Local",
        "train_category": "Local",
        "train_type": "Suburban Local",
        "source_station_code": "BOR",
        "destination_station_code": "DRD",
        "running_days": "1111111",
        "total_distance_km": 21.0,
        "duration_minutes": 25,
        "classes": ["2S"],
        "pantry_car": False,
        "return_train_number": "93026",
        "is_special": False,
        "source_of_data": "WR Suburban Official Schedule",
        "stops": [
            {"station_code": "BOR", "seq": 1, "arr": None, "dep": "14:10", "halt": 0, "dist": 0.0, "day": 1, "plat": "2"},
            {"station_code": "VGN", "seq": 2, "arr": "14:20", "dep": "14:21", "halt": 1, "dist": 9.0, "day": 1, "plat": "1"},
            {"station_code": "DRD", "seq": 3, "arr": "14:35", "dep": None, "halt": 0, "dist": 21.0, "day": 1, "plat": "2"}
        ]
    },
    {
        "train_number": "93026",
        "train_name": "Dahanu Road - Boisar Shuttle Local",
        "train_category": "Local",
        "train_type": "Suburban Local",
        "source_station_code": "DRD",
        "destination_station_code": "BOR",
        "running_days": "1111111",
        "total_distance_km": 21.0,
        "duration_minutes": 25,
        "classes": ["2S"],
        "pantry_car": False,
        "return_train_number": "93025",
        "is_special": False,
        "source_of_data": "WR Suburban Official Schedule",
        "stops": [
            {"station_code": "DRD", "seq": 1, "arr": None, "dep": "15:00", "halt": 0, "dist": 0.0, "day": 1, "plat": "1"},
            {"station_code": "VGN", "seq": 2, "arr": "15:11", "dep": "15:12", "halt": 1, "dist": 12.0, "day": 1, "plat": "2"},
            {"station_code": "BOR", "seq": 3, "arr": "15:25", "dep": None, "halt": 0, "dist": 21.0, "day": 1, "plat": "1"}
        ]
    },
    {
        "train_number": "97001",
        "train_name": "CSMT - Kalyan Slow Local",
        "train_category": "Local",
        "train_type": "Suburban Local",
        "source_station_code": "CSMT",
        "destination_station_code": "KYN",
        "running_days": "1111111",
        "total_distance_km": 54.0,
        "duration_minutes": 88,
        "classes": ["FC", "2S"],
        "pantry_car": False,
        "return_train_number": "97002",
        "is_special": False,
        "source_of_data": "CR Suburban Official Schedule",
        "stops": [
            {"station_code": "CSMT", "seq": 1, "arr": None, "dep": "06:10", "halt": 0, "dist": 0.0, "day": 1, "plat": "4"},
            {"station_code": "BY", "seq": 2, "arr": "06:17", "dep": "06:18", "halt": 1, "dist": 4.0, "day": 1, "plat": "2"},
            {"station_code": "DR", "seq": 3, "arr": "06:26", "dep": "06:27", "halt": 1, "dist": 9.0, "day": 1, "plat": "3"},
            {"station_code": "CLA", "seq": 4, "arr": "06:36", "dep": "06:37", "halt": 1, "dist": 15.0, "day": 1, "plat": "3"},
            {"station_code": "GC", "seq": 5, "arr": "06:44", "dep": "06:45", "halt": 1, "dist": 19.0, "day": 1, "plat": "3"},
            {"station_code": "TNA", "seq": 6, "arr": "07:05", "dep": "07:07", "halt": 2, "dist": 34.0, "day": 1, "plat": "4"},
            {"station_code": "DI", "seq": 7, "arr": "07:18", "dep": "07:19", "halt": 1, "dist": 42.0, "day": 1, "plat": "2"},
            {"station_code": "KYN", "seq": 8, "arr": "07:38", "dep": None, "halt": 0, "dist": 54.0, "day": 1, "plat": "5"}
        ]
    },

    # --------------------------------------------------------------------------
    # CATEGORY E: RAJDHANI & PREMIER SUPERFAST EXPRESS TRAINS
    # --------------------------------------------------------------------------
    {
        "train_number": "12953",
        "train_name": "August Kranti Tejas Rajdhani Express",
        "short_name": "AK Tejas Raj Ex",
        "train_category": "Rajdhani Express",
        "train_type": "Rajdhani",
        "source_station_code": "MMCT",
        "destination_station_code": "NZM",
        "running_days": "1111111",
        "total_distance_km": 1377.0,
        "duration_minutes": 993,
        "classes": ["1A", "2A", "3A"],
        "pantry_car": True,
        "return_train_number": "12954",
        "is_special": False,
        "is_active": True,
        "source_of_data": "CRIS / NTES Official Timetable",
        "last_verified_date": "2026-11-17",
        "aliases": [
            "12953",
            "AK Tejas Raj Ex",
            "AK Tejas Raj",
            "August Kranti",
            "August Kranti Tejas Rajdhani",
            "August Kranti Rajdhani",
            "Mumbai Central Nizamuddin Rajdhani",
            "MMCT NZM"
        ],
        "tags": ["Rajdhani", "Tejas", "Premium", "Overnight", "Superfast", "Express"],
        "stops": [
            {"station_code": "MMCT", "seq": 1, "arr": None, "dep": "17:10", "halt": 0, "dist": 0.0, "day": 1, "plat": "1"},
            {"station_code": "BVI", "seq": 2, "arr": "17:33", "dep": "17:35", "halt": 2, "dist": 30.0, "day": 1, "plat": "6"},
            {"station_code": "VAPI", "seq": 3, "arr": "19:17", "dep": "19:19", "halt": 2, "dist": 168.0, "day": 1, "plat": "1"},
            {"station_code": "BL", "seq": 4, "arr": "19:37", "dep": "19:39", "halt": 2, "dist": 194.0, "day": 1, "plat": "2"},
            {"station_code": "ST", "seq": 5, "arr": "20:30", "dep": "20:35", "halt": 5, "dist": 263.0, "day": 1, "plat": "1"},
            {"station_code": "BH", "seq": 6, "arr": "21:13", "dep": "21:15", "halt": 2, "dist": 322.0, "day": 1, "plat": "3"},
            {"station_code": "BRC", "seq": 7, "arr": "22:08", "dep": "22:18", "halt": 10, "dist": 392.0, "day": 1, "plat": "2"},
            {"station_code": "RTM", "seq": 8, "arr": "01:50", "dep": "01:53", "halt": 3, "dist": 653.0, "day": 2, "plat": "5"},
            {"station_code": "KOTA", "seq": 9, "arr": "04:35", "dep": "04:40", "halt": 5, "dist": 920.0, "day": 2, "plat": "1"},
            {"station_code": "SWM", "seq": 10, "arr": "05:43", "dep": "05:45", "halt": 2, "dist": 1028.0, "day": 2, "plat": "1"},
            {"station_code": "MTJ", "seq": 11, "arr": "07:58", "dep": "08:00", "halt": 2, "dist": 1243.0, "day": 2, "plat": "3"},
            {"station_code": "NZM", "seq": 12, "arr": "09:43", "dep": None, "halt": 0, "dist": 1377.0, "day": 2, "plat": "6"}
        ]
    },
    {
        "train_number": "12954",
        "train_name": "August Kranti Tejas Rajdhani Express",
        "short_name": "AK Tejas Raj Ex",
        "train_category": "Rajdhani Express",
        "train_type": "Rajdhani",
        "source_station_code": "NZM",
        "destination_station_code": "MMCT",
        "running_days": "1111111",
        "total_distance_km": 1377.0,
        "duration_minutes": 1000,
        "classes": ["1A", "2A", "3A"],
        "pantry_car": True,
        "return_train_number": "12953",
        "is_special": False,
        "is_active": True,
        "source_of_data": "CRIS / NTES Official Timetable",
        "last_verified_date": "2026-11-17",
        "aliases": [
            "12954",
            "AK Tejas Raj Ex",
            "AK Tejas Raj",
            "August Kranti",
            "August Kranti Tejas Rajdhani",
            "August Kranti Rajdhani",
            "Nizamuddin Mumbai Central Rajdhani",
            "NZM MMCT"
        ],
        "tags": ["Rajdhani", "Tejas", "Premium", "Overnight", "Superfast", "Express"],
        "stops": [
            {"station_code": "NZM", "seq": 1, "arr": None, "dep": "17:15", "halt": 0, "dist": 0.0, "day": 1, "plat": "6"},
            {"station_code": "MTJ", "seq": 2, "arr": "18:43", "dep": "18:45", "halt": 2, "dist": 134.0, "day": 1, "plat": "1"},
            {"station_code": "SWM", "seq": 3, "arr": "20:48", "dep": "20:50", "halt": 2, "dist": 349.0, "day": 1, "plat": "2"},
            {"station_code": "KOTA", "seq": 4, "arr": "22:00", "dep": "22:10", "halt": 10, "dist": 457.0, "day": 1, "plat": "2"},
            {"station_code": "RTM", "seq": 5, "arr": "01:05", "dep": "01:15", "halt": 10, "dist": 724.0, "day": 2, "plat": "4"},
            {"station_code": "BRC", "seq": 6, "arr": "04:39", "dep": "04:49", "halt": 10, "dist": 985.0, "day": 2, "plat": "1"},
            {"station_code": "BH", "seq": 7, "arr": "05:36", "dep": "05:38", "halt": 2, "dist": 1055.0, "day": 2, "plat": "4"},
            {"station_code": "ST", "seq": 8, "arr": "06:13", "dep": "06:18", "halt": 5, "dist": 1114.0, "day": 2, "plat": "2"},
            {"station_code": "BL", "seq": 9, "arr": "07:10", "dep": "07:12", "halt": 2, "dist": 1183.0, "day": 2, "plat": "3"},
            {"station_code": "VAPI", "seq": 10, "arr": "07:30", "dep": "07:32", "halt": 2, "dist": 1209.0, "day": 2, "plat": "2"},
            {"station_code": "BVI", "seq": 11, "arr": "09:10", "dep": "09:12", "halt": 2, "dist": 1347.0, "day": 2, "plat": "7"},
            {"station_code": "MMCT", "seq": 12, "arr": "09:55", "dep": None, "halt": 0, "dist": 1377.0, "day": 2, "plat": "1"}
        ]
    },
    {
        "train_number": "12951",
        "train_name": "Mumbai Tejas Rajdhani Express",
        "short_name": "Tejas Rajdhani",
        "train_category": "Rajdhani Express",
        "train_type": "Rajdhani",
        "source_station_code": "MMCT",
        "destination_station_code": "NDLS",
        "running_days": "1111111",
        "total_distance_km": 1384.0,
        "duration_minutes": 932,
        "classes": ["1A", "2A", "3A"],
        "pantry_car": True,
        "return_train_number": "12952",
        "is_special": False,
        "is_active": True,
        "source_of_data": "CRIS / NTES Official Timetable",
        "last_verified_date": "2026-11-17",
        "aliases": ["12951", "Mumbai Tejas Rajdhani", "Tejas Rajdhani", "Mumbai Rajdhani", "MMCT NDLS", "Mumbai Delhi Rajdhani"],
        "tags": ["Rajdhani", "Tejas", "Premium", "Overnight", "Superfast"],
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
        "short_name": "Tejas Rajdhani",
        "train_category": "Rajdhani Express",
        "train_type": "Rajdhani",
        "source_station_code": "NDLS",
        "destination_station_code": "MMCT",
        "running_days": "1111111",
        "total_distance_km": 1384.0,
        "duration_minutes": 935,
        "classes": ["1A", "2A", "3A"],
        "pantry_car": True,
        "return_train_number": "12951",
        "is_special": False,
        "is_active": True,
        "source_of_data": "CRIS / NTES Official Timetable",
        "last_verified_date": "2026-11-17",
        "aliases": ["12952", "Delhi Mumbai Tejas Rajdhani", "Tejas Rajdhani", "NDLS MMCT", "Delhi Mumbai Rajdhani"],
        "tags": ["Rajdhani", "Tejas", "Premium", "Overnight", "Superfast"],
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
    {
        "train_number": "12002",
        "train_name": "New Delhi - Rani Kamlapati (Bhopal) Shatabdi Express",
        "short_name": "Bhopal Shatabdi",
        "train_category": "Shatabdi Express",
        "train_type": "Shatabdi",
        "source_station_code": "NDLS",
        "destination_station_code": "RKMP",
        "running_days": "1111111",
        "total_distance_km": 707.0,
        "duration_minutes": 510,
        "classes": ["EC", "CC"],
        "pantry_car": True,
        "return_train_number": "12001",
        "is_special": False,
        "is_active": True,
        "source_of_data": "CRIS / NTES Official Timetable",
        "last_verified_date": "2026-11-17",
        "aliases": ["12002", "Bhopal Shatabdi", "NDLS RKMP", "Delhi Bhopal Shatabdi", "Shatabdi Express"],
        "tags": ["Shatabdi", "Day Train", "High Speed", "Superfast", "Express"],
        "stops": [
            {"station_code": "NDLS", "seq": 1, "arr": None, "dep": "06:00", "halt": 0, "dist": 0.0, "day": 1, "plat": "1"},
            {"station_code": "MTJ", "seq": 2, "arr": "07:19", "dep": "07:20", "halt": 1, "dist": 141.0, "day": 1, "plat": "1"},
            {"station_code": "AGC", "seq": 3, "arr": "07:50", "dep": "07:55", "halt": 5, "dist": 195.0, "day": 1, "plat": "1"},
            {"station_code": "GWL", "seq": 4, "arr": "09:23", "dep": "09:28", "halt": 5, "dist": 313.0, "day": 1, "plat": "1"},
            {"station_code": "VGLJ", "seq": 5, "arr": "10:45", "dep": "10:50", "halt": 5, "dist": 410.0, "day": 1, "plat": "1"},
            {"station_code": "BPL", "seq": 6, "arr": "14:07", "dep": "14:12", "halt": 5, "dist": 701.0, "day": 1, "plat": "1"},
            {"station_code": "RKMP", "seq": 7, "arr": "14:30", "dep": None, "halt": 0, "dist": 707.0, "day": 1, "plat": "1"}
        ]
    },
    {
        "train_number": "12051",
        "train_name": "Mumbai CSMT - Madgaon Jan Shatabdi Express",
        "short_name": "Jan Shatabdi Ex",
        "train_category": "Jan Shatabdi",
        "train_type": "Jan Shatabdi",
        "source_station_code": "CSMT",
        "destination_station_code": "MAO",
        "running_days": "1111111",
        "total_distance_km": 571.0,
        "duration_minutes": 520,
        "classes": ["CC", "2S"],
        "pantry_car": False,
        "return_train_number": "12052",
        "is_special": False,
        "is_active": True,
        "source_of_data": "CRIS / NTES Official Timetable",
        "last_verified_date": "2026-11-17",
        "aliases": ["12051", "Madgaon Jan Shatabdi", "Goa Jan Shatabdi", "CSMT MAO", "Jan Shatabdi Express"],
        "tags": ["Jan Shatabdi", "Konkan Railway", "Express", "Day Train"],
        "stops": [
            {"station_code": "CSMT", "seq": 1, "arr": None, "dep": "05:10", "halt": 0, "dist": 0.0, "day": 1, "plat": "18"},
            {"station_code": "DR", "seq": 2, "arr": "05:22", "dep": "05:25", "halt": 3, "dist": 9.0, "day": 1, "plat": "4"},
            {"station_code": "TNA", "seq": 3, "arr": "05:48", "dep": "05:50", "halt": 2, "dist": 34.0, "day": 1, "plat": "7"},
            {"station_code": "PNVL", "seq": 4, "arr": "06:23", "dep": "06:25", "halt": 2, "dist": 69.0, "day": 1, "plat": "7"},
            {"station_code": "KRMI", "seq": 5, "arr": "13:20", "dep": "13:22", "halt": 2, "dist": 540.0, "day": 1, "plat": "1"},
            {"station_code": "MAO", "seq": 6, "arr": "14:10", "dep": None, "halt": 0, "dist": 571.0, "day": 1, "plat": "1"}
        ]
    },
    {
        "train_number": "12267",
        "train_name": "Mumbai Central - Hapa AC Duronto Express",
        "short_name": "Hapa Duronto",
        "train_category": "Duronto Express",
        "train_type": "Duronto",
        "source_station_code": "MMCT",
        "destination_station_code": "HAPA",
        "running_days": "1111111",
        "total_distance_km": 807.0,
        "duration_minutes": 715,
        "classes": ["1A", "2A", "3A"],
        "pantry_car": True,
        "return_train_number": "12268",
        "is_special": False,
        "is_active": True,
        "source_of_data": "CRIS / NTES Official Timetable",
        "last_verified_date": "2026-11-17",
        "aliases": ["12267", "Mumbai Hapa Duronto", "Duronto Express", "MMCT HAPA"],
        "tags": ["Duronto", "AC Express", "Non-stop", "Premium", "Overnight"],
        "stops": [
            {"station_code": "MMCT", "seq": 1, "arr": None, "dep": "23:00", "halt": 0, "dist": 0.0, "day": 1, "plat": "1"},
            {"station_code": "ST", "seq": 2, "arr": "02:37", "dep": "02:42", "halt": 5, "dist": 263.0, "day": 2, "plat": "1"},
            {"station_code": "BRC", "seq": 3, "arr": "04:14", "dep": "04:24", "halt": 10, "dist": 392.0, "day": 2, "plat": "3"},
            {"station_code": "ADI", "seq": 4, "arr": "05:55", "dep": "06:05", "halt": 10, "dist": 491.0, "day": 2, "plat": "1"},
            {"station_code": "HAPA", "seq": 5, "arr": "10:55", "dep": None, "halt": 0, "dist": 807.0, "day": 2, "plat": "1"}
        ]
    },
    {
        "train_number": "12909",
        "train_name": "Bandra Terminus - Hazrat Nizamuddin Garib Rath Express",
        "short_name": "NZM Garib Rath",
        "train_category": "Garib Rath",
        "train_type": "Garib Rath",
        "source_station_code": "BDTS",
        "destination_station_code": "NZM",
        "running_days": "0101010",
        "total_distance_km": 1367.0,
        "duration_minutes": 1000,
        "classes": ["3A", "CC"],
        "pantry_car": False,
        "return_train_number": "12910",
        "is_special": False,
        "is_active": True,
        "source_of_data": "CRIS / NTES Official Timetable",
        "last_verified_date": "2026-11-17",
        "aliases": ["12909", "Delhi Garib Rath", "Garib Rath Express", "BDTS NZM"],
        "tags": ["Garib Rath", "AC 3 Tier", "Affordable AC", "Superfast"],
        "stops": [
            {"station_code": "BDTS", "seq": 1, "arr": None, "dep": "17:30", "halt": 0, "dist": 0.0, "day": 1, "plat": "4"},
            {"station_code": "BVI", "seq": 2, "arr": "17:55", "dep": "17:59", "halt": 4, "dist": 19.0, "day": 1, "plat": "8"},
            {"station_code": "ST", "seq": 3, "arr": "20:47", "dep": "20:52", "halt": 5, "dist": 252.0, "day": 1, "plat": "1"},
            {"station_code": "BRC", "seq": 4, "arr": "22:19", "dep": "22:29", "halt": 10, "dist": 381.0, "day": 1, "plat": "2"},
            {"station_code": "RTM", "seq": 5, "arr": "02:15", "dep": "02:20", "halt": 5, "dist": 642.0, "day": 2, "plat": "5"},
            {"station_code": "KOTA", "seq": 6, "arr": "05:20", "dep": "05:30", "halt": 10, "dist": 909.0, "day": 2, "plat": "1"},
            {"station_code": "MTJ", "seq": 7, "arr": "08:18", "dep": "08:20", "halt": 2, "dist": 1233.0, "day": 2, "plat": "3"},
            {"station_code": "NZM", "seq": 8, "arr": "10:10", "dep": None, "halt": 0, "dist": 1367.0, "day": 2, "plat": "6"}
        ]
    },
    {
        "train_number": "12907",
        "train_name": "Maharashtra Sampark Kranti Express",
        "short_name": "MH Sampark Kranti",
        "train_category": "Sampark Kranti",
        "train_type": "Sampark Kranti",
        "source_station_code": "BDTS",
        "destination_station_code": "NZM",
        "running_days": "0010001",
        "total_distance_km": 1367.0,
        "duration_minutes": 985,
        "classes": ["1A", "2A", "3A", "SL"],
        "pantry_car": True,
        "return_train_number": "12908",
        "is_special": False,
        "is_active": True,
        "source_of_data": "CRIS / NTES Official Timetable",
        "last_verified_date": "2026-11-17",
        "aliases": ["12907", "Sampark Kranti", "BDTS NZM", "Maharashtra Sampark Kranti"],
        "tags": ["Sampark Kranti", "Superfast", "Express", "Biweekly"],
        "stops": [
            {"station_code": "BDTS", "seq": 1, "arr": None, "dep": "17:30", "halt": 0, "dist": 0.0, "day": 1, "plat": "4"},
            {"station_code": "BVI", "seq": 2, "arr": "17:55", "dep": "17:59", "halt": 4, "dist": 19.0, "day": 1, "plat": "8"},
            {"station_code": "ST", "seq": 3, "arr": "20:47", "dep": "20:52", "halt": 5, "dist": 252.0, "day": 1, "plat": "1"},
            {"station_code": "BRC", "seq": 4, "arr": "22:19", "dep": "22:29", "halt": 10, "dist": 381.0, "day": 1, "plat": "2"},
            {"station_code": "KOTA", "seq": 5, "arr": "05:20", "dep": "05:30", "halt": 10, "dist": 909.0, "day": 2, "plat": "1"},
            {"station_code": "NZM", "seq": 6, "arr": "09:55", "dep": None, "halt": 0, "dist": 1367.0, "day": 2, "plat": "6"}
        ]
    },
    {
        "train_number": "22119",
        "train_name": "Mumbai CSMT - Karmali Tejas Express",
        "short_name": "Goa Tejas Ex",
        "train_category": "Tejas Express",
        "train_type": "Tejas",
        "source_station_code": "CSMT",
        "destination_station_code": "KRMI",
        "running_days": "0101010",
        "total_distance_km": 552.0,
        "duration_minutes": 510,
        "classes": ["EC", "CC"],
        "pantry_car": True,
        "return_train_number": "22120",
        "is_special": False,
        "is_active": True,
        "source_of_data": "CRIS / NTES Official Timetable",
        "last_verified_date": "2026-11-17",
        "aliases": ["22119", "CSMT Karmali Tejas", "Goa Tejas", "CSMT KRMI", "Tejas Express"],
        "tags": ["Tejas", "Premium", "Konkan Railway", "Day Train", "Superfast"],
        "stops": [
            {"station_code": "CSMT", "seq": 1, "arr": None, "dep": "05:50", "halt": 0, "dist": 0.0, "day": 1, "plat": "18"},
            {"station_code": "DR", "seq": 2, "arr": "06:00", "dep": "06:02", "halt": 2, "dist": 9.0, "day": 1, "plat": "4"},
            {"station_code": "TNA", "seq": 3, "arr": "06:23", "dep": "06:25", "halt": 2, "dist": 34.0, "day": 1, "plat": "7"},
            {"station_code": "PNVL", "seq": 4, "arr": "06:55", "dep": "06:57", "halt": 2, "dist": 69.0, "day": 1, "plat": "7"},
            {"station_code": "KRMI", "seq": 5, "arr": "14:20", "dep": None, "halt": 0, "dist": 552.0, "day": 1, "plat": "1"}
        ]
    },
    {
        "train_number": "15557",
        "train_name": "Darbhanga - Anand Vihar Terminal Amrit Bharat Express",
        "short_name": "Amrit Bharat Ex",
        "train_category": "Amrit Bharat",
        "train_type": "Amrit Bharat",
        "source_station_code": "DBG",
        "destination_station_code": "ANVT",
        "running_days": "0100100",
        "total_distance_km": 1137.0,
        "duration_minutes": 1280,
        "classes": ["SL", "2S"],
        "pantry_car": False,
        "return_train_number": "15558",
        "is_special": False,
        "is_active": True,
        "source_of_data": "CRIS / NTES Official Timetable",
        "last_verified_date": "2026-11-17",
        "aliases": ["15557", "Amrit Bharat Express", "Darbhanga Delhi Amrit Bharat", "DBG ANVT"],
        "tags": ["Amrit Bharat", "Push Pull", "Affordable", "Superfast"],
        "stops": [
            {"station_code": "DBG", "seq": 1, "arr": None, "dep": "15:00", "halt": 0, "dist": 0.0, "day": 1, "plat": "1"},
            {"station_code": "PNBE", "seq": 2, "arr": "18:45", "dep": "18:55", "halt": 10, "dist": 147.0, "day": 1, "plat": "4"},
            {"station_code": "DDU", "seq": 3, "arr": "22:15", "dep": "22:25", "halt": 10, "dist": 358.0, "day": 1, "plat": "6"},
            {"station_code": "PRYJ", "seq": 4, "arr": "01:00", "dep": "01:05", "halt": 5, "dist": 511.0, "day": 2, "plat": "2"},
            {"station_code": "CNB", "seq": 5, "arr": "03:30", "dep": "03:35", "halt": 5, "dist": 705.0, "day": 2, "plat": "1"},
            {"station_code": "ANVT", "seq": 6, "arr": "12:20", "dep": None, "halt": 0, "dist": 1137.0, "day": 2, "plat": "7"}
        ]
    },
    {
        "train_number": "22961",
        "train_name": "Mumbai Central - Ahmedabad Vande Bharat Express",
        "train_category": "Superfast",
        "train_type": "Vande Bharat",
        "source_station_code": "MMCT",
        "destination_station_code": "ADI",
        "running_days": "1111110",
        "total_distance_km": 491.0,
        "duration_minutes": 330,
        "classes": ["EC", "CC"],
        "pantry_car": True,
        "return_train_number": "22962",
        "is_special": False,
        "source_of_data": "CRIS / NTES Official Timetable",
        "stops": [
            {"station_code": "MMCT", "seq": 1, "arr": None, "dep": "15:45", "halt": 0, "dist": 0.0, "day": 1, "plat": "5"},
            {"station_code": "BVI", "seq": 2, "arr": "16:10", "dep": "16:13", "halt": 3, "dist": 30.0, "day": 1, "plat": "6"},
            {"station_code": "VAPI", "seq": 3, "arr": "17:40", "dep": "17:42", "halt": 2, "dist": 168.0, "day": 1, "plat": "1"},
            {"station_code": "ST", "seq": 4, "arr": "18:38", "dep": "18:43", "halt": 5, "dist": 263.0, "day": 1, "plat": "1"},
            {"station_code": "BRC", "seq": 5, "arr": "20:07", "dep": "20:10", "halt": 3, "dist": 392.0, "day": 1, "plat": "2"},
            {"station_code": "ADI", "seq": 6, "arr": "21:15", "dep": None, "halt": 0, "dist": 491.0, "day": 1, "plat": "1"}
        ]
    },
    {
        "train_number": "22962",
        "train_name": "Ahmedabad - Mumbai Central Vande Bharat Express",
        "train_category": "Superfast",
        "train_type": "Vande Bharat",
        "source_station_code": "ADI",
        "destination_station_code": "MMCT",
        "running_days": "1111110",
        "total_distance_km": 491.0,
        "duration_minutes": 340,
        "classes": ["EC", "CC"],
        "pantry_car": True,
        "return_train_number": "22961",
        "is_special": False,
        "source_of_data": "CRIS / NTES Official Timetable",
        "stops": [
            {"station_code": "ADI", "seq": 1, "arr": None, "dep": "06:05", "halt": 0, "dist": 0.0, "day": 1, "plat": "1"},
            {"station_code": "BRC", "seq": 2, "arr": "06:55", "dep": "06:58", "halt": 3, "dist": 99.0, "day": 1, "plat": "2"},
            {"station_code": "ST", "seq": 3, "arr": "08:15", "dep": "08:20", "halt": 5, "dist": 228.0, "day": 1, "plat": "1"},
            {"station_code": "VAPI", "seq": 4, "arr": "09:13", "dep": "09:15", "halt": 2, "dist": 323.0, "day": 1, "plat": "2"},
            {"station_code": "BVI", "seq": 5, "arr": "10:43", "dep": "10:45", "halt": 2, "dist": 461.0, "day": 1, "plat": "7"},
            {"station_code": "MMCT", "seq": 6, "arr": "11:45", "dep": None, "halt": 0, "dist": 491.0, "day": 1, "plat": "5"}
        ]
    },
    {
        "train_number": "22954",
        "train_name": "Gujarat Superfast Express",
        "train_category": "Superfast",
        "train_type": "Superfast",
        "source_station_code": "ADI",
        "destination_station_code": "MMCT",
        "running_days": "1111111",
        "total_distance_km": 491.0,
        "duration_minutes": 534,
        "classes": ["CC", "2S", "SL"],
        "pantry_car": False,
        "return_train_number": "22953",
        "is_special": False,
        "source_of_data": "WR Official Timetable",
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
    {
        "train_number": "22953",
        "train_name": "Gujarat Superfast Express",
        "train_category": "Superfast",
        "train_type": "Superfast",
        "source_station_code": "MMCT",
        "destination_station_code": "ADI",
        "running_days": "1111111",
        "total_distance_km": 491.0,
        "duration_minutes": 540,
        "classes": ["CC", "2S", "SL"],
        "pantry_car": False,
        "return_train_number": "22954",
        "is_special": False,
        "source_of_data": "WR Official Timetable",
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
        "train_category": "Superfast",
        "train_type": "Vande Bharat",
        "source_station_code": "NDLS",
        "destination_station_code": "BSB",
        "running_days": "1101111",
        "total_distance_km": 759.0,
        "duration_minutes": 480,
        "classes": ["EC", "CC"],
        "pantry_car": True,
        "return_train_number": "22435",
        "is_special": False,
        "source_of_data": "NR Official Timetable",
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
        "train_category": "Superfast",
        "train_type": "Vande Bharat",
        "source_station_code": "BSB",
        "destination_station_code": "NDLS",
        "running_days": "1101111",
        "total_distance_km": 759.0,
        "duration_minutes": 480,
        "classes": ["EC", "CC"],
        "pantry_car": True,
        "return_train_number": "22436",
        "is_special": False,
        "source_of_data": "NR Official Timetable",
        "stops": [
            {"station_code": "BSB", "seq": 1, "arr": None, "dep": "15:00", "halt": 0, "dist": 0.0, "day": 1, "plat": "1"},
            {"station_code": "PRYJ", "seq": 2, "arr": "16:30", "dep": "16:32", "halt": 2, "dist": 124.0, "day": 1, "plat": "6"},
            {"station_code": "CNB", "seq": 3, "arr": "18:30", "dep": "18:32", "halt": 2, "dist": 319.0, "day": 1, "plat": "1"},
            {"station_code": "NDLS", "seq": 4, "arr": "23:00", "dep": None, "halt": 0, "dist": 759.0, "day": 1, "plat": "16"}
        ]
    },
    {
        "train_number": "12009",
        "train_name": "Mumbai - Ahmedabad Shatabdi Express",
        "train_category": "Superfast",
        "train_type": "Shatabdi",
        "source_station_code": "MMCT",
        "destination_station_code": "ADI",
        "running_days": "1111110",
        "total_distance_km": 493.0,
        "duration_minutes": 385,
        "classes": ["EC", "CC"],
        "pantry_car": True,
        "return_train_number": "12010",
        "is_special": False,
        "source_of_data": "WR Official Timetable",
        "stops": [
            {"station_code": "MMCT", "seq": 1, "arr": None, "dep": "06:20", "halt": 0, "dist": 0.0, "day": 1, "plat": "1"},
            {"station_code": "BVI", "seq": 2, "arr": "06:43", "dep": "06:45", "halt": 2, "dist": 30.0, "day": 1, "plat": "6"},
            {"station_code": "ST", "seq": 3, "arr": "09:30", "dep": "09:35", "halt": 5, "dist": 263.0, "day": 1, "plat": "1"},
            {"station_code": "BRC", "seq": 4, "arr": "11:00", "dep": "11:05", "halt": 5, "dist": 392.0, "day": 1, "plat": "2"},
            {"station_code": "ADI", "seq": 5, "arr": "12:45", "dep": None, "halt": 0, "dist": 493.0, "day": 1, "plat": "1"}
        ]
    },

    # --------------------------------------------------------------------------
    # CATEGORY F: EXPRESS TRAINS
    # --------------------------------------------------------------------------
    {
        "train_number": "12933",
        "train_name": "Karnavati Express",
        "train_category": "Express",
        "train_type": "Intercity Express",
        "source_station_code": "MMCT",
        "destination_station_code": "ADI",
        "running_days": "1111111",
        "total_distance_km": 491.0,
        "duration_minutes": 465,
        "classes": ["CC", "2S"],
        "pantry_car": True,
        "return_train_number": "12934",
        "is_special": False,
        "source_of_data": "WR Official Timetable",
        "stops": [
            {"station_code": "MMCT", "seq": 1, "arr": None, "dep": "14:05", "halt": 0, "dist": 0.0, "day": 1, "plat": "4"},
            {"station_code": "BVI", "seq": 2, "arr": "14:28", "dep": "14:33", "halt": 5, "dist": 30.0, "day": 1, "plat": "6"},
            {"station_code": "VAPI", "seq": 3, "arr": "15:59", "dep": "16:01", "halt": 2, "dist": 168.0, "day": 1, "plat": "1"},
            {"station_code": "BL", "seq": 4, "arr": "16:24", "dep": "16:26", "halt": 2, "dist": 194.0, "day": 1, "plat": "2"},
            {"station_code": "ST", "seq": 5, "arr": "17:15", "dep": "17:20", "halt": 5, "dist": 263.0, "day": 1, "plat": "1"},
            {"station_code": "BH", "seq": 6, "arr": "18:02", "dep": "18:04", "halt": 2, "dist": 322.0, "day": 1, "plat": "3"},
            {"station_code": "BRC", "seq": 7, "arr": "19:02", "dep": "19:07", "halt": 5, "dist": 392.0, "day": 1, "plat": "2"},
            {"station_code": "ANND", "seq": 8, "arr": "19:41", "dep": "19:43", "halt": 2, "dist": 427.0, "day": 1, "plat": "3"},
            {"station_code": "ND", "seq": 9, "arr": "19:58", "dep": "20:00", "halt": 2, "dist": 446.0, "day": 1, "plat": "2"},
            {"station_code": "MAN", "seq": 10, "arr": "20:34", "dep": "20:36", "halt": 2, "dist": 488.0, "day": 1, "plat": "1"},
            {"station_code": "ADI", "seq": 11, "arr": "21:05", "dep": None, "halt": 0, "dist": 491.0, "day": 1, "plat": "2"}
        ]
    },
    {
        "train_number": "19015",
        "train_name": "Saurashtra Express",
        "train_category": "Express",
        "train_type": "Express",
        "source_station_code": "DDR",
        "destination_station_code": "ADI",
        "running_days": "1111111",
        "total_distance_km": 485.0,
        "duration_minutes": 595,
        "classes": ["3A", "SL", "2S"],
        "pantry_car": False,
        "return_train_number": "19016",
        "is_special": False,
        "source_of_data": "WR Official Timetable",
        "stops": [
            {"station_code": "DDR", "seq": 1, "arr": None, "dep": "09:20", "halt": 0, "dist": 0.0, "day": 1, "plat": "5"},
            {"station_code": "BVI", "seq": 2, "arr": "09:47", "dep": "09:52", "halt": 5, "dist": 24.0, "day": 1, "plat": "6"},
            {"station_code": "PLG", "seq": 3, "arr": "10:39", "dep": "10:41", "halt": 2, "dist": 81.0, "day": 1, "plat": "1"},
            {"station_code": "BOR", "seq": 4, "arr": "10:52", "dep": "10:54", "halt": 2, "dist": 92.0, "day": 1, "plat": "2"},
            {"station_code": "DRD", "seq": 5, "arr": "11:15", "dep": "11:17", "halt": 2, "dist": 114.0, "day": 1, "plat": "1"},
            {"station_code": "UBR", "seq": 6, "arr": "11:38", "dep": "11:40", "halt": 2, "dist": 135.0, "day": 1, "plat": "1"},
            {"station_code": "VAPI", "seq": 7, "arr": "12:08", "dep": "12:10", "halt": 2, "dist": 164.0, "day": 1, "plat": "1"},
            {"station_code": "BL", "seq": 8, "arr": "12:35", "dep": "12:40", "halt": 5, "dist": 190.0, "day": 1, "plat": "2"},
            {"station_code": "BIM", "seq": 9, "arr": "12:56", "dep": "12:58", "halt": 2, "dist": 208.0, "day": 1, "plat": "1"},
            {"station_code": "NVS", "seq": 10, "arr": "13:17", "dep": "13:19", "halt": 2, "dist": 229.0, "day": 1, "plat": "1"},
            {"station_code": "ST", "seq": 11, "arr": "14:10", "dep": "14:15", "halt": 5, "dist": 258.0, "day": 1, "plat": "1"},
            {"station_code": "BH", "seq": 12, "arr": "15:15", "dep": "15:20", "halt": 5, "dist": 317.0, "day": 1, "plat": "3"},
            {"station_code": "BRC", "seq": 13, "arr": "16:25", "dep": "16:30", "halt": 5, "dist": 387.0, "day": 1, "plat": "2"},
            {"station_code": "ANND", "seq": 14, "arr": "17:15", "dep": "17:17", "halt": 2, "dist": 422.0, "day": 1, "plat": "3"},
            {"station_code": "ND", "seq": 15, "arr": "17:35", "dep": "17:37", "halt": 2, "dist": 441.0, "day": 1, "plat": "2"},
            {"station_code": "ADI", "seq": 16, "arr": "19:15", "dep": None, "halt": 0, "dist": 485.0, "day": 1, "plat": "4"}
        ]
    },

    # --------------------------------------------------------------------------
    # CATEGORY G: PASSENGER TRAINS
    # --------------------------------------------------------------------------
    {
        "train_number": "59045",
        "train_name": "Bandra - Vapi Passenger Shuttle",
        "train_category": "Passenger",
        "train_type": "Passenger",
        "source_station_code": "BDTS",
        "destination_station_code": "VAPI",
        "running_days": "1111111",
        "total_distance_km": 159.0,
        "duration_minutes": 245,
        "classes": ["2S"],
        "pantry_car": False,
        "return_train_number": "59046",
        "is_special": False,
        "source_of_data": "WR Official Timetable",
        "stops": [
            {"station_code": "BDTS", "seq": 1, "arr": None, "dep": "09:10", "halt": 0, "dist": 0.0, "day": 1, "plat": "5"},
            {"station_code": "BVI", "seq": 2, "arr": "09:40", "dep": "09:42", "halt": 2, "dist": 19.0, "day": 1, "plat": "8"},
            {"station_code": "BSR", "seq": 3, "arr": "10:10", "dep": "10:12", "halt": 2, "dist": 37.0, "day": 1, "plat": "6"},
            {"station_code": "VR", "seq": 4, "arr": "10:25", "dep": "10:27", "halt": 2, "dist": 45.0, "day": 1, "plat": "5"},
            {"station_code": "SAH", "seq": 5, "arr": "10:48", "dep": "10:50", "halt": 2, "dist": 61.0, "day": 1, "plat": "2"},
            {"station_code": "PLG", "seq": 6, "arr": "11:08", "dep": "11:10", "halt": 2, "dist": 76.0, "day": 1, "plat": "1"},
            {"station_code": "BOR", "seq": 7, "arr": "11:24", "dep": "11:26", "halt": 2, "dist": 87.0, "day": 1, "plat": "2"},
            {"station_code": "DRD", "seq": 8, "arr": "11:50", "dep": "11:52", "halt": 2, "dist": 109.0, "day": 1, "plat": "1"},
            {"station_code": "UBR", "seq": 9, "arr": "12:15", "dep": "12:17", "halt": 2, "dist": 130.0, "day": 1, "plat": "1"},
            {"station_code": "VAPI", "seq": 10, "arr": "13:15", "dep": None, "halt": 0, "dist": 159.0, "day": 1, "plat": "1"}
        ]
    },

    # --------------------------------------------------------------------------
    # CATEGORY H: MAIL & MAIL EXPRESS TRAINS
    # --------------------------------------------------------------------------
    {
        "train_number": "12137",
        "train_name": "Punjab Mail",
        "train_category": "Mail Express",
        "train_type": "Mail Express",
        "source_station_code": "CSMT",
        "destination_station_code": "NDLS",
        "running_days": "1111111",
        "total_distance_km": 1541.0,
        "duration_minutes": 1530,
        "classes": ["1A", "2A", "3A", "SL"],
        "pantry_car": True,
        "return_train_number": "12138",
        "is_special": False,
        "source_of_data": "CR / NR Official Timetable",
        "stops": [
            {"station_code": "CSMT", "seq": 1, "arr": None, "dep": "19:35", "halt": 0, "dist": 0.0, "day": 1, "plat": "18"},
            {"station_code": "DR", "seq": 2, "arr": "19:47", "dep": "19:50", "halt": 3, "dist": 9.0, "day": 1, "plat": "5"},
            {"station_code": "KYN", "seq": 3, "arr": "20:32", "dep": "20:35", "halt": 3, "dist": 54.0, "day": 1, "plat": "4"},
            {"station_code": "BSL", "seq": 4, "arr": "02:05", "dep": "02:10", "halt": 5, "dist": 444.0, "day": 2, "plat": "4"},
            {"station_code": "BPL", "seq": 5, "arr": "09:10", "dep": "09:15", "halt": 5, "dist": 837.0, "day": 2, "plat": "2"},
            {"station_code": "VGLJ", "seq": 6, "arr": "13:30", "dep": "13:38", "halt": 8, "dist": 1129.0, "day": 2, "plat": "3"},
            {"station_code": "GWL", "seq": 7, "arr": "14:50", "dep": "14:52", "halt": 2, "dist": 1226.0, "day": 2, "plat": "2"},
            {"station_code": "AGC", "seq": 8, "arr": "17:00", "dep": "17:05", "halt": 5, "dist": 1344.0, "day": 2, "plat": "2"},
            {"station_code": "NDLS", "seq": 9, "arr": "21:05", "dep": None, "halt": 0, "dist": 1541.0, "day": 2, "plat": "5"}
        ]
    },

    # --------------------------------------------------------------------------
    # CATEGORY I & J: WEEKLY & BIWEEKLY TRAINS
    # --------------------------------------------------------------------------
    {
        "train_number": "22473",
        "train_name": "Bandra Terminus - Bikaner Superfast Weekly Express",
        "train_category": "Weekly",
        "train_type": "Superfast",
        "source_station_code": "BDTS",
        "destination_station_code": "BKN",
        "running_days": "0100000", # Runs Tuesdays only
        "total_distance_km": 1212.0,
        "duration_minutes": 1345,
        "classes": ["2A", "3A", "SL"],
        "pantry_car": False,
        "return_train_number": "22474",
        "is_special": False,
        "source_of_data": "WR / NWR Official Timetable",
        "stops": [
            {"station_code": "BDTS", "seq": 1, "arr": None, "dep": "14:40", "halt": 0, "dist": 0.0, "day": 1, "plat": "2"},
            {"station_code": "BVI", "seq": 2, "arr": "15:00", "dep": "15:03", "halt": 3, "dist": 19.0, "day": 1, "plat": "8"},
            {"station_code": "ST", "seq": 3, "arr": "18:10", "dep": "18:15", "halt": 5, "dist": 252.0, "day": 1, "plat": "1"},
            {"station_code": "BRC", "seq": 4, "arr": "19:52", "dep": "19:57", "halt": 5, "dist": 382.0, "day": 1, "plat": "2"},
            {"station_code": "ADI", "seq": 5, "arr": "21:45", "dep": "21:55", "halt": 10, "dist": 481.0, "day": 1, "plat": "1"},
            {"station_code": "BKN", "seq": 6, "arr": "13:05", "dep": None, "halt": 0, "dist": 1212.0, "day": 2, "plat": "1"}
        ]
    },
    {
        "train_number": "12939",
        "train_name": "Pune - Jaipur Biweekly Superfast Express",
        "train_category": "Weekly",
        "train_type": "Superfast",
        "source_station_code": "PUNE",
        "destination_station_code": "JP",
        "running_days": "0010001", # Runs Wednesday and Sunday
        "total_distance_km": 1294.0,
        "duration_minutes": 1335,
        "classes": ["1A", "2A", "3A", "SL"],
        "pantry_car": True,
        "return_train_number": "12940",
        "is_special": False,
        "source_of_data": "CR / NWR Official Timetable",
        "stops": [
            {"station_code": "PUNE", "seq": 1, "arr": None, "dep": "17:30", "halt": 0, "dist": 0.0, "day": 1, "plat": "1"},
            {"station_code": "LNL", "seq": 2, "arr": "18:28", "dep": "18:30", "halt": 2, "dist": 64.0, "day": 1, "plat": "2"},
            {"station_code": "KYN", "seq": 3, "arr": "19:57", "dep": "20:00", "halt": 3, "dist": 139.0, "day": 1, "plat": "7"},
            {"station_code": "BSR", "seq": 4, "arr": "20:55", "dep": "21:00", "halt": 5, "dist": 180.0, "day": 1, "plat": "6"},
            {"station_code": "ST", "seq": 5, "arr": "23:45", "dep": "23:50", "halt": 5, "dist": 396.0, "day": 1, "plat": "1"},
            {"station_code": "BRC", "seq": 6, "arr": "01:13", "dep": "01:23", "halt": 10, "dist": 526.0, "day": 2, "plat": "2"},
            {"station_code": "RTM", "seq": 7, "arr": "05:00", "dep": "05:05", "halt": 5, "dist": 787.0, "day": 2, "plat": "5"},
            {"station_code": "KOTA", "seq": 8, "arr": "08:50", "dep": "09:00", "halt": 10, "dist": 1053.0, "day": 2, "plat": "1"},
            {"station_code": "JP", "seq": 9, "arr": "13:45", "dep": None, "halt": 0, "dist": 1294.0, "day": 2, "plat": "2"}
        ]
    },

    # --------------------------------------------------------------------------
    # CATEGORY K & L: FESTIVAL & SPECIAL TRAINS (Date-Aware Validity)
    # --------------------------------------------------------------------------
    {
        "train_number": "09001",
        "train_name": "Mumbai Central - New Delhi AC Festival Special",
        "train_category": "Special",
        "train_type": "Special Fare",
        "source_station_code": "MMCT",
        "destination_station_code": "NDLS",
        "running_days": "0000100", # Runs Fridays
        "total_distance_km": 1384.0,
        "duration_minutes": 1020,
        "classes": ["2A", "3A", "3E"],
        "pantry_car": False,
        "return_train_number": "09002",
        "validity_start": "2026-10-15",
        "validity_end": "2026-12-15",
        "is_special": True,
        "source_of_data": "CRIS Special Notification #104/2026",
        "stops": [
            {"station_code": "MMCT", "seq": 1, "arr": None, "dep": "22:15", "halt": 0, "dist": 0.0, "day": 1, "plat": "2"},
            {"station_code": "BVI", "seq": 2, "arr": "22:45", "dep": "22:48", "halt": 3, "dist": 30.0, "day": 1, "plat": "6"},
            {"station_code": "ST", "seq": 3, "arr": "01:45", "dep": "01:50", "halt": 5, "dist": 263.0, "day": 2, "plat": "1"},
            {"station_code": "BRC", "seq": 4, "arr": "03:15", "dep": "03:25", "halt": 10, "dist": 392.0, "day": 2, "plat": "3"},
            {"station_code": "RTM", "seq": 5, "arr": "07:05", "dep": "07:15", "halt": 10, "dist": 653.0, "day": 2, "plat": "4"},
            {"station_code": "KOTA", "seq": 6, "arr": "11:20", "dep": "11:30", "halt": 10, "dist": 920.0, "day": 2, "plat": "1"},
            {"station_code": "NDLS", "seq": 7, "arr": "15:15", "dep": None, "halt": 0, "dist": 1384.0, "day": 2, "plat": "14"}
        ]
    },
    {
        "train_number": "09415",
        "train_name": "Bandra Terminus - Ahmedabad Diwali Special",
        "train_category": "Special",
        "train_type": "Special Fare",
        "source_station_code": "BDTS",
        "destination_station_code": "ADI",
        "running_days": "1001000", # Mondays and Thursdays
        "total_distance_km": 481.0,
        "duration_minutes": 470,
        "classes": ["3A", "SL", "2S"],
        "pantry_car": False,
        "return_train_number": "09416",
        "validity_start": "2026-10-20",
        "validity_end": "2026-11-30",
        "is_special": True,
        "source_of_data": "WR Diwali Special Circular #42",
        "stops": [
            {"station_code": "BDTS", "seq": 1, "arr": None, "dep": "19:25", "halt": 0, "dist": 0.0, "day": 1, "plat": "4"},
            {"station_code": "BVI", "seq": 2, "arr": "19:55", "dep": "20:00", "halt": 5, "dist": 19.0, "day": 1, "plat": "8"},
            {"station_code": "VAPI", "seq": 3, "arr": "22:00", "dep": "22:02", "halt": 2, "dist": 157.0, "day": 1, "plat": "1"},
            {"station_code": "ST", "seq": 4, "arr": "23:25", "dep": "23:30", "halt": 5, "dist": 252.0, "day": 1, "plat": "1"},
            {"station_code": "BRC", "seq": 5, "arr": "01:05", "dep": "01:10", "halt": 5, "dist": 382.0, "day": 2, "plat": "3"},
            {"station_code": "ANND", "seq": 6, "arr": "01:45", "dep": "01:47", "halt": 2, "dist": 417.0, "day": 2, "plat": "3"},
            {"station_code": "ADI", "seq": 7, "arr": "03:15", "dep": None, "halt": 0, "dist": 481.0, "day": 2, "plat": "5"}
        ]
    }
]

# ==============================================================================
# 3. SERVICE ADVISORIES & ALERTS DATA
# ==============================================================================

ALERTS_DATA = [
    {
        "title": "Winter Fog Precautionary Speed Restriction (Northern Railway)",
        "alert_type": "weather",
        "severity": "warning",
        "description": "Due to dense fog conditions in Delhi-NCR, Uttar Pradesh and Bihar sections, maximum speed is regulated to 75 km/h for safety. Rajdhani and Shatabdi trains may experience moderate delays of 15 to 45 minutes.",
        "affected_train_numbers": ["12951", "12952", "22436", "22435"],
        "affected_station_codes": ["NDLS", "CNB", "PRYJ", "BSB"]
    },
    {
        "title": "Palghar - Boisar Automatic Signaling Upgrade (Western Railway)",
        "alert_type": "maintenance",
        "severity": "info",
        "description": "Electronic interlocking and 4-aspect automatic signaling modernization on Palghar - Boisar - Dahanu Road suburban section. Expect minor 5 min regulation for suburban locals.",
        "affected_train_numbers": ["93005", "93006", "93025", "93026", "22954"],
        "affected_station_codes": ["PLG", "BOR", "DRD"]
    },
    {
        "title": "Special Festival Frequency Enhancement on Western Railway",
        "alert_type": "special",
        "severity": "info",
        "description": "Additional rake inducted to ensure 99.8% punctuality during festive rush on Western Railway and Northern Railway sectors.",
        "affected_train_numbers": ["22436", "22961", "22962", "09001", "09415"],
        "affected_station_codes": ["MMCT", "BDTS", "ADI", "NDLS"]
    }
]

# ==============================================================================
# 4. DATABASE SEEDING ENGINE
# ==============================================================================

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

    # 2. Seed Stations (Insert or Update with full fields)
    for s_data in STATIONS_DATA:
        existing = db.query(Station).filter(Station.code == s_data["code"]).first()
        if existing:
            for k, v in s_data.items():
                setattr(existing, k, v)
        else:
            st = Station(**s_data)
            db.add(st)
    db.commit()

    # 3. Seed Trains & Timetable Stops
    for t_data_raw in TRAINS_DATA:
        t_data = dict(t_data_raw)
        stops_info = t_data.pop("stops", [])
        train_num = t_data["train_number"]

        if "short_name" not in t_data or not t_data["short_name"]:
            t_data["short_name"] = t_data["train_name"][:30]
        if "aliases" not in t_data or not t_data["aliases"]:
            t_data["aliases"] = [
                t_data["train_number"],
                t_data["train_name"],
                f"{t_data['source_station_code']} {t_data['destination_station_code']}",
                f"{t_data['source_station_code']} to {t_data['destination_station_code']}"
            ]
        if "tags" not in t_data or not t_data["tags"]:
            t_data["tags"] = [t_data.get("train_category", "Express"), t_data.get("train_type", "Express")]

        existing_train = db.query(Train).filter(Train.train_number == train_num).first()
        if existing_train:
            for k, v in t_data.items():
                setattr(existing_train, k, v)
            train = existing_train
        else:
            train = Train(**t_data)
            db.add(train)
            db.flush()

        # Update / Insert Stops with distance_from_prev computation
        prev_dist = 0.0
        for s in stops_info:
            dist = float(s["dist"])
            dist_from_prev = s.get("distance_from_prev", round(dist - prev_dist, 1) if dist >= prev_dist else 0.0)
            prev_dist = dist

            existing_stop = db.query(Stop).filter(
                Stop.train_id == train.id,
                Stop.stop_sequence == s["seq"]
            ).first()

            if existing_stop:
                existing_stop.station_code = s["station_code"]
                existing_stop.arrival_time = s["arr"]
                existing_stop.departure_time = s["dep"]
                existing_stop.halt_minutes = s["halt"]
                existing_stop.distance_km = s["dist"]
                existing_stop.distance_from_prev = dist_from_prev
                existing_stop.day_number = s["day"]
                existing_stop.platform = s["plat"]
            else:
                stop = Stop(
                    train_id=train.id,
                    station_code=s["station_code"],
                    stop_sequence=s["seq"],
                    arrival_time=s["arr"],
                    departure_time=s["dep"],
                    halt_minutes=s["halt"],
                    distance_km=s["dist"],
                    distance_from_prev=dist_from_prev,
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
    print("Database seeding completed successfully: all stations and train categories updated.")

if __name__ == "__main__":
    from backend.app.database import SessionLocal, Base, engine
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db)
    db.close()
