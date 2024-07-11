import aiosqlite3
import asyncio 
# import asyncpg


async def connect():
    conn = await aiosqlite3.connect("./database.db")
    c = await conn.cursor()
    #conn = await asyncpg.connect(dsn = "postgres://xfncuobagwnpds:3bbdfa8d408627d23f03bd921b2069d10753e9a7beca633d7ed8179a3a588246@ec2-3-225-204-194.compute-1.amazonaws.com:5432/d9b9pkomfij9cf")
    
    
    #await conn.cursor.execute("INSERT INTO server_details VALUES (?, ?, ?, ?, ?)", )


    await c.execute("""CREATE TABLE server_details(
            guild_id int,
            prefix text,
            modroles text,
            adminroles text,
            cooldown real,
            msg_wh_url text
            )""")
    await conn.commit()

    await c.execute("""CREATE TABLE trigger_response(
            guild_id int,
            trigger text,
            response text,
            type text,
            user id,
            added_time real
            )""")
    await conn.commit()



#     await c.execute("""CREATE TABLE channel_triggered(
#             guild_id int,
#             channel_id int,
#             last_triggered real,
#             cooldown real
#             )""")
#     await conn.commit()

#     await c.execute("""CREATE TABLE to_do(
#             guild_id int,
#             to_do_id int,
#             details text,
#             status text,
#             added_time real
#             )""")
#     await conn.commit()



asyncio.run(connect())
    
