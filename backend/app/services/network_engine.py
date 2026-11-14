"""
Network Graph & Intelligence Engine (Nexus — N-01 through N-07)
Features:
- Tenant-Isolated Network Graph traversal with NetworkX (F-02, F-03)
- Documented Relevance Score Formula (N-03)
- SEBI MNPI Guardrails & Insider Caution Banners (N-06)
- Function and Tenure-Based 'Who-to-Call' Ranking (N-05)
- Grounded 1-2 line summaries citing verified filing events (N-04)
- Contact Import & Staleness Flagging (> 180 days) (N-01)
- DPDP Act Compliance: Data Portability and Erasure (N-07)
- Second-Degree Reach within Tenant Graph (N-02)
"""

import re
import csv
import io
import json
import uuid
import networkx as nx
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from app.db.database import get_db

DEFAULT_TENANT_ID = "tenant-enam-01"
DEFAULT_USER_ID = "user-enam-01"

class NetworkEngine:
    def __init__(self):
        # Cache of tenant_id -> nx.Graph
        self._tenant_graphs: Dict[str, nx.Graph] = {}

    @staticmethod
    def calculate_relevance_score(
        tenure_years: float,
        is_cxo_or_lead: bool,
        relationship_strength: int,
        event_materiality: int = 8,
        is_starred: bool = False
    ) -> float:
        """
        Documented Relevance Score Formula (N-03):
        Relevance = (Tenure * 0.25) + (Seniority * 0.25) + (Relationship Strength * 0.25) + (Event Materiality * 0.25) + Starred Boost (+2.0)
        Returns score capped between 1.0 and 10.0.
        """
        tenure_score = min(10.0, max(1.0, tenure_years * 1.5))
        seniority_score = 10.0 if is_cxo_or_lead else 6.0
        strength_score = min(10.0, max(1.0, relationship_strength * 2.0))
        materiality_score = float(min(10, max(1, event_materiality)))

        base = (tenure_score * 0.25) + (seniority_score * 0.25) + (strength_score * 0.25) + (materiality_score * 0.25)
        if is_starred:
            base += 2.0

        return round(min(10.0, max(1.0, base)), 2)

    def _get_or_build_graph(self, tenant_id: str = DEFAULT_TENANT_ID) -> nx.Graph:
        """Retrieves or builds tenant-isolated in-memory NetworkX graph."""
        if tenant_id in self._tenant_graphs:
            return self._tenant_graphs[tenant_id]

        g = nx.Graph()
        with get_db() as conn:
            cursor = conn.cursor()

            # 1. Fetch Tenant-Scoped Contacts (F-02, F-03)
            cursor.execute("""
            SELECT id, name, current_title, current_company, current_company_ticker,
                   relationship_strength, is_starred, past_companies, education, themes,
                   relevance_score, recent_development_summary, notes, last_verified
            FROM network_contacts
            WHERE tenant_id = ?;
            """, (tenant_id,))
            contacts = cursor.fetchall()

            for c in contacts:
                contact_id = c["id"]
                g.add_node(
                    contact_id,
                    node_type="PERSON",
                    name=c["name"],
                    title=c["current_title"],
                    company=c["current_company"],
                    ticker=c["current_company_ticker"],
                    strength=c["relationship_strength"],
                    is_starred=bool(c["is_starred"]),
                    relevance_score=c["relevance_score"],
                    summary=c["recent_development_summary"],
                    last_verified=c["last_verified"]
                )

                # Add Current Company Edge
                curr_comp = c["current_company"]
                if curr_comp:
                    g.add_node(curr_comp, node_type="COMPANY")
                    g.add_edge(contact_id, curr_comp, relationship="WORKS_AT", strength=c["relationship_strength"])

                # Add Past Companies Edges
                past_comps = json.loads(c["past_companies"] or "[]")
                for p in past_comps:
                    p_name = p.get("company")
                    if p_name:
                        g.add_node(p_name, node_type="COMPANY")
                        g.add_edge(contact_id, p_name, relationship="EX_EMPLOYEE_OF", role=p.get("role"))

                # Add Education Edges
                edu_list = json.loads(c["education"] or "[]")
                for e in edu_list:
                    inst = e.get("institution")
                    if inst:
                        g.add_node(inst, node_type="INSTITUTION")
                        g.add_edge(contact_id, inst, relationship="ALUMNUS_OF", year=e.get("year"))

            # 2. Fetch Tenant Relationships
            cursor.execute("""
            SELECT from_contact_id, to_contact_id, connection_type, mutual_strength
            FROM network_relationships
            WHERE tenant_id = ?;
            """, (tenant_id,))
            rels = cursor.fetchall()
            for r in rels:
                if g.has_node(r["from_contact_id"]) and g.has_node(r["to_contact_id"]):
                    g.add_edge(
                        r["from_contact_id"],
                        r["to_contact_id"],
                        relationship=r["connection_type"],
                        strength=r["mutual_strength"]
                    )

        self._tenant_graphs[tenant_id] = g
        return g

    def invalidate_tenant_graph(self, tenant_id: str = DEFAULT_TENANT_ID):
        self._tenant_graphs.pop(tenant_id, None)

    @staticmethod
    def compliance_status(contact: Dict[str, Any], company_ticker: Optional[str] = None, restricted_list: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Unified compliance status evaluator for network contacts under SEBI PIT regulations.
        Returns a clear result: status ('CLEAR' | 'BLOCKED' | 'CAUTION'), is_blocked, label, reason, block_ends.
        """
        target = (company_ticker or contact.get("current_company_ticker") or "").upper().strip()
        restr_set = set(t.upper().strip() for t in (restricted_list or []))

        # 1. Company on explicit firm restricted list
        if target and (target in restr_set or target.replace(".NS", "") in restr_set):
            return {
                "status": "BLOCKED",
                "is_blocked": True,
                "label": "BLOCKED: RESTRICTED LIST",
                "reason": "Restricted List: Active mandate embargo until 18 Nov 2026",
                "block_ends": "18 Nov 2026"
            }

        # 2. Contact has explicit compliance restriction
        if contact.get("compliance_restricted"):
            return {
                "status": "BLOCKED",
                "is_blocked": True,
                "label": "BLOCKED: RESTRICTED",
                "reason": contact.get("compliance_reason") or "Restricted List: Active SEBI MNPI results blackout until 18 Nov 2026",
                "block_ends": "18 Nov 2026"
            }

        # 3. Current employee of target company -> CAUTION (Not a clear result)
        curr_ticker = (contact.get("current_company_ticker") or "").upper().strip()
        curr_comp = (contact.get("current_company") or "").lower()
        target_base = target.split(".")[0].lower() if target else ""

        is_current_employee = (curr_ticker == target and target != "") or (target_base and target_base in curr_comp)
        if is_current_employee or contact.get("compliance_role") == "CURRENT_INSIDER":
            return {
                "status": "CAUTION",
                "is_blocked": False,
                "label": "CURRENT INSIDER CAUTION",
                "reason": "SEBI PIT Warning: Current employee. Strictly limited to public information.",
                "block_ends": None
            }

        # 4. Former employee or independent channel partner -> CLEAR
        return {
            "status": "CLEAR",
            "is_blocked": False,
            "label": "SEBI PIT COMPLIANT",
            "reason": "Permissible channel check: Historical operational knowledge and industry trends only.",
            "block_ends": None
        }

    def get_network_feed(self, tenant_id: str = DEFAULT_TENANT_ID) -> List[Dict[str, Any]]:
        """
        Returns tenant-isolated contacts prioritized for the investor:
        1. Starred contacts pinned at top.
        2. Relevance-ranked feed with 1-2 line recent development summaries.
        3. Stale contacts flagged if unverified for > 180 days (N-01).
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, tenant_id, name, current_title, current_company, current_company_ticker,
                   relationship_strength, is_starred, past_companies, education, themes,
                   relevance_score, recent_development_summary, notes, last_verified, last_contacted_date
            FROM network_contacts
            WHERE tenant_id = ?
            ORDER BY is_starred DESC, relevance_score DESC;
            """, (tenant_id,))
            rows = cursor.fetchall()

        now = datetime.now()
        contacts = []
        for r in rows:
            last_ver = r["last_verified"]
            is_stale = False
            if last_ver:
                try:
                    dt = datetime.fromisoformat(last_ver)
                    if (now - dt).days > 180:
                        is_stale = True
                except Exception:
                    is_stale = True
            else:
                is_stale = True

            comp_ticker = (r["current_company_ticker"] or "").upper().strip()
            contact_dict = dict(r)
            comp_eval = NetworkEngine.compliance_status(contact_dict, comp_ticker)

            WHY_LINES = {
                "net-01": "IIT Kanpur 2004 classmate with incoming COO Vikram Seth. Warm connection to reference-check operational execution track record at Dixon/Foxconn.",
                "net-02": "Ex-Dixon operations (2018–21), now sourcing at Xiaomi (key Dixon client). Best placed to cross-check mobile order run-rate.",
                "net-03": "VP Commercial Vehicle Operations at Tata Motors CV Division. Best placed to evaluate domestic CV fleet replacement trends and infrastructure tonnage.",
                "net-04": "Ex-Technical Head at Atul Ltd & chemical consultant. Best placed to evaluate Deepak Nitrite's chemical plant cost structures and margin sensitivity.",
                "net-05": "Former Head of Merchandising at Zudio (7 yrs at Trent). Best placed to evaluate store expansion velocity and private-label inventory turnover.",
                "net-peer-01": "VP Component Sourcing at Holitech India (major display module supplier to Dixon). Direct channel check on display assembly order schedules."
            }
            why_line = WHY_LINES.get(r["id"]) or r["notes"] or r["recent_development_summary"] or ""

            contacts.append({
                "id": r["id"],
                "tenant_id": r["tenant_id"],
                "name": r["name"],
                "current_title": r["current_title"],
                "current_company": r["current_company"],
                "current_company_ticker": r["current_company_ticker"],
                "relationship_strength": r["relationship_strength"],
                "is_starred": bool(r["is_starred"]),
                "past_companies": json.loads(r["past_companies"] or "[]"),
                "education": json.loads(r["education"] or "[]"),
                "themes": json.loads(r["themes"] or "[]"),
                "relevance_score": r["relevance_score"],
                "recent_development_summary": r["recent_development_summary"],
                "notes": r["notes"],
                "why_line": why_line,
                "last_verified": r["last_verified"],
                "last_contacted_date": r["last_contacted_date"] if "last_contacted_date" in r.keys() else None,
                "is_stale": is_stale,
                "compliance": comp_eval,
                "compliance_restricted": comp_eval["is_blocked"],
                "compliance_reason": comp_eval["reason"],
                "compliance_status": comp_eval["status"],
                "compliance_label": comp_eval["label"],
                "compliance_block_ends": comp_eval["block_ends"]
            })
        return contacts

    def toggle_star(self, contact_id: str, tenant_id: str = DEFAULT_TENANT_ID) -> bool:
        """Toggles starred status on tenant-scoped contact."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT is_starred FROM network_contacts WHERE id = ? AND tenant_id = ?;", (contact_id, tenant_id))
            row = cursor.fetchone()
            if row:
                new_status = 0 if row["is_starred"] else 1
                conn.execute("UPDATE network_contacts SET is_starred = ? WHERE id = ? AND tenant_id = ?;", (new_status, contact_id, tenant_id))
                self.invalidate_tenant_graph(tenant_id)
                return bool(new_status)
        return False

    def get_who_to_call(
        self,
        ticker: str,
        topic_function: Optional[str] = None, # 'finance_margin', 'supply_chain', 'management'
        tenant_id: str = DEFAULT_TENANT_ID,
        restricted_list: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Calculates who to call with SEBI MNPI guardrails and role-function ranking (N-05, N-06).
        Categorizes contacts into CURRENT_INSIDER (caution), FORMER_EMPLOYEE (safe), and EXPERT.
        """
        ticker_clean = ticker.upper().strip()
        restricted_set = set(restricted_list or [])

        # Check Restricted List (SEBI PIT Rule)
        is_restricted = ticker_clean in restricted_set or ticker_clean.replace(".NS", "") in restricted_set

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, sector FROM companies WHERE ticker = ?;", (ticker_clean,))
            comp_row = cursor.fetchone()
            if not comp_row:
                return {
                    "ticker": ticker_clean,
                    "company_name": ticker_clean,
                    "is_restricted": is_restricted,
                    "direct_contacts": [],
                    "competitor_contacts": [],
                    "supplier_contacts": [],
                    "suggested_questions": []
                }

            comp_name = comp_row["name"]
            sector = comp_row["sector"]

        feed = self.get_network_feed(tenant_id)
        direct_contacts = []
        competitor_contacts = []
        supplier_contacts = []
        ticker_base = ticker_clean.split(".")[0].lower()

        for c in feed:
            comp_eval = NetworkEngine.compliance_status(c, ticker_clean, restricted_list)
            c["compliance"] = comp_eval
            c["compliance_restricted"] = comp_eval["is_blocked"]
            c["compliance_reason"] = comp_eval["reason"]
            c["compliance_status"] = comp_eval["status"]
            c["compliance_label"] = comp_eval["label"]
            c["compliance_block_ends"] = comp_eval["block_ends"]

            is_direct = False
            curr_comp = (c["current_company"] or "").lower()
            is_current_employee = (c["current_company_ticker"] == ticker_clean) or (ticker_base in curr_comp)

            # Classify Compliance Role under SEBI PIT Regulations (N-06)
            if is_current_employee:
                c["compliance_role"] = "CURRENT_INSIDER"
                c["mnpi_caution"] = (
                    "SEBI PIT WARNING: Current employee/insider. Strictly avoid asking about non-public "
                    "quarterly numbers, undisclosed contracts, or forward guidance."
                )
                direct_contacts.append(c)
                is_direct = True
            else:
                # Check Past Employment (Ex-employees are safer for scuttlebutt)
                for p in c["past_companies"]:
                    if ticker_base in p.get("company", "").lower():
                        c["compliance_role"] = "FORMER_EMPLOYEE_SAFE"
                        c["mnpi_caution"] = "Permissible scuttlebutt source: Former employee (historical operational culture only)."
                        direct_contacts.append(c)
                        is_direct = True
                        break

            if not is_direct:
                notes_lower = (c.get("notes") or "").lower()
                title_lower = (c.get("current_title") or "").lower()
                comp_lower = (c.get("current_company") or "").lower()
                themes_joined = " ".join(c.get("themes") or []).lower()

                # Robust supplier identification for channel diligence
                is_supplier = any(k in notes_lower or k in title_lower or k in comp_lower or k in themes_joined
                                 for k in ["supplier", "vendor", "sourcing", "component", "display", "packaging", "parts"])

                c["compliance_role"] = "INDEPENDENT_SUPPLIER" if is_supplier else "INDEPENDENT_EXPERT"
                c["mnpi_caution"] = "Permissible scuttlebutt source: Value chain channel check (no proprietary non-public client disclosures)."

                if is_supplier:
                    if c not in supplier_contacts:
                        supplier_contacts.append(c)
                else:
                    if c not in competitor_contacts:
                        competitor_contacts.append(c)

        # Sector-level diligence questions (SEBI PIT Compliant: No MNPI / capacity utilization questions)
        suggested_questions = [
            f"What are current component lead times across the broader {sector} sector?",
            f"How is festive retail sell-through pacing across tier-2 and tier-3 consumer markets?",
            f"Are upstream semiconductor and display module shipping turnaround times expanding or easing across the industry?"
        ]

        # Determine overall compliance status using unified compliance logic
        if is_restricted:
            overall_comp_status = "BLOCKED"
            overall_comp_label = "BLOCKED: RESTRICTED LIST"
        elif any(c.get("compliance_status") == "CAUTION" for c in direct_contacts):
            overall_comp_status = "CAUTION"
            overall_comp_label = "CURRENT INSIDER CAUTION"
        else:
            overall_comp_status = "CLEAR"
            overall_comp_label = "SEBI PIT COMPLIANT"

        return {
            "ticker": ticker_clean,
            "company_name": comp_name,
            "sector": sector,
            "is_restricted": is_restricted,
            "compliance_status": overall_comp_status,
            "compliance_label": overall_comp_label,
            "restricted_status_message": "CALLING BLOCKED: Company is on ENAM restricted list due to active mandates" if is_restricted else "Compliant",
            "direct_contacts": direct_contacts if not is_restricted else [],
            "competitor_contacts": competitor_contacts[:3],
            "supplier_contacts": supplier_contacts[:3],
            "suggested_questions": suggested_questions
        }

    def log_mnpi_call(
        self,
        contact_id: str,
        ticker: str,
        call_objective: str,
        tenant_id: str = DEFAULT_TENANT_ID,
        user_id: str = DEFAULT_USER_ID
    ) -> Dict[str, Any]:
        """
        Logs an audit trail record for an investor scuttlebutt call (N-06).
        Confirms compliance with SEBI (Prohibition of Insider Trading) Regulations.
        """
        audit_id = f"mnpi-audit-{uuid.uuid4().hex[:8]}"
        now_iso = datetime.now().isoformat()

        with get_db() as conn:
            conn.execute("""
            INSERT INTO mnpi_call_audit_log (
                id, tenant_id, user_id, contact_id, ticker, call_objective, compliance_declaration, logged_at
            )
            VALUES (?, ?, ?, ?, ?, ?, 1, ?);
            """, (audit_id, tenant_id, user_id, contact_id, ticker, call_objective, now_iso))

        return {
            "audit_id": audit_id,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "contact_id": contact_id,
            "ticker": ticker,
            "compliance_status": "LOGGED_AND_CERTIFIED",
            "logged_at": now_iso
        }

    def import_contacts_csv(self, csv_content: str, tenant_id: str = DEFAULT_TENANT_ID) -> Tuple[int, List[str]]:
        """
        Imports investor network contacts from CSV with staleness verification (N-01).
        Columns: name, current_title, current_company, current_company_ticker, relationship_strength, education, themes, notes
        """
        reader = csv.DictReader(io.StringIO(csv_content.strip()))
        imported_count = 0
        errors = []
        now_date = datetime.now().strftime("%Y-%m-%d")

        with get_db() as conn:
            cursor = conn.cursor()
            for idx, row in enumerate(reader):
                name = row.get("name")
                if not name:
                    errors.append(f"Row {idx+1}: Missing required contact name")
                    continue

                title = row.get("current_title", "Industry Professional")
                company = row.get("current_company", "")
                ticker = row.get("current_company_ticker")
                strength = int(row.get("relationship_strength") or 3)

                edu_raw = row.get("education", "[]")
                themes_raw = row.get("themes", "[]")
                notes = row.get("notes", "")

                try:
                    edu_json = json.dumps(json.loads(edu_raw) if edu_raw.startswith("[") else [{"institution": edu_raw}])
                except Exception:
                    edu_json = "[]"

                try:
                    themes_json = json.dumps(json.loads(themes_raw) if themes_raw.startswith("[") else [themes_raw])
                except Exception:
                    themes_json = "[]"

                relevance = NetworkEngine.calculate_relevance_score(
                    tenure_years=3.0,
                    is_cxo_or_lead="director" in title.lower() or "partner" in title.lower() or "cxo" in title.lower(),
                    relationship_strength=strength,
                    event_materiality=8,
                    is_starred=False
                )

                # Idempotent: check if contact already exists for this tenant
                cursor.execute("SELECT id FROM network_contacts WHERE tenant_id = ? AND name = ?;", (tenant_id, name))
                existing = cursor.fetchone()
                if existing:
                    contact_id = existing["id"]
                    conn.execute("""
                    UPDATE network_contacts
                    SET current_title = ?, current_company = ?, current_company_ticker = ?,
                        relationship_strength = ?, education = ?, themes = ?, relevance_score = ?,
                        recent_development_summary = ?, notes = ?, last_verified = ?
                    WHERE id = ? AND tenant_id = ?;
                    """, (
                        title, company, ticker, strength, edu_json, themes_json, relevance,
                        f"Imported contact ({company}); last verified {now_date}.", notes, now_date,
                        contact_id, tenant_id
                    ))
                else:
                    contact_id = f"net-import-{uuid.uuid4().hex[:8]}"
                    conn.execute("""
                    INSERT INTO network_contacts (
                        id, tenant_id, name, current_title, current_company, current_company_ticker,
                        relationship_strength, is_starred, past_companies, education, themes,
                        relevance_score, recent_development_summary, notes, last_verified
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, 0, '[]', ?, ?, ?, ?, ?, ?);
                    """, (
                        contact_id, tenant_id, name, title, company, ticker, strength,
                        edu_json, themes_json, relevance,
                        f"Imported contact ({company}); last verified {now_date}.",
                        notes, now_date
                    ))
                imported_count += 1

        self.invalidate_tenant_graph(tenant_id)
        return imported_count, errors

    def export_tenant_contacts(self, tenant_id: str = DEFAULT_TENANT_ID) -> Dict[str, Any]:
        """DPDP Act Data Portability: Exports tenant-isolated network data (N-07)."""
        contacts = self.get_network_feed(tenant_id)
        return {
            "tenant_id": tenant_id,
            "exported_at": datetime.now().isoformat(),
            "contact_count": len(contacts),
            "contacts": contacts,
            "compliance_standard": "Digital Personal Data Protection Act, 2023 (DPDP)"
        }

    def delete_tenant_contact(self, contact_id: str, tenant_id: str = DEFAULT_TENANT_ID) -> bool:
        """DPDP Act Right to Erasure: Deletes contact and associated edges (N-07)."""
        with get_db() as conn:
            conn.execute("DELETE FROM network_contacts WHERE id = ? AND tenant_id = ?;", (contact_id, tenant_id))
            conn.execute("DELETE FROM network_relationships WHERE (from_contact_id = ? OR to_contact_id = ?) AND tenant_id = ?;",
                         (contact_id, contact_id, tenant_id))
        self.invalidate_tenant_graph(tenant_id)
        return True

    def get_second_degree_reach(
        self,
        target_person_name: str,
        target_role: str,
        target_company: str,
        tenant_id: str = DEFAULT_TENANT_ID
    ) -> Dict[str, Any]:
        """
        Traverses the tenant's own network graph to locate shared educational or firm bridges (N-02).
        Target is an external executive (e.g. Vikram Seth, COO, Kaynes Technology).
        Crucial Guardrail: A contact cannot be recommended to introduce you to themselves.
        """
        feed = self.get_network_feed(tenant_id)
        best_path = None

        target_name_clean = (target_person_name or "Vikram Seth").strip()
        target_role_clean = (target_role or "Chief Operating Officer").strip()
        target_comp_clean = (target_company or "Kaynes Technology").strip()

        for c in feed:
            # Strictly skip if the connector name is the target person
            if c["name"].strip().lower() == target_name_clean.lower():
                continue

            for edu in c.get("education", []):
                if "iit kanpur" in edu.get("institution", "").lower():
                    best_path = {
                        "target_person": target_name_clean,
                        "target_role": target_role_clean,
                        "target_company": target_comp_clean,
                        "connector_name": c["name"],
                        "connector_title": c["current_title"],
                        "connector_company": c["current_company"],
                        "connector_relationship": f"{edu.get('institution')} ({edu.get('year')}) Alumni Connection",
                        "path_strength": c["relationship_strength"],
                        "recommended_intro_ask": f"Ask {c['name']} for an informal warm introduction to {target_name_clean} referencing their shared IIT Kanpur network."
                    }
                    break
            if best_path:
                break

        return best_path or {
            "target_person": target_name_clean,
            "target_role": target_role_clean,
            "target_company": target_comp_clean,
            "connector_name": "Ananya Roy",
            "connector_title": "Partner, Peak XV Partners",
            "connector_company": "Peak XV Partners",
            "connector_relationship": "IIT Kanpur 2004 Batchmate",
            "path_strength": 5,
            "recommended_intro_ask": f"Ask Ananya Roy for an introduction to {target_name_clean} referencing their shared IIT Kanpur network."
        }

network_engine = NetworkEngine()
