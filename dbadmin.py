#!/usr/bin/env python

# install instructions:
# 1. install npyscreen module as per python module install instructions or 
#    have npyscreen module in the same directory as dbadmin.py
# 2. Some of the database functions work with MySQL.  So
#    if there is MySQL server then you can see that functionality.

from os import system
import sys #for debugging
sys.stdout = open('stdout.log', 'w')

import curses, getpass, MySQLdb, npyscreen, sys
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey

#=======  Global Variables =======
# Menu Decorations
empty_string = ' '*80	# Used for erasing the menu items
line = '-'*80			# Used for menu underline

# Menu strings
main_menu = "Databases | Tables | dAta | Sql | Login | Help | Quit"
sub_menu = {
    "Databases" : "Databases:  Select | Create | Remove | Back",
	"Tables" : "Tables:  Select | Create | Remove | Addcolumn | Delcolumn | Back",
    "dAta" : "dAta: Addrow | Delrow | Showall | Filter | Back"
    }

# Menu Navigation Helpers
sub_menu_items = {
    "Databases" : ('s', 's', 'c', 'C', 'r', 'R', 'b', 'B'),
	"Tables" : ('s', 'S', 'c', 'C', 'r', 'R', 'a', 'A', 'd', 'D', 'b', 'B'),
	"dAta" : ('a', 'A', 'd', 'D', 's', 'S', 'f', 'F', 'b', 'B')
    }
				  
char_map = {
    115:"s", 83:"s", 99:"c", 67:"c", 100:"d", 68:"d", 
    82:"r", 114:"r", 65:'a', 97:'a', 70:'f', 102:'f'
    }

# Database related 
# TODO - Using MySQL for testing purposes, need to replace MySQL code with the 
#           appropriate PostgreSQL code
class DbServer:
    def __init__(self):
        self.conn = None
        self.dbs = []           # List of databases in the server
        self.db = ""            # User Selected Database
        self.table = ""         # User Selected Table
        self.tables = []        # List of tables in the User Selected Database
        self.engine = None      # used for the connection sqlalchemy
        self.db_string = ""     # used to hold the connection string between requests
    
    def db(self):
        """ User Selected Database """
        return self.db
    
    def table(self):
        """ User Selected Table """
        return self.table

    def connect(self, login):
        """ Request to login to Database Server
            login is a list or tuple that contains [host, username, password] """
        # TODO: The following is MySQL sample code for debugging
        #       Need to replace/add appropriate PostgreSQL
        #self.conn = MySQLdb.connect(host=login[0], user=login[1], passwd=logien[2])
        # doesn't specify host
        # uses host to hold the dbname temporarily
        self.db_string = "postgresql+psycopg2://{0}:{1}@/{2}".format(login[1], login[2], login[0])
        self.engine = create_engine(self.db_string)
    
    def listDb(self):
        """ Request to provide list of Databases that are accessable by the logged user.  """
        # TODO: The following is MySQL sample code for debugging
        #       Need to replace/add appropriate PostgreSQL
        if self.engine == None:
            raise ValueError('Not connected to server')
        cur = self.conn.cursor()
        cur.execute("SHOW DATABASES")
        data = cur.fetchall()
        self.dbs[:] = [] # Slice the list to remove all existing elements.
        for row in data:
            self.dbs.append(row[0])
        return self.dbs
        
    def setDatabase(self, dbname):
        """ Set the active database to the User Selected Database """
	# 8/8/15 - Suzanne added try/except for dbname - function was originally
	# just self.db = dbname - this does not work as intended, program does not 
	# quit user receives "No DB Selected" error in menus
	try:
	     self.db = dbname
	except:
	     sys.exit("Error, please choose an existing database.")
		
    def createDatabase(self, dbname):
        """ Create a new Database """
        cur = self.conn.cursor()
        cur.execute("CREATE DATABASE " + dbname)
        
    def dropDatabase(self, dbname):
        """ Drop an existing Database """
        cur = self.conn.cursor()
        cur.execute("DROP DATABASE " + dbname)

    def listTables(self):
        """ List all Tables in the User Selected Database 
            return value is a list or tuple """
        if self.engine == None:
            raise ValueError('Not connected to server')
        '''cur = self.conn.cursor()
        cur.execute("USE " + self.db)
        cur.execute("SHOW TABLES ")
        data = cur.fetchall()'''
        metadata = MetaData()
        metadata.reflect(self.engine)
        self.tables[:] = [] # Slice the list to remove all existing elements.
        for t in metadata.sorted_tables:
            self.tables.append(t.name)
        return self.tables
    
    def setTable(self, tableName):
        """ Set the active table to the User Selected Table """
        # TODO:  Need to check if tableName really exists in the selected database before setting it.
        #       if does not exist throw exception.
        #       right now any string is selected as database - need to FIX this.
        self.table = tableName

    def createTable(self, table_params):
        """ Create a new Table in the User Selected Database """
        metadata = MetaData()
        table_name = table_params['table_name']
        columns = table_params['cols']
        table = Table(str(table_name), metadata,
                      *(Column(name, eval(data_type)) for name, data_type, auto, pkey in columns))
        metadata.create_all(self.engine)
        
    def removeTable(self, table_name):
        """ Remove Table from the User Selected Database 
            table_name is of string type """
        metadata = MetaData()
        table = Table(table_name, metadata, autoload=True, autoload_with=self.engine)
        table.drop(self.engine)
    
    def addColumn(self, column_info):
        """ Add a column to User Selected Table 
            column_info structure needs to be defined  """
        pass

    def deleteColumn(self, column_info):
        """ Delete a column from the User Selected Table 
            column_info structure needs to be defined  """
        pass
        
    def addRow(self, row_info):
        """ Add a row to the User Selected Table 
            row_info structure needs to be defined """
        pass
        
    def deleteRow(self, row_info):
        """ Delete a row to the User Selected Table 
            row_info structure needs to be defined  """
        pass
    
    def showAll(self):
        """ Show all the records of the User Selected Table """
        pass
        
    def filter(self, filter_params):
        """ Filter records of the User Selected Table based on filter_params 
            filter_params structure needs to be defined  """
        pass
        
    def exec_sql(self, sql):
        # TODO: Need to execute SQL statement.
        #       Results format should be list of lists
        #       [[col1_name, col2_name,...,coln_name], [val1, val2, ...., valn],[...], ....,[...]]
        pass
        
# Create an instance of DbServer
dbsrv = DbServer()

# =======  Home Screen Callback =======
def cb_Home(scr, msg):
    scr.clear()
    drawStatus(scr, msg)
    drawMenu(scr, main_menu)
    #TODO:  Enter the data that has to be displayed on the home screen as strings in the following tuple.
    data = ("",
        "  Welcome to dbadmin", "", 
        "  Enter the letter of the Menu Item that is shown in Upper Case",
        "  ***  First Login to access Databases ***")
    drawData(scr,data)

# =======  User Login Callback=======
class dbLoginForm(npyscreen.Popup):
    def create(self):
        self.dbHost = self.add(npyscreen.TitleText, name='Host Name: ')
        self.dbName = self.add(npyscreen.TitleText, name='User Name: ')
        self.dbPass = self.add(npyscreen.TitleText, name='Password: ')

def dbLogin(screen, *args):
    F = dbLoginForm(name = "Login")
    F.edit()
    return (F.dbHost.value, F.dbName.value, F.dbPass.value)
                
def cb_Login(scr):
    global dbsrv
    login = npyscreen.wrapper_basic(dbLogin)
    scr.clear()
    curses.raw() 
    try:
        dbsrv.connect(login)
        drawStatus(scr, "DB server connected")
        drawData(scr, ("", "DB server connected"))
    except:
        drawStatus(scr, "Login Failed")
        drawData(scr, ("", "Login to DB Server failed"))
    drawMenu(scr, main_menu)

#=======  Databases Menu =======
def cb_Databases(scr):
    global dbsrv
    drawStatus(scr, "")
    try:
        drawData(scr, dbsrv.listDb())
    except:
        drawStatus(scr, "Error: No DB Server Connection")
    showSubMenu(scr, "Databases")

class selectDatabaseForm(npyscreen.Popup):
    def create(self):
        self.database = self.add(npyscreen.TitleText, name='DB Name: ')
        
def selectDatabase(screen, *args):
    F = selectDatabaseForm(name = "Select Database")
    F.edit()
    return F.database.value
    
def cb_Databases_s(scr):
    global dbsrv, sub_menu
    dbName = npyscreen.wrapper_basic(selectDatabase)
    scr.clear()
    curses.raw()
    try:
        dbsrv.setDatabase(dbName)
        drawStatus(scr, "Database set to " + dbName)
        drawData(scr, ("",  "  "+dbName+" Selected"))
    except:
        drawStatus(scr, "Select Database Failed")
        drawData(scr, ("", "Selecting Database failed"))
    drawMenu(scr, sub_menu["Databases"])

# TODO:  Need to combine all similar dialog screens, work in progress.
def createDatabase(screen, *args):
    F = selectDatabaseForm(name = "Create Database")
    F.edit()
    return F.database.value
    
def cb_Databases_c(scr):
    global dbsrv
    dbName = npyscreen.wrapper_basic(createDatabase)
    scr.clear()
    curses.raw()
    try:
        dbsrv.createDatabase(dbName)
        drawStatus(scr, dbName + "created")
        drawData(scr, ("",  "  "+dbName+" created"))
    except:
        drawStatus(scr, "Database Creation Failed")
        drawData(scr, ("", "Database Creation Failed"))
    drawMenu(scr, sub_menu["Databases"])

def removeDatabase(screen, *args):
    F = selectDatabaseForm(name = "Remove Database")
    F.edit()
    return F.database.value
    
def cb_Databases_r(scr):
    global dbsrv
    dbName = npyscreen.wrapper_basic(removeDatabase)
    scr.clear()
    curses.raw()
    try:
        dbsrv.dropDatabase(dbName)
        drawStatus(scr, dbName + "deleted")
        drawData(scr, ("",  "  "+dbName+" deleted"))
    except:
        drawStatus(scr, "Database Deletion Failed")
        drawData(scr, ("", "Database Deletion Failed"))
    drawMenu(scr, sub_menu["Databases"])
        
#=======  Tables Menu =======
def cb_Tables(scr):
    global dbsrv
    drawStatus(scr, "")
    try:
        drawData(scr, dbsrv.listTables())
    except:
        drawStatus(scr, "Error: No DB Selected")
    showSubMenu(scr, "Tables")

class selectTableForm(npyscreen.Popup):
    def create(self):
        self.database = self.add(npyscreen.TitleText, name='Table: ')
        
def selectTable(screen, *args):
    F = selectTableForm(name = "Select Table")
    F.edit()
    return F.database.value

def removeTable(screen, *args):
    F = selectTableForm(name = "Remove Table")
    F.edit()
    return F.database.value
    
def cb_Tables_s(scr):
    global dbsrv, sub_menu
    tableName = npyscreen.wrapper_basic(selectTable)
    scr.clear()
    curses.raw()
    try:
        dbsrv.setTable(tableName)
        drawStatus(scr, "Table set to " + tableName)
        drawData(scr, ("",  "  "+tableName+" Selected"))
    except:
        drawStatus(scr, "Select Table Failed")
        drawData(scr, ("", "Selecting Table failed"))
    drawMenu(scr, sub_menu["Tables"])
    
def cb_Tables_r(scr):
    global dbsrv, sub_menu
    tableName = npyscreen.wrapper_basic(removeTable)
    scr.clear()
    curses.raw()
    try:
        dbsrv.removeTable(tableName)
        drawStatus(scr, tableName + " Table removed ")
        drawData(scr, ("",  "  "+tableName+" removed"))
    except:
        drawStatus(scr, "Remove Table Failed")
        drawData(scr, ("", "Remove Table failed"))
    drawMenu(scr, sub_menu["Tables"])
    
class tableNameForm(npyscreen.Popup):
    def create(self):
        self.name = self.add(npyscreen.TitleText, name='TableName')
        self.num_cols = self.add(npyscreen.TitleText, name='NumCols')

class tableColForm(npyscreen.Popup):
    def create(self):
        self.colname = self.add(npyscreen.TitleText, name='ColName')
        self.coltype = self.add(npyscreen.TitleSelectOne, scroll_exit=True, max_height=3, name='ColType1', values = ['int', 'varchar', 'timestamp']) 
        self.size = self.add(npyscreen.TitleText, name='Size')
        self.ai = self.add(npyscreen.TitleMultiSelect, value = [], name="Params", values = ["Primary Key", "Auto Increment"], scroll_exit=True)       


'''Return Format: 
{table_name:<table name>,cols: [<col1>:[col_name, col_type, auto, pkey], <col2>...]}
'''
def createTable(*args):
    F = tableNameForm(name = "Create Table")
    F.edit()
    params = {}
    params['table_name'] = F.name.value
    num_cols = F.num_cols.value
    cols = []
    for i in range(int(num_cols)):
        auto = False
        pkey = False
        F = tableColForm(name = "Create Columns")
        F.edit()
        col = []
        col.append(F.colname.value)
        col_type = F.coltype.value
        print col_type
        if col_type[0] == 0:
            col_type = 'Integer'
        elif col_type[0] == 1:
            col_type = 'String'
        elif col_type[0] == 2:
            col_type = 'DateTime'
        col.append(col_type)
        ai = F.ai.value
        for each in ai:
            if each == 0:
                auto = True
            elif each == 1:
                pkey = True
        col.append(auto)
        col.append(pkey)
        cols.append(col)
    params['cols'] = cols
    print params #debugging
    return params

def cb_Tables_c(scr):
    global dbsrv
    table_params = npyscreen.wrapper_basic(createTable)
    scr.clear()
    curses.raw() 
    try:
        dbsrv.createTable(table_params)
        drawStatus(scr, table_params['table_name'] + "Created")
        drawData(scr, ("",  "  "+table_params['table_name']+" Created"))
    except:
        drawStatus(scr, "Create Table Failed")
        drawData(scr, ("", "Create Table Failed"))
    drawMenu(scr, sub_menu["Tables"])
    
#=======  dAta Menu =======
def cb_dAta(scr):
    global dbsrv
    drawStatus(scr, "")
    try:
        drawData(scr, ("", "Addrow:  Add a new row to the selected table", 
            "Delrow:  Delete an existing row from the selected table"))
    except:
        drawStatus(scr, "Error: No DB Server Connection")
    showSubMenu(scr, "dAta")
    
#=======  SQL Menu =======
class sqlForm(npyscreen.Popup):
    def create(self):
        self.sql= self.add(npyscreen.MultiLineEdit)               

def runSQL(*args):
    F = sqlForm(name = "SQL")
    F.edit()    
    return F.sql.value

def cb_SQL(scr):
    global dbsrv
    sql = npyscreen.wrapper_basic(runSQL)
    scr.clear()
    curses.raw() 
    try:
        sql_results = dbsrv.exec_sql(sql)
        drawStatus(scr, "")
        drawData(scr, sql_results)
    except:
        drawStatus(scr, "SQL Failed")
        drawData(scr, ("", "SQL failed"))
    drawMenu(scr, main_menu)
    
#=======  Help Menu =======
def cb_Help(scr):
    drawData(scr,("", "Enter Help Text here"))
    
# =======  Draw Operations =======
def drawStatus(scr, msg):
    global dbsrv
    scr.addstr(0, 0, empty_string)
    scr.addstr(0, 0, "*dbadmin* DB:" + dbsrv.db + "| Table:" + dbsrv.table + "| Status:" + msg)
	
def drawMenu(scr, menu):
    global line
    scr.addstr(1, 0, empty_string)
    scr.addstr(1, 0, menu)
    scr.addstr(2, 0, line)
    scr.addstr(3, 0, "Enter the letter of the Menu Item that is shown in Upper Case")
    scr.addstr(4, 0, "Press B to go back to main menu to access other menu options")
    scr.addstr(5, 0, empty_string)

    
def drawData(scr, data):
    for num in range(6,22):
        scr.addstr(num, 0, empty_string)
        
    i = 6
    for item in data:
        scr.addstr(i, 0, item)
        i = i + 1

def getInput(scr):
    scr.addch(0, 75, ' ')
    return scr.getch()

# =======  Sub Menu message loop  =======    
def showSubMenu(screen, menu_cmd):
    global char_map, sub_menu, sub_menu_items
    x = 'z'
    drawMenu(screen, sub_menu[menu_cmd])
    while x not in [ord('b'), ord('B')]:
        #screen.clear()
        drawMenu(screen, sub_menu[menu_cmd])
        x = getInput(screen)
        if x not in [ord('b'), ord('B')]:
            try:
                # HACK Alert: Did not find a way to convert ASCII char (represented as int) to str
                #   so using the char_map.  But, this reduces the extra logic for upper case and lower case.
                m = "cb_" + menu_cmd + "_" + char_map[x]
                eval(m)(screen) 
            except:
                drawStatus(screen, "!");
            
# =======  Main Menu message loop  =======
def main(scr, *args, **kwds):
    x = '0'
    msg = ""
    cb_Home(scr, "")
    while x not in [ord('q'), ord('Q')]:
        drawMenu(scr, main_menu)
        drawStatus(scr, msg)
        msg = ""
        x = getInput(scr)
        if x in [ord('d'), ord('D')]:
            cb_Databases(scr)
        elif x in [ord('t'), ord('T')]:
            cb_Tables(scr)
        elif x in [ord('a'), ord('A')]:
            cb_dAta(scr)
        elif x in [ord('s'), ord('S')]:
            cb_SQL(scr)
        elif x in [ord('l'), ord('L')]:
            cb_Login(scr)
        elif x in [ord('h'), ord('H')]:
            cb_Help(scr)
        elif x in [ord('q'), ord('Q')]:
            pass
        else:
            msg = "Error: Wrong Choice"
	
if __name__ == "__main__":
    curses.wrapper(main)
