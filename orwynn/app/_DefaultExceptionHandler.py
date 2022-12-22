from orwynn import app
from orwynn.util import validation
from orwynn.util.web import JSONResponse, Request, Response
from orwynn.boot._BootProxy import BootProxy


class DefaultExceptionHandler(app.ErrorHandler):
    E = Exception.__subclasses__()

    def handle(self, request: Request, error: Exception) -> Response:
        return JSONResponse(BootProxy.ie().api_indication.digest(error), 400)

    def set_handled_exception(
        self, E: type[Exception] | list[type[Exception]]
    ) -> None:
        if isinstance(E, list):
            validation.validate_each(E, Exception)
        else:
            validation.validate(E, Exception)

        self.__class__.E = E
