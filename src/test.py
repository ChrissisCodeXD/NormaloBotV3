import os
import asyncio
import aiomysql
import ssl



ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ctx.check_hostname = False
ctx.load_verify_locations(cafile="D:\\Benutzer\\Dokumente\\python\\normaloBotV3\\src\\data\\cacert-2022-10-11.pem")



async def connect_db():
   loop = asyncio.get_event_loop()
   #ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
   #ssl_context.load_verify_locations(cafile="D:\\Benutzer\\Dokumente\\python\\normaloBotV3\\src\\data\\cacert-2022-03-29.pem")
   connection = await aiomysql.connect(
       host='eu-central.connect.psdb.cloud', port=3306,
       user='j1ebq7dqgit20yz1geie', password='pscale_pw_Ja4YcuMeJAXGCsVImqDMFCx8nxYVvj8JIMrwqxmkGUd',
       db='normalobotv3', ssl=ssl_context, loop=loop
   )
   cursor = await connection.cursor()
   await cursor.execute("select @@version")
   version = await cursor.fetchall()
   print('Running version: ', version)
   await cursor.close()
   connection.close()
loop = asyncio.get_event_loop()
loop.run_until_complete(connect_db())
