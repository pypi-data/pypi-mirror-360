from enum import Enum


class RegionType(Enum):
	OTHER = "OTHER"		# неизвестный регион
	CONTINENT = "CONTINENT"		# континент
	REGION = "REGION"		# регион
	COUNTRY = "COUNTRY"		# страна
	COUNTRY_DISTRICT = "COUNTRY_DISTRICT"		# область
	REPUBLIC = "REPUBLIC"		# субъект федерации
	CITY = "CITY"		# крупный город
	VILLAGE = "VILLAGE"		# город
	CITY_DISTRICT = "CITY_DISTRICT"		# район города
	SUBWAY_STATION = "SUBWAY_STATION"		# станция метро
	REPUBLIC_AREA = "REPUBLIC_AREA"		# район субъекта федерации
