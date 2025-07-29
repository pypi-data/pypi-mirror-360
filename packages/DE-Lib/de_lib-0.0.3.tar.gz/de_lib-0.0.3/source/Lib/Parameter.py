import json
import datetime as dt
import os
from sqlalchemy  import text

from DE_Lib.Utils.Cipher import Fernet
from DE_Lib.DataBase import SQLite, Oracle
from DE_Lib.Utils import Generic, DateUtils, Sql

from source.Lib import Etl, Connect

oracle = Oracle.ORACLE()
sqlite = SQLite.SQLITE()
#
fernet = Fernet.FERNET()
#
gen = Generic.GENERIC()
dtu = DateUtils.DATEUTILS()
sql = Sql.SQL()
#
etl = Etl.ETL()
con = Connect.CONNECT()

class PARAMETER:
    def __init__(self):
        self.__connection_valid = None
        self.__database_error = None
        self.__connection = None
        self.__nome_database = None
        self.__database_driver = None
        self.__token_parameters = None
        self.__error = None


    # ---------------------------------
    def getParameter(self, cols:list, cols_where:list, cols_value:list, orderby:bool=True):
        msg, result = None, True
        try:
            __owner = "BI_DAX."
            __table = "DAX_PARAMETROS"
            __where = None
            __and = ""
            #
            cols_select = ','.join(cols)

            if (len(cols_where) != len(cols_value)) or len(cols_where)==0:
                raise Exception("Numero de colunas <where> esta diferente do numero de colunas <value>")

            for i, __cols in enumerate(cols_value):
                if isinstance(__cols, list):
                    if not __where:
                        if isinstance(__cols[0], str):
                            __where = f""" where {cols_where[i]} in  ('{"','".join(__cols)}') """
                        elif isinstance(__cols[0], int):
                            __where = f""" where {cols_where[i]} in  ({",".join(list(map(str,__cols)))}) """
                    else:
                        if isinstance(__cols[0], str):
                            __and = f"""\n   and {cols_where[i]} in  ('{"','".join(__cols)}') """
                        elif isinstance(__cols[0], int):
                            __and = f"""\n   and {cols_where[i]} in  ({",".join(list(map(str, __cols)))}) """
                elif isinstance(__cols, str):
                    if not __where:
                        __where = f"""where {cols_where[i]} = '{__cols}'"""
                    else:
                        __and = f"""\n   and {cols_where[i]} = '{__cols}'"""
                elif isinstance(__cols, int):
                    if not __where:
                        __where = f"""where {cols_where[i]} = {str(__cols)}"""
                    else:
                        __and = f"""\n   and {cols_where[i]} = {str(__cols)}"""

                __where = __where + __and
            stmt = f"""
                    Select {cols_select}
                      from {__owner}{__table}
                     {__where} 
                     {gen.iif(orderby, "order by num_ordem", "")}
                    """
            result = etl.getQryExecute(qry=stmt, con=self.CONNECTION, driver=self.DATABASE_DRIVER)
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result


    # ---------------------------------
    def getParameterOld(self,cols: list, cols_where: list, cols_value:list):
        msg, result = None, True
        try:
            __owner = ""
            __table = "DAX_PARAMETROS"
            __signal = gen.iif(len(cols_where) > 1, value_true="=", value_false="in")
            __cols = ','.join(cols)
            __where = f"""{gen.iif(__signal=="=", "", "(")}{",".join(cols_where)}{gen.iif(__signal=="=", "", ")")}"""
            __value_list = f"""{gen.iif(__signal=="=", "'", "('")}{"','".join(cols_value)}{gen.iif(__signal=="=", "'", "')")}"""
            stmt = f"""
                    Select {__cols}
                      from {__owner}{__table}
                     where {__where} {__signal} {__value_list} 
                     order by num_ordem
                    """
            result = etl.getQryExecute(qry=stmt, con=self.CONNECTION, driver=os.getenv("driver"))
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    # ---------------------------------
    def setParametersListToDict(self, parlist: list) -> dict:
        result, msg = None, None
        try:
            par = {}
            for index, row in enumerate(parlist):  # range(len(parlist)):
                __datatype = row["DES_DATATYPE"].upper()
                __flg_encrypt = row["FLG_ENCRYPT"].upper()
                __flg_ativo = gen.iif(row["FLG_ATIVO"] == "", "S", row["FLG_ATIVO"].upper())
                if __flg_ativo == "S":
                    # if row["TIPO_PARAMETRO"] == "Objeto ETL":
                    #     par["hash"] = row["HASH"]
                    # Analisando se o parametro esta criptografado
                    if __flg_encrypt == "S":
                        #row["VAL_PARAMETRO"] = b64.CRYPTOGRAPHY(str(row["VAL_PARAMETRO"]).encode(), "D", self.TOKEN)
                        row["VAL_PARAMETRO"] = fernet.decrypt(row["VAL_PARAMETRO"])
                    # Analisando o datatype
                    if __datatype != 'NONE':
                        if __datatype in ('STRING'):
                            row["VAL_PARAMETRO"] = str(row["VAL_PARAMETRO"])
                            # if row["TIPO_PARAMETRO"].upper() == "QUERY":
                            #     par[row["NOM_VARIAVEL"]] = str(row["VAL_PARAMETRO"])
                        elif __datatype in ("INT", "INTEGER"):
                            row["VAL_PARAMETRO"] = int(str(row["VAL_PARAMETRO"]))
                        elif __datatype in ("NUMERIC", "FLOAT", "DOUBLE", "REAL"):
                            row["VAL_PARAMETRO"] = float(str(row["VAL_PARAMETRO"]))
                        elif __datatype in ("DATE", "DATETIME", "TIMESTAMP"):
                            row["VAL_PARAMETRO"] = dt.datetime.strptime(str(row["VAL_PARAMETRO"]), dtu.MILLISECONDS_FORMAT_PYTHON)
                        elif __datatype == "TIME":
                            row["VAL_PARAMETRO"] = dt.datetime.strptime(str(row["VAL_PARAMETRO"]), dtu.TIME_FORMAT_PYTHON)
                        elif __datatype == "LIST/RECORD":
                            # z = str(row["VAL_PARAMETRO"]).split(",")
                            if row["TIPO_PARAMETRO"].upper() == "OBJETO ETL":
                                par[row["NOM_VARIAVEL"]] = json.loads(str(row["VAL_PARAMETRO"]))
                                par[row["NOM_VARIAVEL"]]["HASH"] = row["HASH"]
                        elif __datatype == "RECORD":
                            par[row["NOM_VARIAVEL"]] = json.loads(str(row["VAL_PARAMETRO"]))
                            par[row["NOM_VARIAVEL"]]["HASH"] = row["HASH"]

            result = par
        except Exception as error:
            result = error.args[0]
            self.setError(result)
        finally:
            return result

    # ---------------------------------
    def setInit(self):
        msg, result = None, None
        try:
            # obtendo o token da tabela de parametros
            fernet.setToken(os.getenv("token"))
            tkp = os.getenv("token_parametros")
            __strToken = fernet.decrypt(tkp)
            __dictToken = json.loads(__strToken)
            __dictToken["password"] = fernet.decrypt(__dictToken["password"])

            # efetuando conexao com o banco de dados da tabela de parametros
            con.setConectionDataBase(__dictToken)
            self.__connection_valid = con.CONNECTION_VALID
            self.__database_error = con.DATABASE_ERROR
            self.__connection = con.CONNECTION
            self.__nome_database = con.NOME_DATABASE
            self.__database_driver = con.DATABASE_DRIVER
            # Consistindo se a conexao com a base de parametros foi bem sucedida
            if not self.CONNECTION_VALID:
                result = self.DATABASE_ERROR
                raise Exception(result)
            else:
                #msg = "Conexao com a base de parametros foi efetuada com sucesso!"
                msg = ""
                result = msg
        except Exception as error:
            msg = error.args[0]
            result = msg
        finally:
            return result

    # region Metodos diversos locais
    # ---------------------------------
    def setError(self, value):
        msg, result = None, True
        try:
            self.__error = gen.nvl(value, True)
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result
    # @endregion

    # ---------------------------------
    def setSaveParameters(self, par: dict):
        msg, result, conn, cur = None, True, None, None
        try:
            __owner = "BI_DAX."
            __table = "DAX_PARAMETROS"
            __values = [ {"value": "", "hash": par["Objetos_Candidatos"]["HASH"]},
                         {"value": "", "hash": par["Resumo"]["HASH"]}
                         ]
            __values[0]["value"] = json.dumps(par["Objetos_Candidatos"], indent=4)
            __values[1]["value"] = json.dumps(par["Resumo"], indent=4)
            #del __values[0]["hash"]
            #del __values[1]["hash"]

            stmt = f"""
                    update {__owner}{__table}
                       set val_parametro = :value
                     where hash = :hash
                    """
            conn = self.CONNECTION
            # if self..DataBaseConnection["database"].upper() == "MYSQL":
            #     conn.execute(text(stmt, __values))
            # cur = conn.cursor()
            # if con.DATABASE_DRIVER.upper() == "SQLALCHEMY":
            #     cur.execute(text(stmt), __values)
            #else:
            cur = conn.cursor()
            cur.executemany(stmt, __values)
            conn.commit()
            if cur:
                cur.close()
            if conn is None:
                conn.close()
        except Exception as error:
            if cur:
                cur.close()
            if conn is None:
                conn.close()
            msg = error
            result = msg
        finally:
            return result

    # ---------------------------------
    def getEmailProcesso(self, hash_processo: str):
        msg, result = None, True
        try:
            __owner = "bi_dax."
            stmt = f"""
                    select e.EMAIL
                      from {__owner}email e
                      join {__owner}email_processo ep
                        on ep.hash_email = e.hash
                     where e.flg_ativo = 'S'
                       and ep.flg_ativo = 'S'
                       and ep.dat_fim_vigencia is null
                       and e.dat_fim_vigencia is null
                       and ep.hash_processo = '{hash_processo}'
                    """
            result = etl.getQryExecute(qry=stmt, con=self.CONNECTION, driver=os.getenv("driver"))
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    # region Property´s
    @property
    def CONNECTION_VALID(self):
        return self.__connection_valid

    @property
    def CONNECTION(self):
        return self.__connection

    @property
    def DATABASE_ERROR(self):
        return self.__database_error

    @property
    def NOME_DATABASE(self):
        return self.__nome_database

    @property
    def ERROR_PARAMETER(self):
        return self.__error

    @property
    def DATABASE_DRIVER(self):
        return self.__database_driver

    # endregion