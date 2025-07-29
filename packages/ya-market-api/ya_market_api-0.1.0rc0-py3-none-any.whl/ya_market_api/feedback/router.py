from ya_market_api.base.router import Router
from ya_market_api.const import BASE_URL


class FeedbackRouter(Router):
	def feedback_list(self, business_id: int) -> str:
		return f"{BASE_URL}/businesses/{business_id}/goods-feedback"

	def feedback_comment_list(self, business_id: int) -> str:
		return f"{BASE_URL}/businesses/{business_id}/goods-feedback/comments"

	def feedback_comment_add(self, business_id: int) -> str:
		return f"{BASE_URL}/businesses/{business_id}/goods-feedback/comments/update"

	def feedback_comment_update(self, business_id: int) -> str:
		return f"{BASE_URL}/businesses/{business_id}/goods-feedback/comments/update"

	def feedback_comment_delete(self, business_id: int) -> str:
		return f"{BASE_URL}/businesses/{business_id}/goods-feedback/comments/delete"

	def feedback_reaction_skip(self, business_id: int) -> str:
		return f"{BASE_URL}/businesses/{business_id}/goods-feedback/skip-reaction"
