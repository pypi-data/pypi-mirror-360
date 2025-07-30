import datetime
import typing
import numpy as np

from fastapi.responses import JSONResponse as J, StreamingResponse


class JSONResponse(J):

    def render(self, content: typing.Any):
        if isinstance(content, (np.integer, np.floating, np.bool_)):
            return content.item()
        elif isinstance(content, np.ndarray):
            return content.tolist()
        elif isinstance(content, (datetime.datetime, datetime.timedelta)):
            return content.__str__()
        else:
            return super(J, self).render(content)
