"""
Objeto ...: ETL
data .....: 22/02/2025
autor ....: almir j gomes - almir.jg@hotmail.com
descricao : Biblioteca GENERICA de colaboracao. Classes abstratas
"""
import os
import datetime as dt
from dateutil import relativedelta as rd
import re
from dotenv import load_dotenv

from DE_Lib.Utils.Cipher import Base64
from DE_Lib.Utils import Generic, DateUtils, Sql, System
from DE_Lib.Log import Log, Level
from DE_Lib.DataBase import Metadata
#from DE_Lib.Files import Zip

# instanciando classes diversas
b64 = Base64.B64_Cipher()
gen = Generic.GENERIC()
dtu = DateUtils.DATEUTILS()
sql = Sql.SQL()
so = System.SO()
md = Metadata.METADATA()
log = Log.LOG()
lvl = Level.LEVEL()
#zip = Zip.ZIP()

class ETL:
    def __init__(self):
        ...

    #region Metodos internos para montar select
    def getTableSelect(self, column_list: list, alias: str = "x", quoted: str = ""):
        msg, result = None, None
        try:
            result = "select " + alias + '.' + quoted + eval(f"""'{quoted},{alias}.{quoted}'.join(column_list)""") + quoted
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    def getTableFrom(self, owner: str, table: str, alias: str = "x", quoted: str = ""):
        msg, result = None, None
        try:
            result = f"""From {quoted}{owner}{quoted}.{quoted}{table}{quoted} {alias}"""
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    def getTableWhere(self, origem: dict, delta: dict, filters: dict, conn, qry:str=None):
        """
        Monta a clausula WHERE da query
        :param origem:
        :param delta:
        :param filters:
        :param conn:
        :param qry:
        :return:
        """
        msg, result = None, None
        try:
            __startValue = delta["start_value"]
            __endValue = delta["end_value"]
            __filters = filters
            #__col = f"""{origem["alias"]}.{origem["quoted"]}{delta["coluna"]}{origem["quoted"]}"""
            __where = None
            __f = []
            if __startValue is not None:
                if __endValue is not None:
                    __database = conn.DATABASE
                    if delta["type"].upper() == "DATETIME":
                        __where = f""" {origem["alias"]}.{origem["quoted"]}{delta["coluna"]}{origem["quoted"]} 
                        between {self.DataBaseConvertDateTime(conn.DATABASE, __startValue, delta["type"])}
                        and {self.DataBaseConvertDateTime(conn.DATABASE, __endValue, delta["type"])}"""
                    if delta["type"].upper() == "DATE":
                        __where = f""" {origem["alias"]}.{origem["quoted"]}{delta["coluna"]}{origem["quoted"]} 
                                                between {self.DataBaseConvertDateTime(conn.DATABASE, __startValue.date(), delta["type"])}
                                                and {self.DataBaseConvertDateTime(conn.DATABASE, __endValue.date(), delta["type"])}"""
                    elif delta["type"].upper() == "NUMERIC":
                        __where = f""" {origem["alias"]}.{origem["quoted"]}{delta["coluna"]}{origem["quoted"]} 
                                                between {__startValue}
                                                and {__endValue}"""

            if __where is not None:
                __f.append(" ")
            for f in filters:
                if filters[f]["flg_ativo"] == "S":
                    if filters[f]["datatype"].upper() == "STRING":
                        __f.append(f"""{origem["alias"]}.{origem["quoted"]}{f}{origem["quoted"]} = '{filters[f]["valor"]}'""")
                    elif filters[f]["datatype"].upper() == 'DATETIME':
                        __f.append(f"""{origem["alias"]}.{origem["quoted"]}{f}{origem["quoted"]} = '{self.DataBaseConvertDateTime(conn.NOME_DATABASE, filters[f]["valor"], delta["type"])}'""")
                    elif filters[f]["datatype"].upper() == 'DATE':
                        __value = filters[f]["valor"]
                        __f.append(f"""{origem["alias"]}.{origem["quoted"]}{f}{origem["quoted"]} = {self.DataBaseConvertDateTime(conn.NOME_DATABASE, filters[f]["valor"], delta["type"])}""")
                    elif filters[f]["datatype"].upper() == 'LIST':
                        __value = filters[f]["valor"].replace(" ","")
                        __v = __value.split(",")
                        __v1 = f"{f} in ('"+"','".join(__v)+"')"
                        __f.append( __v1)
                    else:
                        #__f.append(f"""{origem["alias"]}.{origem["quoted"]}{f}{origem["quoted"]} = '{filters[f]["valor"]}'""")
                        __f.append(f"""{origem["alias"]}.{origem["quoted"]}{f}{origem["quoted"]} = {filters[f]["valor"]}""")

            __y = ' and '.join(__f)
            #__y = __f
            result = gen.nvl(__where, "") + gen.nvl(__y, "")
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result
    #endregion

    #region Metodos diversos locais
    def setError(self, value):
        msg, result = None, None
        try:
            self.__error = gen.nvl(value, True)
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result
    #@endregion

    #region - Espaco para funcionalidades que devem ir par alguma biblioteca
    # ---------------------------------
    def getColumnsCursor(self, cur):
        msg, result = None, True
        try:
            result = [coluna[0] for coluna in cur.description]
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    # ---------------------------------
    def close_cursor(self, cur):
        msg, result = None, True
        try:
            if cur is not None:
                cur.close()
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    def DataBaseConvertDateTime(self, database, column, datatype: str = dtu.MILLISECONDS_FORMAT_SQL):
        msg, result = None, None
        try:
            # __lista = ["%H","%M","%S", "%F"]
            # if not ([item for item in __lista if item in formato]):
            #     __mask = dtu.DATE_FORMAT_SQL
            #     __date = "DATE"
            # else:
            #     __mask = dtu.DATETIME_FORMAT_SQL
            #     __date = "DATETIME"
            #     # formato DATETIME
            if database.upper() in ("CACHE", "POSTGRES", "ORACLE", "DB2", "VERTICA"):
                if datatype.upper() == 'DATETIME':
                    result = f"""to_timestamp('{column}', '{dtu.MILLISECONDS_FORMAT_SQL}')"""
                else:
                    result = f"""to_date('{column}', '{dtu.DATE_FORMAT_SQL}')"""
            elif database.upper() == "MYSQL":
                if datatype.upper() == "DATETIME":
                    result = f"""Str_To_Date('{column}', '{dtu.MILLISECONDS_FORMAT_SQL}')"""
                else:
                    result = f"""Str_To_Date('{column}', '{dtu.DATE_FORMAT_SQL}')"""
            elif database.upper() == "MSSQL":
                if datatype.upper() == "DATETIME":
                    result = f"""Cast('{column}', '{dtu.MILLISECONDS_FORMAT_SQL}'as date)"""
                else:
                    result = f"""Cast('{column}', '{dtu.DATE_FORMAT_SQL}'as date)"""
            elif database.upper() == "SNOWFLAKE":
                result = f"""to_timestamp('{column}')"""
            else:
                result = f"""to_date('{column}', '{dtu.DATETIME_FORMAT_SQL}')"""
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    def getQueryExtract(self, obj, name, conn, qry:str=None):  # df, origem, delta, filters, conn):
        msg, result = None, True
        try:
            __origem = obj["Objetos_Candidatos"][name]["origem"]
            __estrategia = obj["Objetos_Candidatos"][name]["estrategia"]
            __filters = obj["Objetos_Candidatos"][name]["filters"]
            # __destino = obj["Objetos_Candidatos"][name]["destino"]
            __delta = obj["Objetos_Candidatos"][name]["estrategia"]["delta"]
            # -------
            __origem["quoted"] = gen.nvl(__origem["quoted"], "")
            __origem["alias"] = gen.nvl(__origem["alias"], "x")
            # -------
            if __origem["tipo_objeto"].upper() == "TABLE":
                # Definindo as colunas
                __md = md.getMetadados(table=__origem["name"], owner=__origem["schema"], con=conn.CONNECTION, driver=conn.DATABASE_DRIVER)
                #__md = conn.getMetadados(__origem["name"], __origem["schema"], conn.CONNECTION)
                __select = self.getTableSelect(column_list=__md["COLUMN_NAME"].tolist(), alias=__origem["alias"],
                                               quoted=__origem["quoted"])
                __from = self.getTableFrom(owner=__md["OWNER"].unique()[0], table=__md["TABLE_NAME"].unique()[0],
                                           alias=__origem["alias"], quoted=__origem["quoted"])

                # falta tratar as intrucoes do WHERE
                # --------------------------------------------------------------
                query = f"""{__select}\n{__from}"""
                new_where = self.getTableWhere(origem=__origem, delta=__delta, filters=__filters, conn=conn)
                result = sql.setQueryWhere(query, new_where)

                #__where = self.getTableWhere(origem=__origem, delta=__delta, filters=__filters, conn=conn)
                #result = f"""{__select}\n{__from}\n{__where}"""
            else:

                new_where = self.getTableWhere(origem=__origem, delta=__delta, filters=__filters, conn=conn)
                if not isinstance(qry, str):
                    qry = str(qry)
                result = sql.setQueryWhere(qry, new_where)

                #result = f"""{qry}\n{__where}"""

        except Exception as error:
            msg = error
            result = msg
            self.setError(result)
        finally:
            return result

    def getQryExecute(self, qry: str, con, driver: str ="SQLALCHEMY") -> list:
        msg, result, cur = None, None, None
        try:
            # if driver.upper() == "SQLALCHEMY":
            #     cur = con.connection.cursor()
            # else:
            cur = con.cursor()
            cur.execute(qry)
            result = sql.CursorToDict(cursor=cur)
            cur.close()
        except Exception as error:
            cur.close()
            result = error.args[0]
        finally:
            return result

    def getDateFormat(self, datatype):
        msg, result = None, None
        try:
            if datatype.upper() == "DATE":
                __mask = dtu.DATE_FORMAT_PYTHON
                __td = dt.timedelta(days=1)
            elif datatype.upper() == "TIME":
                __mask = dtu.TIME_FORMAT_PYTHON
                __td = dt.timedelta(microseconds=1)
            elif datatype.upper() == "DATETIME":
                __mask = dtu.MILLISECONDS_FORMAT_PYTHON
                __td = dt.timedelta(microseconds=1)
            result = [__mask, __td]
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    def getRangeDateNew(self, delta):
        msg, result = None, None
        try:
            __rd = dtu.DATE_FORMAT_PYTHON
            if delta["type"] == "DATE":
                __rd = dt.timedelta(days=1)
            elif delta["type"] == "DATETIME":
                __rd = dt.timedelta(microseconds=1)
            elif delta["type"] == "TIME":
                __rd = dt.timedelta(microseconds=1)
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    def getRangeDate(self, delta):
        msg, result, dateFormat = None, True, None
        try:
            dateFormat = self.getDateFormat(delta["type"])
            # if delta["type"].upper() == "DATE":
            #     dateFormat = dtu.DATE_FORMAT_PYTHON
            # elif delta["type"].upper() == "TIME":
            #     dateFormat = dtu.TIME_FORMAT_PYTHON
            # elif delta["type"].upper() == "DATETIME":
            #     dateFormat = dtu.MILLISECONDS_FORMAT_PYTHON
            __now = dt.datetime.now()
            __inc = gen.is_valid_type(value=delta["incremento"], type="INT", default_value=1)
            # Consistindo o scopo
            if delta["scopo"].upper() in ("ANO", "ANUAL", "YEAR", "A"):
                if not delta["end_value"]:
                    __lano = __now - rd.relativedelta(years=__inc)
                    delta["start_value"] = dtu.getPrimeiroDiaAno(__lano)
                    delta["end_value"] = delta["start_value"] + rd.relativedelta(years=__inc) - dt.timedelta(
                        microseconds=1)
                else:
                    __lano = dt.datetime.strptime(delta["end_value"], dateFormat[0]) + dateFormat[1]
                    delta["start_value"] = __lano
                    delta["end_value"] = delta["start_value"] + rd.relativedelta(years=__inc) - dateFormat[1]
            elif delta["scopo"].upper() in ("MES", "MENSAL", "MONTH", "M"):
                if not delta["end_value"]:
                    __lmes = __now - rd.relativedelta(months=__inc)
                    delta["start_value"] = dtu.getPrimeiroDiaMes(__lmes)
                    delta["end_value"] = dtu.getUltimoDiaMes(__lmes) + rd.relativedelta(
                        months=__inc - 1) - dateFormat[1]
                else:
                    __lmes = dt.datetime.strptime(delta["end_value"], dateFormat[0]) + dateFormat[1]
                    delta["start_value"] = __lmes
                    delta["end_value"] = delta["start_value"] + rd.relativedelta(months=__inc) - dateFormat[1]
            elif delta["scopo"].upper() in("DAY", "DIA", "DIARIO", "D"):
                if not delta["end_value"]:
                    __ldia = __now - dt.timedelta(days=__inc)
                    delta["start_value"] = dtu.getPrimeiraHoraDia(__ldia)
                    delta["end_value"] = dtu.getUltimaHoraDia(__ldia) + dt.timedelta(days=__inc - 1) - dateFormat[1]
                else:
                    __ldia = dt.datetime.strptime(delta["end_value"], dateFormat[0]) + dateFormat[1]
                    delta["start_value"] = __ldia
                    delta["end_value"] = delta["start_value"] + dt.timedelta(days=__inc) - dateFormat[1]
            elif delta["scopo"].upper() in ("HORA", 'HOUR",' "H", "HR"):
                if not delta["end_value"]:
                    __lhora = __now - dt.timedelta(hours=__inc)
                    delta["start_value"] = dtu.getPrimeiroMinutoHora(__lhora)
                    delta["end_value"] = delta["start_value"] + dt.timedelta(hours=__inc) - dateFormat[1]
                else:
                    __lhora = dt.datetime.strptime(delta["end_value"], dateFormat[0]) + dateFormat[1]
                    delta["start_value"] = __lhora
                    delta["end_value"] = delta["start_value"] + dt.timedelta(hours=__inc) - dateFormat[1]
            elif delta["scopo"].upper() in ("MINUTO", "MINUTE", "MM", "MIN"):
                if not delta["end_value"]:
                    __lmin = __now - dt.timedelta(minutes=__inc)
                    delta["start_value"] = dtu.getPrimeiroSegundoMinuto(__lmin)
                    delta["end_value"] = delta["start_value"] + dt.timedelta(minutes=__inc) - dateFormat[1]
                else:
                    __lmin = dt.datetime.strptime(delta["end_value"], dateFormat[0]) + dateFormat[1]
                    delta["start_value"] = __lmin
                    delta["end_value"] = delta["start_value"] + dt.timedelta(minutes=__inc) - dateFormat[1]

            if delta["end_value"] >= __now:
                __lmin = __now - dt.timedelta(minutes=1)
                delta["end_value"] = dt.datetime.strptime((dtu.getUltimoSegundoMinuto(__lmin) + dt.timedelta(microseconds=999999)).strftime(dateFormat[0]), dateFormat[0])

            result = [delta["start_value"], delta["end_value"], delta["scopo"]]

        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    def getRangeDate_old(self, delta):
        msg, result = None, None
        try:
            __scp = gen.nvl(delta["scopo"], "D")
            __inc = gen.is_valid_type(value=delta["incremento"], type="INT", default_value=1)
            __start = delta["start_value"]
            __end = delta["end_value"]
            __now = dt.datetime.now()

            # if delta["type"].upper() == "DATE":
            #     __start = dt.datetime.strptime(__end, dtu.DATE_FORMAT_PYTHON) + dt.timedelta(days=1)
            # elif delta["type"].upper() == "DATETIME":
            #     __start = dt.datetime.strptime(__end, dtu.MILLISECONDS_FORMAT_PYTHON) + dt.timedelta(microseconds=1)

            if __end is not None:
                if delta["type"].upper() == "DATETIME":
                    __start = dt.datetime.strptime(__end, dtu.DATE_FORMAT_PYTHON) + dt.timedelta(days=1)
                    __end = dt.datetime(year=__start.year, month=__start.month, day=__start.day, hour=23, minute=59, second=59, microsecond=999999)
                elif delta["type"].upper() == "DATE":
                    __end = dt.date(year=__start.year, month=__start.month, day=__start.day)
            else:
                if delta["type"].upper() == "DATE":
                    __start = dt.date(year=__now.year, month=__now.month, day=__now.day) + dt.timedelta(days=1)
                    __end = dt.date(year=__start.year, month=__start.month, day=__start.day) + dt.timedelta(days=1)
                elif delta["type"].upper() == "DATETIME":
                    __start = dt.datetime(year=__now.year, month=__now.month, day=__now.day, hour=0, minute=0, second=0, microsecond=0) - dt.timedelta(days=1)
                    __end = dt.datetime(year=__start.year, month=__start.month, day=__start.day, hour=23, minute=59, second=59, microsecond=999999) - dt.timedelta(days=1)

            if __scp == "A":
                __end = __start + rd.relativedelta.relativedelta(years=__inc)
            elif __scp == "M":
                __end = __start + rd.relativedelta.relativedelta(months=__inc)
            elif __scp == "D":
                __end = __start + dt.timedelta(days=__inc)
            elif __scp == "H":
                __end = __start + dt.timedelta(hours=__inc) - dt.timedelta(microseconds=1)
            else:
                __end = __start + dt.timedelta(days=__inc)

            if __end >= __now:
                __end = __now - dt.timedelta(seconds=1)

            result = __start, __end, __scp
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    def getNumericRangeValue(self, delta) -> list:
        msg, result = None, None
        try:
            __initial = delta["start_value"]
            __final = delta["end_value"]
            if __initial is None:
                __initial = 0
            else:
                if __final is None:
                    __final = int(__initial)
                else:
                    __initial = int(__final)
            if delta["incremento"] is None:
                __final = __initial + 1
            else:
                __final = __initial + int(delta["incremento"])
            result = [__initial, __final, None]
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    # ---------------------------------
    def getPathFilesRoot(self, path_base: str, platform: str, path_file: str):
        msg, result = None, True
        try:

            if "WINDOWS" in platform.upper():
                __base = "c:\\"
            else:
                __base = "\\"

            __root = __base
            for p in path_base.split("/"):
                __root = os.path.join(__root, p)

            result = os.path.join(__root, path_file)

        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    # ---------------------------------
    def setFileName(self, file: dict, resumo: dict, paths: dict, args: dict):
        msg, result = None, True
        try:

            # ----------------------------
            __root = self.getPathFilesRoot(paths["path_base"], so.OSINFO["so_platform"], paths[file["local_destino"]])

            # ----------------------------
            __prefix = file["prefix"]
            __sufix = file["sufix"]
            __lote = file["lote"]
            __seq = file["sequencia"]
            __sep = file["separador"]
            __dth = file["datahora"]
            __zip = file["zip"]

            # ----------------------------
            __sep = gen.iif(__sep["flg_ativo"].upper() == "S", __sep["valor"], "")
            __numlote = gen.iif(__lote["flg_ativo"].upper() == "S", int(resumo["identificacao"]["ultimo_lote"]), 0)
            __sizeseq = gen.iif(__seq["flg_ativo"].upper() == "S", int(__seq["size"]), 0)

            # ----------------------------
            __process = args["process"]  # nome do processo
            __objname = __sep + args["objname"]  # nome do objeto (tabela|query)
            __prefixName = gen.iif(__prefix["flg_ativo"].upper() == "S", __sep + __prefix["name"], "")
            #__sufixName = gen.iif(__sufix["flg_ativo"].upper() == "S", __sep + gen.nvl(__sufix["name"],""), "")
            __loteName = gen.iif(__numlote>=0, f"""{__sep}{__numlote:0{__lote["size"]}d}""", "")
            __seqName = gen.iif(__sizeseq > 0, f"""{__sep}{args['sequencia']:0{__sizeseq}d}""","")
            __dthFormato = gen.iif(__dth["flg_ativo"].upper()=="S", __sep+__dth["formato"], "")

            # consistindo o sufix
            if __sufix["flg_ativo"].upper() == "S":
                if isinstance(__sufix["name"], dict):
                    __sufixName = __sep + args["rowprequery"][__sufix["name"]["pre-query"]]
                else:
                    __sufixName = gen.iif(__sufix["flg_ativo"].upper() == "S", __sep + gen.nvl(__sufix["name"],""), "")
            else:
                __sufixName=""

            # ----------------------------
            __filename = f"""{__process}{__objname}{__prefixName}{__sufixName}{__loteName}{__seqName}{dt.datetime.now().strftime(__dthFormato)}"""
            result = os.path.join(__root, __filename)

        except Exception as error:
                msg = error
                result = msg
        finally:
            # 'C:\\SERVER_DASA\\BI\\PRD\\TempFiles\\MULTIMAGEM_PETROPOLIS_RECEITA-FT_ATENDIMENTO-FATO_RECEITA_DIARIA-LEME_DOMICILIAR-000001-001-20250316170406'
            return result

    # ---------------------------------
    def setPurge(self, path, regex_include, regex_exclude, minutos=86400):
        msg, result = None, True
        try:
            __filelist = []
            for dir, subdir, files in os.walk(path):
                for file in files:
                    if re.match(regex_include, file):
                        if len(regex_exclude) > 0:
                            if re.match(regex_exclude, file):
                                continue
                        __fileModified = dt.datetime.fromtimestamp(os.path.getmtime(os.path.join(dir, file)))
                        __fileDateLimite = (dt.datetime.now()-dt.timedelta(minutes=minutos))
                        if __fileModified <= __fileDateLimite:
                        #if (dt.datetime.now() - __fileModified) > dt.timedelta(minutes=minutos):
                            os.remove(os.path.join(dir,file))
                            #__filelist.append(os.path.join(dir,file))
            #result = __filelist
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    # ---------------------------------
    def datetime_encoder(self, value):
        msg, result = None, True
        try:
            #import json.encoder as je
            if isinstance(value, dt.datetime):
                result = value.isoformat() #value.strftime(dtu.MILLISECONDS_FORMAT_PYTHON)
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

            # region Obtendo os parametros do processo
            __parListDict = par.getParameter(cols=["*"], cols_where=["NOM_PROJETO"],
                                             cols_value=[[self.NameProcess, "Paths"]])
            __hashes = sql.fromListDictToList(listDict=__parListDict, keyValue="HASH")
            self.Parameters = par.setParametersListToDict(__parListDict)
            # --------------------------------------------------------------

    # ----------------------------------
    def getEnviroment(self):
        # Arquivo de variaveis de ambiente, apenas utilizar em modo de desenvolvimento
        # Para producao criar as variaveis de ambiente "token" e "token_parametros"
        msg, result = None, True
        try:
            if os.environ.get("token") is None or os.environ.get("token_parametros"):
                __fileEnv = "..\config\env\.env"
                if os.path.exists(__fileEnv):
                    load_dotenv(__fileEnv)
                else:
                    raise Exception(
                        f"""Arquivo ENVIROMENT ("{__fileEnv}"), não foi localizado!\nVariaveis de ambiente "token" e "token_parametros", precisam ser inicializadas!""")
            # fernet.setToken(os.getenv('token'))  # vide a propriedade TOKEN desta classe, ela armazena o valor do token
        except Exception as error:
            msg = error
            self.setError(msg.args[0])
            result = False
            log.setLogEvent(content=f"""{result}""", level=lvl.ERROR)
        finally:
            return result

    # class DateTimeEncoder(json.JSONEncoder):
    #     def default(self, obj):
    #         if isinstance(obj, datetime):
    #             return obj.isoformat()  # Converte datetime para string ISO
    #         return super().default(obj)



    #endregion