from enum import Enum


class ReactionStatus(Enum):
	ALL = "ALL"
	NEED_REACTION = "NEED_REACTION"


class CommentAuthorType(Enum):
	USER = "USER"
	BUSINESS = "BUSINESS"


class CommentStatus(Enum):
	PUBLISHED = "PUBLISHED"
	UNMODERATED = "UNMODERATED"
	BANNED = "BANNED"
	DELETED = "DELETED"
