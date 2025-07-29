from ya_market_api.const import Header
from ya_market_api.generic.requests.auth import APIKeyAuth
from ya_market_api.guide.sync_api import SyncGuideAPI
from ya_market_api.feedback.sync_api import SyncFeedbackAPI

from typing import Optional

from requests.sessions import Session


class SyncAPI:
	guide: SyncGuideAPI
	feedback: SyncFeedbackAPI
	session: Session

	def __init__(self, session: Session, *, business_id: Optional[int] = None) -> None:
		self.session = session
		self.guide = SyncGuideAPI(session)
		self.feedback = SyncFeedbackAPI(session, business_id)

	@classmethod
	def build(cls, api_key: str, *, business_id: Optional[int] = None) -> "SyncAPI":
		session = cls.make_session(api_key)

		return cls(session, business_id=business_id)

	@staticmethod
	def make_session(api_key: str) -> Session:
		session = Session()
		session.auth = APIKeyAuth(api_key, Header.API_KEY.value)

		return session
