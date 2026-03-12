def validate_sql(sql):

    forbidden = ["DELETE", "UPDATE", "DROP", "ALTER"]

    for word in forbidden:
        if word in sql.upper():
            raise Exception("Unsafe SQL detected")