import os
from typing import List, Any, Literal
from urllib.parse import urlparse


class Service:
    def __init__(self, bpm):
        self.bpm = bpm

    def sendMail(self, msg: dict):
        """
        Envía un email desde el backend de BPM.

        Es mensaje es un dict con el contenido del mensaje. Tiene los siguientes atributos:
        - from:str = el remitente
        - to:[str] = destinatarios
        - cc:[str] = con copia
        - bcc:[str] = con copia oculta
        - subject:str = asunto
        - message:str = cuerpo del mensaje. Se interpreta como html si comienza con < y termina con >
        - resource:str = cuerpo del mensaje en un archivo (si message está vacío)
        - deleteAfterSend:bool = eliminar el mensaje del servidor luego de enviarlo
        - headers:dict = cabeceras del mail (RFC822)
        - images:dict = imágenes incrustadas en el mail {"cid":"recurso"}
        - attachments:dict = archivos adjuntos en el mail {"nombre":"recurso"}

        :param msg: el mensaje en forma de dict
        :return:
        """
        return self.bpm.call("EBHBPMService.sendMail", msg)

    def execute(self, script: str, context: dict):
        """
        Ejecuta un script en la BPM y devuelve el resultado. Útil, por ejemplo, para ejecutar
        una plantilla VTL.

        Por ejemplo:

        plantilla_procesada=bpm.execute("MI_PLANTILLA_VTL",{"nombre":"Juan","edad":30})

        :param script: el id del script
        :param context: los datos que le pasamos al script como variables
        :return: el resultado
        """
        return self.bpm.call("EBHBPMService.execute", body={
            "script": script,
            "context": context
        })

    def notifyUser(self, user: str, title: str, description: str, target: str = None, sound: bool = False):
        """
        Emite una notificación a un usuario logueado en la BPM.

        :param user: el nombre del usuario
        :param title: el título de la notificación
        :param description: la descripción de la notificación
        :param target: destino de la notificación (cuando hace clic se puede redirigir a otra sección de la BPM o url)
        :param sound: indica si e debe reproducir o no sonido
        """
        self.bpm.call("EBHBPMService.notifyUser", body={
            "user": user,
            "title": title,
            "description": description,
            "target": target,
            "sound": sound})

    def notifyGroup(self, group: str, title: str, description: str, target: str = None, sound: bool = False):
        """
        Emite una notificación a un usuario logueado en la BPM.

        :param group: el nombre del groupo
        :param title: el título de la notificación
        :param description: la descripción de la notificación
        :param target: destino de la notificación (cuando hace clic se puede redirigir a otra sección de la BPM o url)
        :param sound: indica si e debe reproducir o no sonido
        """
        self.bpm.call("EBHBPMService.notifyGroup", body={
            "group": group,
            "title": title,
            "description": description,
            "target": target,
            "sound": sound})

    def env(self) -> dict:
        return self.bpm.call("EBHBPMService.env", body={})

    def now(self):
        return self.bpm.call("EBHBPMService.now", body={})

    def nextBusinessKey(self, processKey: str):
        return self.bpm.call("EBHBPMService.nextBusinessKey", body={"processKey": processKey})

    def today(self):
        return self.bpm.call("EBHBPMService.today", body={})

    def getProperty(self, code: str, the_property: str):
        return self.bpm.call("EBHBPMService.getProperty", body={
            "code": code,
            "property": the_property})

    def text(self, name: str):
        return self.bpm.call("EBHBPMService.text", body={
            "name": name})

    def code(self, name: str):
        return self.bpm.call("EBHBPMService.code", body={
            "name": name})

    def code_properties(self, name: str):
        return self.bpm.call("EBHBPMService.codeProperties", body={
            "name": name})

    def list(self, name: str, the_filter: dict = None):
        return self.bpm.call("EBHBPMService.list", body={
            "name": name,
            "filter": the_filter})

    def tokenize(self, user: str, payload: dict = None):
        return self.bpm.call("EBHBPMService.tokenize", body={
            "user": user, "payload": payload})


class Logger:
    def __init__(self, bpm):
        self.bpm = bpm

    def log(self, logger: str, message: str,
            level: Literal["info", "warn", "error", "debug", "trace"] = "info"):
        """
        Logs a message with the specified logger and level.

        :param message: The message to log
        :param logger: The logger to use (default is "bpm.general")
        :param level: The log level (default is "info"). One of: "info", "warn", "error", "debug", "trace"
        """
        return self.bpm.call("EBHBPMService.log", body={
            "message": message, "logger": logger, "level": level})

    def info(self, logger: str, message: str):
        return self.log(logger, message, "info")

    def warn(self, logger: str, message: str):
        return self.log(logger, message, "warn")

    def error(self, logger: str, message: str):
        return self.log(logger, message, "error")

    def debug(self, logger: str, message: str):
        return self.log(logger, message, "debug")

    def trace(self, logger: str, message: str):
        return self.log(logger, message, "trace")


class ContextInput(object):

    def __init__(self):
        self.context = None

    def __getitem__(self, item):
        return self.context.getInputValue(item)

    def __setitem__(self, key, value):
        self.context.setInputValue(key, value)


class ContextJsonValue(object):

    def __init__(self):
        self.context = None
        self.item = None

    def __getitem__(self, item):
        return self.context.getJsonValue(self.item, item)

    def __setitem__(self, key, value):
        self.context.setJsonValue(self.item, key, value)


class ContextJson(object):
    def __getattr__(self, item):
        json_value = ContextJsonValue()
        json_value.context = self.context
        json_value.item = item
        try:
            self.context.getValue(item + "!=null")
        except ValueError:
            if item == '_responseHeaders':
                self.context.fakeContext[item] = {}
            else:
                raise NameError(item) from None
        return json_value


class Context(object):
    input: ContextInput
    json: ContextJson

    def __init__(self, bpm):
        super(Context, self).__setattr__('bpm', bpm)
        super(Context, self).__setattr__('input', ContextInput())
        super(Context, self).__setattr__('json', ContextJson())
        super(Context, self).__setattr__('fakeContext', {})
        self.input.context = self
        self.json.context = self

    def __setattr__(self, key, value):
        if key in dir(self):
            super(Context, self).__setattr__(key, value)
        else:
            self.setValue(key, value)

    def __getattr__(self, item):
        try:
            if item in dir(self):
                super(Context, self).__getattribute__(item)
            else:
                return self.getValue(item)
        except ValueError as x:
            if str(x) == 'No address supplied':
                try:
                    return self.fakeContext[item]
                except KeyError:
                    if item in os.environ:
                        self.fakeContext[item] = os.environ.get(item)
                        return os.environ.get(item)
            raise NameError(item) from None

    def __getitem__(self, item):
        try:
            return self.getValue(item)
        except ValueError as x:
            if str(x) == 'No address supplied':
                try:
                    return self.fakeContext[item]
                except KeyError:
                    if item in os.environ:
                        self.fakeContext[item] = os.environ.get(item)
                        return os.environ.get(item)
            raise KeyError(item) from None

    def __setitem__(self, key, value):
        try:
            self.setValue(key, value)
        except ValueError as x:
            if str(x) == 'No address supplied':
                self.fakeContext[key] = value
            else:
                raise x

    def setValue(self, variable: str, value: Any, address=None):
        try:
            self.bpm.exec(script=f"${{_____context_____.setAttribute('{variable}',_____variable_____,100)}}",
                          context={"_____variable_____": value},
                          address=address)
        except ValueError as x:
            if str(x) == 'No address supplied':
                self.fakeContext[variable] = value
            else:
                raise x

    def setJsonValue(self, variable: str, key: str, value: Any, address=None):
        try:
            if value is None:
                self.bpm.exec(script=f"${{{variable}.putNull('{key}')}}",
                              context={},
                              address=address)
            else:
                self.bpm.exec(script=f"${{{variable}.put('{key}',_____variable_____)}}",
                              context={"_____variable_____": value},
                              address=address)
        except ValueError as x:
            if str(x) == 'No address supplied':
                if variable not in self.fakeContext.keys():
                    self.fakeContext[variable] = {}
                self.fakeContext[variable][key] = value
            else:
                raise x

    def setInputValue(self, key: str, value: Any, address=None):
        self.setJsonValue("input", key, value, address)

    def getValue(self, variable: str, address=None):
        return self.bpm.exec(script=f"${{{variable}}}", address=address)

    def get(self, variable: str, default: Any = None):
        try:
            return self.__getitem__(variable)
        except KeyError:
            return default

    def getJsonValue(self, variable: str, key: str, address=None):
        return self.bpm.exec(script=f"${{{variable}.getValue(\"{key}\")}}", address=address)

    def getInputValue(self, key: str, address=None):
        return self.getJsonValue("input", key, address)


class ResourceService:
    def __init__(self, bpm):
        self.bpm = bpm

    def accessFile(self, path: str):
        file_url = self.accessPath(path)
        p = urlparse(file_url)
        return os.path.abspath(os.path.join(p.netloc, p.path))

    def accessTempFile(self, path: str):
        file_url = self.accessTempPath(path)
        p = urlparse(file_url)
        return os.path.abspath(os.path.join(p.netloc, p.path))

    def accessPath(self, path: str):
        return self.bpm.call("EBHBPMResourceService.accessPath", body={"path": path})

    def accessTempPath(self, path: str):
        return self.bpm.call("EBHBPMResourceService.accessTempPath", body={"path": path})

    def getResourceInfo(self, path: str):
        return self.bpm.call("EBHBPMResourceService.getResourceInfo", body={"path": path})

    def listPaths(self, path: str):
        return self.bpm.call("EBHBPMResourceService.listPaths", body={"path": path})


class ReportService:
    def __init__(self, bpm):
        self.bpm = bpm

    def renderReport(self, options: dict, reportData: dict):
        return self.bpm.call("EBHBPMReportService.renderReport", body={"options": options, "reportData": reportData})

    def renderReports(self, options: dict, reports: list):
        return self.bpm.call("EBHBPMReportService.renderReports",
                             body={"options": options, "reports": {"reports": reports}})


class DocumentService:
    def __init__(self, bpm):
        self.bpm = bpm

    def registerCollection(self, schema: dict):
        return self.bpm.call("EBHBPMDocumentService.registerCollection", body={"schema": schema})

    def unregisterCollection(self, collection: str) -> bool:
        return self.bpm.call("EBHBPMDocumentService.unregisterCollection", body={"collection": collection})

    def listCollections(self) -> List[str]:
        return self.bpm.call("EBHBPMDocumentService.listCollections", body={})

    def getSchema(self, collection: str) -> dict:
        return self.bpm.call("EBHBPMDocumentService.getSchema", body={"collection": collection})

    def create(self, collection: str, theObject: dict) -> str:
        return self.bpm.call("EBHBPMDocumentService.create", body={"collection": collection, "object": theObject})

    def createList(self, collection: str, theObject: List[dict]):
        return self.bpm.call("EBHBPMDocumentService.createList", body={"collection": collection, "object": theObject})

    def readByOid(self, oid: str) -> dict:
        return self.bpm.call("EBHBPMDocumentService.readByOid", body={"oid": oid})

    def readById(self, collection: str, theId: str) -> dict:
        return self.bpm.call("EBHBPMDocumentService.readById", body={"collection": collection, "id": theId})

    def readList(self, collection: str, criteria: str = None, parameters: dict = None, sorting: str = None) -> \
            List[dict]:
        return self.bpm.call("EBHBPMDocumentService.readList",
                             body={"collection": collection, "criteria": criteria, "parameters": parameters,
                                   "sorting": sorting})

    def upsert(self, collection: str, theObject: dict) -> str:
        return self.bpm.call("EBHBPMDocumentService.upsert", body={"collection": collection, "object": theObject})

    def updateByCriteria(self, collection: str, toSet: dict, criteria: str = None, parameters: dict = None) -> int:
        return self.bpm.call("EBHBPMDocumentService.updateByCriteria",
                             body={"collection": collection, "criteria": criteria,
                                   "set": toSet,
                                   "parameters": parameters})

    def updateById(self, collection: str, theId: str, toSet: dict) -> bool:
        return self.bpm.call("EBHBPMDocumentService.updateById", body={"collection": collection,
                                                                       "id": theId,
                                                                       "set": toSet})

    def updateByOid(self, collection: str, oid: str, toSet: dict) -> bool:
        return self.bpm.call("EBHBPMDocumentService.updateByOid", body={"collection": collection,
                                                                        "oid": oid,
                                                                        "set": toSet})

    def deleteByOid(self, oid: str) -> bool:
        return self.bpm.call("EBHBPMDocumentService.deleteByOid", body={"oid": oid})

    def deleteById(self, collection: str, theId: str) -> dict:
        return self.bpm.call("EBHBPMDocumentService.deleteById", body={"collection": collection, "id": theId})

    def deleteByCriteria(self, collection: str, criteria: str = None, parameters: dict = None) -> int:
        return self.bpm.call("EBHBPMDocumentService.updateByCriteria",
                             body={"collection": collection, "criteria": criteria, "parameters": parameters})


class RuntimeService:
    def __init__(self, bpm):
        self.bpm = bpm

    def startProcessInstanceByKey(self, processDefinitionKey: str, businessKey: str, variables: dict):
        return self.bpm.call("EBHBPMRuntime.startProcessInstanceByKey", body={
            "processDefinitionKey": processDefinitionKey, "businessKey": businessKey, "variables": variables})

    def startProcessInstanceByKeyAndTenantId(self, processDefinitionKey: str, businessKey: str, tenantId: str,
                                             variables: dict):
        return self.bpm.call("EBHBPMRuntime.startProcessInstanceByKeyAndTenantId", body={
            "processDefinitionKey": processDefinitionKey, "businessKey": businessKey, "tenantId": tenantId,
            "variables": variables})

    def startProcessInstanceById(self, processDefinitionId: str, businessKey: str, variables: dict):
        return self.bpm.call("EBHBPMRuntime.startProcessInstanceById", body={
            "processDefinitionId": processDefinitionId, "businessKey": businessKey, "variables": variables})

    def startProcessInstanceByMessage(self, messageName: str, businessKey: str, variables: dict):
        return self.bpm.call("EBHBPMRuntime.startProcessInstanceByMessage", body={
            "messageName": messageName, "businessKey": businessKey, "variables": variables})

    def startProcessInstanceByMessageAndTenantId(self, messageName: str, businessKey: str, tenantId: str,
                                                 variables: dict):
        return self.bpm.call("EBHBPMRuntime.startProcessInstanceByMessageAndTenantId", body={
            "messageName": messageName, "businessKey": businessKey, "tenantId": tenantId,
            "variables": variables})

    def deleteProcessInstance(self, processInstanceId: str, deleteReason: str):
        self.bpm.call("EBHBPMRuntime.deleteProcessInstance", body={
            "processInstanceId": processInstanceId, "deleteReason": deleteReason})

    def updateBusinessKey(self, processInstanceId: str, businessKey: str):
        self.bpm.call("EBHBPMRuntime.updateBusinessKey", body={
            "processInstanceId": processInstanceId, "businessKey": businessKey})

    def getBusinessKey(self, processInstanceId: str):
        return self.bpm.call("EBHBPMRuntime.getProcessBusinessKey", body={
            "processInstanceId": processInstanceId})

    def getProcessInstance(self, processInstanceId: str):
        return self.bpm.call("EBHBPMRuntime.getProcessInstance", body={
            "processInstanceId": processInstanceId})

    def setProcessInstanceName(self, processInstanceId: str, name: str):
        self.bpm.call("EBHBPMRuntime.setProcessInstanceName",
                      body={"processInstanceId": processInstanceId, "name": name})

    def getVariables(self, executionId: str):
        return self.bpm.call("EBHBPMRuntime.getVariables", body={"executionId": executionId})

    def getVariable(self, executionId: str, variableName: str):
        return self.bpm.call("EBHBPMRuntime.getVariable",
                             body={"executionId": executionId, "variableName": variableName})

    def hasVariable(self, executionId: str, variableName: str):
        return self.bpm.call("EBHBPMRuntime.hasVariable",
                             body={"executionId": executionId, "variableName": variableName})

    def setVariable(self, executionId: str, variableName: str, value: Any):
        return self.bpm.call("EBHBPMRuntime.setVariable",
                             body={"executionId": executionId, "variableName": variableName, "value": value})

    def removeVariable(self, executionId: str, variableName: str):
        self.bpm.call("EBHBPMRuntime.removeVariable",
                      body={"executionId": executionId, "variableName": variableName})

    def signalEventReceived(self, executionId: str, signalName: str, processVariables=None):
        if processVariables is None:
            processVariables = {}
        self.bpm.call("EBHBPMRuntime.signalEventReceived",
                      body={"executionId": executionId, "signalName": signalName,
                            "processVariables": processVariables})

    def messageEventReceived(self, executionId: str, messageName: str, processVariables=None):
        if processVariables is None:
            processVariables = {}
        self.bpm.call("EBHBPMRuntime.messageEventReceived",
                      body={"executionId": executionId, "messageName": messageName,
                            "processVariables": processVariables})


class ExecutionService:
    def __init__(self, bpm):
        self.bpm = bpm

    def getBusinessKey(self):
        process_instance_id = self.bpm.context.getValue('execution.getProcessInstanceId()')
        return self.bpm.call("EBHBPMRuntime.getProcessBusinessKey", body={
            "processInstanceId": process_instance_id})

    def updateBusinessKey(self, businessKey: str):
        process_instance_id = self.bpm.context.getValue('execution.getProcessInstanceId()')
        try:
            self.bpm.exec(script="${runtimeService.updateBusinessKey(________pi,________bk)}",
                          context={"________pi": process_instance_id, "________bk": businessKey})
        except ValueError as x:
            self.bpm.call("EBHBPMRuntime.updateBusinessKey", body={
                "processInstanceId": process_instance_id, "businessKey": businessKey})

    def setProcessInstanceName(self, name: str):
        process_instance_id = self.bpm.context.getValue('execution.getProcessInstanceId()')
        try:
            self.bpm.exec(script="${runtimeService.setProcessInstanceName(________pi,________name)}",
                          context={"________pi": process_instance_id, "________name": name})
        except ValueError as x:
            self.bpm.call("EBHBPMRuntime.setProcessInstanceName",
                          body={"processInstanceId": process_instance_id, "name": name})

    def getVariables(self):
        process_instance_id = self.bpm.context.getValue('execution.getProcessInstanceId()')
        return self.bpm.call("EBHBPMRuntime.getVariables", body={"executionId": process_instance_id})

    def getVariable(self, variableName: str):
        process_instance_id = self.bpm.context.getValue('execution.getProcessInstanceId()')
        return self.bpm.call("EBHBPMRuntime.getVariable",
                             body={"executionId": process_instance_id, "variableName": variableName})

    def hasVariable(self, variableName: str):
        process_instance_id = self.bpm.context.getValue('execution.getProcessInstanceId()')
        return self.bpm.call("EBHBPMRuntime.hasVariable",
                             body={"executionId": process_instance_id, "variableName": variableName})

    def setVariable(self, variableName: str, value: Any):
        try:
            self.bpm.exec(script="${execution.setVariable(_____variable_____,jsonHelper.toFlowable(_____value_____))}",
                          context={"_____variable_____": variableName, "_____value_____": value})
        except ValueError as x:
            process_instance_id = self.bpm.context.getValue('execution.getProcessInstanceId()')
            return self.bpm.call("EBHBPMRuntime.setVariable",
                                 body={"executionId": process_instance_id, "variableName": variableName,
                                       "value": value})

    def removeVariable(self, variableName: str):
        try:
            self.bpm.exec(script="${execution.removeVariable(_____variable_____)}",
                          context={"_____variable_____": variableName})
        except ValueError as x:
            process_instance_id = self.bpm.context.getValue('execution.getProcessInstanceId()')
            self.bpm.call("EBHBPMRuntime.removeVariable",
                          body={"executionId": process_instance_id, "variableName": variableName})

    def getProcessInstanceId(self):
        process_instance_id = self.bpm.context.getValue('execution.getProcessInstanceId()')
        return process_instance_id


class AgentService:
    def __init__(self, bpm):
        self.bpm = bpm

    def startChat(self, agent: str, userId: str, handler: callable, body=None):
        if body is None:
            body = {}
        address: str = self.bpm.call("EBHBPMAgentService.startChat",
                                     body={"agent": agent, "userId": userId, "body": body})
        self.bpm.register_handler(address, handler)
        return address

    def chat(self, chatId: str, message: str, body=None) -> bool:
        if body is None:
            body = {}
        return self.bpm.call("EBHBPMAgentService.chat", body={"chatId": chatId, "message": message, "body": body})

    def endChat(self, chatId: str, body=None) -> bool:
        if body is None:
            body = {}
        self.bpm.unregister_handler(chatId)
        return self.bpm.call("EBHBPMAgentService.endChat", body={"chatId": chatId, "body": body})
