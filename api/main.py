from http.client import HTTPException

from fastapi import FastAPI, Depends

from psycopg2.extras import RealDictCursor
from model import ItemSearch, HouseRentListRequest
from function import get_db_connection, get_list_ward_ids, get_lists_environment_ids

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
@app.post("/search/")
def search(item_search: ItemSearch, conn=Depends(get_db_connection)):
    try:
        list_ward_ids = get_list_ward_ids(
            item_search.province_id,
            item_search.district_id,
            item_search.ward_id,
            conn
        )
        str_ward_ids = ','.join(map(str, list_ward_ids))

        list_environment_ids = get_lists_environment_ids(
            item_search.search_content,
            conn
        )
        str_environment_ids = ','.join(map(str, list_environment_ids))

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT DISTINCT hr.id FROM
                public.house_rent_environment hre
                LEFT JOIN public.house_rent hr
                ON hre.house_rent_id = hr.id
                WHERE hr.available = TRUE
                AND hr.ward_id IN (%s)
                AND hre.environment_id IN (%s)
                AND hr.price BETWEEN %s AND %s
                AND hr.acreage BETWEEN %s AND %s
                AND (%s IS NULL OR %s = '' OR hr.house_type = %s)
                AND (%s IS NULL OR %s = '' OR hr.contract_period = %s)
                AND (%s IS NULL OR hr.bedrooms = %s)
                AND (%s IS NULL OR hr.living_rooms = %s)
                AND (%s IS NULL OR hr.kitchens = %s)
            """
            cur.execute(query, (
                str_ward_ids,
                str_environment_ids,
                item_search.price_min,
                item_search.price_max,
                item_search.acreage_min,
                item_search.acreage_max,
                item_search.house_type,
                item_search.contract_period,
                item_search.bedrooms,
                item_search.living_rooms,
                item_search.kitchens
            ))
            results = cur.fetchall()
        conn.close()
        return results
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
    
# Detail endpoint
@app.post("/house_rents/details/")
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