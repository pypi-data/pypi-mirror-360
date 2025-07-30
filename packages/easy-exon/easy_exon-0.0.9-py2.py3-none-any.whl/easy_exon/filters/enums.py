from enum import Enum

class City(Enum):
    MOSCOW      = "Москва"
    ZELENOGRAD  = "Зеленоград"

class Category(Enum):
    HEALTHCARE               = "здравоохранение"
    ROAD_CONSTRUCTION        = "дорожное строительство"
    EDUCATION                = "наука и образование"
    ENGINEERING              = "инженерные сооружения"
    HOUSING                  = "жилье"
    SPORT                    = "спорт"
    CULTURE                  = "культура"
    PUBLIC                   = "общественное"
    SAFE_CITY                = "безопасный город"
    DATA_CENTER              = "объект хранения и обработки данных"
    TRANSPORT_INFRASTRUCTURE = "транспортная инфраструктура"

class CityArea(Enum):
    NORTH_WEST        = "Северо-западный"
    EAST              = "Восточный"
    SOUTH             = "Южный"
    TROITSKY          = "Троицкий"
    WEST              = "Западный"
    SOUTH_WEST        = "Юго-западный"
    NOVO_MOSCOW       = "Новомосковский"
    NORTH_EAST        = "Северо-восточный"
    SOUTH_EAST        = "Юго-восточный"
    NORTH             = "Северный"
    CENTRAL           = "Центральный"
    ZELENOGRADSKIY    = "Зеленоградский"

class Status(Enum):
    IN_PROGRESS     = "в работе"
    COMPLETED       = "завершено"
    DESIGN          = "проектирование"
    PAUSED          = "приостановлено"
    CONSTRUCTION    = "строительство"
    RECONSTRUCTION  = "реконструкция"
    RV_GRANTED      = "получено РВ"
    DEMOLITION      = "снос"
