from http.client import HTTPException

from fastapi import FastAPI, Depends

from psycopg2.extras import RealDictCursor
from typing import List
from model import ItemSearch, HouseRentListRequest
from function import get_db_connection, get_list_ward_ids, get_lists_environment_ids, save_actions_results, save_log_actions

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI service!"}

@app.get("/db-check")
def db_check():
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "success", "message": "Database connection successful!"}
    except Exception as e:
        return {"status": "error", "message": f"Database connection failed: {e}"}

# Endpoint to get list of provinces, districts, and wards
@app.get("/provinces")
def get_provinces(conn=Depends(get_db_connection)):
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, name FROM public.provinces")
            provinces = cur.fetchall()
        conn.close()
        return provinces
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
    
@app.get("/districts/{province_id}")
def get_districts(province_id: int, conn=Depends(get_db_connection)):
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, name, province_id FROM public.districts WHERE province_id = %s", (province_id,))
            districts = cur.fetchall()
        conn.close()
        return districts
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
    
@app.get("/wards/{district_id}")
def get_wards(district_id: int, conn=Depends(get_db_connection)):
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, name, district_id FROM public.wards WHERE district_id = %s", (district_id,))
            wards = cur.fetchall()
        conn.close()
        return wards
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
    
# Endpoint to get distinct house types and contract periods
@app.get("/house_types")
def get_house_types(conn=Depends(get_db_connection)):
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT DISTINCT house_type FROM public.house_rent")
            house_types = cur.fetchall()
        conn.close()
        return house_types
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")

@app.get("/contract_periods")
def get_contract_periods(conn=Depends(get_db_connection)):
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT DISTINCT contract_period FROM public.house_rent")
            contract_periods = cur.fetchall()
        conn.close()
        return contract_periods
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
    
# Search endpoint
@app.post("/search")
def search(item_search: ItemSearch, conn=Depends(get_db_connection)):
    try:
        list_ward_ids = get_list_ward_ids(
            item_search.province_id,
            item_search.district_id,
            item_search.ward_id,
            conn
        )
        list_environment_ids = get_lists_environment_ids(
            item_search.search_content,
            conn
        )

        sql = """
            SELECT DISTINCT hr.id
            FROM public.house_rent_environment hre
            LEFT JOIN public.house_rent hr ON hre.house_rent_id = hr.id
            WHERE hr.available = TRUE
        """
        params: List = []

        sql += " AND hr.ward_id = ANY(%s)"
        params.append(list_ward_ids)

        sql += " AND hre.environment_id = ANY(%s)"
        params.append(list_environment_ids)

        if item_search.price_min is not None:
            sql += " AND hr.price >= %s"
            params.append(item_search.price_min)
        if item_search.price_max is not None:
            sql += " AND hr.price <= %s"
            params.append(item_search.price_max)

        if item_search.acreage_min is not None:
            sql += " AND hr.acreage >= %s"
            params.append(item_search.acreage_min)
        if item_search.acreage_max is not None:
            sql += " AND hr.acreage <= %s"
            params.append(item_search.acreage_max)

        if item_search.house_type is not None and str(item_search.house_type).strip() != "":
            sql += " AND hr.house_type = %s"
            params.append(item_search.house_type)

        if item_search.contract_period is not None and str(item_search.contract_period).strip() != "":
            sql += " AND hr.contract_period = %s"
            params.append(item_search.contract_period)

        if item_search.bedrooms is not None:
            sql += " AND hr.bedrooms = %s"
            params.append(item_search.bedrooms)

        if item_search.living_rooms is not None:
            sql += " AND hr.living_rooms = %s"
            params.append(item_search.living_rooms)

        if item_search.kitchens is not None:
            sql += " AND hr.kitchens = %s"
            params.append(item_search.kitchens)
        
        print("Final SQL:", sql)

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            final_query = cur.mogrify(sql, tuple(params)).decode('utf-8')
            print("Final SQL:", final_query)
            cur.execute(sql, tuple(params))
            results = cur.fetchall()

            action_id = save_log_actions("SEARCH", item_search, conn)
            save_actions_results(action_id, [row["id"] for row in results], conn)
        return results

    except HTTPException:
        raise
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass
    
# Detail endpoint
@app.post("/house_rents_details")
def get_house_rent_details(
    req: HouseRentListRequest,
    conn=Depends(get_db_connection)
):
    ids = req.house_rent_ids
    if not ids:
        try:
            return []
        finally:
            conn.close()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT hr.*
                FROM public.house_rent hr
                WHERE hr.id = ANY(%s)
                ORDER BY array_position(%s::int[], hr.id)
                """,
                (ids, ids)
            )
            results = cur.fetchall()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
    finally:
        conn.close()