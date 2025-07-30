import sys

sys.path.append("../src")

import redflagbpm
from redflagbpm.MSSQLUtils import get_connection, fetch_dicts

bpm = redflagbpm.BPMService()

with get_connection(bpm, 'MY_DB') as connection:
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT viaje,tviaje,peso
            FROM [SAP].[dbo].[OF_CV_VIAJES]
            WHERE tviaje = %s
        """, ('RESERVAS',))
        result = fetch_dicts(cursor)
        for row in result:
            print(row)
