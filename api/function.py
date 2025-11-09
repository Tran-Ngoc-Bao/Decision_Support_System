from http.client import HTTPException
import os
from typing import List, Optional
import psycopg2

from model import ItemSearch

def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST"),
        database=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        port=os.environ.get("POSTGRES_PORT")
    )
    return conn

def get_list_ward_ids(
    province_id: Optional[int],
    district_id: Optional[int],
    ward_id: Optional[int],
    conn
) -> List[int]:
    try:
        if ward_id is not None:
            return [ward_id]

        sql = """
            SELECT w.id
            FROM public.wards w
            JOIN public.districts d ON w.district_id = d.id
            JOIN public.provinces p ON d.province_id = p.id
        """
        conditions = []
        params = []
        if province_id is not None:
            conditions.append("p.id = %s")
            params.append(province_id)
        if district_id is not None:
            conditions.append("d.id = %s")
            params.append(district_id)
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        with conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            ward_ids = [row[0] for row in cur.fetchall()]

        return ward_ids
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve ward IDs: {e}")
    
def get_lists_environment_ids(
    search: Optional[str],
    conn
) -> List[int]:
    try:
        sql = "SELECT e.id FROM public.environment e"
        params = []

        if search is not None and str(search).strip() != "":
            sql += " WHERE e.value ILIKE %s"
            params.append(f"%{search}%")

        with conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            environment_ids = [row[0] for row in cur.fetchall()]

        return environment_ids
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve environment IDs: {e}")
    
def save_log_actions(
    action: str,
    item_search: ItemSearch,
    conn
) -> int:
    try:
        sql = """
            INSERT INTO public.log_actions (
                action,
                province_id,
                district_id,
                ward_id,
                search_content,
                persons,
                price_min,
                price_max,
                acreage_min,
                acreage_max,
                house_type,
                contract_period,
                bedrooms,
                living_rooms,
                kitchens
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        params = (
            action,
            item_search.province_id,
            item_search.district_id,
            item_search.ward_id,
            item_search.search_content,
            item_search.persons,
            item_search.price_min,
            item_search.price_max,
            item_search.acreage_min,
            item_search.acreage_max,
            item_search.house_type,
            item_search.contract_period,
            item_search.bedrooms,
            item_search.living_rooms,
            item_search.kitchens,
        )

        with conn.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            if not row:
                conn.rollback()
                raise HTTPException(status_code=500, detail="Failed to retrieve inserted id")
            inserted_id = row[0]
            conn.commit()
        return inserted_id

    except HTTPException:
        raise
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Failed to save log actions: {e}")
    
def save_actions_results(
    action_id: int,
    house_rent_ids: List[int],
    conn
):
    try:
        sql = """
            INSERT INTO public.actions_results (log_action_id, house_rent_id, house_rent_order)
            VALUES (%s, %s, %s)
        """
        with conn.cursor() as cur:
            for house_rent_id in house_rent_ids:
                cur.execute(sql, (action_id, house_rent_id, house_rent_ids.index(house_rent_id)))
            conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save actions results: {e}")