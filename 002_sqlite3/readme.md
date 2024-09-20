df = pd.read_sql_query("select * from instructor;", conn)
这个函数用的比较少，后期如果用到数据库，可以考虑尝试一下。