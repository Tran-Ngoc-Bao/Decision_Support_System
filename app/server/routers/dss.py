from typing import List

from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor

from ..logic.house import HouseService
from ..logic.topsis import TOPSIS
from ..utils.normL2 import normL2

import pandas as pd
import numpy as np

from ..dependency.db_connect import get_db_connection
from ..model.models import CompareRequest, CompareResultItem, TopsisCompareResponse

router = APIRouter(prefix="/dss", tags=["DSS"])

@router.post("/compare", response_model=TopsisCompareResponse)
def compare(request: CompareRequest, conn=Depends(get_db_connection)):

    if not request.prefer_location:
        request.prefer_location = [21.0285, 105.8542]

    if not request.house_rent_ids:
        return []

    try:
        houses = HouseService.get_multiple_houses_by_ids(conn, request.house_rent_ids)

        houses_df = pd.DataFrame(houses)
        
        dss_matrix = _data_vectorizer(houses, request)
        
        houses_df = pd.merge(houses_df, dss_matrix[['id', 'acreage_ratio', 'amenities_w', 'amenities_ratio', 'distance_to_prefer_location']], on='id')

        cols = ['price', 'acreage', 'acreage_ratio', 'amenities_w', 'amenities_ratio', 'distance_to_prefer_location']
        decision_matrix = houses_df[cols].to_numpy()
        
        topsis_weights = normL2(request.topsis_weight) \
            if request.topsis_weight is not None and len(request.topsis_weight) != 0 \
            else np.ones(len(cols)) / len(cols)
            
        criteria_types = ['cost', 'benefit', 'benefit', 'benefit', 'benefit', 'cost']
        topsis = TOPSIS(decision_matrix, topsis_weights, criteria_types)
        scores = topsis.solve()

        # Gán điểm TOPSIS và xếp hạng
        houses_df['topsis_score'] = scores
        houses_df = houses_df.sort_values(by='topsis_score', ascending=False).reset_index(drop=True)
        houses_df['rank'] = houses_df.index + 1

        # Thêm thông tin tiện ích khớp và tiện ích có sẵn
        requested_amenities_ids = set(request.amenities)
        houses_df['matched_amenities'] = houses_df['environments'].apply(lambda envs: [env for env in envs if env['id'] in requested_amenities_ids])
        ranked_houses = houses_df.to_dict('records')

        # Lấy ideal best/worst từ dữ liệu gốc (chưa chuẩn hóa)
        ideal_best_raw, ideal_worst_raw = topsis.find_ideal_solutions_raw()

        return {
            "ranked_houses": ranked_houses,
            "ideal_best": dict(zip(cols, ideal_best_raw)),
            "ideal_worst": dict(zip(cols, ideal_worst_raw))
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")

def _data_vectorizer(house_data: list, request: CompareRequest):
    if not house_data:
        return []

    df = pd.DataFrame(house_data)

    weights = request.weights \
        if request.weights is not None and len(request.weights) != 0 \
        else np.ones(len(request.amenities)) * 100

    amenities = request.amenities

    dss_matrix = df[['id']].copy()

    dss_matrix['price'] = df['price']
    dss_matrix['acreage'] = df['acreage']
    dss_matrix['acreage_ratio'] = df['acreage'] / df['price']

    amenity_weight_map = dict(zip(amenities, weights))

    dss_matrix['amenities_w'] = df['environments'].apply(
        lambda house_amenities: sum(amenity_weight_map.get(amenity['id'], 0) for amenity in house_amenities)
    )
    dss_matrix['amenities_ratio'] = dss_matrix['amenities_w'] / df['price']
    prefer_location = request.prefer_location
    dss_matrix['distance_to_prefer_location'] = df.apply(
        lambda row: np.inf if pd.isna(row['latitude']) or pd.isna(row['longitude'])
        else ((prefer_location[0] - row['latitude']) ** 2 + (prefer_location[1] - row['longitude']) ** 2) ** 0.5,
        axis=1
    )

    return dss_matrix