import sqlite3

connection = sqlite3.connect("student.db")
cursor = connection.cursor()

# create table
table_info = """
create table CHATSTUDENT(NAME VARCHAR(25), CLASS VARCHAR(25),
SECTION VARCHAR(25), MARKS INT)
"""


cursor.execute(table_info)

# insert more records
cursor.execute('''Insert into CHATSTUDENT values('amju', 'coding', 'A', '39')''')
cursor.execute('''Insert into CHATSTUDENT values('jgyf', 'sing', 'F', '23')''')
cursor.execute('''Insert into CHATSTUDENT values('nhny', 'sweep', 'E', '56')''')
cursor.execute('''Insert into CHATSTUDENT values('sgt', 'dance', 'B', '54')''')

# Display all records
print("inserted records are")
data = cursor.execute('''Select * from CHATSTUDENT''')
for row in data:
    print(row)

# commit changes in database
connection.close()
connection.commit()
