"""
상점 API 라우터
아이템 조회, 구매, 인벤토리 관리
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from core.database.supabase import supabase
from core.middleware.auth import CurrentUser

router = APIRouter()


# ===== Request Models =====

class PurchaseItemRequest(BaseModel):
    """아이템 구매 요청"""
    itemId: str = Field(..., description="아이템 ID")
    currency: str = Field("coin", description="사용할 화폐 (coin 또는 gem)")


# ===== Endpoints =====

@router.get("/categories")
async def get_categories():
    """
    상점 카테고리 목록 조회

    **Response:**
    ```json
    {
        "categories": [
            {
                "category_id": "emoticons",
                "name": "이모티콘",
                "icon_url": "...",
                "sort_order": 1
            }
        ]
    }
    ```
    """
    try:
        result = supabase.table("shop_categories")\
            .select("*")\
            .order("sort_order")\
            .execute()

        return {"categories": result.data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@router.get("/items")
async def get_shop_items(
    category: Optional[str] = None,
    is_available: bool = True
):
    """
    상점 아이템 목록 조회

    **Query Parameters:**
    - category: 카테고리 ID (옵션)
    - is_available: 구매 가능 여부 (기본: true)

    **Response:**
    ```json
    {
        "items": [
            {
                "item_id": "uuid",
                "name": "하트 이모티콘",
                "description": "귀여운 하트",
                "type": "emoticon",
                "price": 100,
                "currency": "coin",
                "thumbnail_url": "...",
                "is_animated": false
            }
        ]
    }
    ```
    """
    try:
        query = supabase.table("shop_items").select("*")

        if category:
            query = query.eq("category_id", category)

        query = query.eq("is_available", is_available)

        result = query.execute()

        return {"items": result.data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@router.get("/featured")
async def get_featured_items(limit: int = 6):
    """
    추천 아이템 조회

    **Query Parameters:**
    - limit: 조회할 개수 (기본: 6)

    **Response:**
    ```json
    {
        "featured": [...]
    }
    ```
    """
    try:
        result = supabase.table("shop_items")\
            .select("*")\
            .eq("is_available", True)\
            .limit(limit)\
            .execute()

        return {"featured": result.data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@router.post("/purchase")
async def purchase_item(
    request: PurchaseItemRequest,
    user: CurrentUser,
):
    """
    아이템 구매 (JWT 인증 필요)

    **Request Body:**
    ```json
    {
        "itemId": "uuid",
        "currency": "coin"
    }
    ```

    **Response:**
    ```json
    {
        "success": true,
        "message": "구매 완료",
        "item": {...},
        "remainingBalance": {
            "coins": 900,
            "gems": 100
        }
    }
    ```
    """
    try:
        user_id = user["uid"]

        # 1. 아이템 정보 조회
        item_result = supabase.table("shop_items")\
            .select("*")\
            .eq("item_id", request.itemId)\
            .single()\
            .execute()

        if not item_result.data:
            raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다")

        item = item_result.data

        if not item["is_available"]:
            raise HTTPException(status_code=400, detail="구매할 수 없는 아이템입니다")

        # 2. 사용자 재화 확인
        currency_result = supabase.table("user_currency")\
            .select("*")\
            .eq("user_id", user_id)\
            .single()\
            .execute()

        if not currency_result.data:
            raise HTTPException(status_code=404, detail="사용자 정보를 찾을 수 없습니다")

        user_currency = currency_result.data
        price = item["price"]
        currency_type = request.currency

        # 3. 재화 충분한지 확인
        if currency_type == "coin":
            if user_currency["coins"] < price:
                raise HTTPException(status_code=400, detail="코인이 부족합니다")
        elif currency_type == "gem":
            if user_currency["gems"] < price:
                raise HTTPException(status_code=400, detail="젬이 부족합니다")
        else:
            raise HTTPException(status_code=400, detail="잘못된 화폐 타입입니다")

        # 4. 이미 소유한 아이템인지 확인
        inventory_check = supabase.table("user_inventory")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("item_id", request.itemId)\
            .execute()

        if inventory_check.data:
            raise HTTPException(status_code=400, detail="이미 소유한 아이템입니다")

        # 5. 재화 차감
        new_balance = {}
        if currency_type == "coin":
            new_balance["coins"] = user_currency["coins"] - price
            new_balance["gems"] = user_currency["gems"]
        else:
            new_balance["coins"] = user_currency["coins"]
            new_balance["gems"] = user_currency["gems"] - price

        supabase.table("user_currency")\
            .update(new_balance)\
            .eq("user_id", user_id)\
            .execute()

        # 6. 인벤토리에 추가
        supabase.table("user_inventory").insert({
            "user_id": user_id,
            "item_id": request.itemId,
            "acquired_type": "purchase"
        }).execute()

        # 7. 구매 이력 저장
        supabase.table("purchase_history").insert({
            "user_id": user_id,
            "item_id": request.itemId,
            "price": price,
            "currency": currency_type
        }).execute()

        return {
            "success": True,
            "message": "구매 완료",
            "item": item,
            "remainingBalance": new_balance
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@router.get("/inventory")
async def get_inventory(user: CurrentUser):
    """
    사용자 인벤토리 조회 (JWT 인증 필요)

    **Response:**
    ```json
    {
        "items": [
            {
                "item": {...},
                "acquired_at": "2024-01-01T00:00:00",
                "acquired_type": "purchase"
            }
        ],
        "currency": {
            "coins": 1000,
            "gems": 100
        }
    }
    ```
    """
    try:
        user_id = user["uid"]

        # 1. 인벤토리 조회 (아이템 정보 포함)
        inventory_result = supabase.table("user_inventory")\
            .select("*, shop_items(*)")\
            .eq("user_id", user_id)\
            .execute()

        # 2. 재화 조회
        currency_result = supabase.table("user_currency")\
            .select("*")\
            .eq("user_id", user_id)\
            .single()\
            .execute()

        return {
            "items": inventory_result.data,
            "currency": currency_result.data if currency_result.data else {"coins": 0, "gems": 0}
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@router.get("/balance")
async def get_balance(user: CurrentUser):
    """
    사용자 재화 조회 (JWT 인증 필요)

    **Response:**
    ```json
    {
        "coins": 1000,
        "gems": 100
    }
    ```
    """
    try:
        user_id = user["uid"]

        result = supabase.table("user_currency")\
            .select("*")\
            .eq("user_id", user_id)\
            .single()\
            .execute()

        if not result.data:
            # 사용자 재화 초기화
            default_currency = {
                "user_id": user_id,
                "coins": 1000,
                "gems": 100
            }
            supabase.table("user_currency").insert(default_currency).execute()
            return default_currency

        return result.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")
