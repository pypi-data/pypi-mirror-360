import sqlglot as sg

"""
Calculate the cyclomatic complexity of a SQL query.

Args:
    sql (str): The SQL query string.

Returns:
    int: The calculated cyclomatic complexity.
"""
def calc(sql: str) -> int:
    result = 1
    parsed = sg.parse_one(sql)
    cyclomatics = [
        # Logic
        sg.exp.And, sg.exp.Or, sg.exp.In, sg.exp.Between, sg.exp.Like, sg.exp.Group,
        # Columns
        sg.exp.Case, sg.exp.Func,
        # Sets
        sg.exp.Join
    ]
    for cyclom in cyclomatics:
        for item in parsed.find_all(cyclom):
            if item.key == sg.exp.Join.key:
                result = result + 2
            else:
                result += 1
    return result
