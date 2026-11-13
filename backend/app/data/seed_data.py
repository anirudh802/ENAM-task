import json
import hashlib
from datetime import datetime, timedelta
from app.db.database import get_db, init_db

def compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

TENANTS_SEED = [
    {"id": "tenant-enam-01", "name": "ENAM Public Markets Fund", "created_at": "2026-01-01T00:00:00"},
    {"id": "tenant-test-02", "name": "Isolated Peer Fund", "created_at": "2026-01-01T00:00:00"}
]

USERS_SEED = [
    {"id": "user-enam-01", "tenant_id": "tenant-enam-01", "email": "basalt802@gmail.com", "role": "PORTFOLIO_MANAGER", "created_at": "2026-01-01T00:00:00"},
    {"id": "user-test-02", "tenant_id": "tenant-test-02", "email": "peer_analyst@fund.local", "role": "ANALYST", "created_at": "2026-01-01T00:00:00"}
]

# Canonical Company Master Keyed by Official Indian ISIN (F-06)
COMPANIES_SEED = [
    {"isin": "INE002A01018", "ticker": "RELIANCE.NS", "name": "Reliance Industries Ltd", "sector": "Energy & Conglomerate", "market_cap_tier": "Large Cap", "market_cap_cr": 1980000.0, "screener_slug": "reliance-industries", "description": "India's largest private enterprise spanning oil-to-chemicals, telecom (Jio), and retail."},
    {"isin": "INE155A01022", "ticker": "TATAMOTORS.NS", "name": "Tata Motors Ltd", "sector": "Automotive", "market_cap_tier": "Large Cap", "market_cap_cr": 310000.0, "screener_slug": "tata-motors", "description": "Global automotive manufacturer across commercial vehicles, passenger cars, EVs, and luxury (Jaguar Land Rover)."},
    {"isin": "INE806N01020", "ticker": "DIXON.NS", "name": "Dixon Technologies (India) Ltd", "sector": "Electronics EMS", "market_cap_tier": "Mid Cap", "market_cap_cr": 92000.0, "screener_slug": "dixon-technologies", "description": "Leading Indian electronic manufacturing services (EMS) company specializing in consumer electronics, mobiles, and home appliances."},
    {"isin": "INE849A01020", "ticker": "TRENT.NS", "name": "Trent Ltd", "sector": "Retail", "market_cap_tier": "Large Cap", "market_cap_cr": 235000.0, "screener_slug": "trent", "description": "Tata group's flagship retail entity operating Westside, Zudio, and Star Bazaar hypermarkets."},
    {"isin": "INE062Y01012", "ticker": "KAYNES.NS", "name": "Kaynes Technology India Ltd", "sector": "Defense & Aerospace EMS", "market_cap_tier": "Mid Cap", "market_cap_cr": 34000.0, "screener_slug": "kaynes-technology", "description": "Integrated electronics manufacturing player focusing on mission-critical aerospace, defense, automotive, and railway electronics."},
    {"isin": "INE736A01011", "ticker": "CDSL.NS", "name": "Central Depository Services (India) Ltd", "sector": "Financial Infrastructure", "market_cap_tier": "Mid Cap", "market_cap_cr": 31000.0, "screener_slug": "central-depository-services-india", "description": "First listed Indian securities depository providing dematerialized transaction services with ~70% market share in demat accounts."},
    {"isin": "INE040A01034", "ticker": "HDFCBANK.NS", "name": "HDFC Bank Ltd", "sector": "Banking", "market_cap_tier": "Large Cap", "market_cap_cr": 1320000.0, "screener_slug": "hdfc-bank", "description": "India's largest private sector bank following its historic merger with housing parent HDFC Ltd."},
    {"isin": "INE288B01029", "ticker": "DEEPAKNTR.NS", "name": "Deepak Nitrite Ltd", "sector": "Specialty Chemicals", "market_cap_tier": "Mid Cap", "market_cap_cr": 38000.0, "screener_slug": "deepak-nitrite", "description": "Leading chemical intermediates manufacturer dominating sodium nitrite, phenol, acetone, and optical brightening agents."},
    {"isin": "INE455K01017", "ticker": "POLYCAB.NS", "name": "Polycab India Ltd", "sector": "Capital Goods & Cables", "market_cap_tier": "Large Cap", "market_cap_cr": 98000.0, "screener_slug": "polycab-india", "description": "Market leader in wires & cables and fast-moving electrical goods (FMEG) with expansive domestic distribution."},
    {"isin": "INE262H01013", "ticker": "PERSISTENT.NS", "name": "Persistent Systems Ltd", "sector": "IT & Digital Services", "market_cap_tier": "Mid Cap", "market_cap_cr": 84000.0, "screener_slug": "persistent-systems", "description": "High-growth digital engineering and enterprise modernization IT services provider."},
    {"isin": "INE044A01036", "ticker": "SUNPHARMA.NS", "name": "Sun Pharmaceutical Industries Ltd", "sector": "Pharmaceuticals", "market_cap_tier": "Large Cap", "market_cap_cr": 425000.0, "screener_slug": "sun-pharmaceutical-industries", "description": "India's largest drugmaker with global footprint across specialty dermatology, ophthalmology, and generics."},
    {"isin": "INE018A01030", "ticker": "LT.NS", "name": "Larsen & Toubro Ltd", "sector": "Infrastructure & Defense", "market_cap_tier": "Large Cap", "market_cap_cr": 510000.0, "screener_slug": "larsen-toubro", "description": "National engineering, procurement, and construction (EPC) conglomerate executing mega infrastructure and defense projects."},
    {"isin": "INE280A01028", "ticker": "TITAN.NS", "name": "Titan Company Ltd", "sector": "Consumer Discretionary", "market_cap_tier": "Large Cap", "market_cap_cr": 315000.0, "screener_slug": "titan-company", "description": "Market leader in branded jewellery (Tanishq, Mia, CaratLane), watches, and lifestyle accessories."},
    {"isin": "INE042L01014", "ticker": "KPITTECH.NS", "name": "KPIT Technologies Ltd", "sector": "Automotive Software", "market_cap_tier": "Mid Cap", "market_cap_cr": 41000.0, "screener_slug": "kpit-technologies", "description": "Pure-play software engineering and autonomous driving/electrification solutions partner to global OEMs."},
    {"isin": "INE006I01046", "ticker": "ASTRAL.NS", "name": "Astral Ltd", "sector": "Building Materials", "market_cap_tier": "Mid Cap", "market_cap_cr": 52000.0, "screener_slug": "astral", "description": "Pioneer in CPVC piping and plumbing systems, diversifying into adhesives, bathware, and paints."},
    {"isin": "INE603J01030", "ticker": "PIIND.NS", "name": "PI Industries Ltd", "sector": "Agrochemicals & CSM", "market_cap_tier": "Large Cap", "market_cap_cr": 68000.0, "screener_slug": "pi-industries", "description": "Global custom synthesis and manufacturing (CSM) partner for innovator agrochemical and pharmaceutical molecules."},
    {"isin": "INE398R01022", "ticker": "SYNGENE.NS", "name": "Syngene International Ltd", "sector": "Biotech & CRO", "market_cap_tier": "Mid Cap", "market_cap_cr": 31000.0, "screener_slug": "syngene-international", "description": "Integrated scientific research and contract development and manufacturing organization (CDMO)."},
    {"isin": "INE227W01023", "ticker": "CLEAN.NS", "name": "Clean Science and Technology Ltd", "sector": "Specialty Chemicals", "market_cap_tier": "Small Cap", "market_cap_cr": 14000.0, "screener_slug": "clean-science-technology", "description": "Proprietary catalytic green chemistry manufacturer of performance chemicals like MEHQ, BHA, and DCC."},
    # Watchlist Tickers (Non-Portfolio)
    {"isin": "INE758T01015", "ticker": "ZOMATO.NS", "name": "Zomato Ltd (Eternal)", "sector": "Internet / Quick Commerce", "market_cap_tier": "Large Cap", "market_cap_cr": 230000.0, "screener_slug": "zomato", "description": "Market leader in food delivery and quick commerce (Blinkit) expanding into 'going-out' entertainment."},
    {"isin": "INE361B01024", "ticker": "DIVISLAB.NS", "name": "Divi's Laboratories Ltd", "sector": "Active Pharmaceutical Ingredients", "market_cap_tier": "Large Cap", "market_cap_cr": 155000.0, "screener_slug": "divis-laboratories", "description": "World's top supplier of generic APIs (Naproxen, Dextromethorphan) and custom synthesis for global pharma."},
    {"isin": "INE066F01012", "ticker": "HAL.NS", "name": "Hindustan Aeronautics Ltd", "sector": "Aerospace & Defense", "market_cap_tier": "Large Cap", "market_cap_cr": 295000.0, "screener_slug": "hindustan-aeronautics", "description": "State-backed monopoly manufacturer of fighter aircraft (Tejas), helicopters (Prachand), and avionics."},
    {"isin": "INE192R01011", "ticker": "DMART.NS", "name": "Avenue Supermarts Ltd (DMart)", "sector": "Value Retail", "market_cap_tier": "Large Cap", "market_cap_cr": 270000.0, "screener_slug": "avenue-supermarts", "description": "Lowest-cost everyday supermarket operator owning its store real estate with exceptional inventory turns."}
]

# Tenant Holdings (F-04: Confidential Portfolio Scoping for ENAM)
TENANT_HOLDINGS_SEED = [
    {"tenant_id": "tenant-enam-01", "isin": c["isin"], "ticker": c["ticker"], "shares_held": 50000.0, "conviction_level": "HIGH"}
    for c in COMPANIES_SEED[:18] # First 18 companies are in ENAM portfolio
]

# Market Technicals Seed
MARKET_EOD_SEED = [
    {"isin": "INE806N01020", "ticker": "DIXON.NS", "trade_date": "2026-11-12", "close_price": 15420.0, "volume": 1680000, "volume_sma_20d": 350000.0, "daily_return_pct": 5.2, "volume_multiple": 4.8},
    {"isin": "INE849A01020", "ticker": "TRENT.NS", "trade_date": "2026-11-12", "close_price": 6480.0, "volume": 820000, "volume_sma_20d": 790000.0, "daily_return_pct": 1.1, "volume_multiple": 1.04},
    {"isin": "INE155A01022", "ticker": "TATAMOTORS.NS", "trade_date": "2026-11-12", "close_price": 782.5, "volume": 24500000, "volume_sma_20d": 10200000.0, "daily_return_pct": -4.1, "volume_multiple": 2.40},
    {"isin": "INE062Y01012", "ticker": "KAYNES.NS", "trade_date": "2026-11-12", "close_price": 5840.0, "volume": 940000, "volume_sma_20d": 260000.0, "daily_return_pct": 6.8, "volume_multiple": 3.62},
    {"isin": "INE736A01011", "ticker": "CDSL.NS", "trade_date": "2026-11-12", "close_price": 1520.0, "volume": 3900000, "volume_sma_20d": 1390000.0, "daily_return_pct": 3.8, "volume_multiple": 2.81},
    {"isin": "INE002A01018", "ticker": "RELIANCE.NS", "trade_date": "2026-11-12", "close_price": 2715.0, "volume": 5100000, "volume_sma_20d": 4900000.0, "daily_return_pct": 0.4, "volume_multiple": 1.04},
    {"isin": "INE455K01017", "ticker": "POLYCAB.NS", "trade_date": "2026-11-12", "close_price": 6550.0, "volume": 410000, "volume_sma_20d": 390000.0, "daily_return_pct": 2.1, "volume_multiple": 1.05},
    {"isin": "INE040A01034", "ticker": "HDFCBANK.NS", "trade_date": "2026-11-12", "close_price": 1740.0, "volume": 12100000, "volume_sma_20d": 11800000.0, "daily_return_pct": -0.2, "volume_multiple": 1.03},
    {"isin": "INE288B01029", "ticker": "DEEPAKNTR.NS", "trade_date": "2026-11-12", "close_price": 2740.0, "volume": 850000, "volume_sma_20d": 380000.0, "daily_return_pct": -3.6, "volume_multiple": 2.24},
    {"isin": "INE262H01013", "ticker": "PERSISTENT.NS", "trade_date": "2026-11-12", "close_price": 5410.0, "volume": 320000, "volume_sma_20d": 310000.0, "daily_return_pct": 1.8, "volume_multiple": 1.03},
    {"isin": "INE044A01036", "ticker": "SUNPHARMA.NS", "trade_date": "2026-11-12", "close_price": 1780.0, "volume": 1400000, "volume_sma_20d": 1450000.0, "daily_return_pct": 0.9, "volume_multiple": 0.97},
    {"isin": "INE018A01030", "ticker": "LT.NS", "trade_date": "2026-11-12", "close_price": 3610.0, "volume": 1800000, "volume_sma_20d": 1750000.0, "daily_return_pct": 1.2, "volume_multiple": 1.03},
    {"isin": "INE280A01028", "ticker": "TITAN.NS", "trade_date": "2026-11-12", "close_price": 3290.0, "volume": 980000, "volume_sma_20d": 950000.0, "daily_return_pct": 1.4, "volume_multiple": 1.03},
    {"isin": "INE042L01014", "ticker": "KPITTECH.NS", "trade_date": "2026-11-12", "close_price": 1610.0, "volume": 610000, "volume_sma_20d": 580000.0, "daily_return_pct": -1.5, "volume_multiple": 1.05},
    {"isin": "INE006I01046", "ticker": "ASTRAL.NS", "trade_date": "2026-11-12", "close_price": 1890.0, "volume": 250000, "volume_sma_20d": 240000.0, "daily_return_pct": 0.3, "volume_multiple": 1.04},
    {"isin": "INE603J01030", "ticker": "PIIND.NS", "trade_date": "2026-11-12", "close_price": 4350.0, "volume": 210000, "volume_sma_20d": 200000.0, "daily_return_pct": 1.6, "volume_multiple": 1.05},
    {"isin": "INE398R01022", "ticker": "SYNGENE.NS", "trade_date": "2026-11-12", "close_price": 820.0, "volume": 350000, "volume_sma_20d": 340000.0, "daily_return_pct": -0.8, "volume_multiple": 1.03},
    {"isin": "INE227W01023", "ticker": "CLEAN.NS", "trade_date": "2026-11-12", "close_price": 1410.0, "volume": 120000, "volume_sma_20d": 1150000.0, "daily_return_pct": 0.1, "volume_multiple": 1.04},
]

# Corporate Announcements with SHA-256 Content Hash (F-08)
ANNOUNCEMENTS_SEED = [
    {
        "id": "ann-kaynes-mgmt-01",
        "isin": "INE062Y01012",
        "ticker": "KAYNES.NS",
        "category": "management_change",
        "title": "Appointment of Mr. Vikram Seth as Chief Operating Officer (COO)",
        "description": "Kaynes Technology India Limited has appointed Mr. Vikram Seth as COO effective December 1, 2026. He previously led manufacturing operations at Dixon Technologies and holds a B.Tech from IIT Kanpur.",
        "filing_time": (datetime.now() - timedelta(hours=3)).isoformat(),
        "materiality_score": 9,
        "content_hash": compute_hash("Kaynes Technology India Limited appointment Vikram Seth COO Dec 2026"),
        "financial_basis": "CONSOLIDATED",
        "headline_metrics": None,
        "executive_profile": {
            "name": "Vikram Seth",
            "role": "Chief Operating Officer",
            "previous_employer": "Dixon Technologies (India) Ltd",
            "previous_title": "Senior VP - Electronics Manufacturing",
            "education": "B.Tech Mechanical Engineering, IIT Kanpur (Class of 2004)",
            "tenure_past": "8 years at Dixon, 6 years at Foxconn India"
        },
        "network_connection": {
            "connected_person_id": "net-01",
            "connected_person_name": "Ananya Roy",
            "relationship": "IIT Kanpur 2004 Batchmate (Computer Science)",
            "degree_of_separation": 1,
            "context": "Ananya Roy is in your network (Strength: 5/5). She co-founded an IoT hardware venture with Vikram during college and has maintained close personal contact."
        }
    },
    {
        "id": "ann-dixon-results-q2",
        "isin": "INE806N01020",
        "ticker": "DIXON.NS",
        "category": "results",
        "title": "Unaudited Financial Results for Quarter ended September 30, 2026",
        "description": "Board approved Q2FY25 standalone and consolidated results. Stellar performance in mobile phone assembly; consolidated revenue up 120% YoY.",
        "filing_time": (datetime.now() - timedelta(hours=5)).isoformat(),
        "materiality_score": 10,
        "content_hash": compute_hash("Dixon Technologies Unaudited Financial Results Q2FY25 Sept 30 2026"),
        "financial_basis": "CONSOLIDATED",
        "headline_metrics": {
            "revenue_cr": 11534.0,
            "ebitda_cr": 420.0,
            "ebitda_margin_pct": 3.64,
            "pbt_cr": 482.0,
            "pat_cr": 412.0,
            "revenue_qoq_pct": 75.2,
            "revenue_yoy_pct": 120.4,
            "pat_qoq_pct": 96.8,
            "pat_yoy_pct": 263.1
        },
        "executive_profile": None,
        "network_connection": {
            "connected_person_id": "net-02",
            "connected_person_name": "Rohan Deshmukh",
            "relationship": "Director of Sourcing, Xiaomi India (Key Dixon Client)",
            "degree_of_separation": 1,
            "context": "Rohan manages Dixon's largest customer assembly line. Best person to speak with on component pipeline and Q3 production run-rate."
        }
    },
    {
        "id": "ann-deepak-mgmt-02",
        "isin": "INE288B01029",
        "ticker": "DEEPAKNTR.NS",
        "category": "management_change",
        "title": "Resignation of Chief Financial Officer Sanjay Upadhyay; Transition Plan",
        "description": "Mr. Sanjay Upadhyay has tendered resignation due to health reasons after 12 years. Board announces Ms. Radhika Sharma (ex-Tata Chemicals) as CFO designate.",
        "filing_time": (datetime.now() - timedelta(hours=6)).isoformat(),
        "materiality_score": 9,
        "content_hash": compute_hash("Deepak Nitrite CFO Sanjay Upadhyay resignation Radhika Sharma"),
        "financial_basis": "CONSOLIDATED",
        "headline_metrics": None,
        "executive_profile": {
            "name": "Radhika Sharma",
            "role": "Chief Financial Officer (Designate)",
            "previous_employer": "Tata Chemicals Ltd",
            "previous_title": "VP Finance & Treasury",
            "education": "Chartered Accountant (AIR 14), B.Com Shri Ram College of Commerce"
        },
        "network_connection": {
            "connected_person_id": "net-03",
            "connected_person_name": "Karan Mehra",
            "relationship": "Senior Partner, BSR & Co (Auditor)",
            "degree_of_separation": 1,
            "context": "Karan was lead engagement partner on Tata Chemicals audit while Radhika was VP Finance."
        }
    },
    {
        "id": "ann-trent-results-q2",
        "isin": "INE849A01020",
        "ticker": "TRENT.NS",
        "category": "results",
        "title": "Financial Results for the Second Quarter ended September 30, 2026",
        "description": "Standalone revenue at Rs 4,035 Cr (+39% YoY). Operating margin at 15.3%. Zudio footprint crossed 570 stores.",
        "filing_time": (datetime.now() - timedelta(hours=14)).isoformat(),
        "materiality_score": 9,
        "content_hash": compute_hash("Trent Financial Results Q2FY25 Sept 30 2026 Zudio 570 stores"),
        "financial_basis": "STANDALONE",
        "headline_metrics": {
            "revenue_cr": 4035.0,
            "ebitda_cr": 617.0,
            "ebitda_margin_pct": 15.29,
            "pbt_cr": 465.0,
            "pat_cr": 335.0,
            "revenue_qoq_pct": 1.2,
            "revenue_yoy_pct": 39.1,
            "pat_qoq_pct": -4.2,
            "pat_yoy_pct": 46.2
        },
        "executive_profile": None,
        "network_connection": {
            "connected_person_id": "net-04",
            "connected_person_name": "Pooja Singhania",
            "relationship": "Ex-Head of Merchandising, Trent Ltd (now at Nykaa)",
            "degree_of_separation": 1,
            "context": "Pooja worked at Trent for 7 years until 2024. Great natural reason to reconnect and ask about Zudio supply chain inventory turns."
        }
    },
    {
        "id": "ann-reliance-ma-01",
        "isin": "INE002A01018",
        "ticker": "RELIANCE.NS",
        "category": "M&A",
        "title": "Completion of Media JV with The Walt Disney Company",
        "description": "Reliance Industries Limited, Viacom18, and The Walt Disney Company announce the successful closing of their strategic transaction to create an Indian media titan valued at Rs 70,352 Cr.",
        "filing_time": (datetime.now() - timedelta(hours=18)).isoformat(),
        "materiality_score": 8,
        "content_hash": compute_hash("Reliance Viacom18 Disney media transaction 70352 cr"),
        "financial_basis": "CONSOLIDATED",
        "headline_metrics": None,
        "executive_profile": None,
        "network_connection": None
    },
    {
        "id": "ann-kaynes-capex-01",
        "isin": "INE062Y01012",
        "ticker": "KAYNES.NS",
        "category": "capex",
        "title": "Groundbreaking of Semiconductor OSAT Facility at Sanand, Gujarat",
        "description": "Kaynes Semicon Private Limited commenced construction of its advanced semiconductor packaging and test facility with total planned capex of Rs 3,300 Cr supported by India Semiconductor Mission.",
        "filing_time": (datetime.now() - timedelta(hours=22)).isoformat(),
        "materiality_score": 8,
        "content_hash": compute_hash("Kaynes Semicon OSAT facility Sanand Gujarat 3300 cr"),
        "financial_basis": "CONSOLIDATED",
        "headline_metrics": None,
        "executive_profile": None,
        "network_connection": None
    },
    {
        "id": "ann-polycab-lit-01",
        "isin": "INE455K01017",
        "ticker": "POLYCAB.NS",
        "category": "litigation",
        "title": "Regulatory Clarification Regarding Income Tax Department Assessment",
        "description": "Company clarifies that search assessments have concluded with demand order of Rs 42 Cr for disputed expense disallowances, which the company is contesting in appeal. No impact on business operations.",
        "filing_time": (datetime.now() - timedelta(days=1, hours=4)).isoformat(),
        "materiality_score": 7,
        "content_hash": compute_hash("Polycab income tax assessment clarification 42 cr"),
        "financial_basis": "CONSOLIDATED",
        "headline_metrics": None,
        "executive_profile": None,
        "network_connection": None
    },
    {
        "id": "ann-tatamotors-results-q2",
        "isin": "INE155A01022",
        "ticker": "TATAMOTORS.NS",
        "category": "results",
        "title": "Consolidated Financial Results for Q2 FY25",
        "description": "Revenue at Rs 101,450 Cr (-0.4% YoY). JLR EBIT margin stood at 5.1% impacted by temporary flooding at high-grade aluminum supplier Novelis. Indian commercial vehicle business maintained healthy margins.",
        "filing_time": (datetime.now() - timedelta(days=1, hours=8)).isoformat(),
        "materiality_score": 9,
        "content_hash": compute_hash("Tata Motors Q2FY25 consolidated results JLR 5.1 margin"),
        "financial_basis": "CONSOLIDATED",
        "headline_metrics": {
            "revenue_cr": 101450.0,
            "ebitda_cr": 11565.0,
            "ebitda_margin_pct": 11.40,
            "pbt_cr": 4980.0,
            "pat_cr": 3450.0,
            "revenue_qoq_pct": -6.1,
            "revenue_yoy_pct": -0.4,
            "pat_qoq_pct": -34.8,
            "pat_yoy_pct": -11.2
        },
        "executive_profile": None,
        "network_connection": {
            "connected_person_id": "net-05",
            "connected_person_name": "Siddharth Verma",
            "relationship": "VP Supply Chain, Tata Motors Commercial Vehicles",
            "degree_of_separation": 1,
            "context": "IIT Kanpur senior alumnus. Can provide on-the-ground clarity on domestic truck tonnage demand and raw material steel cost pass-through."
        }
    },
    {
        "id": "ann-hdfc-esop-01",
        "isin": "INE040A01034",
        "ticker": "HDFCBANK.NS",
        "category": "unclassified",
        "title": "Allotment of Equity Shares under Employee Stock Option Scheme",
        "description": "Allotment of 18,240 equity shares of face value Re 1 each pursuant to exercise of stock options.",
        "filing_time": (datetime.now() - timedelta(hours=2)).isoformat(),
        "materiality_score": 2,
        "content_hash": compute_hash("HDFC Bank allotment of equity shares ESOP 18240"),
        "financial_basis": "STANDALONE",
        "headline_metrics": None,
        "executive_profile": None,
        "network_connection": None
    },
    {
        "id": "ann-reliance-reg74-01",
        "isin": "INE002A01018",
        "ticker": "RELIANCE.NS",
        "category": "unclassified",
        "title": "Compliance Certificate under Reg. 74(5) of SEBI (DP) Regulations",
        "description": "Certificate received from KFin Technologies certifying dematerialization of shares for the quarter.",
        "filing_time": (datetime.now() - timedelta(hours=7)).isoformat(),
        "materiality_score": 1,
        "content_hash": compute_hash("Reliance Reg 74(5) SEBI DP compliance certificate KFin"),
        "financial_basis": "STANDALONE",
        "headline_metrics": None,
        "executive_profile": None,
        "network_connection": None
    },
    {
        "id": "ann-lt-duplicate-01",
        "isin": "INE018A01030",
        "ticker": "LT.NS",
        "category": "unclassified",
        "title": "Intimation of loss of share certificate / issue of duplicate",
        "description": "Intimation regarding issue of letter of confirmation in lieu of lost share certificates.",
        "filing_time": (datetime.now() - timedelta(hours=9)).isoformat(),
        "materiality_score": 1,
        "content_hash": compute_hash("Larsen Toubro loss of share certificate duplicate"),
        "financial_basis": "STANDALONE",
        "headline_metrics": None,
        "executive_profile": None,
        "network_connection": None
    },
    {
        "id": "ann-persistent-cp-01",
        "isin": "INE262H01013",
        "ticker": "PERSISTENT.NS",
        "category": "fund_raise",
        "title": "Commercial Paper Issuance of Rs 200 Crore",
        "description": "Persistent Systems has placed commercial paper for short-term liquidity and treasury optimization at 7.25% coupon.",
        "filing_time": (datetime.now() - timedelta(days=2)).isoformat(),
        "materiality_score": 4,
        "content_hash": compute_hash("Persistent Systems commercial paper issuance 200 cr"),
        "financial_basis": "STANDALONE",
        "headline_metrics": None,
        "executive_profile": None,
        "network_connection": None
    }
]

# Canonical Anomaly Facts
ANOMALIES_SEED = [
    {
        "id": "anom-dixon-vol-01",
        "isin": "INE806N01020",
        "ticker": "DIXON.NS",
        "anomaly_type": "VOLUME_SURGE",
        "severity": "CRITICAL",
        "headline": "Dixon Tech: 4.8x Volume Explosion with +5.2% Price Breakout",
        "detail": "End-of-day traded volume reached 1.68M shares vs 20-day SMA of 350k shares (4.80x surge). Coincides with blockbuster Q2 mobile assembly revenue growth (+120% YoY).",
        "metrics": {"volume_multiple": 4.8, "daily_return_pct": 5.2, "volume": 1680000, "sma_20d": 350000},
        "created_at": (datetime.now() - timedelta(hours=4)).isoformat(),
    },
    {
        "id": "anom-kaynes-mgmt-01",
        "isin": "INE062Y01012",
        "ticker": "KAYNES.NS",
        "anomaly_type": "MANAGEMENT_CHANGE",
        "severity": "CRITICAL",
        "headline": "Kaynes Technology: Poaches Dixon Tech Manufacturing Head as COO",
        "detail": "Vikram Seth appointed COO. High network relevance: Vikram is an IIT Kanpur 2004 alumnus with direct personal connection to Ananya Roy in your network.",
        "metrics": {"connected_contact": "Ananya Roy", "relationship": "IIT Kanpur 2004 classmate", "strength": 5},
        "created_at": (datetime.now() - timedelta(hours=3)).isoformat(),
    },
    {
        "id": "anom-tatamotors-price-01",
        "isin": "INE155A01022",
        "ticker": "TATAMOTORS.NS",
        "anomaly_type": "PRICE_BREAKOUT",
        "severity": "HIGH",
        "headline": "Tata Motors: Sharp -4.1% Drop on 2.4x Volume following JLR Margin Compression",
        "detail": "JLR EBIT margin collapsed to 5.1% (vs 8.5% guided) due to Novelis aluminum supply chain disruption. Traded volume spiked to 24.5M shares.",
        "metrics": {"daily_return_pct": -4.1, "volume_multiple": 2.4, "jlr_ebit_margin": 5.1, "guided_margin": 8.5},
        "created_at": (datetime.now() - timedelta(hours=8)).isoformat(),
    },
    {
        "id": "anom-deepak-cfo-01",
        "isin": "INE288B01029",
        "ticker": "DEEPAKNTR.NS",
        "anomaly_type": "MANAGEMENT_CHANGE",
        "severity": "HIGH",
        "headline": "Deepak Nitrite: Sudden CFO Resignation Triggers -3.6% Price Slump",
        "detail": "Veteran CFO Sanjay Upadhyay stepping down. Incoming CFO Radhika Sharma from Tata Chemicals. Volume jumped 2.24x average.",
        "metrics": {"daily_return_pct": -3.6, "volume_multiple": 2.24, "incoming_cfo": "Radhika Sharma"},
        "created_at": (datetime.now() - timedelta(hours=6)).isoformat(),
    },
    {
        "id": "anom-cdsl-vol-01",
        "isin": "INE736A01011",
        "ticker": "CDSL.NS",
        "anomaly_type": "VOLUME_SURGE",
        "severity": "MEDIUM",
        "headline": "CDSL: Volume Surge 2.81x with +3.8% Gain on Record Demat Growth",
        "detail": "Total demat accounts on CDSL crossed 13.5 Crore. Margin profile expanded to 61.2% in Q2 results.",
        "metrics": {"volume_multiple": 2.81, "daily_return_pct": 3.8},
        "created_at": (datetime.now() - timedelta(hours=10)).isoformat(),
    }
]

# Guidance Track Record v2 Schema (D-04: Range and Verbatim Support)
GUIDANCE_HISTORY_SEED = [
    {
        "isin": "INE806N01020",
        "ticker": "DIXON.NS",
        "fiscal_quarter": "Q1FY25",
        "metric": "Mobile Volume Run Rate",
        "guidance_type": "RANGE",
        "min_guidance": 3500.0,
        "max_guidance": 4000.0,
        "promised_guidance": "Mobile segment will cross 3,500 Cr quarterly run rate in Q1, reaching 4,000 Cr+ by H1.",
        "delivered_actual": "Reported Q1 Mobile revenue of 4,800 Cr and Q2 Mobile revenue of 9,400 Cr.",
        "variance": "+37% beat in Q1; massive outperformance in Q2 (+135%) driven by Xiaomi and Motorola ramp-up.",
        "status": "BEAT",
        "management_quote": "We guided for 3,500 Cr quarterly run-rate, but customer orders exceeded our most optimistic forecasts.",
        "source_doc_ref": "Dixon Q4FY24 Concall Transcript, Page 4, Remarks by MD",
        "delivery_notes": "Execution ahead of schedule. Component localization is improving overall gross dollar profit."
    },
    {
        "isin": "INE806N01020",
        "ticker": "DIXON.NS",
        "fiscal_quarter": "Q4FY24",
        "metric": "Consolidated EBITDA Margin",
        "guidance_type": "NUMERIC",
        "min_guidance": 4.0,
        "max_guidance": 4.0,
        "promised_guidance": "Expect consolidated EBITDA margins to sustain at or above 4.0% through FY25.",
        "delivered_actual": "Reported Q1 margin of 3.8% and Q2 margin of 3.64%.",
        "variance": "-36 bps margin dilution vs promised floor.",
        "status": "MISSED",
        "management_quote": "The dilution is purely mathematical: mobile assembly has lower % margins (3.2%) but enormous ROIC and absolute profit dollars.",
        "source_doc_ref": "Dixon Q4FY24 Earnings Deck, Slide 12",
        "delivery_notes": "Revenue exploded but % margin suffered due to mix shift toward pass-through smartphone assembly."
    },
    {
        "isin": "INE849A01020",
        "ticker": "TRENT.NS",
        "fiscal_quarter": "Q4FY24",
        "metric": "Zudio Store Expansion",
        "guidance_type": "RANGE",
        "min_guidance": 150.0,
        "max_guidance": 200.0,
        "promised_guidance": "Targeting 150-200 net new Zudio store additions in FY25 while preserving store unit economics.",
        "delivered_actual": "Added 86 net stores in H1FY25 alone; operating margin sustained at 15.3%.",
        "variance": "On track for top-end of 200 stores with zero margin erosion.",
        "status": "MET",
        "management_quote": "We continue to see immense white space in tier 2 and tier 3 micro-markets for Zudio without cannibalization.",
        "source_doc_ref": "Trent FY24 Annual Report, MD&A Section, Page 28",
        "delivery_notes": "Inventory turnover sustained at 45 days, proving supply chain scalability."
    },
    {
        "isin": "INE155A01022",
        "ticker": "TATAMOTORS.NS",
        "fiscal_quarter": "Q4FY24",
        "metric": "JLR FY25 EBIT Margin",
        "guidance_type": "NUMERIC",
        "min_guidance": 8.5,
        "max_guidance": 8.5,
        "promised_guidance": "JLR EBIT margin guided to sustain above 8.5% for full-year FY25.",
        "delivered_actual": "Delivered 8.9% in Q1, but compressed severely to 5.1% in Q2 due to Swiss aluminum flooding.",
        "variance": "-340 bps deficit in Q2; full-year guidance revised down to ~7.5%.",
        "status": "MISSED",
        "management_quote": "A once-in-a-century flood at Novelis Sierre plant constrained body-panel aluminum for Defender and Range Rover.",
        "source_doc_ref": "Tata Motors Q1FY25 Investor Concall Transcript, Page 9",
        "delivery_notes": "Exogenous supply shock caused 14,000 lost wholesale units; management expects recovery in Q3/Q4."
    }
]

# Concalls with SHA-256 Content Hash (F-08)
CONCALL_SEED = [
    {
        "id": "concall-dixon-q2fy25",
        "isin": "INE806N01020",
        "ticker": "DIXON.NS",
        "fiscal_quarter": "Q2FY25",
        "transcript_date": "2026-11-05",
        "content_hash": compute_hash("Atul Lall MD Dixon Q2 consolidated revenues 11534 Cr mobile 9400 Cr run rate 3.8M"),
        "management_remarks": "Atul Lall (MD): In Q2, our consolidated revenues stood at Rs 11,534 Cr, representing a phenomenal 120% YoY growth. The mobile division delivered Rs 9,400 Cr against our internal budget of Rs 8,000 Cr. Our smartphone monthly run rate has crossed 3.8 million units.",
        "guidance_excerpts": "Guidance for H2: We expect full-year FY25 revenues to approach Rs 38,000 Cr to Rs 40,000 Cr. For display modules and precision components, our JV with HKC is on schedule for pilot production in Q4FY25.",
        "analyst_qa_excerpts": "Analyst (UBS): What is the sustainable margin on the mobile business? Atul Lall: On pure assembly, margins will be 3.0% to 3.2%. However, as backward integration into display and battery packs kicks in, blended mobile margin will expand toward 4.2%."
    },
    {
        "id": "concall-trent-q2fy25",
        "isin": "INE849A01020",
        "ticker": "TRENT.NS",
        "fiscal_quarter": "Q2FY25",
        "transcript_date": "2026-11-08",
        "content_hash": compute_hash("Noel Tata Venkatesalu CEO Standalone Q2 revenue 4035 Cr up 39 pct YoY Zudio 50 to 60 stores Q3"),
        "management_remarks": "Noel Tata / P. Venkatesalu (CEO): Standalone Q2 revenue was Rs 4,035 Cr, up 39% YoY. Westside and Zudio combined registered 12% like-for-like (LFL) sales growth across mature stores.",
        "guidance_excerpts": "We will open between 50 to 60 Zudio stores in Q3 ahead of the festive and winter season. Capex per store remains tightly controlled at Rs 2.2 Cr.",
        "analyst_qa_excerpts": "Analyst (Morgan Stanley): Are you seeing any demand fatigue in small towns? Venkatesalu: Absolutely none. In fact, tier 3 stores are reaching cash breakeven within 45 days of launch."
    }
]

# Tenant-Isolated Network Contacts (F-02, F-03)
NETWORK_CONTACTS_SEED = [
    {
        "id": "net-01",
        "tenant_id": "tenant-enam-01",
        "name": "Ananya Roy",
        "current_title": "Partner",
        "current_company": "Peak XV Partners",
        "current_company_ticker": None,
        "relationship_strength": 5,
        "is_starred": 1,
        "past_companies": [
            {"company": "McKinsey & Co", "role": "Associate Partner", "start_year": 2010, "end_year": 2017},
            {"company": "Foxconn India", "role": "Supply Chain Strategist", "start_year": 2005, "end_year": 2008}
        ],
        "education": [
            {"institution": "IIT Kanpur", "degree": "B.Tech Computer Science", "year": "2004"},
            {"institution": "IIM Ahmedabad", "degree": "MBA", "year": "2010"}
        ],
        "themes": ["Electronics EMS", "Hardware Tech", "Venture Capital"],
        "relevance_score": 9.8,
        "recent_development_summary": "IIT Kanpur 2004 classmate of Vikram Seth (newly appointed COO of Kaynes Tech); ex-colleague at Foxconn.",
        "notes": "Go-to expert on Indian electronics manufacturing and contract assembly economics.",
        "last_verified": "2026-11-01"
    },
    {
        "id": "net-02",
        "tenant_id": "tenant-enam-01",
        "name": "Rohan Deshmukh",
        "current_title": "Director of Sourcing & Supply Chain",
        "current_company": "Xiaomi India",
        "current_company_ticker": None,
        "relationship_strength": 5,
        "is_starred": 1,
        "past_companies": [
            {"company": "Dixon Technologies", "role": "Head of Vendor Quality", "start_year": 2016, "end_year": 2021},
            {"company": "Samsung Electronics", "role": "Component Sourcing Manager", "start_year": 2011, "end_year": 2016}
        ],
        "education": [
            {"institution": "IIT Kanpur", "degree": "B.Tech Electrical Engineering", "year": "2007"}
        ],
        "themes": ["Electronics EMS", "Smartphone Supply Chain", "China-India Tech Sourcing"],
        "relevance_score": 9.6,
        "recent_development_summary": "Manages Xiaomi's primary assembly contract with Dixon Tech; reported 120% YoY mobile ramp in Q2.",
        "notes": "Direct line to Dixon's factory floor yields and component bottleneck reality.",
        "last_verified": "2026-11-05"
    },
    {
        "id": "net-03",
        "tenant_id": "tenant-enam-01",
        "name": "Karan Mehra",
        "current_title": "Senior Audit Partner",
        "current_company": "BSR & Co LLP",
        "current_company_ticker": None,
        "relationship_strength": 4,
        "is_starred": 1,
        "past_companies": [
            {"company": "Deloitte Haskins & Sells", "role": "Director", "start_year": 2008, "end_year": 2015}
        ],
        "education": [
            {"institution": "ICAI", "degree": "Chartered Accountant", "year": "2005"}
        ],
        "themes": ["Corporate Governance", "Audit Quality", "Specialty Chemicals"],
        "relevance_score": 9.2,
        "recent_development_summary": "Lead audit partner on Tata Chemicals; audited incoming Deepak Nitrite CFO Radhika Sharma for 5 years.",
        "notes": "Sharpest eye on forensic accounting and working capital manipulation.",
        "last_verified": "2026-10-20"
    },
    {
        "id": "net-04",
        "tenant_id": "tenant-enam-01",
        "name": "Pooja Singhania",
        "current_title": "Chief Merchandising Officer",
        "current_company": "Nykaa Fashion",
        "current_company_ticker": None,
        "relationship_strength": 4,
        "is_starred": 1,
        "past_companies": [
            {"company": "Trent Ltd", "role": "Head of Merchandising (Zudio)", "start_year": 2017, "end_year": 2024},
            {"company": "Zara India (Inditex)", "role": "Senior Buyer", "start_year": 2013, "end_year": 2017}
        ],
        "education": [
            {"institution": "NIFT Delhi", "degree": "Fashion Merchandising", "year": "2011"},
            {"institution": "ISB Hyderabad", "degree": "MBA", "year": "2013"}
        ],
        "themes": ["Retail", "Fashion Supply Chain", "Quick Inventory Turns"],
        "relevance_score": 8.9,
        "recent_development_summary": "Ex-Head of Zudio Merchandising at Trent; Trent just announced 39% revenue growth and 570 store milestone.",
        "notes": "Natural reconnect hook: discuss how Zudio's 45-day turnaround model stacks against Nykaa.",
        "last_verified": "2026-11-09"
    },
    {
        "id": "net-05",
        "tenant_id": "tenant-enam-01",
        "name": "Siddharth Verma",
        "current_title": "VP Commercial Vehicle Operations",
        "current_company": "Tata Motors Ltd",
        "current_company_ticker": "TATAMOTORS.NS",
        "relationship_strength": 5,
        "is_starred": 1,
        "past_companies": [
            {"company": "Ashok Leyland", "role": "Chief Engineer", "start_year": 2006, "end_year": 2014}
        ],
        "education": [
            {"institution": "IIT Kanpur", "degree": "B.Tech Mechanical Engineering", "year": "2002"}
        ],
        "themes": ["Automotive", "Heavy Commercial Vehicles", "EV Powertrains"],
        "relevance_score": 9.4,
        "recent_development_summary": "VP at Tata Motors; directly oversees domestic commercial vehicle assembly after JLR Q2 margin drop.",
        "notes": "Can speak with high authority on fleet replacement cycles and CV tonnage demand.",
        "last_verified": "2026-11-10"
    },
    # Peer fund contact (Tenant B isolation test)
    {
        "id": "net-peer-01",
        "tenant_id": "tenant-test-02",
        "name": "Confidential Peer Advisor",
        "current_title": "Partner",
        "current_company": "Secret Alpha Capital",
        "current_company_ticker": None,
        "relationship_strength": 5,
        "is_starred": 1,
        "past_companies": [],
        "education": [],
        "themes": ["Stealth Investing"],
        "relevance_score": 10.0,
        "recent_development_summary": "Confidential research on undisclosed small-caps.",
        "notes": "STRICTLY PRIVATE: Should never be visible to ENAM users.",
        "last_verified": "2026-11-12"
    }
]

# Corporate Actions Seed (P-07: Stock Split Example)
CORPORATE_ACTIONS_SEED = [
    {
        "id": "ca-cdsl-split-2024",
        "isin": "INE736A01011",
        "ticker": "CDSL.NS",
        "action_type": "BONUS",
        "ratio_from": 1.0,
        "ratio_to": 1.0, # 1:1 bonus issue
        "record_date": "2024-08-24",
        "ex_date": "2024-08-23",
        "adjustment_factor": 2.0
    }
]

def seed_database():
    """Seeds the SQLite database with multi-tenant isolation, ISIN master, and provenance hashes."""
    init_db()
    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Seed Tenants
        for t in TENANTS_SEED:
            cursor.execute("INSERT OR REPLACE INTO tenants (id, name, created_at) VALUES (?, ?, ?);",
                           (t["id"], t["name"], t["created_at"]))

        # 2. Seed Users
        for u in USERS_SEED:
            cursor.execute("INSERT OR REPLACE INTO users (id, tenant_id, email, role, created_at) VALUES (?, ?, ?, ?, ?);",
                           (u["id"], u["tenant_id"], u["email"], u["role"], u["created_at"]))

        # 3. Seed User Preferences
        cursor.execute("""
        INSERT OR REPLACE INTO user_preferences (user_id, volume_multiplier_threshold, price_move_pct_threshold, auto_notify_critical, starred_tickers, enabled_categories)
        VALUES ('user-enam-01', 2.0, 3.5, 1, '[]', '["results","M&A","management_change","fund_raise","litigation","capex"]');
        """)

        # 4. Seed Companies (ISIN Master)
        for c in COMPANIES_SEED:
            cursor.execute("""
            INSERT OR REPLACE INTO companies (isin, ticker, name, sector, market_cap_tier, market_cap_cr, screener_slug, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (c["isin"], c["ticker"], c["name"], c["sector"], c["market_cap_tier"], c["market_cap_cr"], c["screener_slug"], c["description"]))

            # Primary ticker history
            cursor.execute("""
            INSERT OR IGNORE INTO company_tickers_history (isin, exchange, ticker, valid_from, is_primary)
            VALUES (?, 'NSE', ?, '2000-01-01', 1);
            """, (c["isin"], c["ticker"]))

        # 5. Seed Tenant Holdings (Confidential Portfolio)
        for h in TENANT_HOLDINGS_SEED:
            cursor.execute("""
            INSERT OR REPLACE INTO tenant_holdings (tenant_id, isin, ticker, shares_held, conviction_level, created_at)
            VALUES (?, ?, ?, ?, ?, ?);
            """, (h["tenant_id"], h["isin"], h["ticker"], h["shares_held"], h["conviction_level"], datetime.now().isoformat()))

        # 6. Seed Market EOD
        for m in MARKET_EOD_SEED:
            cursor.execute("""
            INSERT OR REPLACE INTO market_eod (isin, ticker, trade_date, close_price, volume, volume_sma_20d, daily_return_pct, volume_multiple)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (m["isin"], m["ticker"], m["trade_date"], m["close_price"], m["volume"], m["volume_sma_20d"], m["daily_return_pct"], m["volume_multiple"]))

        # 7. Seed Announcements
        for a in ANNOUNCEMENTS_SEED:
            cursor.execute("""
            INSERT OR REPLACE INTO announcements (id, isin, ticker, category, title, description, filing_time, materiality_score, content_hash, financial_basis, headline_metrics, executive_profile, network_connection)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                a["id"], a["isin"], a["ticker"], a["category"], a["title"], a["description"], a["filing_time"],
                a["materiality_score"], a["content_hash"], a["financial_basis"],
                json.dumps(a["headline_metrics"]) if a["headline_metrics"] else None,
                json.dumps(a["executive_profile"]) if a["executive_profile"] else None,
                json.dumps(a["network_connection"]) if a["network_connection"] else None
            ))

        # 8. Seed Detected Anomalies
        for anom in ANOMALIES_SEED:
            cursor.execute("""
            INSERT OR REPLACE INTO detected_anomalies (id, isin, ticker, anomaly_type, severity, headline, detail, metrics, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                anom["id"], anom["isin"], anom["ticker"], anom["anomaly_type"], anom["severity"],
                anom["headline"], anom["detail"], json.dumps(anom["metrics"]), anom["created_at"]
            ))

            # Default alert state for user-enam-01 (F-05)
            is_pinned = 1 if anom["severity"] == "CRITICAL" else 0
            cursor.execute("""
            INSERT OR REPLACE INTO user_alert_state (user_id, anomaly_id, is_pinned, is_dismissed, notified_at)
            VALUES ('user-enam-01', ?, ?, 0, ?);
            """, (anom["id"], is_pinned, datetime.now().isoformat()))

        # 9. Seed Guidance History
        for g in GUIDANCE_HISTORY_SEED:
            cursor.execute("""
            INSERT INTO guidance_history (isin, ticker, fiscal_quarter, metric, guidance_type, min_guidance, max_guidance, promised_guidance, delivered_actual, variance, status, management_quote, source_doc_ref, delivery_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                g["isin"], g["ticker"], g["fiscal_quarter"], g["metric"], g["guidance_type"],
                g["min_guidance"], g["max_guidance"], g["promised_guidance"], g["delivered_actual"],
                g["variance"], g["status"], g["management_quote"], g["source_doc_ref"], g["delivery_notes"]
            ))

        # 10. Seed Concalls
        for ct in CONCALL_SEED:
            cursor.execute("""
            INSERT OR REPLACE INTO concall_transcripts (id, isin, ticker, fiscal_quarter, transcript_date, content_hash, management_remarks, guidance_excerpts, analyst_qa_excerpts)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                ct["id"], ct["isin"], ct["ticker"], ct["fiscal_quarter"], ct["transcript_date"],
                ct["content_hash"], ct["management_remarks"], ct["guidance_excerpts"], ct["analyst_qa_excerpts"]
            ))

        # 11. Seed Network Contacts
        for nc in NETWORK_CONTACTS_SEED:
            cursor.execute("""
            INSERT OR REPLACE INTO network_contacts (id, tenant_id, name, current_title, current_company, current_company_ticker, relationship_strength, is_starred, past_companies, education, themes, relevance_score, recent_development_summary, notes, last_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                nc["id"], nc["tenant_id"], nc["name"], nc["current_title"], nc["current_company"], nc["current_company_ticker"],
                nc["relationship_strength"], nc["is_starred"], json.dumps(nc["past_companies"]),
                json.dumps(nc["education"]), json.dumps(nc["themes"]), nc["relevance_score"],
                nc["recent_development_summary"], nc["notes"], nc["last_verified"]
            ))

        # 12. Seed Corporate Actions
        for ca in CORPORATE_ACTIONS_SEED:
            cursor.execute("""
            INSERT OR REPLACE INTO corporate_actions (id, isin, ticker, action_type, ratio_from, ratio_to, record_date, ex_date, adjustment_factor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                ca["id"], ca["isin"], ca["ticker"], ca["action_type"], ca["ratio_from"],
                ca["ratio_to"], ca["record_date"], ca["ex_date"], ca["adjustment_factor"]
            ))

    print(f"Successfully seeded FINN database with {len(COMPANIES_SEED)} ISIN-keyed companies, {len(TENANTS_SEED)} tenants, {len(USERS_SEED)} users, and {len(NETWORK_CONTACTS_SEED)} network contacts.")

if __name__ == "__main__":
    seed_database()
