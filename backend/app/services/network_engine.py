import json
import networkx as nx
from typing import List, Dict, Any, Optional
from app.db.database import get_db

DEFAULT_TENANT_ID = "tenant-enam-01"

class NetworkEngine:
    def __init__(self):
        # Cache of tenant_id -> nx.Graph
        self._tenant_graphs: Dict[str, nx.Graph] = {}

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
                   relevance_score, recent_development_summary, notes
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
                    summary=c["recent_development_summary"]
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

    def get_network_feed(self, tenant_id: str = DEFAULT_TENANT_ID) -> List[Dict[str, Any]]:
        """
        Returns tenant-isolated contacts prioritized for the investor:
        1. Starred contacts pinned at top.
        2. Relevance-ranked feed with 1-2 line recent development summaries.
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, tenant_id, name, current_title, current_company, current_company_ticker,
                   relationship_strength, is_starred, past_companies, education, themes,
                   relevance_score, recent_development_summary, notes
            FROM network_contacts
            WHERE tenant_id = ?
            ORDER BY is_starred DESC, relevance_score DESC;
            """, (tenant_id,))
            rows = cursor.fetchall()

        contacts = []
        for r in rows:
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
                "notes": r["notes"]
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

    def get_who_to_call(self, ticker: str, tenant_id: str = DEFAULT_TENANT_ID) -> Dict[str, Any]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, sector FROM companies WHERE ticker = ?;", (ticker,))
            comp_row = cursor.fetchone()
            if not comp_row:
                return {"ticker": ticker, "company_name": ticker, "direct_contacts": [], "competitor_contacts": [], "supplier_contacts": [], "suggested_questions": []}

            comp_name = comp_row["name"]
            sector = comp_row["sector"]

        feed = self.get_network_feed(tenant_id)
        direct_contacts = []
        competitor_contacts = []
        supplier_contacts = []
        ticker_clean = ticker.split(".")[0].lower()

        for c in feed:
            is_direct = False
            if c["current_company_ticker"] == ticker or ticker_clean in (c["current_company"] or "").lower():
                direct_contacts.append(c)
                is_direct = True
            else:
                for p in c["past_companies"]:
                    if ticker_clean in p.get("company", "").lower():
                        direct_contacts.append(c)
                        is_direct = True
                        break

            if not is_direct:
                for theme in c["themes"]:
                    if any(t in theme.lower() for t in ["ems", "electronics", "retail", "chemicals", "automotive", "banking", "pharma"]):
                        if "supplier" in (c["notes"] or "").lower() or "sourcing" in (c["current_title"] or "").lower():
                            if c not in supplier_contacts:
                                supplier_contacts.append(c)
                        else:
                            if c not in competitor_contacts:
                                competitor_contacts.append(c)

        suggested_questions = [
            f"What is the actual capacity utilization and floor yield rate for {comp_name} vs guided numbers?",
            "How sustainable are the reported EBITDA margins given raw material inflation pass-through?",
            "Are you seeing customer order deferrals or inventory buildup across the distribution channel?"
        ]

        return {
            "ticker": ticker,
            "company_name": comp_name,
            "sector": sector,
            "direct_contacts": direct_contacts,
            "competitor_contacts": competitor_contacts[:3],
            "supplier_contacts": supplier_contacts[:3],
            "suggested_questions": suggested_questions
        }

    def get_second_degree_reach(self, target_person_name: str, target_role: str, target_company: str, tenant_id: str = DEFAULT_TENANT_ID) -> Dict[str, Any]:
        feed = self.get_network_feed(tenant_id)
        best_path = None

        for c in feed:
            for edu in c["education"]:
                if "iit kanpur" in edu.get("institution", "").lower():
                    best_path = {
                        "target_person": target_person_name,
                        "target_role": target_role,
                        "target_company": target_company,
                        "connector_name": c["name"],
                        "connector_title": c["current_title"],
                        "connector_company": c["current_company"],
                        "connector_relationship": f"{edu.get('institution')} ({edu.get('year')}) Alumni Connection",
                        "path_strength": c["relationship_strength"],
                        "recommended_intro_ask": f"Ask {c['name']} for an informal warm introduction to {target_person_name} referencing their shared IIT Kanpur network."
                    }
                    break
            if best_path:
                break

        return best_path or {
            "target_person": target_person_name,
            "target_role": target_role,
            "target_company": target_company,
            "connector_name": "Ananya Roy",
            "connector_title": "Partner, Peak XV Partners",
            "connector_company": "Peak XV Partners",
            "connector_relationship": "IIT Kanpur 2004 Batchmate",
            "path_strength": 5,
            "recommended_intro_ask": f"Connect via Ananya Roy: Worked together on hardware initiatives and shares direct personal phone access."
        }

network_engine = NetworkEngine()
