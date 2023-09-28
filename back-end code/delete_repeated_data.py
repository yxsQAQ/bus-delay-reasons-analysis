import pymysql


# connect to database
connection = pymysql.connect(
    host="127.0.0.1",
    user="root",
    password="root123",
    database='bods_bus_database'
)

try:
    with connection.cursor() as cursor:
        # get access to all tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]

            # get table name
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            column_names = [column[0] for column in columns]

            duplicate_query = f"""
                DELETE FROM {table_name}
                WHERE id NOT IN (
                    SELECT id FROM (
                        SELECT MIN(id) AS id
                        FROM {table_name}
                        GROUP BY {", ".join(column_names[1:])}
                    ) AS temp
                )
            """

            # execute duplicate data
            cursor.execute(duplicate_query)
            connection.commit()

finally:
    connection.close()
