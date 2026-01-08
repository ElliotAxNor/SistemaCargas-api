from rest_framework.exceptions import APIException


class ConflictoHorarioException(APIException):
    status_code = 409
    default_detail = 'Existe un conflicto de horario con otra carga.'
    default_code = 'conflicto_horario'


class HorasInvalidasException(APIException):
    status_code = 400
    default_detail = 'Las horas de los bloques no coinciden con las horas de la materia.'
    default_code = 'horas_invalidas'


class PeriodoFinalizadoException(APIException):
    status_code = 400
    default_detail = 'No se pueden realizar cambios en un periodo finalizado.'
    default_code = 'periodo_finalizado'
