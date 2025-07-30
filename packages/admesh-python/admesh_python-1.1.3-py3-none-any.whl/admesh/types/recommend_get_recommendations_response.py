# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["RecommendGetRecommendationsResponse", "Intent", "Response", "ResponseRecommendation", "FollowupSuggestion"]


# No decision factors needed


class Intent(BaseModel):
    categories: Optional[List[str]] = None

    goal: Optional[str] = None

    llm_intent_confidence_score: Optional[float] = None

    known_mentions: Optional[List[str]] = None

    intent_type: Optional[str] = None

    intent_group: Optional[str] = None

    tags: Optional[List[str]] = None


class ResponseRecommendation(BaseModel):
    ad_id: str

    admesh_link: str

    product_id: str

    reason: str

    title: str

    intent_match_score: Optional[float] = None

    features: Optional[List[str]] = None

    has_free_tier: Optional[bool] = None

    integrations: Optional[List[str]] = None

    pricing: Optional[str] = None

    redirect_url: Optional[str] = None

    reviews_summary: Optional[str] = None

    reward_note: Optional[str] = None

    security: Optional[List[str]] = None

    slug: Optional[str] = None

    support: Optional[List[str]] = None

    trial_days: Optional[int] = None

    url: Optional[str] = None


class FollowupSuggestion(BaseModel):
    label: Optional[str] = None

    query: Optional[str] = None

    product_mentions: Optional[List[str]] = None

    admesh_links: Optional[dict] = None

    session_id: Optional[str] = None


class Response(BaseModel):
    summary: Optional[str] = None

    recommendations: Optional[List[ResponseRecommendation]] = None

    followup_suggestions: Optional[List[FollowupSuggestion]] = None


class RecommendGetRecommendationsResponse(BaseModel):
    intent: Optional[Intent] = None

    response: Optional[Response] = None

    tokens_used: Optional[int] = None

    api_model_used: Optional[str] = FieldInfo(alias="model_used", default=None)

    recommendation_id: Optional[str] = None

    session_id: Optional[str] = None

    end_of_session: Optional[bool] = None
