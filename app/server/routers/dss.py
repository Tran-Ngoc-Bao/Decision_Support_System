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
    if not request.house_rent_ids:
        return []

    try:
        houses = HouseService.get_multiple_houses_by_ids(conn, request.house_rent_ids)
        data = _data_vectorizer(houses, request)
        cols = ['price', 'acreage', 'acreage_ratio', 'amenities_w', 'amenities_ratio']
        decision_matrix = data[cols].to_numpy()
        topsis_weights = normL2(request.topsis_weight) \
            if request.topsis_weight is not None and len(request.topsis_weight) != 0 \
            else np.ones(len(cols)) / len(cols)
        criteria_types = ['cost', 'benefit', 'benefit', 'benefit', 'benefit']
        topsis = TOPSIS(decision_matrix, topsis_weights, criteria_types)
        scores = topsis.solve() # Unpack the tuple returned by solve

        # set score
        for i, score in enumerate(scores):
            houses[i]['topsis_score'] = score

        # sort by score and assign rank        
        ranked_houses = sorted(houses, key=lambda x: x['topsis_score'], reverse=True)
        for i, house in enumerate(ranked_houses):
            house['rank'] = i + 1

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

    weights = normL2(request.weights) \
        if request.weights is not None and len(request.weights) != 0 \
        else np.ones(len(request.amenities)) / len(request.amenities)

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

    return dss_matrix