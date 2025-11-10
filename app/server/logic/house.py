from collections import defaultdict
from http.client import HTTPException
from typing import Any, Optional, List, Dict

from psycopg2.extras import RealDictCursor


class HouseService:

    @staticmethod
    def build_search_query(
            province_id: Optional[int] = None,
            district_id: Optional[int] = None,
            ward_id: Optional[int] = None,
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            min_acreage: Optional[float] = None,
            max_acreage: Optional[float] = None,
            house_type: Optional[str] = None,
            contract_period: Optional[str] = None,
            bedrooms: Optional[int] = None,
            living_rooms: Optional[int] = None,
            kitchens: Optional[int] = None,
            limit: int = 10,
            offset: int = 0
    ) -> tuple[str, list]:
        """
        Build SQL query and parameters for house rent search

        Returns:
            tuple: (query_string, parameters_list)
        """
        query = """
                SELECT hr.*, w.name as ward_name, d.name as district_name, p.name as province_name
                FROM house_rent hr
                         LEFT JOIN wards w ON hr.ward_id = w.id
                         LEFT JOIN districts d ON w.district_id = d.id
                         LEFT JOIN provinces p ON d.province_id = p.id
                WHERE hr.available = TRUE \
                """
        params = []

        def add_condition(field: str, value: Any, operator: str = "="):
            nonlocal query
            if value is not None:
                query += f" AND {field} {operator} %s"
                params.append(value)

        add_condition("p.id", province_id)
        add_condition("d.id", district_id)
        add_condition("hr.ward_id", ward_id)
        add_condition("hr.price", min_price, ">=")
        add_condition("hr.price", max_price, "<=")
        add_condition("hr.acreage", min_acreage, ">=")
        add_condition("hr.acreage", max_acreage, "<=")
        add_condition("hr.house_type", house_type)
        add_condition("hr.contract_period", contract_period)
        add_condition("hr.bedrooms", bedrooms)
        add_condition("hr.living_rooms", living_rooms)
        add_condition("hr.kitchens", kitchens)

        query += " ORDER BY hr.id LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        return query, params

    @staticmethod
    def get_house_environments(conn, house_ids: List[int]) -> Dict[int, List[Dict]]:
        """Get environment data for given house IDs"""
        if not house_ids:
            return {}

        house_ids_tuple = tuple(house_ids)

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                        SELECT hre.house_rent_id, e.id, e.category, e.value
                        FROM public.house_rent_environment hre
                                 JOIN public.environment e ON hre.environment_id = e.id
                        WHERE hre.house_rent_id IN %s
                        """, (house_ids_tuple,))
            env_rows = cur.fetchall()

        environments_by_house_id = defaultdict(list)
        for env in env_rows:
            environments_by_house_id[env['house_rent_id']].append(dict(env))

        return environments_by_house_id

    @classmethod
    def search_house_rent(
            cls,
            conn,
            province_id: Optional[int] = None,
            district_id: Optional[int] = None,
            ward_id: Optional[int] = None,
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            min_acreage: Optional[float] = None,
            max_acreage: Optional[float] = None,
            house_type: Optional[str] = None,
            contract_period: Optional[str] = None,
            bedrooms: Optional[int] = None,
            living_rooms: Optional[int] = None,
            kitchens: Optional[int] = None,
            limit: int = 10,
            offset: int = 0
    ) -> List[Dict]:
        """
        Search house rent information with filtering and pagination

        Returns:
            List of house rent items with environment data
        """
        try:
            # Build and execute main query
            query, params = cls.build_search_query(
                province_id=province_id,
                district_id=district_id,
                ward_id=ward_id,
                min_price=min_price,
                max_price=max_price,
                min_acreage=min_acreage,
                max_acreage=max_acreage,
                house_type=house_type,
                contract_period=contract_period,
                bedrooms=bedrooms,
                living_rooms=living_rooms,
                kitchens=kitchens,
                limit=limit,
                offset=offset
            )

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, tuple(params))
                results = cur.fetchall()

            if not results:
                return []

            # Convert to list of dictionaries
            houses = [dict(row) for row in results]
            house_ids = [house['id'] for house in houses]

            # Get environment data
            environments_by_house_id = cls.get_house_environments(conn, house_ids)

            # Combine house data with environment data
            for house in houses:
                house['environments'] = environments_by_house_id.get(house['id'], [])

            return houses

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database query failed: {str(e)}"
            )

    @classmethod
    def get_multiple_houses_by_ids(cls, conn, house_ids: List[int]) -> List[Dict]:
        """
        Get multiple houses by their IDs

        Args:
            conn: Database connection
            house_ids: List of house IDs to retrieve

        Returns:
            List of house information dictionaries
        """
        if not house_ids:
            return []

        try:
            house_ids_tuple = tuple(house_ids)
            query = """
                    SELECT hr.*, w.name as ward_name, d.name as district_name, p.name as province_name
                    FROM house_rent hr
                             LEFT JOIN wards w ON hr.ward_id = w.id
                             LEFT JOIN districts d ON w.district_id = d.id
                             LEFT JOIN provinces p ON d.province_id = p.id
                    WHERE hr.id IN %s \
                      AND hr.available = TRUE
                    ORDER BY hr.id \
                    """

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (house_ids_tuple,))
                results = cur.fetchall()

            if not results:
                return []

            # Convert to list of dictionaries
            houses = [dict(row) for row in results]

            # Get environment data for all houses
            environments_by_house_id = cls.get_house_environments(conn, house_ids)

            # Combine house data with environment data
            for house in houses:
                house['environments'] = environments_by_house_id.get(house['id'], [])

            return houses

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database query failed: {str(e)}"
            )

