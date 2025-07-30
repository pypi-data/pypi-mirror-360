#!/usr/bin/env python
# coding: utf-8
import psycopg2
from psycopg2 import pool
from redflagbpm.BPMService import BPMService


def get_connection(bpm: BPMService, datasource: str):
    """
    # Crea
    with get_connection(bpm, 'datasource_name') as connection:
       try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM nombre_de_la_tabla;")
                result = cursor.fetchall()
                print(result)
        except Exception as e:
            print("Error:", e)

    # Cuando sales del bloque 'with', la conexión se cierra automáticamente.

    :param bpm: conexión a la bpm
    :param datasource: nombre del datasource
    :return: la conexión
    """
    dsrc: dict = bpm.documentService.readById('@@@@@DATASOURCE_COLLECTION@@@@@', datasource)
    if dsrc is None:
        raise ValueError("Datasource not found: " + datasource)

    if dsrc['dialect'] != 'POSTGRES':
        raise ValueError("Only POSTGRES dialect is supported: " + dsrc['dialect'])

    url = dsrc['url']
    # extract host from url
    port_host = url.split('/')[2]
    # extract host from port_host
    host = port_host.split(':')[0]
    # extract port from port_host (default 5432)
    port = port_host.split(':')[1] if len(port_host.split(':')) > 1 else '5432'
    # extract database from url
    database = url.split('/')[3]

    conn = psycopg2.connect(database=database,
                            user=dsrc['username'],
                            password=dsrc['password'],
                            host=host,
                            port=port)
    conn.autocommit = True
    return conn


def get_dblink(bpm: BPMService, datasource: str, ignore_host: bool = True):
    """
    Obtiene una cadena para construir un dblink a la base de datos indicada en el datasource

    :param bpm: conexión a la bpm
    :param datasource: nombre del datasource
    :return: el pool de conexiones
    """
    dsrc: dict = bpm.documentService.readById('@@@@@DATASOURCE_COLLECTION@@@@@', datasource)
    if dsrc is None:
        raise ValueError("Datasource not found: " + datasource)

    if dsrc['dialect'] != 'POSTGRES':
        raise ValueError("Only POSTGRES dialect is supported: " + dsrc['dialect'])

    url = dsrc['url']
    # extract host from url
    port_host = url.split('/')[2]
    # extract host from port_host
    host = port_host.split(':')[0]
    # extract port from port_host (default 5432)
    port = port_host.split(':')[1] if len(port_host.split(':')) > 1 else '5432'
    # extract database from url
    database = url.split('/')[3]

    user = dsrc['username'].replace("'", "\\'").replace(" ", "\\ ")
    password = dsrc['password'].replace("'", "\\'").replace(" ", "\\ ")

    if ignore_host:
        return f"host=localhost dbname={database} user={user} password={password}"
    else:
        return f"host={host} port={port} dbname={database} user={user} password={password}"


def get_pool(bpm: BPMService, datasource: str, max_connections=5):
    """
    # Utiliza el grupo de conexiones con la cláusula 'with'
    connection_pool=get_pool(bpm, 'datasource_name', 5)

    with connection_pool.getconn() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM nombre_de_la_tabla;")
                result = cursor.fetchall()
                print(result)
        except Exception as e:
            print("Error:", e)
    ```

    # Cuando sales del bloque 'with', la conexión se devuelve automáticamente al grupo de conexiones.

    # Finalmente, cuando hayas terminado completamente con el grupo de conexiones, ciérralo para liberar los recursos:

    connection_pool.closeall()

    :param bpm: conexión a la bpm
    :param datasource: nombre del datasource
    :param max_connections: número máximo de conexiones en el pool
    :return: el pool de conexiones
    """
    dsrc: dict = bpm.documentService.readById('@@@@@DATASOURCE_COLLECTION@@@@@', datasource)
    if dsrc is None:
        raise ValueError("Datasource not found: " + datasource)

    if dsrc['dialect'] != 'POSTGRES':
        raise ValueError("Only POSTGRES dialect is supported: " + dsrc['dialect'])

    url = dsrc['url']
    # extract host from url
    port_host = url.split('/')[2]
    # extract host from port_host
    host = port_host.split(':')[0]
    # extract port from port_host (default 5432)
    port = port_host.split(':')[1] if len(port_host.split(':')) > 1 else '5432'
    # extract database from url
    database = url.split('/')[3]

    # Configura los parámetros de conexión a tu base de datos
    db_params = {
        "database": database,
        "user": dsrc['username'],
        "password": dsrc['password'],
        "host": host,
        "port": port
    }

    # Crea el grupo de conexiones con SimpleConnectionPool
    connection_pool = psycopg2.pool.SimpleConnectionPool(minconn=1, maxconn=max_connections, **db_params)
    return connection_pool
