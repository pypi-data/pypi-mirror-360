from enum import Enum


class Status(Enum):
	OK = "OK"
	ERROR = "ERROR"


class AuthScope(Enum):
	ALL_METHODS = "ALL_METHODS"		# полное управление кабинетом
	ALL_METHODS_READ_ONLY = "ALL_METHODS_READ_ONLY"		# просмотр всей информации в кабинете
	INVENTORY_AND_ORDER_PROCESSING = "INVENTORY_AND_ORDER_PROCESSING"		# обработка заказов и учет товаров
	INVENTORY_AND_ORDER_PROCESSING_READ_ONLY = "INVENTORY_AND_ORDER_PROCESSING_READ_ONLY"		# просмотр информации о заказах
	PRICING = "PRICING"		# управление ценами
	PRICING_READ_ONLY = "PRICING_READ_ONLY"		# просмотр цен
	OFFERS_AND_CARDS_MANAGEMENT = "OFFERS_AND_CARDS_MANAGEMENT"		# управление товарами и карточками
	OFFERS_AND_CARDS_MANAGEMENT_READ_ONLY = "OFFERS_AND_CARDS_MANAGEMENT_READ_ONLY"		# просмотр товаров и карточек
	PROMOTION = "PROMOTION"		# продвижение товаров
	PROMOTION_READ_ONLY = "PROMOTION_READ_ONLY"		# просмотр информации о продвижении товаров
	FINANCE_AND_ACCOUNTING = "FINANCE_AND_ACCOUNTING"		# просмотр финансовой информации и отчётности
	COMMUNICATION = "COMMUNICATION"		# общение с покупателями
	SETTINGS_MANAGEMENT = "SETTINGS_MANAGEMENT"		# настройка магазинов
	SUPPLIES_MANAGEMENT_READ_ONLY = "SUPPLIES_MANAGEMENT_READ_ONLY"		# получение информации по FBY-заявкам
