#!/usr/bin/env python
# coding: utf-8
import pymssql
from redflagbpm.BPMService import BPMService


def get_connection(bpm: BPMService, datasource: str):
    """
    Crea una conexión a SQL Server utilizando pymssql.

    with get_connection(bpm, 'datasource_name') as connection:
       try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM nombre_de_la_tabla;")
                result = cursor.fetchall()
                print(result)
        except Exception as e:
            print("Error:", e)

    La conexión se cierra automáticamente al salir del bloque 'with'.

    :param bpm: conexión a la bpm
    :param datasource: nombre del datasource
    :return: la conexión
    """
    dsrc: dict = bpm.documentService.readById('@@@@@DATASOURCE_COLLECTION@@@@@', datasource)
    if dsrc is None:
        raise ValueError("Datasource not found: " + datasource)

    if dsrc['dialect'] != 'DEFAULT':
        raise ValueError("Only DEFAULT dialect is supported: " + dsrc['dialect'])

    url = dsrc['url']
    # Extrae host y puerto desde la URL
    # url de ejemplo: jdbc:sqlserver://localhost:1433;databaseName=sap;encrypt=true;trustServerCertificate=true
    host_port = url.split('//')[1].split(';')[0]
    host = host_port.split(':')[0]
    port = int(host_port.split(':')[1]) if len(host_port.split(':')) > 1 else 1433
    # Extrae el nombre de la base de datos desde la URL buscando databaseName=xxxx
    database = [x.split('=')[1] for x in url.split(';') if 'databaseName=' in x][0]
    # 'encryption' option should be dict_keys(['default', 'off', 'request', 'require'])
    encrypt = 'request' if 'encrypt=true' in url else 'off'

    # Conectar a SQL Server usando pymssql
    conn = pymssql.connect(
        server=host,
        port=str(port),
        user=dsrc['username'],
        password=dsrc['password'],
        database=database,
        encryption=str(encrypt),
        autocommit=True
    )
    return conn


def get_dblink(bpm: BPMService, datasource: str, ignore_host: bool = True):
    """
    Obtiene una cadena de conexión directa para SQL Server.

    :param bpm: conexión a la bpm
    :param datasource: nombre del datasource
    :param ignore_host: si se debe ignorar el host y usar localhost
    :return: cadena de conexión
    """
    dsrc: dict = bpm.documentService.readById('@@@@@DATASOURCE_COLLECTION@@@@@', datasource)
    if dsrc is None:
        raise ValueError("Datasource not found: " + datasource)

    if dsrc['dialect'] != 'MSSQL':
        raise ValueError("Only MSSQL dialect is supported: " + dsrc['dialect'])

    url = dsrc['url']
    port_host = url.split('/')[2]
    host = port_host.split(':')[0]
    port = int(port_host.split(':')[1]) if len(port_host.split(':')) > 1 else 1433
    database = url.split('/')[3]

    user = dsrc['username'].replace("'", "\\'").replace(" ", "\\ ")
    password = dsrc['password'].replace("'", "\\'").replace(" ", "\\ ")

    if ignore_host:
        return f"server=localhost,{port};database={database};user={user};password={password};"
    else:
        return f"server={host},{port};database={database};user={user};password={password};"


def get_pool(bpm: BPMService, datasource: str, max_connections=5):
    """
    Crea un pool de conexiones a SQL Server utilizando pymssql.

    connection_pool = get_pool(bpm, 'datasource_name', 5)

    with connection_pool.getconn() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM nombre_de_la_tabla;")
                result = cursor.fetchall()
                print(result)
        except Exception as e:
            print("Error:", e)

    connection_pool.closeall()

    :param bpm: conexión a la bpm
    :param datasource: nombre del datasource
    :param max_connections: número máximo de conexiones en el pool
    :return: el pool de conexiones
    """
    dsrc: dict = bpm.documentService.readById('@@@@@DATASOURCE_COLLECTION@@@@@', datasource)
    if dsrc is None:
        raise ValueError("Datasource not found: " + datasource)

    if dsrc['dialect'] != 'MSSQL':
        raise ValueError("Only MSSQL dialect is supported: " + dsrc['dialect'])

    url = dsrc['url']
    port_host = url.split('/')[2]
    host = port_host.split(':')[0]
    port = int(port_host.split(':')[1]) if len(port_host.split(':')) > 1 else 1433
    database = url.split('/')[3]

    # Conexión directa usando pymssql
    conn_str = {
        "server": host,
        "port": port,
        "user": dsrc['username'],
        "password": dsrc['password'],
        "database": database
    }

    # Simulando un pool de conexiones
    class ConnectionPool:
        def __init__(self, conn_str, max_connections):
            self.conn_str = conn_str
            self.max_connections = max_connections
            self.connections = [pymssql.connect(**conn_str) for _ in range(max_connections)]

        def getconn(self):
            return self.connections.pop() if self.connections else pymssql.connect(**self.conn_str)

        def putconn(self, conn):
            if len(self.connections) < self.max_connections:
                self.connections.append(conn)
            else:
                conn.close()

        def closeall(self):
            for conn in self.connections:
                conn.close()

    return ConnectionPool(conn_str, max_connections)


def fetch_dicts(cursor):
    """
    Convierte los resultados de un cursor pymssql en una lista de diccionarios.
    Las claves son los nombres de las columnas y los valores son los datos de cada fila.

    Se usa de la siguiente forma:

    with get_connection(bpm, 'datasource_name') as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM nombre_de_la_tabla")
            result = fetch_dicts(cursor)
            print(result)
    """
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
