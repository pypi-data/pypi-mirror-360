import os
import time

from nvflare.apis.dxo import DXO, DataKind
from nvflare.apis.fl_component import FLComponent
from nvflare.apis.fl_constant import FLContextKey, ReturnCode
from nvflare.apis.fl_context import FLContext
from nvflare.apis.shareable import make_reply

from .util import get_logger_fn_for_level, sanitised_trace

MESSAGE_TO_SERVER_DELAY = 0.01

message_to_server_delay = os.environ.get(
    "APH_MESSAGE_TO_SERVER_DELAY", MESSAGE_TO_SERVER_DELAY
)


class GatewayLogSenderMixin(FLComponent):

    def _send_to_server_log(self, fl_ctx: FLContext, message: str, level="INFO") -> None:
        """
        Sends message to NVFlare server to log information there.
        """
        self.log_info(fl_ctx, "Sending message to server log")
        get_logger_fn_for_level(component=self, level=level)(fl_ctx, message)
        dxo = DXO(
            DataKind.COLLECTION,
            {
                "message": message,
                "level": level,
                "client_name": fl_ctx.get_prop(FLContextKey.CLIENT_NAME),
            },
        )
        msg_data = dxo.to_shareable()
        self.fire_fed_event(
            event_type="debug_message", event_data=msg_data, fl_ctx=fl_ctx
        )
        time.sleep(float(message_to_server_delay))


def safe_error_catchall_decorator(func):
    """
    A decorator to wrap functions that might throw an unhandled exception, catch the
    exception then sanitise it by removing the raw error message and just passing limited
    details back to the user.

    Will try to use an FLComponents log_xxx methods, but if unavailable, will simply
    print to the terminal.

    """

    def wrapper(self, *args, **kwargs):
        send_to_server = isinstance(self, GatewayLogSenderMixin)

        fl_ctx = None
        for a in args:
            if isinstance(a, FLContext):
                fl_ctx = a
                break

        if fl_ctx is None:
            print(
                "Could not find an FLContext in this function so can not forward"
                " errors to server"
            )

        try:
            return func(self, *args, **kwargs)
        except Exception as err:
            if fl_ctx and send_to_server:
                self._send_to_server_log(
                    fl_ctx,
                    sanitised_trace(),
                    "ERROR",
                )
            else:
                # This will only print on the client, won't be passed back
                print(str(err))
            return make_reply(ReturnCode.ERROR)

    return wrapper
