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
    db_string = "postgresql+psycopg2://{0}:{1}@/{2}".format(usr, pw, db_name)
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
    print "0. Exit"

def create_table(engine):
    table_name = raw_input("Enter table name: ")
    num_col = raw_input("Enter # of columns: ")
    metadata = MetaData()
    cols = []
    for i in range(int(num_col)):
        col = []
        key = raw_input("Enter Column "+str(i+1)+"'s name: ")
        value = input("Enter Column "+str(i+1)+"'s type: ")
        auto = raw_input("Enter Colum auto: ")
        pkey = raw_input("Primary: ")
        col.append(key)
        col.append(value)
        col.append(auto)
        col.append(pkey)
        cols.append(col)
    table = Table(str(table_name), metadata,
                  *(Column(name, data_type, autoincrement=auto, primary_key=pkey) for name, data_type,auto, pkey in cols))
    
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
    
    
def shutdown(engine):
    exit()

menu_options = { 1 : display_tables,
                 2 : create_table,
                 3 : insert_into_table,
                 0 : shutdown}

def main():
    engine = init_sql()
    while True:
        display_menu()
        choice = input('Choice: ')
        menu_options[choice](engine)

if __name__ == "__main__":
    main()


