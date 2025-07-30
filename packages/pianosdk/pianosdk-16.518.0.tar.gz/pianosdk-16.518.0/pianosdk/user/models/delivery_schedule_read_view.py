from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.user.models.delivery_period_read_view import DeliveryPeriodReadView
from typing import List


class DeliveryScheduleReadView(BaseModel):
    edit_threshold: Optional[str] = None
    delivery_periods: Optional['List[DeliveryPeriodReadView]'] = None
    main_period_pub_id: Optional[str] = None


DeliveryScheduleReadView.model_rebuild()
