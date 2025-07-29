from DE_Lib.DataBase import SQLite, Oracle, MsSql, MySql, Postgres, RedShift, Cache

# instanciando conexoes com banco de dados
cache = Cache.CACHE()
redshift = RedShift.REDSHIFT()
postgres = Postgres.POSTGRES()
mysql = MySql.MYSQL()
mssql = MsSql.MSSQL()
oracle = Oracle.ORACLE()
sqlite = SQLite.SQLITE()

class CONNECT:
    def __init__(self):
        self.__connection_valid = None
        self.__database_error = None
        self.__connection = None
        self.__nome_database = None
        self.__database_driver = None

    def setConectionDataBase(self, conn: dict):
        msg, result = None, True
        __valid, __error, __conn, __nomedatabase, __databasedriver = None, None, None, None, None
        try:
            if conn["database"].upper() == 'ORACLE':
                oracle.Connect(conn)
                self.CONNECTION_VALID = oracle.CONNECTION_VALID
                self.DATABASE_ERROR = oracle.DATABASE_ERROR
                self.CONNECTION = oracle.CONNECTION
                self.NOME_DATABASE = oracle.NOME_DATABASE
                self.DATABASE_DRIVER = oracle.DRIVER_CONEXAO
                self.DATABASE = oracle.DATABASE
            elif conn["database"].upper() == 'SQLITE':
                sqlite.Connect(conn)
                self.CONNECTION_VALID = sqlite.CONNECTION_VALID
                self.DATABASE_ERROR = sqlite.DATABASE_ERROR
                self.CONNECTION = sqlite.CONNECTION
                self.NOME_DATABASE = sqlite.NOME_DATABASE
                self.DATABASE_DRIVER = sqlite.DRIVER_CONEXAO
                self.DATABASE = sqlite.DATABASE
            elif conn["database"].upper() == 'MSSQL':
                self.CONNECTIONection = mssql.Connect(conn)
                self.CONNECTION_VALID = mssql.CONNECTION_VALID
                self.DATABASE_ERROR = mssql.DATABASE_ERROR
                self.CONNECTION = mssql.CONNECTION
                self.NOME_DATABASE = mssql.NOME_DATABASE
                self.DATABASE_DRIVER = mssql.DRIVER_CONEXAO
            elif conn["database"].upper() == 'MYSQL':
                mysql.Connect(conn)
                self.CONNECTION_VALID = mysql.CONNECTION_VALID
                self.DATABASE_ERROR = mysql.DATABASE_ERROR
                self.CONNECTION = mysql.CONNECTION
                self.NOME_DATABASE = mysql.NOME_DATABASE
                self.DATABASE_DRIVER = mysql.DRIVER_LIBRARY
                self.DATABASE = mysql.DATABASE
            elif conn["database"].upper() == 'POSTGRES':
                self.CONNECTIONection = postgres.Connect(conn)
                self.CONNECTION_VALID = postgres.CONNECTION_VALID
                self.DATABASE_ERROR = postgres.DATABASE_ERROR
                self.CONNECTION = postgres.CONNECTION
                self.NOME_DATABASE = postgres.NOME_DATABASE
                self.DATABASE_DRIVER = postgres.DATABASE_DRIVER
            elif conn["database"].upper() == 'CACHE':
                #self.CONNECTIONection = db.CACHE(conn=conn)
                # self.CONNECTION_VALID = oracle.CONNECTION_VALID
                # self.DATABASE_ERROR = oracle.DATABASE_ERROR
                # self.CONNECTION = oracle.CONNECTION
                # self.NOME_DATABASE = oracle.NOME_DATABASE
                # self.DATABASE_DRIVER = oracle.DATABASE_DRIVER
                #__connection = cache.
                ...
            elif conn["database"].upper() == 'REDSHIFT':
                #__connection = .REDSHIFT(conn=conn)
                # self.CONNECTION_VALID = oracle.CONNECTION_VALID
                # self.DATABASE_ERROR = oracle.DATABASE_ERROR
                # __conn = oracle.CONNECTION
                # self.NOME_DATABASE = oracle.NOME_DATABASE
                # self.DATABASE_DRIVER = oracle.DATABASE_DRIVER
                ...
            else:
                ...
        except Exception as error:
            msg = error
            result = msg
        finally:
            # self.CONNECTION_VALID = __valid
            # self.DATABASE_ERROR = __error
            # self.CONNECTION = __connection
            # self.NOME_DATABASE = __nomedatabase
            # self.DATABASE_DRIVER = __databasedriver
            # self.DATABASE = __database
            return result

    # region Property´s
    @property
    def CONNECTION_VALID(self):
        return self.__connection_valid

    @CONNECTION_VALID.setter
    def CONNECTION_VALID(self, value):
        self.__connection_valid = value

    @property
    def CONNECTION(self):
        return self.__connection

    @CONNECTION.setter
    def CONNECTION(self, value):
        self.__connection = value

    @property
    def DATABASE_ERROR(self):
        return self.__database_error

    @DATABASE_ERROR.setter
    def DATABASE_ERROR(self, value):
        self.__database_error = value

    @property
    def NOME_DATABASE(self):
        return self.__nome_database

    @NOME_DATABASE.setter
    def NOME_DATABASE(self, value):
        self.__nome_database = value

    @property
    def DATABASE_DRIVER(self):
        return self.__database_driver

    @DATABASE_DRIVER.setter
    def DATABASE_DRIVER(self, value):
        self.__database_driver = value

    @property
    def DATABASE(self):
        return self.__database

    @DATABASE.setter
    def DATABASE(self, value):
        self.__database = value
    # endregion