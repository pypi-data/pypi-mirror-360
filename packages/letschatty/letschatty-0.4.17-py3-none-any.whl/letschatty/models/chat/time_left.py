
from pydantic import BaseModel
from enum import StrEnum

class TimeLeftStatus(StrEnum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
    PURPLE = "purple"
    GREY = "grey"

class TimeLeft(BaseModel):
    status: TimeLeftStatus
    hover_description: str
    time_left: str

    @classmethod
    def get_time_left(cls, time_left_for_free_conversation_seconds: float, time_left_for_free_template_window_seconds: float) -> "TimeLeft":

        if time_left_for_free_conversation_seconds  <= 0 and time_left_for_free_template_window_seconds  <= 0:
            return TimeLeft(
                status=TimeLeftStatus.GREY,
                hover_description="Conversación libre finalizada. Envía una plantilla o inicia una Conversación Continua para contactarte con el cliente.",
                time_left="Conversación libre finalizada."
            )
        elif time_left_for_free_conversation_seconds  <= 0 and time_left_for_free_template_window_seconds  > 0:
            return TimeLeft(
                status=TimeLeftStatus.PURPLE,
                hover_description=f"Conversación libre finalizada. Envío de plantillas de marketing sin cargo adicional: {int(time_left_for_free_template_window_seconds / 3600)}hs restantes.",
                time_left="Conversación libre finalizada."
            )
        elif time_left_for_free_conversation_seconds/3600 < 1:
            return TimeLeft(
                status=TimeLeftStatus.RED,
                hover_description=f"Conversación libre: Menos de 1hs restante. \n Envío de plantillas sin cargo adicional: {int(time_left_for_free_template_window_seconds / 3600)}hs restantes.",
                time_left="Menos de 1hs"
            )
        elif time_left_for_free_conversation_seconds/3600 < 6:
            return TimeLeft(
                status=TimeLeftStatus.YELLOW,
                hover_description=f"Conversación libre: {int(time_left_for_free_conversation_seconds/3600)}hs restantes. \n Envío de plantillas sin cargo adicional: {int(time_left_for_free_template_window_seconds / 3600)}hs restantes.",
                time_left=f"{int(time_left_for_free_conversation_seconds/3600)}hs"
            )
        elif time_left_for_free_conversation_seconds/3600 < 24:
            return TimeLeft(
                status=TimeLeftStatus.GREEN,
                hover_description=f"Conversación libre: {int(time_left_for_free_conversation_seconds/3600)}hs restantes. \n Envío de plantillas sin cargo adicional: {int(time_left_for_free_template_window_seconds / 3600)}hs restantes.",
                time_left=f"{int(time_left_for_free_conversation_seconds/3600)}hs"
            )
        else:
            raise Exception(f"Error en el cálculo de tiempo restante: {time_left_for_free_conversation_seconds} y {time_left_for_free_template_window_seconds}")
