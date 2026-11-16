export interface IntermediateStation {
  code: string;
  name: string;
  distance_km: number;
}

// Master corridor intermediate crossing stations data (Indian Railways Network)
export const CORRIDOR_INTERMEDIATE_STATIONS: Record<string, IntermediateStation[]> = {
  // --- Mumbai Suburban Section: MMCT <-> BVI ---
  'MMCT-BVI': [
    { code: 'MX', name: 'Mahalakshmi', distance_km: 2.0 },
    { code: 'PL', name: 'Lower Parel', distance_km: 4.0 },
    { code: 'PBHD', name: 'Prabhadevi', distance_km: 5.0 },
    { code: 'DDR', name: 'Dadar Western', distance_km: 6.0 },
    { code: 'MRU', name: 'Matunga Road', distance_km: 7.5 },
    { code: 'MM', name: 'Mahim Junction', distance_km: 9.0 },
    { code: 'BA', name: 'Bandra', distance_km: 10.5 },
    { code: 'KHAR', name: 'Khar Road', distance_km: 12.0 },
    { code: 'STC', name: 'Santa Cruz', distance_km: 14.0 },
    { code: 'VLP', name: 'Vile Parle', distance_km: 16.0 },
    { code: 'ADH', name: 'Andheri', distance_km: 18.0 },
    { code: 'JOS', name: 'Jogeshwari', distance_km: 20.0 },
    { code: 'RMAR', name: 'Ram Mandir', distance_km: 22.0 },
    { code: 'GMN', name: 'Goregaon', distance_km: 24.0 },
    { code: 'MDD', name: 'Malad', distance_km: 26.0 },
    { code: 'KILE', name: 'Kandivali', distance_km: 28.0 }
  ],

  // --- Western Mainline: BVI <-> VAPI ---
  'BVI-VAPI': [
    { code: 'DIC', name: 'Dahisar', distance_km: 33.0 },
    { code: 'MIRA', name: 'Mira Road', distance_km: 36.0 },
    { code: 'BYR', name: 'Bhayandar', distance_km: 40.0 },
    { code: 'NIG', name: 'Naigaon', distance_km: 44.0 },
    { code: 'BSR', name: 'Vasai Road', distance_km: 48.0 },
    { code: 'NSP', name: 'Nallasopara', distance_km: 52.0 },
    { code: 'VR', name: 'Virar', distance_km: 56.0 },
    { code: 'VTN', name: 'Vaitarna', distance_km: 64.0 },
    { code: 'SAH', name: 'Saphale', distance_km: 72.0 },
    { code: 'KLV', name: 'Kelve Road', distance_km: 78.0 },
    { code: 'PLG', name: 'Palghar', distance_km: 87.0 },
    { code: 'UOI', name: 'Umroli', distance_km: 94.0 },
    { code: 'BOR', name: 'Boisar', distance_km: 98.0 },
    { code: 'VGN', name: 'Vangaon', distance_km: 107.0 },
    { code: 'DRD', name: 'Dahanu Road', distance_km: 120.0 },
    { code: 'GVD', name: 'Gholvad', distance_km: 131.0 },
    { code: 'BRRD', name: 'Bordi Road', distance_km: 136.0 },
    { code: 'UBR', name: 'Umbergaon Road', distance_km: 141.0 },
    { code: 'SJN', name: 'Sanjan', distance_km: 146.0 },
    { code: 'BLD', name: 'Bhilad', distance_km: 157.0 },
    { code: 'KEB', name: 'Karambeli', distance_km: 162.0 }
  ],

  // --- Western Mainline: VAPI <-> ST (Surat) ---
  'VAPI-ST': [
    { code: 'BAGD', name: 'Bagwada', distance_km: 175.0 },
    { code: 'UVD', name: 'Udvada', distance_km: 178.0 },
    { code: 'PDI', name: 'Pardi', distance_km: 184.0 },
    { code: 'ATUL', name: 'Atul', distance_km: 188.0 },
    { code: 'BL', name: 'Valsad', distance_km: 195.0 },
    { code: 'DGI', name: 'Dungri', distance_km: 204.0 },
    { code: 'BIM', name: 'Bilimora Junction', distance_km: 213.0 },
    { code: 'AML', name: 'Amalsad', distance_km: 218.0 },
    { code: 'ACL', name: 'Ancheli', distance_km: 222.0 },
    { code: 'VDH', name: 'Vedchha', distance_km: 226.0 },
    { code: 'NVS', name: 'Navsari', distance_km: 234.0 },
    { code: 'MRL', name: 'Maroli', distance_km: 243.0 },
    { code: 'SCH', name: 'Sachin', distance_km: 249.0 },
    { code: 'URN', name: 'Udhna Junction', distance_km: 259.0 }
  ],

  // --- Western Mainline: ST (Surat) <-> BRC (Vadodara) ---
  'ST-BRC': [
    { code: 'UTR', name: 'Utran', distance_km: 267.0 },
    { code: 'KSE', name: 'Kosad', distance_km: 270.0 },
    { code: 'GYN', name: 'Gayan', distance_km: 275.0 },
    { code: 'SYN', name: 'Sayan', distance_km: 278.0 },
    { code: 'KIM', name: 'Kim', distance_km: 287.0 },
    { code: 'KSB', name: 'Kosamba Junction', distance_km: 296.0 },
    { code: 'HAT', name: 'Hathuran', distance_km: 300.0 },
    { code: 'PAO', name: 'Panoli', distance_km: 304.0 },
    { code: 'AKV', name: 'Ankleshwar Junction', distance_km: 314.0 },
    { code: 'BH', name: 'Bharuch Junction', distance_km: 323.0 },
    { code: 'CVJ', name: 'Chavaj', distance_km: 329.0 },
    { code: 'NIU', name: 'Nabipur', distance_km: 336.0 },
    { code: 'VRE', name: 'Varediya', distance_km: 343.0 },
    { code: 'PLJ', name: 'Palej', distance_km: 349.0 },
    { code: 'LND', name: 'Lakodara', distance_km: 356.0 },
    { code: 'MYG', name: 'Miyagam Karjan Junction', distance_km: 364.0 },
    { code: 'ITA', name: 'Itola', distance_km: 372.0 },
    { code: 'VRM', name: 'Varnama', distance_km: 376.0 },
    { code: 'MPR', name: 'Makarpura', distance_km: 383.0 },
    { code: 'VS', name: 'Vishvamitri', distance_km: 389.0 }
  ],

  // --- Western Mainline: BRC (Vadodara) <-> ADI (Ahmedabad) ---
  'BRC-ADI': [
    { code: 'BWS', name: 'Bajva', distance_km: 400.0 },
    { code: 'RNO', name: 'Ranoli', distance_km: 405.0 },
    { code: 'NDR', name: 'Nandesari', distance_km: 407.0 },
    { code: 'VDA', name: 'Vasad Junction', distance_km: 412.0 },
    { code: 'ADD', name: 'Adas Road', distance_km: 417.0 },
    { code: 'VXD', name: 'Vadod', distance_km: 421.0 },
    { code: 'ANND', name: 'Anand Junction', distance_km: 427.0 },
    { code: 'KBRV', name: 'Kanjari Boriyavi', distance_km: 435.0 },
    { code: 'UTD', name: 'Utarsanda', distance_km: 440.0 },
    { code: 'ND', name: 'Nadiad Junction', distance_km: 446.0 },
    { code: 'GTE', name: 'Gothaj', distance_km: 455.0 },
    { code: 'MHD', name: 'Mahemdavad Kheda Road', distance_km: 463.0 },
    { code: 'NEP', name: 'Nenpur', distance_km: 467.0 },
    { code: 'KANJ', name: 'Kanij', distance_km: 471.0 },
    { code: 'BJD', name: 'Barejadi Nandej', distance_km: 475.0 },
    { code: 'GER', name: 'Geratpur', distance_km: 478.0 },
    { code: 'VTA', name: 'Vatva', distance_km: 483.0 },
    { code: 'MAN', name: 'Maninagar', distance_km: 488.0 }
  ],

  // --- 12951 Fast Route: BVI <-> ST (No commercial halt at VAPI) ---
  'BVI-ST': [
    { code: 'BSR', name: 'Vasai Road', distance_km: 48.0 },
    { code: 'VR', name: 'Virar', distance_km: 56.0 },
    { code: 'SAH', name: 'Saphale', distance_km: 72.0 },
    { code: 'PLG', name: 'Palghar', distance_km: 87.0 },
    { code: 'BOR', name: 'Boisar', distance_km: 98.0 },
    { code: 'DRD', name: 'Dahanu Road', distance_km: 120.0 },
    { code: 'GVD', name: 'Gholvad', distance_km: 131.0 },
    { code: 'UBR', name: 'Umbergaon Road', distance_km: 141.0 },
    { code: 'BLD', name: 'Bhilad', distance_km: 157.0 },
    { code: 'VAPI', name: 'Vapi (Through Line)', distance_km: 168.0 },
    { code: 'UVD', name: 'Udvada', distance_km: 178.0 },
    { code: 'BL', name: 'Valsad', distance_km: 195.0 },
    { code: 'BIM', name: 'Bilimora Junction', distance_km: 213.0 },
    { code: 'NVS', name: 'Navsari', distance_km: 234.0 },
    { code: 'MRL', name: 'Maroli', distance_km: 243.0 },
    { code: 'URN', name: 'Udhna Junction', distance_km: 259.0 }
  ],

  // --- Western-Central Mainline: BRC <-> RTM (Ratlam) ---
  'BRC-RTM': [
    { code: 'CYI', name: 'Chhayapuri', distance_km: 396.0 },
    { code: 'PIL', name: 'Pilol', distance_km: 403.0 },
    { code: 'SMLA', name: 'Samlaya Junction', distance_km: 414.0 },
    { code: 'CPN', name: 'Champaner Road', distance_km: 425.0 },
    { code: 'DRL', name: 'Derol', distance_km: 437.0 },
    { code: 'GDA', name: 'Godhra Junction', distance_km: 458.0 },
    { code: 'TUWA', name: 'Tuwa', distance_km: 473.0 },
    { code: 'TMA', name: 'Timba Road', distance_km: 482.0 },
    { code: 'DK', name: 'Dakor', distance_km: 508.0 },
    { code: 'DHD', name: 'Dahod', distance_km: 532.0 },
    { code: 'MGN', name: 'Meghnagar', distance_km: 565.0 },
    { code: 'THDR', name: 'Thandla Road', distance_km: 573.0 },
    { code: 'BMI', name: 'Bamnia', distance_km: 608.0 }
  ],

  // --- Central Mainline: RTM <-> KOTA ---
  'RTM-KOTA': [
    { code: 'NGW', name: 'Nagda Junction', distance_km: 694.0 },
    { code: 'KUH', name: 'Khachrod', distance_km: 708.0 },
    { code: 'MEP', name: 'Mahidpur Road', distance_km: 725.0 },
    { code: 'VMA', name: 'Vikramgarh Alot', distance_km: 747.0 },
    { code: 'CMU', name: 'Chaumahla', distance_km: 770.0 },
    { code: 'SVA', name: 'Suwasra', distance_km: 786.0 },
    { code: 'SGZ', name: 'Shamgarh', distance_km: 800.0 },
    { code: 'GOH', name: 'Garoth', distance_km: 810.0 },
    { code: 'BWM', name: 'Bhawani Mandi', distance_km: 833.0 },
    { code: 'JHW', name: 'Jhalawar Road', distance_km: 849.0 },
    { code: 'RMA', name: 'Ramganj Mandi', distance_km: 861.0 },
    { code: 'MKX', name: 'Morak', distance_km: 872.0 },
    { code: 'DARA', name: 'Dara', distance_km: 886.0 }
  ],

  // --- Northern Mainline: KOTA <-> NDLS ---
  'KOTA-NDLS': [
    { code: 'KPTN', name: 'Keshorai Patan', distance_km: 933.0 },
    { code: 'LKE', name: 'Lakheri', distance_km: 981.0 },
    { code: 'SWM', name: 'Sawai Madhopur Junction', distance_km: 1028.0 },
    { code: 'GGC', name: 'Gangapur City', distance_km: 1092.0 },
    { code: 'SMVJ', name: 'Shri Mahabirji', distance_km: 1126.0 },
    { code: 'HAN', name: 'Hindaun City', distance_km: 1136.0 },
    { code: 'BXN', name: 'Bayana Junction', distance_km: 1168.0 },
    { code: 'BTE', name: 'Bharatpur Junction', distance_km: 1210.0 },
    { code: 'MTJ', name: 'Mathura Junction', distance_km: 1244.0 },
    { code: 'KSV', name: 'Kosi Kalan', distance_km: 1285.0 },
    { code: 'HDL', name: 'Hodal', distance_km: 1298.0 },
    { code: 'PWL', name: 'Palwal', distance_km: 1328.0 },
    { code: 'FDB', name: 'Faridabad', distance_km: 1357.0 },
    { code: 'NZM', name: 'Hazrat Nizamuddin', distance_km: 1377.0 }
  ],

  // --- Northern Corridor: NDLS <-> CNB ---
  'NDLS-CNB': [
    { code: 'GZB', name: 'Ghaziabad Junction', distance_km: 25.0 },
    { code: 'ALJN', name: 'Aligarh Junction', distance_km: 131.0 },
    { code: 'TDL', name: 'Tundla Junction', distance_km: 209.0 },
    { code: 'ETW', name: 'Etawah Junction', distance_km: 300.0 }
  ],

  // --- Northern Corridor: CNB <-> PRYJ ---
  'CNB-PRYJ': [
    { code: 'FTP', name: 'Fatehpur', distance_km: 518.0 },
    { code: 'SRO', name: 'Sirathu', distance_km: 578.0 }
  ],

  // --- Northern Corridor: PRYJ <-> BSB ---
  'PRYJ-BSB': [
    { code: 'JNH', name: 'Janghai Junction', distance_km: 690.0 },
    { code: 'BOY', name: 'Bhadohi', distance_km: 720.0 }
  ]
};

/**
 * Helper to fetch intermediate stations between any two station codes.
 * Works symmetrically regardless of direction (Down or Up trains).
 */
export function getIntermediateStations(
  code1: string,
  code2: string,
  dist1: number,
  dist2: number
): IntermediateStation[] {
  const directKey = `${code1}-${code2}`;
  const reverseKey = `${code2}-${code1}`;

  let list = CORRIDOR_INTERMEDIATE_STATIONS[directKey] || CORRIDOR_INTERMEDIATE_STATIONS[reverseKey];

  if (!list || list.length === 0) {
    // If no direct key, check if there's a broader corridor that contains both distances
    return [];
  }

  // Deep copy so we don't mutate master list
  let result = [...list];

  // If train is traveling in reverse direction (dist1 > dist2, e.g. Up train ADI -> MMCT)
  if (dist1 > dist2) {
    result.reverse();
  }

  return result;
}

/**
 * Estimate the passing time of a train through an intermediate non-stopping station.
 */
export function estimatePassingTime(
  stationDist: number,
  depDist: number,
  arrDist: number,
  depTimeStr: string | null | undefined,
  arrTimeStr: string | null | undefined
): string {
  if (!depTimeStr || !arrTimeStr || !depTimeStr.includes(':') || !arrTimeStr.includes(':')) {
    return '—';
  }

  try {
    const [h1, m1] = depTimeStr.split(':').map(Number);
    const [h2, m2] = arrTimeStr.split(':').map(Number);

    let depMins = h1 * 60 + m1;
    let arrMins = h2 * 60 + m2;
    if (arrMins < depMins) {
      arrMins += 1440; // Crossed midnight
    }

    const totalDist = Math.abs(arrDist - depDist);
    if (totalDist <= 0) return depTimeStr;

    const coveredDist = Math.abs(stationDist - depDist);
    const fraction = Math.min(1.0, Math.max(0.0, coveredDist / totalDist));

    const passMins = Math.round(depMins + fraction * (arrMins - depMins)) % 1440;
    const passH = Math.floor(passMins / 60);
    const passM = passMins % 60;

    return `${String(passH).padStart(2, '0')}:${String(passM).padStart(2, '0')}`;
  } catch {
    return '—';
  }
}
