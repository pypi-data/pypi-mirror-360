from typing import List, Optional

from pydantic import BaseModel, Field


class Location(BaseModel):
    longitude: Optional[float] = Field(default=None)
    latitude: Optional[float] = Field(default=None)
    horizontal_accuracy: Optional[float] = Field(default=None)
    live_period: Optional[int] = Field(default=None)
    heading: Optional[int] = Field(default=None)
    proximity_alert_radius: Optional[int] = Field(default=None)


class User(BaseModel):
    id: Optional[int] = Field(default=None)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)
    is_bot: Optional[bool] = Field(default=None)
    language_code: Optional[str] = Field(default=None)
    profile_photos: Optional[str] = Field(default=None)


class InlineQuery(BaseModel):
    id: Optional[str] = Field(default=None)
    from_user: Optional[User] = Field(default=None, alias="from")
    query: Optional[str] = Field(default=None)
    offset: Optional[str] = Field(default=None)
    chat_type: Optional[str] = Field(default=None)
    location: Optional[Location] = Field(default=None)


class ChosenInlineResult(BaseModel):
    result_id: Optional[str] = Field(default=None)
    from_user: Optional[User] = Field(default=None, alias="from")
    location: Optional[Location] = Field(default=None)
    inline_message_id: Optional[str] = Field(default=None)
    query: Optional[str] = Field(default=None)


class CallbackQuery(BaseModel):
    id: Optional[str] = Field(default=None)
    from_user: Optional[User] = Field(default=None, alias="from")
    message: Optional[dict] = Field(default=None)
    inline_message_id: Optional[str] = Field(default=None)
    chat_instance: Optional[str] = Field(default=None)
    data: Optional[str] = Field(default=None)
    game_short_name: Optional[str] = Field(default=None)


class ShippingQuery(BaseModel):
    id: Optional[str] = Field(default=None)
    from_user: Optional[User] = Field(default=None, alias="from")
    message: Optional[dict] = Field(default=None)
    inline_message_id: Optional[str] = Field(default=None)
    chat_instance: Optional[str] = Field(default=None)
    data: Optional[str] = Field(default=None)
    game_short_name: Optional[str] = Field(default=None)


class ShippingAddress(BaseModel):
    country_code: Optional[str] = Field(default=None)
    state: Optional[str] = Field(default=None)
    city: Optional[str] = Field(default=None)
    street_line1: Optional[str] = Field(default=None)
    street_line2: Optional[str] = Field(default=None)
    post_code: Optional[str] = Field(default=None)


class OrderInfo(BaseModel):
    name: Optional[str] = Field(default=None)
    phone_number: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    shipping_address: Optional[ShippingAddress] = Field(default=None)


class PreCheckoutQuery(BaseModel):
    id: Optional[str] = Field(default=None)
    from_user: Optional[User] = Field(default=None, alias="from")
    currency: Optional[str] = Field(default=None)
    total_amount: Optional[int] = Field(default=None)
    invoice_payload: Optional[str] = Field(default=None)
    shipping_option_id: Optional[str] = Field(default=None)
    order_info: Optional[OrderInfo] = Field(default=None)


class PollOption(BaseModel):
    text: Optional[str] = Field(default=None)
    voter_count: Optional[int] = Field(default=None)


class Poll(BaseModel):
    id: Optional[str] = Field(default=None)
    question: Optional[str] = Field(default=None)
    options: Optional[List[PollOption]] = Field(default=None)
    total_voter_count: Optional[int] = Field(default=None)
    is_closed: Optional[bool] = Field(default=None)
    is_anonymous: Optional[bool] = Field(default=None)
    type: Optional[str] = Field(default=None)
    allows_multiple_answers: Optional[bool] = Field(default=None)
    correct_option_id: Optional[int] = Field(default=None)
    explanation: Optional[str] = Field(default=None)


class PollAnswer(BaseModel):
    poll_id: Optional[str] = Field(default=None)
    user: Optional[User] = Field(default=None)
    option_ids: Optional[List[int]] = Field(default=None)
