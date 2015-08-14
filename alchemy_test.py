#!/usr/bin/python
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
from getpass import getpass

db_string = None
tables = None
usr = None
pw = None

def init_sql():
    global usr, pw, db_string
    db_name = raw_input("Enter database name: ")
    usr = raw_input('Enter username: ')
    pw = getpass('Enter password: ')
    choice = raw_input('Pick 1) MySql 2) Postgresql: ')
    if choice == str(1):
        db_string = "mysql+mysqldb://{0}:{1}@/{2}".format(usr, pw, db_name)
    elif choice == str(2):
        db_string = "postgresql+psycopg2://{0}:{1}@/{2}".format(usr, pw, db_name)
    else:
        print "Not a valid Choice!"
        exit(1)
    print db_string
    engine = create_engine(db_string)
    return engine

def display_tables(engine):
    metadata = MetaData()
    metadata.reflect(engine)
    for t in metadata.sorted_tables:
        print t.name

def display_menu():
    print "1. Display Tables"
    print "2. Create Table"
    print "3. Insert Into Table"
    print "4. Delete Table"
    print "5. Select All Data From Table"
    print "6. Remove Row From Table"
    print "7. Run SQL Command"
    print "0. Exit"

def run_sql(engine):
    sql = raw_input("Enter SQL command: ")
    con = engine.connect()
    result = con.engine.execute(sql)
    for row in result:
        for col in row:
            print col
    
def create_table(engine):
    table_name = raw_input("Enter table name: ")
    num_col = raw_input("Enter # of columns: ")
    metadata = MetaData()
    cols = {}
    for i in range(int(num_col)):
        key = raw_input("Enter Column "+str(i+1)+"'s name: ")
        value = input("Enter Column "+str(i+1)+"'s type: ")
        cols[key] = value
    
    table = Table(str(table_name), metadata,
                  Column('id', Integer, primary_key=True, autoincrement=True),
                  *(Column(name, data_type(20)) for name, data_type in cols.iteritems()))
    
    metadata.create_all(engine)

def insert_into_table(engine):
    metadata = MetaData()
    table_name = raw_input("Enter table name to edit: ")
    table = Table(table_name, metadata, autoload=True, autoload_with=engine)
    print [col.name for col in table.columns]
    print "Input data for each column"
    params = {}
    for col in table.columns:
        if col.name == 'id':
            continue
        params[col.name] = raw_input(str(col.name) + "  " + str( col.type) + ": ")
    ins = table.insert().values(params)
    ins.compile().params
    con = engine.connect()
    con.execute(ins)

def remove_from_table(engine):
    metadata = MetaData()
    table_name = raw_input("Enter table name to edit: ")
    table = Table(table_name, metadata, autoload=True, autoload_with=engine)
    print [col.name for col in table.columns]
    by_col = raw_input("Enter column to use for where clause: ")
    value = raw_input("Enter value to be searched for: ")
    where_clause = "table.c." + by_col
    delete = table.delete().where(eval(where_clause) == value)
    con = engine.connect()
    con.execute(delete)

# help from http://stackoverflow.com/questions/11233128/how-to-clean-the-database-dropping-all-records-using-sqlalchemy
def delete_table(engine):
    metadata = MetaData()
    table_name = raw_input("Enter table name to delete: ")
    table = Table(table_name, metadata, autoload=True, autoload_with=engine)
    table.drop(engine)

# help from http://stackoverflow.com/questions/636548/select-in-sqlalchemy
# getting error sqlalchemy.exc.ProgrammingError: (ProgrammingError) permission denied for relation - could be issue with 
# my Postgresql setup?
def select_all(engine):
    metadata = MetaData()
    table_name = raw_input("Enter table name to view all data in table: ")
    table = Table(table_name, metadata, autoload=True, autoload_with=engine)
    con = engine.connect()
    query = table.select()
    result = con.execute(query)
    for row in result:
        print row
    
def shutdown(engine):
    exit()

menu_options = { 1 : display_tables,
                 2 : create_table,
                 3 : insert_into_table,
		 4 : delete_table,
		 5 : select_all,
                 6 : remove_from_table,
                 7 : run_sql,
                 0 : shutdown}

def main():
    engine = init_sql()
    while True:
	display_menu()
	choice = input('Choice: ')
	menu_options[choice](engine)


if __name__ == "__main__":
    main()
