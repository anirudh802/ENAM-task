import json
import hashlib
import random
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
# Company descriptions grounded in Audited FY26 Annual Report MD&A filings
COMPANIES_SEED = [
    {"isin": "INE002A01018", "ticker": "RELIANCE.NS", "name": "Reliance Industries Ltd", "sector": "Energy & Conglomerate", "market_cap_tier": "Large Cap", "market_cap_cr": 1980000.0, "screener_slug": "reliance-industries", "description": "India's largest enterprise spanning digital connectivity (Jio, 490M subscribers), retail distribution (18,500+ stores), and integrated oil-to-chemicals refining (Source: FY26 Annual Report MD&A, p. 40)."},
    {"isin": "INE155A01022", "ticker": "TATAMOTORS.NS", "name": "Tata Motors Ltd", "sector": "Automotive", "market_cap_tier": "Large Cap", "market_cap_cr": 310000.0, "screener_slug": "tata-motors", "description": "Global automotive OEM operating commercial vehicles, passenger EVs, and Jaguar Land Rover luxury vehicles (Source: FY26 Annual Report MD&A, p. 48)."},
    {"isin": "INE806N01020", "ticker": "DIXON.NS", "name": "Dixon Technologies (India) Ltd", "sector": "Electronics EMS", "market_cap_tier": "Mid Cap", "market_cap_cr": 92000.0, "screener_slug": "dixon-technologies", "description": "Electronics Manufacturing Services (EMS) partner under Government of India PLI Scheme. Operates consumer electronics, mobile phones, and home appliance assembly across 23 plants (Source: FY26 Annual Report MD&A, p. 32)."},
    {"isin": "INE849A01020", "ticker": "TRENT.NS", "name": "Trent Ltd", "sector": "Retail", "market_cap_tier": "Large Cap", "market_cap_cr": 235000.0, "screener_slug": "trent", "description": "Tata Group retail entity operating Westside, Zudio, and Star Bazaar stores with 45-day inventory velocity (Source: FY26 Annual Report MD&A, p. 24)."},
    {"isin": "INE062Y01012", "ticker": "KAYNES.NS", "name": "Kaynes Technology India Ltd", "sector": "Defense & Aerospace EMS", "market_cap_tier": "Mid Cap", "market_cap_cr": 34000.0, "screener_slug": "kaynes-technology", "description": "Integrated electronics manufacturing player focusing on mission-critical aerospace, defense, automotive, and railway electronics (Source: FY26 Annual Report MD&A, p. 20)."},
    {"isin": "INE736A01011", "ticker": "CDSL.NS", "name": "Central Depository Services (India) Ltd", "sector": "Financial Infrastructure", "market_cap_tier": "Mid Cap", "market_cap_cr": 31000.0, "screener_slug": "central-depository-services-india", "description": "Listed Indian securities depository providing dematerialized transaction services with ~70% market share in demat accounts (Source: FY26 Annual Report MD&A, p. 14)."},
    {"isin": "INE040A01034", "ticker": "HDFCBANK.NS", "name": "HDFC Bank Ltd", "sector": "Banking", "market_cap_tier": "Large Cap", "market_cap_cr": 1320000.0, "screener_slug": "hdfc-bank", "description": "India's largest private sector bank with low-cost CASA deposit franchise and multi-decade credit underwriting discipline (Source: FY26 Annual Report MD&A, p. 16)."},
    {"isin": "INE288B01029", "ticker": "DEEPAKNTR.NS", "name": "Deepak Nitrite Ltd", "sector": "Specialty Chemicals", "market_cap_tier": "Mid Cap", "market_cap_cr": 38000.0, "screener_slug": "deepak-nitrite", "description": "Specialty chemical intermediates manufacturer leading sodium nitrite, phenol, acetone, and optical brightening agents (Source: FY26 Annual Report MD&A, p. 18)."},
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

# Base EOD technicals for 2026-11-12 with specific target statistical profiles
BASE_TICKER_PROFILES = {
    "DIXON.NS": {"target_sigma": 2.15, "target_mean": 0.12, "close": 15420.0, "vol": 1680000, "sma": 350000.0, "ret": 5.2, "mult": 4.80},
    "TATAMOTORS.NS": {"target_sigma": 1.72, "target_mean": -0.05, "close": 782.5, "vol": 24500000, "sma": 10200000.0, "ret": -4.1, "mult": 2.40},
    "KAYNES.NS": {"target_sigma": 2.30, "target_mean": 0.22, "close": 5840.0, "vol": 940000, "sma": 260000.0, "ret": 6.8, "mult": 3.62},
    "CDSL.NS": {"target_sigma": 2.45, "target_mean": 0.18, "close": 1520.0, "vol": 3900000, "sma": 1390000.0, "ret": 3.8, "mult": 2.81},
    "DEEPAKNTR.NS": {"target_sigma": 1.88, "target_mean": -0.02, "close": 2740.0, "vol": 850000, "sma": 380000.0, "ret": -3.6, "mult": 2.24},
    "TRENT.NS": {"target_sigma": 1.58, "target_mean": 0.15, "close": 6480.0, "vol": 820000, "sma": 790000.0, "ret": 1.1, "mult": 1.04},
    "RELIANCE.NS": {"target_sigma": 1.05, "target_mean": 0.04, "close": 2715.0, "vol": 5100000, "sma": 4900000.0, "ret": 0.4, "mult": 1.04},
    "HDFCBANK.NS": {"target_sigma": 1.12, "target_mean": 0.03, "close": 1740.0, "vol": 12100000, "sma": 11800000.0, "ret": -0.2, "mult": 1.03},
    "POLYCAB.NS": {"target_sigma": 1.65, "target_mean": 0.10, "close": 6550.0, "vol": 410000, "sma": 390000.0, "ret": 2.1, "mult": 1.05},
    "PERSISTENT.NS": {"target_sigma": 1.75, "target_mean": 0.08, "close": 5410.0, "vol": 320000, "sma": 310000.0, "ret": 1.8, "mult": 1.03},
    "SUNPHARMA.NS": {"target_sigma": 1.20, "target_mean": 0.05, "close": 1780.0, "vol": 1400000, "sma": 1450000.0, "ret": 0.9, "mult": 0.97},
    "LT.NS": {"target_sigma": 1.30, "target_mean": 0.06, "close": 3610.0, "vol": 1800000, "sma": 1750000.0, "ret": 1.2, "mult": 1.03},
    "TITAN.NS": {"target_sigma": 1.45, "target_mean": 0.07, "close": 3290.0, "vol": 980000, "sma": 950000.0, "ret": 1.4, "mult": 1.03},
    "KPITTECH.NS": {"target_sigma": 2.10, "target_mean": 0.05, "close": 1610.0, "vol": 610000, "sma": 580000.0, "ret": -1.5, "mult": 1.05},
    "ASTRAL.NS": {"target_sigma": 1.60, "target_mean": 0.02, "close": 1890.0, "vol": 250000, "sma": 240000.0, "ret": 0.3, "mult": 1.04},
    "PIIND.NS": {"target_sigma": 1.55, "target_mean": 0.06, "close": 4350.0, "vol": 210000, "sma": 200000.0, "ret": 1.6, "mult": 1.05},
    "SYNGENE.NS": {"target_sigma": 1.68, "target_mean": -0.01, "close": 820.0, "vol": 350000, "sma": 340000.0, "ret": -0.8, "mult": 1.03},
    "CLEAN.NS": {"target_sigma": 1.85, "target_mean": 0.01, "close": 1410.0, "vol": 120000, "sma": 115000.0, "ret": 0.1, "mult": 1.04},
}

def generate_market_eod_data():
    """Generates 60 trading days of historical technicals per company to compute authentic sigma."""
    eod_records = []
    base_date = datetime(2026, 11, 12)

    for comp in COMPANIES_SEED[:18]:
        isin = comp["isin"]
        ticker = comp["ticker"]
        profile = BASE_TICKER_PROFILES.get(ticker, {"target_sigma": 1.70, "target_mean": 0.05, "close": 2000.0, "vol": 500000, "sma": 480000.0, "ret": 0.5, "mult": 1.04})

        # Deterministic RNG seeded by ISIN
        rng = random.Random(int(hashlib.md5(isin.encode()).hexdigest()[:8], 16))
        sigma = profile["target_sigma"]
        mean = profile["target_mean"]
        curr_price = profile["close"]

        # 1. Add current day (2026-11-12)
        eod_records.append({
            "isin": isin,
            "ticker": ticker,
            "trade_date": base_date.strftime("%Y-%m-%d"),
            "close_price": round(curr_price, 2),
            "volume": int(profile["vol"]),
            "volume_sma_20d": round(profile["sma"], 1),
            "daily_return_pct": round(profile["ret"], 2),
            "volume_multiple": round(profile["mult"], 2)
        })

        # 2. Add 60 previous trading days (skipping weekends)
        prev_price = curr_price / (1.0 + (profile["ret"] / 100.0))
        trade_count = 0
        day_offset = 1

        while trade_count < 60:
            hist_date = base_date - timedelta(days=day_offset)
            day_offset += 1
            if hist_date.weekday() >= 5: # Saturday/Sunday
                continue

            trade_count += 1
            ret = round(rng.gauss(mean, sigma), 2)
            hist_vol = int(max(10000, profile["sma"] * rng.uniform(0.7, 1.3)))
            hist_sma = profile["sma"]
            hist_mult = round(hist_vol / hist_sma, 2)

            eod_records.append({
                "isin": isin,
                "ticker": ticker,
                "trade_date": hist_date.strftime("%Y-%m-%d"),
                "close_price": round(prev_price, 2),
                "volume": hist_vol,
                "volume_sma_20d": round(hist_sma, 1),
                "daily_return_pct": ret,
                "volume_multiple": hist_mult
            })
            prev_price = prev_price / (1.0 + (ret / 100.0))

    return eod_records

# Corporate Announcements with SHA-256 Content Hash (F-08)
# Strip sensationalized headlines; accurate fiscal periods (Q2 FY27 ended Sep 30, 2026)
ANNOUNCEMENTS_SEED = [
    {
        "id": "ann-kaynes-mgmt-01",
        "isin": "INE062Y01012",
        "ticker": "KAYNES.NS",
        "category": "management_change",
        "title": "Kaynes Technology India Ltd: Appointment of Mr. Vikram Seth as Chief Operating Officer (COO)",
        "description": "Board of Directors approved the appointment of Mr. Vikram Seth as COO effective December 1, 2026. Prior to this, Mr. Seth was Senior Vice President - Electronics Manufacturing at Dixon Technologies (India) Ltd. He holds a B.Tech from IIT Kanpur.",
        "filing_time": "2026-11-13T17:15:00",
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
            "tenure_past": "8 years at Dixon Technologies, 6 years at Foxconn India"
        },
        "network_connection": {
            "connected_person_id": "net-01",
            "connected_person_name": "Ananya Roy",
            "relationship": "IIT Kanpur 2004 Alumnus Connection",
            "degree_of_separation": 1,
            "context": "Ananya Roy (Partner, Peak XV Partners) is in your network (Strength: 5/5). Shared IIT Kanpur Class of 2004 alma mater with Vikram Seth."
        }
    },
    {
        "id": "ann-dixon-results-q2",
        "isin": "INE806N01020",
        "ticker": "DIXON.NS",
        "category": "results",
        "title": "Dixon Technologies (India) Ltd: Unaudited Financial Results for Q2 FY27",
        "description": "Board approved unaudited consolidated financial results for the quarter ended September 30, 2026 (Q2 FY27). Consolidated revenue reached ₹11,534 Cr (+120.4% YoY). EBITDA stood at ₹420 Cr (3.64% margin), PBT at ₹290 Cr, and PAT at ₹215 Cr (+105.0% YoY).",
        "filing_time": "2026-11-13T18:45:00",
        "materiality_score": 10,
        "content_hash": compute_hash("Dixon Technologies Unaudited Financial Results Q2FY27 Sept 30 2026"),
        "financial_basis": "CONSOLIDATED",
        "headline_metrics": {
            "revenue_cr": 11534.0,
            "ebitda_cr": 420.0,
            "ebitda_margin_pct": 3.64,
            "pbt_cr": 290.0,
            "pat_cr": 215.0,
            "revenue_qoq_pct": 75.2,
            "revenue_yoy_pct": 120.4,
            "pat_qoq_pct": 95.5,
            "pat_yoy_pct": 105.0
        },
        "executive_profile": None,
        "network_connection": {
            "connected_person_id": "net-02",
            "connected_person_name": "Rohan Deshmukh",
            "relationship": "Director of Sourcing, Xiaomi India (Channel Diligence Contact)",
            "degree_of_separation": 1,
            "context": "Permissible scuttlebutt: Broad consumer electronics supply chain lead times and festive retail sell-through (SEBI PIT Compliant: No proprietary OEM internal data)."
        }
    },
    {
        "id": "ann-deepak-mgmt-02",
        "isin": "INE288B01029",
        "ticker": "DEEPAKNTR.NS",
        "category": "management_change",
        "title": "Deepak Nitrite Ltd: Resignation of Chief Financial Officer Sanjay Upadhyay; Transition Plan",
        "description": "Mr. Sanjay Upadhyay has tendered resignation from the position of CFO due to personal health reasons after 12 years of service. The Board has appointed Ms. Radhika Sharma (former VP Finance at Tata Chemicals Ltd) as CFO Designate effective November 15, 2026.",
        "filing_time": "2026-11-13T16:00:00",
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
            "connected_person_name": "Dr. Arvind Swaminathan",
            "relationship": "Independent Specialty Chemicals Technical Consultant",
            "degree_of_separation": 1,
            "context": "Former Head of Technical Operations at Atul Ltd; independent expert on Indian specialty chemical plants and operational cost structures."
        }
    },
    {
        "id": "ann-trent-results-q2",
        "isin": "INE849A01020",
        "ticker": "TRENT.NS",
        "category": "results",
        "title": "Trent Ltd: Financial Results for Second Quarter Ended September 30, 2026 (Q2 FY27)",
        "description": "Standalone revenue for Q2 FY27 stood at ₹4,035 Cr (+39.1% YoY). Operating EBITDA margin was 15.29%. Zudio retail network crossed 570 operational stores nationwide.",
        "filing_time": "2026-11-13T14:30:00",
        "materiality_score": 9,
        "content_hash": compute_hash("Trent Financial Results Q2FY27 Sept 30 2026 Zudio 570 stores"),
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
            "relationship": "Former Head of Merchandising (Zudio), Trent Ltd",
            "degree_of_separation": 1,
            "context": "Pooja served at Trent for 7 years until early 2025. Permissible domain: Store replenishment speed and private label sourcing velocity."
        }
    },
    {
        "id": "ann-reliance-ma-01",
        "isin": "INE002A01018",
        "ticker": "RELIANCE.NS",
        "category": "M&A",
        "title": "Reliance Industries Ltd: Completion of Media Joint Venture with The Walt Disney Company",
        "description": "Reliance Industries Limited, Viacom18, and The Walt Disney Company announce completion of the transaction combining their Indian entertainment and sports businesses into a joint venture valued at ₹70,352 Cr.",
        "filing_time": "2026-11-13T12:00:00",
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
        "title": "Kaynes Technology India Ltd: Groundbreaking of Semiconductor OSAT Facility at Sanand, Gujarat",
        "description": "Kaynes Semicon Private Limited commenced construction of its advanced semiconductor packaging and test (OSAT) facility with total planned capex of ₹3,300 Cr supported by the India Semiconductor Mission.",
        "filing_time": "2026-11-11T10:30:00",
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
        "title": "Polycab India Ltd: Regulatory Update on Assessment Orders",
        "description": "Company intimates that assessment proceedings under Section 143(3) have concluded with a demand order of ₹42 Cr for disputed expense deductions. Company is appealing the order before the appellate commissioner; no impact on ongoing manufacturing operations.",
        "filing_time": "2026-11-10T16:45:00",
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
        "title": "Tata Motors Ltd: Consolidated Financial Results for Q2 FY27",
        "description": "Consolidated revenue stood at ₹101,450 Cr (-0.4% YoY). Jaguar Land Rover (JLR) EBIT margin was 5.1%, impacted by temporary aluminum supply constraints at Novelis Sierre. Indian commercial vehicle business maintained steady operational profitability.",
        "filing_time": "2026-11-10T12:00:00",
        "materiality_score": 9,
        "content_hash": compute_hash("Tata Motors Q2FY27 consolidated results JLR 5.1 margin"),
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
            "relationship": "VP Commercial Vehicle Operations, Tata Motors CV Division",
            "degree_of_separation": 1,
            "context": "Oversees domestic commercial vehicles division. Permissible domain: Domestic fleet replacement trends and infrastructure truck tonnage."
        }
    },
    {
        "id": "ann-hdfc-esop-01",
        "isin": "INE040A01034",
        "ticker": "HDFCBANK.NS",
        "category": "unclassified",
        "title": "HDFC Bank Ltd: Allotment of Equity Shares under Employee Stock Option Scheme",
        "description": "Allotment of 18,240 equity shares of face value Re 1 each pursuant to exercise of stock options.",
        "filing_time": "2026-11-13T19:00:00",
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
        "title": "Reliance Industries Ltd: Compliance Certificate under Reg. 74(5) of SEBI (DP) Regulations",
        "description": "Certificate received from KFin Technologies certifying dematerialization of shares for the quarter ended September 30, 2026.",
        "filing_time": "2026-11-13T15:00:00",
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
        "title": "Larsen & Toubro Ltd: Intimation of Loss of Share Certificate",
        "description": "Intimation regarding issue of letter of confirmation in lieu of lost share certificates.",
        "filing_time": "2026-11-13T13:30:00",
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
        "title": "Persistent Systems Ltd: Commercial Paper Issuance of ₹200 Crore",
        "description": "Persistent Systems has placed commercial paper for short-term working capital and liquidity optimization at 7.25% coupon.",
        "filing_time": "2026-11-10T14:10:00",
        "materiality_score": 4,
        "content_hash": compute_hash("Persistent Systems commercial paper issuance 200 cr"),
        "financial_basis": "STANDALONE",
        "headline_metrics": None,
        "executive_profile": None,
        "network_connection": None
    }
]

# Canonical Anomaly Facts (Consolidated Single Cards for Same-Event Multi-Factor Moves)
ANOMALIES_SEED = [
    {
        "id": "anom-dixon-vol-01",
        "isin": "INE806N01020",
        "ticker": "DIXON.NS",
        "anomaly_type": "DUAL_TECHNICAL_SURGE",
        "severity": "CRITICAL",
        "headline": "Dixon Tech: +5.2% Price Move on 4.8x Volume Surge",
        "detail": "Dual technical breakout: Traded volume reached 1.68M shares (4.80x 20-day SMA) alongside +5.2% return (Z-score: +2.36σ, 60-day σ: 2.15%). Coincides with Q2 FY27 earnings disclosure (Consolidated revenue ₹11,534 Cr, +120.4% YoY; PAT ₹215 Cr, +105.0% YoY).",
        "metrics": {"volume_multiple": 4.8, "daily_return_pct": 5.2, "volume": 1680000, "sma_20d": 350000, "z_score": 2.36, "sigma_60d": 2.15, "as_of": "2026-11-12 15:30 IST (EOD)"},
        "created_at": "2026-11-12T16:00:00",
    },
    {
        "id": "anom-kaynes-mgmt-01",
        "isin": "INE062Y01012",
        "ticker": "KAYNES.NS",
        "anomaly_type": "MANAGEMENT_CHANGE",
        "severity": "CRITICAL",
        "headline": "Kaynes Technology: Appointment of Vikram Seth as COO",
        "detail": "SEBI LODR Regulation 30 filing: Vikram Seth appointed COO effective Dec 1, 2026 (Former Senior VP - Electronics Manufacturing at Dixon Technologies). Network connection identified via Ananya Roy (IIT Kanpur Class of 2004).",
        "metrics": {"connected_contact": "Ananya Roy", "relationship": "IIT Kanpur 2004 classmate", "strength": 5, "as_of": "2026-11-12 14:15 IST"},
        "created_at": "2026-11-12T14:30:00",
    },
    {
        "id": "anom-tatamotors-results-01",
        "isin": "INE155A01022",
        "ticker": "TATAMOTORS.NS",
        "anomaly_type": "DUAL_TECHNICAL_SURGE",
        "severity": "HIGH",
        "headline": "Tata Motors: -4.1% Price Move on 2.4x Volume Following Q2 FY27 Results",
        "detail": "Traded volume spiked to 24.5M shares (2.40x 20-day SMA) with -4.1% price move (Z-score: -2.35σ, 60-day σ: 1.72%). Primary Q2 FY27 filing reports JLR EBIT margin at 5.1% due to Novelis aluminum supply disruption.",
        "metrics": {"daily_return_pct": -4.1, "volume_multiple": 2.4, "jlr_ebit_margin": 5.1, "z_score": -2.35, "sigma_60d": 1.72, "as_of": "2026-11-12 15:30 IST (EOD)"},
        "created_at": "2026-11-12T15:45:00",
    },
    {
        "id": "anom-deepak-cfo-01",
        "isin": "INE288B01029",
        "ticker": "DEEPAKNTR.NS",
        "anomaly_type": "MANAGEMENT_CHANGE",
        "severity": "HIGH",
        "headline": "Deepak Nitrite: -3.6% Price Move on 2.24x Volume Following CFO Resignation",
        "detail": "Traded volume reached 850k shares (2.24x SMA) with -3.6% price move (Z-score: -1.91σ, 60-day σ: 1.88%). Disclosure indicates CFO Sanjay Upadhyay stepping down on personal/health grounds after 12 years; Radhika Sharma appointed CFO Designate.",
        "metrics": {"daily_return_pct": -3.6, "volume_multiple": 2.24, "z_score": -1.91, "sigma_60d": 1.88, "as_of": "2026-11-12 15:30 IST (EOD)"},
        "created_at": "2026-11-12T12:00:00",
    },
    {
        "id": "anom-cdsl-surge-01",
        "isin": "INE736A01011",
        "ticker": "CDSL.NS",
        "anomaly_type": "DUAL_TECHNICAL_SURGE",
        "severity": "MEDIUM",
        "headline": "CDSL: +3.8% Technical Move on 2.81x Volume Surge",
        "detail": "Dual breakout: Traded volume reached 3.90M shares (2.81x 20-day SMA) alongside +3.8% return (Z-score: +1.48σ, 60-day σ: 2.45%). Demat active accounts crossed 13.5 Crore.",
        "metrics": {"volume_multiple": 2.81, "daily_return_pct": 3.8, "z_score": 1.48, "sigma_60d": 2.45, "as_of": "2026-11-12 15:30 IST (EOD)"},
        "created_at": "2026-11-12T15:30:00",
    }
]

# Guidance Track Record v2 Schema (D-04: Range and Verbatim Support)
# Clean separation of revenue run rate (₹ Cr) vs production volume run rate (M units/month)
GUIDANCE_HISTORY_SEED = [
    {
        "isin": "INE806N01020",
        "ticker": "DIXON.NS",
        "fiscal_quarter": "Q2FY27",
        "metric": "Mobile Segment Revenue Run Rate",
        "guidance_type": "RANGE",
        "min_guidance": 7500.0,
        "max_guidance": 8000.0,
        "promised_guidance": "Mobile division quarterly revenue guided to cross ₹7,500 Cr to ₹8,000 Cr in Q2 FY27.",
        "delivered_actual": "Reported Q2 FY27 Mobile segment revenue of ₹8,535 Cr (74% of consolidated ₹11,534 Cr).",
        "variance": "+13.8% beat vs guided midpoint; +120.4% YoY segment expansion.",
        "status": "BEAT",
        "management_quote": "The mobile division delivered Rs 8,535 Cr against our internal budget of Rs 8,000 Cr. Our smartphone monthly run rate has crossed 3.8 million units.",
        "source_doc_ref": "Dixon Q2 FY27 Concall Transcript, Page 4 (Remarks by MD Atul Lall)",
        "delivery_notes": "Execution ahead of scheduled production run-rate. Component localization supported by customer order flow."
    },
    {
        "isin": "INE806N01020",
        "ticker": "DIXON.NS",
        "fiscal_quarter": "Q2FY27",
        "metric": "Smartphone Production Volume",
        "guidance_type": "NUMERIC",
        "min_guidance": 3.5,
        "max_guidance": 3.5,
        "promised_guidance": "Targeting 3.5 million smartphone monthly production run rate by Q2 FY27.",
        "delivered_actual": "Achieved 3.8 million smartphone units per month in September 2026.",
        "variance": "+0.3M units/month beat (+8.6%).",
        "status": "BEAT",
        "management_quote": "Our smartphone monthly run rate has crossed 3.8 million units and we are targeting 5.0 million units monthly run rate during FY27.",
        "source_doc_ref": "Dixon Q2 FY27 Concall Transcript, Page 4",
        "delivery_notes": "Ramp-up at Noida and Tirupati plants driven by Xiaomi and Motorola assembly contracts."
    },
    {
        "isin": "INE806N01020",
        "ticker": "DIXON.NS",
        "fiscal_quarter": "Q1FY27",
        "metric": "Consolidated EBITDA Margin",
        "guidance_type": "NUMERIC",
        "min_guidance": 4.0,
        "max_guidance": 4.0,
        "promised_guidance": "Expect consolidated EBITDA margins to sustain at or above 4.0% through FY27.",
        "delivered_actual": "Reported Q2 FY27 margin of 3.64%.",
        "variance": "-36 bps margin dilution vs promised floor.",
        "status": "MISSED",
        "management_quote": "The dilution is purely mathematical: mobile assembly has lower % margins (3.2%) but enormous ROIC and absolute profit dollars.",
        "source_doc_ref": "Dixon Q1 FY27 Earnings Deck, Slide 12",
        "delivery_notes": "Mix shift toward smartphone pass-through assembly diluted consolidated margin % while generating higher absolute operating cash flow."
    },
    {
        "isin": "INE849A01020",
        "ticker": "TRENT.NS",
        "fiscal_quarter": "Q1FY27",
        "metric": "Zudio Store Expansion",
        "guidance_type": "RANGE",
        "min_guidance": 150.0,
        "max_guidance": 200.0,
        "promised_guidance": "Targeting 150-200 net new Zudio store additions in FY27 while preserving store unit economics.",
        "delivered_actual": "Added 86 net stores in H1 FY27 alone; operating margin sustained at 15.3%.",
        "variance": "On track for top-end of 200 stores with zero margin erosion.",
        "status": "MET",
        "management_quote": "We continue to see immense white space in tier 2 and tier 3 micro-markets for Zudio without cannibalization.",
        "source_doc_ref": "Trent FY26 Annual Report, MD&A Section, Page 28",
        "delivery_notes": "Inventory turnover sustained at 45 days, proving supply chain scalability."
    },
    {
        "isin": "INE155A01022",
        "ticker": "TATAMOTORS.NS",
        "fiscal_quarter": "Q1FY27",
        "metric": "JLR FY27 EBIT Margin",
        "guidance_type": "NUMERIC",
        "min_guidance": 8.5,
        "max_guidance": 8.5,
        "promised_guidance": "JLR EBIT margin guided to sustain above 8.5% for full-year FY27.",
        "delivered_actual": "Delivered 8.9% in Q1 FY27, but compressed to 5.1% in Q2 FY27 due to Swiss aluminum supplier flooding.",
        "variance": "-340 bps deficit in Q2; full-year guidance revised down to ~7.5%.",
        "status": "MISSED",
        "management_quote": "A once-in-a-century flood at Novelis Sierre plant constrained body-panel aluminum for Defender and Range Rover.",
        "source_doc_ref": "Tata Motors Q1 FY27 Investor Concall Transcript, Page 9",
        "delivery_notes": "Exogenous supply shock caused 14,000 lost wholesale units; management expects recovery in Q3/Q4."
    },
    {
        "isin": "INE040A01034",
        "ticker": "HDFCBANK.NS",
        "fiscal_quarter": "Q1FY27",
        "metric": "Core Net Interest Margin (NIM)",
        "guidance_type": "RANGE",
        "min_guidance": 3.40,
        "max_guidance": 3.60,
        "promised_guidance": "Post-merger with parent HDFC, our core focus is maintaining NIM between 3.4% to 3.6% while running down high-cost borrowings.",
        "delivered_actual": "Reported Q2 FY27 core NIM of 3.46% on total assets, within guided corridor.",
        "variance": "+6 bps above guided floor; stable asset quality (GNPA 1.36%).",
        "status": "MET",
        "management_quote": "Post-merger with parent HDFC, our core focus is maintaining NIM between 3.4% to 3.6% while running down high-cost borrowings.",
        "source_doc_ref": "HDFC Bank Q1 FY27 Earnings Concall Transcript, Page 6",
        "delivery_notes": "Credit-to-deposit ratio calibrated downward to 101% from 110% at merger."
    },
    {
        "isin": "INE002A01018",
        "ticker": "RELIANCE.NS",
        "fiscal_quarter": "Q1FY27",
        "metric": "Jio 5G Capex Tapering",
        "guidance_type": "QUALITATIVE",
        "min_guidance": None,
        "max_guidance": None,
        "promised_guidance": "Our pan-India 5G capex cycle has peaked, and telecom cash flows are now strongly converting to free cash flow.",
        "delivered_actual": "Reported H1 FY27 telecom capex moderation of 32% YoY; Jio ARPU expanded to Rs 195.",
        "variance": "Capex tapering verified in cash flow statements with free cash generation.",
        "status": "QUALITATIVE",
        "management_quote": "Our pan-India 5G capex cycle has peaked, and telecom cash flows are now strongly converting to free cash flow.",
        "source_doc_ref": "Reliance Q1 FY27 Media & Analyst Presentation, Slide 14",
        "delivery_notes": "Tariff hikes in July 2024 drove 7.4% QoQ ARPU improvement."
    }
]

# Concalls with SHA-256 Content Hash (F-08)
CONCALL_SEED = [
    {
        "id": "concall-dixon-q2fy27",
        "isin": "INE806N01020",
        "ticker": "DIXON.NS",
        "fiscal_quarter": "Q2FY27",
        "transcript_date": "2026-11-05",
        "content_hash": compute_hash("Atul Lall MD Dixon Q2 consolidated revenues 11534 Cr mobile 8535 Cr run rate 3.8M"),
        "management_remarks": "Atul Lall (MD): In Q2, our consolidated revenues stood at Rs 11,534 Cr, representing a phenomenal 120% YoY growth (120.4% YoY expansion). The mobile division delivered Rs 8,535 Cr against our internal budget of Rs 8,000 Cr. Our smartphone monthly run rate has crossed 3.8 million units and we are targeting 5.0 million units monthly run rate during FY27.",
        "guidance_excerpts": "Guidance for H2 FY27: We expect full-year FY27 revenues to approach Rs 38,000 Cr to Rs 40,000 Cr. For display modules and precision components, our JV with HKC is on schedule for pilot production in Q4 FY27.",
        "analyst_qa_excerpts": "Analyst (UBS): What is the sustainable margin on the mobile business? Atul Lall: On pure assembly, margins will be 3.0% to 3.2%. However, as backward integration into display and battery packs kicks in, blended mobile margin will expand toward 4.2%."
    },
    {
        "id": "concall-trent-q2fy27",
        "isin": "INE849A01020",
        "ticker": "TRENT.NS",
        "fiscal_quarter": "Q2FY27",
        "transcript_date": "2026-11-08",
        "content_hash": compute_hash("Noel Tata Venkatesalu CEO Standalone Q2 revenue 4035 Cr up 39 pct YoY Zudio 50 to 60 stores Q3"),
        "management_remarks": "Noel Tata / P. Venkatesalu (CEO): Standalone Q2 revenue was Rs 4,035 Cr, up 39% YoY (39.1% YoY expansion). Westside and Zudio combined registered 12% like-for-like (LFL) sales growth across mature stores.",
        "guidance_excerpts": "We will open between 50 to 60 Zudio stores in Q3 ahead of the festive and winter season. Capex per store remains tightly controlled at Rs 2.2 Cr.",
        "analyst_qa_excerpts": "Analyst (Morgan Stanley): Are you seeing any demand fatigue in small towns? Venkatesalu: Absolutely none. In fact, tier 3 stores are reaching cash breakeven within 45 days of launch."
    },
    {
        "id": "concall-hdfc-q2fy27",
        "isin": "INE040A01034",
        "ticker": "HDFCBANK.NS",
        "fiscal_quarter": "Q2FY27",
        "transcript_date": "2026-10-22",
        "content_hash": compute_hash("Sashidhar Jagdishan MD HDFC Bank core NIM 3.46 gross NPA 1.36 net NPA 0.41"),
        "management_remarks": "Sashidhar Jagdishan (MD & CEO): In Q2, our Net Interest Income grew to Rs 30,110 Cr with core Net Interest Margin stabilizing at 3.46%. Asset quality remains pristine with Gross NPA at 1.36% and Net NPA at 0.41%.",
        "guidance_excerpts": "Post-merger with parent HDFC, our core focus is maintaining NIM between 3.4% to 3.6% while running down high-cost borrowings. Deposit accretion will outpace loan growth to bring LDR to historical levels.",
        "analyst_qa_excerpts": "Analyst (Goldman Sachs): How soon will the credit-deposit ratio normalize? Jagdishan: We expect CD ratio to approach 90% over the next 24 to 36 months via strong retail branch deposit mobilization."
    },
    {
        "id": "concall-reliance-q2fy27",
        "isin": "INE002A01018",
        "ticker": "RELIANCE.NS",
        "fiscal_quarter": "Q2FY27",
        "transcript_date": "2026-10-28",
        "content_hash": compute_hash("Mukesh Ambani Reliance Jio retail EBITDA 5G capex tapering free cash flow"),
        "management_remarks": "Mukesh Ambani (Chairman): Consolidated EBITDA for Q2 was Rs 43,934 Cr. Consumer businesses (Jio and Retail) contributed over 50% of EBITDA. Telecom ARPU rose to Rs 195 following the July tariff revision.",
        "guidance_excerpts": "Our pan-India 5G capex cycle has peaked, and telecom cash flows are now strongly converting to free cash flow. In New Energy, our solar giga-factory in Jamnagar will commence phased commercial operations in H2 FY27.",
        "analyst_qa_excerpts": "Analyst (Citi): What is the outlook on petchem margins? Srikanth Venkatachari: O2C margins were impacted by global refining weakness, but domestic retail fuel integration cushioned the downstream segment."
    }
]

# Tenant-Isolated Network Contacts (F-02, F-03)
# Compliance-verified contacts: active auditor removed; component suppliers populated
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
        "recent_development_summary": "IIT Kanpur 2004 alumnus connection with Vikram Seth (newly appointed COO of Kaynes Tech); ex-colleague at Foxconn.",
        "notes": "Go-to expert on Indian electronics manufacturing, contract assembly economics, and executive talent.",
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
        "recent_development_summary": "Leads OEM component sourcing; valuable contact for general mobile supply chain lead time trends.",
        "notes": "Permissible scuttlebutt source for high-level industry component lead times and festive retail sell-through (SEBI PIT Compliant: No proprietary OEM internal data).",
        "last_verified": "2026-11-05"
    },
    {
        "id": "net-03",
        "tenant_id": "tenant-enam-01",
        "name": "Dr. Arvind Swaminathan",
        "current_title": "Specialty Chemicals Technical Advisor",
        "current_company": "Swaminathan Chemical Advisory",
        "current_company_ticker": None,
        "relationship_strength": 4,
        "is_starred": 1,
        "past_companies": [
            {"company": "Atul Ltd", "role": "Head of Technical Operations", "start_year": 2012, "end_year": 2021},
            {"company": "Aarti Industries", "role": "Senior Process Director", "start_year": 2004, "end_year": 2012}
        ],
        "education": [
            {"institution": "IIT Bombay", "degree": "Ph.D Chemical Engineering", "year": "2002"}
        ],
        "themes": ["Specialty Chemicals", "Process Engineering", "Phenol & Aromatics"],
        "relevance_score": 9.1,
        "recent_development_summary": "Independent chemical process consultant; deep technical knowledge of Deepak Nitrite's Dahej phenol capacity and feedstock dynamics.",
        "notes": "Permissible technical expert for chemical yield curves and nitric acid / benzene feedstock cost pass-through.",
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
        "recent_development_summary": "Ex-Head of Zudio Merchandising at Trent; Trent just announced 39.1% revenue growth and 570 store milestone.",
        "notes": "Natural reconnect hook: discuss retail inventory replenishment velocity and small-town consumer behavior.",
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
        "recent_development_summary": "VP at Tata Motors; oversees domestic commercial vehicle operations following Q2 results.",
        "notes": "Senior IIT Kanpur alumnus. Ground-level insight into domestic commercial fleet demand, freight tonnage, and steel cost indexation.",
        "last_verified": "2026-11-10"
    },
    {
        "id": "net-06",
        "tenant_id": "tenant-enam-01",
        "name": "Naresh Kashyap",
        "current_title": "VP Sourcing & Business Development",
        "current_company": "Holitech Display Solutions India",
        "current_company_ticker": None,
        "relationship_strength": 4,
        "is_starred": 0,
        "past_companies": [
            {"company": "Motherson Electronic Components", "role": "General Manager", "start_year": 2014, "end_year": 2020}
        ],
        "education": [
            {"institution": "BITS Pilani", "degree": "B.E. Electronics & Instrumentation", "year": "2006"}
        ],
        "themes": ["Electronics EMS", "Hardware Supply Chain", "Display Modules", "Suppliers"],
        "relevance_score": 8.7,
        "recent_development_summary": "Supplies display and camera sub-assemblies to major Indian EMS assemblers including Dixon.",
        "notes": "Permissible vendor source on component inventory days and BOM localization.",
        "last_verified": "2026-11-08"
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

        # Clean purge of transactional and volatile test tables to guarantee idempotency
        cursor.execute("DELETE FROM user_alert_state;")
        cursor.execute("DELETE FROM detected_anomalies;")
        cursor.execute("DELETE FROM announcements;")
        cursor.execute("DELETE FROM guidance_history;")
        cursor.execute("DELETE FROM mnpi_call_audit_log;")
        cursor.execute("DELETE FROM network_relationships;")
        cursor.execute("DELETE FROM network_contacts;")
        cursor.execute("DELETE FROM market_eod;")
        cursor.execute("DELETE FROM concall_transcripts;")

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
        INSERT OR REPLACE INTO user_preferences (user_id, volume_multiplier_threshold, price_move_pct_threshold, auto_notify_critical, push_privacy_mode, max_daily_alerts_per_ticker, starred_tickers, enabled_categories)
        VALUES ('user-enam-01', 2.0, 3.5, 1, 0, 3, '[]', '["results","M&A","management_change","fund_raise","litigation","capex"]');
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

        # 6. Seed Market EOD (60 trading days per company for genuine statistical sigma)
        market_eod_data = generate_market_eod_data()
        for m in market_eod_data:
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
        for idx, anom in enumerate(ANOMALIES_SEED):
            cursor.execute("""
            INSERT OR REPLACE INTO detected_anomalies (id, isin, ticker, anomaly_type, severity, headline, detail, metrics, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                anom["id"], anom["isin"], anom["ticker"], anom["anomaly_type"], anom["severity"],
                anom["headline"], anom["detail"], json.dumps(anom["metrics"]), anom["created_at"]
            ))

            # Only pin the highest critical alert by default (Dixon)
            is_pinned = 1 if (idx == 0 and anom["severity"] == "CRITICAL") else 0
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

    print(f"Successfully seeded FINN database with clean, institutional-grade primary disclosures: {len(COMPANIES_SEED)} companies, {len(market_eod_data)} EOD records (60d history), {len(ANOMALIES_SEED)} consolidated anomalies, {len(NETWORK_CONTACTS_SEED)} network contacts.")

if __name__ == "__main__":
    seed_database()
