"""
Common models and data structures for the Mealie SDK.

This module contains base models, enums, and shared data structures
used across the SDK for consistent data handling.
"""

from datetime import datetime, date
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class BaseModel:
    """
    Base model class with common functionality.
    
    This provides a simple base class for data models without external dependencies.
    In a full implementation, this could be replaced with Pydantic BaseModel.
    """

    def __init__(self, **data: Any) -> None:
        """Initialize the model with provided data."""
        for key, value in data.items():
            setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary."""
        result = {}
        for key, value in self.__dict__.items():
            if key == "group_id":
                result["groupId"] = self.__normalize_value(value)
            elif key == "user_id":
                result["userId"] = self.__normalize_value(value)
            elif key == "household_id":
                result["householdId"] = self.__normalize_value(value)
            elif key == "entry_type":
                result["entryType"] = self.__normalize_value(value)
            elif key == "recipe_id":
                result["recipeId"] = self.__normalize_value(value)
            elif key == "recipe_servings":
                result["recipeServings"] = self.__normalize_value(value)
            elif key == "recipe_yield":
                result["recipeYield"] = self.__normalize_value(value)
            elif key == "recipe_yield_quantity":
                result["recipeYieldQuantity"] = self.__normalize_value(value)
            elif key == "recipe_category":
                result["recipeCategory"] = self.__normalize_value(value)
            elif key == "total_time":
                result["totalTime"] = self.__normalize_value(value)
            elif key == "prep_time":
                result["prepTime"] = self.__normalize_value(value)
            elif key == "cook_time":
                result["cookTime"] = self.__normalize_value(value)
            elif key == "perform_time":
                result["performTime"] = self.__normalize_value(value)
            elif key == "org_url":
                result["orgURL"] = self.__normalize_value(value)
            elif key == "date_added":
                result["dateAdded"] = self.__normalize_value(value)
            elif key == "date_updated":
                result["dateUpdated"] = self.__normalize_value(value)
            elif key == "created_at":
                result["created_at"] = self.__normalize_value(value)
                result["createdAt"] = self.__normalize_value(value)
            elif key == "updated_at":
                result["updated_at"] = self.__normalize_value(value)
                result["updatedAt"] = self.__normalize_value(value)
            elif key == "last_made":
                result["lastMade"] = self.__normalize_value(value)
            elif key == "full_name":
                result["fullName"] = self.__normalize_value(value)
            elif key == "auth_method":
                result["authMethod"] = self.__normalize_value(value)
            elif key == "can_invite":
                result["canInvite"] = self.__normalize_value(value)
            elif key == "can_manage":
                result["canManage"] = self.__normalize_value(value)
            elif key == "can_organize":
                result["canOrganize"] = self.__normalize_value(value)
            elif key == "can_manage_household":
                result["canManageHousehold"] = self.__normalize_value(value)
            elif key == "group_slug":
                result["groupSlug"] = self.__normalize_value(value)
            elif key == "household_slug":
                result["householdSlug"] = self.__normalize_value(value)
            elif key == "cache_key":
                result["cacheKey"] = self.__normalize_value(value)
            else:
                result[key] = self.__normalize_value(value)
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create a model instance from a dictionary."""
        if "groupId" in data:
            data["group_id"] = data.pop("groupId")
        if "userId" in data:
            data["user_id"] = data.pop("userId")
        if "householdId" in data:
            data["household_id"] = data.pop("householdId")
        if "entryType" in data:
            data["entry_type"] = data.pop("entryType")
        if "recipeId" in data:
            data["recipe_id"] = data.pop("recipeId")
        if "recipeServings" in data:
            data["recipe_servings"] = data.pop("recipeServings")
        if "recipeYield" in data:
            data["recipe_yield"] = data.pop("recipeYield")
        if "recipeYieldQuantity" in data:
            data["recipe_yield_quantity"] = data.pop("recipeYieldQuantity")
        if "recipeCategory" in data:
            data["recipe_category"] = data.pop("recipeCategory")
        if "totalTime" in data:
            data["total_time"] = data.pop("totalTime")
        if "prepTime" in data:
            data["prep_time"] = data.pop("prepTime")
        if "cookTime" in data:
            data["cook_time"] = data.pop("cookTime")
        if "performTime" in data:
            data["perform_time"] = data.pop("performTime")
        if "orgURL" in data:
            data["org_url"] = data.pop("orgURL")
        if "dateAdded" in data:
            data["date_added"] = data.pop("dateAdded")
        if "dateUpdated" in data:
            data["date_updated"] = data.pop("dateUpdated")
        if "createdAt" in data:
            data["created_at"] = data.pop("createdAt")
        if "updatedAt" in data:
            data["updated_at"] = data.pop("updatedAt")
        if "lastMade" in data:
            data["last_made"] = data.pop("lastMade")
        if "fullName" in data:
            data["full_name"] = data.pop("fullName")
        if "authMethod" in data:
            data["auth_method"] = data.pop("authMethod")
        if "canInvite" in data:
            data["can_invite"] = data.pop("canInvite")
        if "canManage" in data:
            data["can_manage"] = data.pop("canManage")
        if "canOrganize" in data:
            data["can_organize"] = data.pop("canOrganize")
        if "canManageHousehold" in data:
            data["can_manage_household"] = data.pop("canManageHousehold")
        if "groupSlug" in data:
            data["group_slug"] = data.pop("groupSlug")
        if "householdSlug" in data:
            data["household_slug"] = data.pop("householdSlug")
        if "cacheKey" in data:
            data["cache_key"] = data.pop("cacheKey")
        return cls(**data)

    def __repr__(self) -> str:
        """Return string representation of the model."""
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"

    def __eq__(self, other: Any) -> bool:
        """Check equality with another model."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__
    
    @classmethod
    def __normalize_value(cls, value):
        if isinstance(value, BaseModel):
            return value.to_dict()
        elif isinstance(value, list) and value and isinstance(value[0], BaseModel):
            return [item.to_dict() for item in value]
        elif isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, date):
            return value.isoformat()
        elif isinstance(value, Enum):
            return value.value
        else:
            return value

# Enums for various Mealie data types

class RecipeVisibility(str, Enum):
    """Recipe visibility levels."""
    PUBLIC = "public"
    PRIVATE = "private"


class UserRole(str, Enum):
    """User roles in the system."""
    ADMIN = "admin"
    USER = "user"


class MealPlanType(str, Enum):
    """Types of meal plans."""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SIDE = "side"


class ShoppingListItemStatus(str, Enum):
    """Status of shopping list items."""
    UNCHECKED = "unchecked"
    CHECKED = "checked"


class RecipeScale(str, Enum):
    """Recipe scaling options."""
    HALF = "0.5"
    NORMAL = "1"
    DOUBLE = "2"
    TRIPLE = "3"


class TimeUnit(str, Enum):
    """Time units for durations."""
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"


# Common data structures

class Nutrition(BaseModel):
    """Nutritional information."""
    
    def __init__(
        self,
        calories: Optional[float] = None,
        fat_content: Optional[float] = None,
        protein_content: Optional[float] = None,
        carbohydrate_content: Optional[float] = None,
        fiber_content: Optional[float] = None,
        sugar_content: Optional[float] = None,
        sodium_content: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        self.calories = calories
        self.fat_content = fat_content
        self.protein_content = protein_content
        self.carbohydrate_content = carbohydrate_content
        self.fiber_content = fiber_content
        self.sugar_content = sugar_content
        self.sodium_content = sodium_content
        super().__init__(**kwargs)


class RecipeIngredient(BaseModel):
    """Recipe ingredient with quantity and notes."""
    
    def __init__(
        self,
        title: str,
        text: str,
        quantity: Optional[float] = None,
        unit: Optional[str] = None,
        food: Optional[str] = None,
        note: Optional[str] = None,
        original_text: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.title = title
        self.text = text
        self.quantity = quantity
        self.unit = unit
        self.food = food
        self.note = note
        self.original_text = original_text
        super().__init__(**kwargs)


class RecipeInstruction(BaseModel):
    """Recipe instruction step."""
    
    def __init__(
        self,
        id: Optional[str] = None,
        title: Optional[str] = None,
        text: str = "",
        ingredient_references: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.title = title
        self.text = text
        self.ingredient_references = ingredient_references or []
        super().__init__(**kwargs)


class RecipeAsset(BaseModel):
    """Recipe asset (image, file, etc.)."""
    
    def __init__(
        self,
        name: str,
        icon: Optional[str] = None,
        file_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.name = name
        self.icon = icon
        self.file_name = file_name
        super().__init__(**kwargs)


class RecipeSettings(BaseModel):
    """Recipe settings and preferences."""
    
    def __init__(
        self,
        public: bool = False,
        show_nutrition: bool = True,
        show_assets: bool = True,
        landscape_view: bool = False,
        disable_comments: bool = False,
        disable_amount: bool = False,
        locked: bool = False,
        **kwargs: Any,
    ) -> None:
        self.public = public
        self.show_nutrition = show_nutrition
        self.show_assets = show_assets
        self.landscape_view = landscape_view
        self.disable_comments = disable_comments
        self.disable_amount = disable_amount
        self.locked = locked
        super().__init__(**kwargs)


class RecipeCategory(BaseModel):
    """Recipe category."""
    
    def __init__(
        self,
        id: Optional[str] = None,
        name: str = "",
        slug: str = "",
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.name = name
        self.slug = slug
        super().__init__(**kwargs)


class RecipeTag(BaseModel):
    """Recipe tag."""
    
    def __init__(
        self,
        id: Optional[str] = None,
        name: str = "",
        slug: str = "",
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.name = name
        self.slug = slug
        super().__init__(**kwargs)


class RecipeTool(BaseModel):
    """Recipe tool/equipment."""
    
    def __init__(
        self,
        id: Optional[str] = None,
        name: str = "",
        slug: str = "",
        on_hand: bool = False,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.name = name
        self.slug = slug
        self.on_hand = on_hand
        super().__init__(**kwargs)


class PaginationInfo(BaseModel):
    """Pagination information for list responses."""
    
    def __init__(
        self,
        page: int = 1,
        per_page: int = 50,
        total: int = 0,
        total_pages: int = 0,
        **kwargs: Any,
    ) -> None:
        self.page = page
        self.per_page = per_page
        self.total = total
        self.total_pages = total_pages
        super().__init__(**kwargs)


class OrderDirection(str, Enum):
    """Ordering direction for queries."""
    ASC = "asc"
    DESC = "desc"


class OrderByNullPosition(str, Enum):
    """Position of null values in ordering."""
    FIRST = "first"
    LAST = "last"

class QueryFilter(BaseModel):
    """Base query filter for API requests."""
    
    def __init__(
        self,
        page: int = 1,
        per_page: int = 50,
        order_by: Optional[str] = None,
        order_direction: OrderDirection = OrderDirection.ASC,
        order_by_null_position: OrderByNullPosition = OrderByNullPosition.LAST,
        search: Optional[str] = None,
        accept_language: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.page = page
        self.per_page = per_page
        self.order_by = order_by
        self.order_direction = order_direction
        self.order_by_null_position = order_by_null_position
        self.search = search
        self.accept_language = accept_language
        super().__init__(**kwargs)

    def to_params(self) -> Dict[str, Any]:
        """Convert filter to query parameters."""
        params: Dict[str, Any] = {
            "page": self.page,
            "perPage": self.per_page,
        }
        
        if self.order_by:
            params["orderBy"] = self.order_by
            params["orderDirection"] = self.order_direction.value
            
        if self.order_by_null_position:
            params["orderByNullPosition"] = self.order_by_null_position.value

        if self.search:
            params["search"] = self.search

        if self.accept_language:
            params["accept-language"] = self.accept_language
        return params


class DateRange(BaseModel):
    """Date range for filtering."""
    
    def __init__(
        self,
        start_date: Optional[Union[date, datetime, str]] = None,
        end_date: Optional[Union[date, datetime, str]] = None,
        **kwargs: Any,
    ) -> None:
        self.start_date = start_date
        self.end_date = end_date
        super().__init__(**kwargs)

    def to_params(self) -> Dict[str, str]:
        """Convert date range to query parameters."""
        params = {}
        
        if self.start_date:
            if isinstance(self.start_date, (date, datetime)):
                params["start_date"] = self.start_date.isoformat()
            else:
                params["start_date"] = str(self.start_date)
                
        if self.end_date:
            if isinstance(self.end_date, (date, datetime)):
                params["end_date"] = self.end_date.isoformat()
            else:
                params["end_date"] = str(self.end_date)
                
        return params


class APIResponse(BaseModel):
    """Generic API response wrapper."""
    
    def __init__(
        self,
        data: Any = None,
        message: Optional[str] = None,
        success: bool = True,
        pagination: Optional[PaginationInfo] = None,
        **kwargs: Any,
    ) -> None:
        self.data = data
        self.message = message
        self.success = success
        self.pagination = pagination
        super().__init__(**kwargs)


class ErrorDetail(BaseModel):
    """Error detail information."""
    
    def __init__(
        self,
        field: str,
        message: str,
        code: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.field = field
        self.message = message
        self.code = code
        super().__init__(**kwargs)


# Utility functions for model handling

def convert_datetime(value: Union[str, datetime, None]) -> Optional[datetime]:
    """Convert various datetime formats to datetime object."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        # Try to parse ISO format
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            # If parsing fails, return None
            return None
    return None


def convert_date(value: Union[str, date, datetime, None]) -> Optional[date]:
    """Convert various date formats to date object."""
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        # Try to parse ISO format
        try:
            parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
            return parsed.date()
        except ValueError:
            # Try date-only format
            try:
                return datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                return None
    return None


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get a value from a dictionary with default."""
    return data.get(key, default) if data else default


def filter_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """Filter out None values from a dictionary."""
    return {k: v for k, v in data.items() if v is not None} 