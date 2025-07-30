import asyncio
import sys
import time
import os
import atexit
import threading
import subprocess
from typing import Any
from vertx import EventBus
from queue import Queue
import traceback
import inspect
from redflagbpm.Services import Service, DocumentService, Context, ResourceService, ExecutionService, RuntimeService, \
    ReportService, Logger, AgentService


class ServiceError(Exception):
    def __init__(self, body: dict):
        super().__init__(body.get("error"))
        self.trace = body.get("trace")


class BPMService:
    service: Service
    context: Context
    execution: ExecutionService
    documentService: DocumentService
    resourceService: ResourceService
    runtimeService: RuntimeService
    agentService: AgentService
    logger: Logger

    __eb_calls: EventBus
    __eb_handlers: EventBus
    delay = 10
    call_timeout = 30.0
    __handlers = []
    __address_dict: dict

    def __init__(self, host=None, port=None, options=None, err_handler=None, ssl_context=None):
        if host != None:
            pass
        elif 'BPM_HOST' in os.environ:
            host = os.environ['BPM_HOST']
        else:
            host = 'localhost'
        if port != None:
            pass
        elif 'BPM_HOST' in os.environ:
            port = int(os.environ['BPM_PORT'])
        else:
            port = 7000
        if options is None:
            options = {}
        self.__eb_calls = EventBus(host=host, port=port, options=options, err_handler=err_handler,
                                   ssl_context=ssl_context)
        self.__eb_handlers = EventBus(host=host, port=port, options=options, err_handler=err_handler,
                                      ssl_context=ssl_context)
        self.__address_dict = {}
        self.service = Service(self)
        self.context = Context(self)
        self.execution = ExecutionService(self)
        self.documentService = DocumentService(self)
        self.resourceService = ResourceService(self)
        self.runtimeService = RuntimeService(self)
        self.reportService = ReportService(self)
        self.agentService = AgentService(self)
        self.logger = Logger(self)

        self.connect()
        atexit.register(self.close)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __setAddress(self, address: Any = None):
        """
        Este método se utiliza durante la conexión con el backend de la BPM.
        Establece la dirección vertx habilitada en el backend para comunicarse con el contexto.
        En el uso diario no es necesario invocarlo porque se autoconfigura.
        :param address:
        """
        if isinstance(address, dict):
            addr = address['replyAddress']
        elif isinstance(address, str):
            addr = address
        elif 'BPM_EVENT_BUS_REPLY' in os.environ:
            addr = os.environ['BPM_EVENT_BUS_REPLY']
        else:
            raise ValueError('No address supplied')
        tid = threading.get_ident()
        self.__address_dict[tid] = addr

    def __getAddress(self, address: Any = None) -> str:
        if isinstance(address, dict):
            return address['replyAddress']
        elif isinstance(address, str):
            return address
        elif threading.get_ident() in self.__address_dict:
            return self.__address_dict[threading.get_ident()]
        elif 'BPM_EVENT_BUS_REPLY' in os.environ:
            return os.environ['BPM_EVENT_BUS_REPLY']
        else:
            raise ValueError('No address supplied')

    def send(self, address, headers=None, body=None):
        ret = Queue()
        self.__eb_calls.send(address=address, headers=headers, body=body, reply_handler=lambda msg: ret.put(msg))
        return ret.get(True, self.call_timeout)

    def reply(self, body=None, address=None, headers=None):
        try:
            addr = self.__getAddress(address)
            self.__eb_calls.send(address=addr, headers=headers, body={"reply": body})
        except ValueError as x:
            if str(x) == 'No address supplied':
                print({"reply": body})
                exit(0)
            else:
                raise x

    def fail(self, message: str = None, do_quit=True, address=None, headers=None):
        if message is None:
            message = traceback.format_exc()
        try:
            addr = self.__getAddress(address)
            body = {"error": message, "succeeded": False}
            self.__eb_calls.send(address=addr, headers=headers, body=body)
        except ValueError as x:
            if str(x) == 'No address supplied':
                print({"error": message, "succeeded": False})
            else:
                raise x
        if do_quit:
            quit()

    def call(self, address, body=None, headers=None):
        ret = self.send(address, headers, body)
        if 'body' in ret:
            if 'succeeded' in ret['body']:
                if not ret['body']['succeeded']:
                    raise ServiceError(ret['body'])
            if 'reply' in ret['body']:
                return ret['body']['reply']
            else:
                return ret['body']
        return None

    def connect(self):
        if not self.__eb_calls.is_connected():
            self.__eb_calls.connect()
        if not self.__eb_handlers.is_connected():
            self.__eb_handlers.connect()

    def close(self):
        for address in self.__handlers:
            self.unregister_handler(address)
        if self.__eb_calls.is_connected():
            self.__eb_calls.close()
        if self.__eb_handlers.is_connected():
            self.__eb_handlers.close()

    def __run_external(self, address, handler):
        my_env = os.environ.copy()
        my_env["BPM_EVENT_BUS_REPLY"] = address["replyAddress"]
        subprocess.Popen(sys.executable + " " + handler, env=my_env, shell=True)

    def register_app(self, app, prefix=None):
        try:
            app.routes
        except AttributeError:
            raise ValueError("Invalid app. Must be FastApi app")

        def make_handler_for(path, func):
            def t_handler(msg):
                if "body" in msg and "address" in msg["body"]:
                    address = msg["body"]["address"]
                    signature = inspect.signature(func)
                    parameters = signature.parameters
                    param_values = {k: self.context.getValue(k, address) for k in parameters.keys()}
                    param_values = {k: (v if v is not None else parameters[k].default) for k, v in param_values.items()}
                    bound_args = signature.bind(**param_values)
                    arguments = bound_args.arguments
                    try:
                        # check if signature is async
                        if inspect.iscoroutinefunction(func):
                            # if it is, await it
                            result = asyncio.run(func(**arguments))
                        else:
                            # if not, call it
                            result = func(**arguments)
                        self.reply(body=result, address=address)
                    except Exception as e:
                        self.fail(address=address, do_quit=False)
                else:
                    body = msg["body"] if "body" in msg else {}
                    signature = inspect.signature(func)
                    parameters = signature.parameters
                    param_values = {k: (body[k] if k in body else v.default) for k, v in parameters.items()}
                    bound_args = signature.bind(**param_values)
                    arguments = bound_args.arguments
                    try:
                        # check if signature is async
                        if inspect.iscoroutinefunction(func):
                            # if it is, await it
                            result = asyncio.run(func(**arguments))
                        else:
                            # if not, call it
                            result = func(**arguments)
                        if 'replyAddress' in msg:
                            self.__eb_calls.send(address=msg["replyAddress"], body={"reply": result, "succeeded": True})
                    except Exception as e:
                        self.__eb_calls.send(address=msg["replyAddress"], body={"error": str(e), "succeeded": False})

            def handler(msg):
                t = threading.Thread(target=t_handler, args=(msg,))
                t.start()

            return handler

        for route in app.routes:
            if "endpoint" in dir(route) and "path" in dir(route):
                path = route.path
                if prefix is not None:
                    path = prefix + path
                self.register_handler(path, make_handler_for(route.path, route.endpoint))

    def register_handler(self, address, handler):
        if isinstance(handler, str):
            self.__eb_handlers.register_handler(address, lambda msg: self.__run_external(msg, handler))
        else:
            self.__eb_handlers.register_handler(address, handler)
        self.__handlers.append(address)

    def unregister_handler(self, address, handler=None):
        self.__eb_handlers.unregister_handler(address, handler)
        self.__handlers.remove(address)

    def run(self, address, handler):
        self.register_handler(address, handler)
        self.start()

    def exec(self, script: str, lang: str = 'juel', context: dict = None, address: object = None) -> object:
        addr = self.__getAddress(address)
        ret = Queue()
        self.__eb_calls.send(address=addr, body={
            "lang": lang,
            "script": script,
            "context": context
        }, reply_handler=lambda x: ret.put(x))
        result = ret.get(True, self.call_timeout)
        if result['body']['succeeded']:
            return result['body']['body']
        else:
            raise ValueError(result['body']['trace'])

    def request(self, request: str, address=None):
        addr = self.__getAddress(address)
        ret = Queue()
        self.__eb_calls.send(address=addr, body={"request": request}, reply_handler=lambda x: ret.put(x))
        return ret.get(True, self.call_timeout)

    def start(self):
        # self.connect()
        try:
            while True:
                time.sleep(self.delay)
        except KeyboardInterrupt:
            self.stop()

    def isConnected(self):
        return self.__eb_calls.is_connected()

    def stop(self):
        print("Stopping...")
        self.close()
        print("Stopped...")
        sys.exit(0)
