from rest_framework.throttling import UserRateThrottle


class EventosConsultaThrottle(UserRateThrottle):
    """Throttle para consulta de eventos: 20 requisições por dia"""
    rate = '20/day'
    scope = 'eventos_consulta'


class EventosInscricaoThrottle(UserRateThrottle):
    """Throttle para inscrição em eventos: 50 requisições por dia"""
    rate = '50/day'
    scope = 'eventos_inscricao'
