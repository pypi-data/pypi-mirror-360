import datetime as dt
import os
import json
import sys
import re

import pandas as pd
from dotenv import load_dotenv

from DE_Lib.Utils import Sql, Generic, DateUtils, System
from DE_Lib.Utils.Cipher import Fernet
from DE_Lib.Files import Csv, JSon, Txt, Parquet, Zip
from DE_Lib.Log import Log, Level

from source.Lib import Parameter, Connect, Etl

sql = Sql.SQL()
gen = Generic.GENERIC()
fernet = Fernet.FERNET()
con = Connect.CONNECT()
so = System.SO()
dtu = DateUtils.DATEUTILS()
log = Log.LOG()
lvl = Level.LEVEL()

csv = Csv.CSV()
txt = Txt.TXT()
jsn = JSon.JSON()
#parquet = Parquet.PARQUET()
zip = Zip.ZIP()

par = Parameter.PARAMETER()
etl = Etl.ETL()


class EXTRACT:
    def __init__(self):
        msg, result = None, ""
        try:
            self._RowIterator = None
            if not etl.getEnviroment():
                raise Exception(self.ERROR)
            fernet.setToken(os.environ.get("token"))
        except Exception as error:
            msg = error
            result = gen.getError(error)
            log.setLogEvent(
                content=f"""Erro na linha: {result["line"]}, Tipo de erro: {result["error_type"]}, mensagem: {msg}""",
                level=lvl.ERROR)
        finally:
            print(result)

    def Execute(self, process_name: str):
        msg, result = None, None
        try:

            #region Iniciando o processo
            self.NameProcess = process_name
            self.START_DATE = dt.datetime.now()
            #endregion

            #region Obtendo a conexao com a base de parametros
            par.setInit()
            if not par.CONNECTION_VALID:
                raise Exception(par.ERROR_PARAMETER)
            #endregion

            #region Obtendo os parametros do processo
            __parListDict = par.getParameter(cols=["*"], cols_where=["NOM_PROJETO"], cols_value=[[self.NameProcess, "Paths"]])
            __hashes = sql.fromListDictToList(listDict=__parListDict, keyValue="HASH")
            self.Parameters = par.setParametersListToDict(__parListDict)
            # --------------------------------------------------------------

            # region Start LOG
            __fileLog = os.path.join(self.Parameters['Paths']['path_base'], self.Parameters['Paths']['log_files'], f"{self.NameProcess}-{self.START_DATE.strftime(dtu.DATETIME_FILENAME)}.log")
            __procDict = {"processo": self.NameProcess,
                          "descricao": "Teste de rotina de LOG",
                          "file": __fileLog,
                          "conexao": par.CONNECTION,
                          "table": "BI_DAX.LOG",
                          "event": "BI_DAX.LOG_EVENT"
                          }
            log.setInit(__procDict)
            log.setLogEvent(content=f"""Inicializando os parametros!""", level=lvl.INFO)
            # endregion

            # --------------------------------------------------------------
            log.setLogEvent(content=f"""Preparando o resumo do processo!""", level=lvl.INFO)
            self.Resumo["identificacao"] = {"obj": self.NameProcess,
                                            "pid": so.PID,
                                            "ultimo_lote": gen.nvl(self.Resumo["identificacao"]["ultimo_lote"], 0) + 1,
                                            "datahora_inicio": self.START_DATE.strftime(dtu.MILLISECONDS_FORMAT_PYTHON)
                                            }
            #endregion

            #region Looping sobre os objetos candidatos
            log.setLogEvent(content=f"""Obtendo os objetos candidatos!""", level=lvl.INFO)
            for self.TableName in self.Parameters["Objetos_Candidatos"]:
                log.setLogEvent(content=f"""Processo o objeto {self.TableName}!""", level=lvl.INFO)
                #region HASH
                """
                  ------------------------------------------------------------------------------------
                  o elemento HASH foi colocado intensionalmente pela funcao setParamtersListToDict
                  como ele foje da estrutura dos objetos candidatos, foi colocada a instrucao abaixo
                  Se este tipo de objeto for localizado sera dado um bypass e pula para o proximo
                  do looping
                  ------ Ver possibilidade de poipular o hash de outra forma ------
                  ------------------------------------------------------------------------------------
                """
                if self.TableName == "HASH":
                    continue
                #endregion

                # region Identifica se o objeto candidato esta ativo
                if self.TableId["ativo"] != "S":
                    # Objeto selecionado não se encontra ativo, pule para o proximo
                    continue
                #endregion

                # region faz conexao com a base do objeto candidato selecionado
                """
                    Utiliza o token de conexao com a base de origem do objeto
                    descriptografado e faz a conexão com a base de dados
                    respectiva
                    Esta conexao instancia algumas propriedades
                    CONNECTION_VALID: True|False se a conexão esta validada ou não
                    CONNETCION: Driver de conexão
                    DATABASE_DRIVER: Qual é o driver utilizado para esta conexao
                    DATABASE_ERROR: Apresenta mensage de erro se houver, se não houver sera True
                    DATABASE_NAME: Nome popular da base em que esta tentanto a conexao
                """
                log.setLogEvent(content=f"""Conectando com a base de dados de origem!""", level=lvl.INFO)
                con.setConectionDataBase(self.DataBaseConnection)
                if not con.CONNECTION_VALID:
                    raise Exception(con.DATABASE_ERROR)
                else:
                    self.DATABASE = con.DATABASE
                    self.CONNECTION = con.CONNECTION
                    self.CONNECTION_IS_VALID = con.CONNECTION_VALID
                    self.DATABASE_ERROR = con.DATABASE_ERROR
                    self.DATABASE_DRIVER = con.DATABASE_DRIVER
                    self.NOME_DATABASE = con.NOME_DATABASE
                # endregion

                log.setLogEvent(content=f"""Definindo o ITERATOR!""", level=lvl.INFO)
                self.Iterator = self.Delta["iteracao"]
                rows = self.getIterator(self.Iterator)

                # region Iniciando Iterações para o objeto selecionado
                log.setLogEvent(content=f"""Iniciando o ITERATOR: {len(rows)} linha(s)!""", level=lvl.INFO)
                for row in rows:

                    # Inicializando variavel publica com o conteudo da row
                    self.RowIterator = row

                    if not gen.is_valid_int(row):
                        ...
                        """
                        Tem que avaliar neste ponto se o iterator utilizado
                        """
                        #log.setLogEvent(content=f"""Processando o ITERATOR: {self.RowIterator["empr_cod_empresa"]}-{self.RowIterator["empr_nom_empresa"]}!""", level=lvl.DESTAQUE)

                    #region  Consistindo o tipo de carga a ser executada
                    log.setLogEvent(content=f"""Processando tipo de carga {self.TipoCarga.upper()}!""", level=lvl.INFO)
                    if self.TipoCarga.upper() == "INCREMENTAL": #Literal["INCREMENTAL","ESTATICA","FULL"]
                        # Incremental
                        __rangeValue = [None, None, None]
                        if self.Delta["type"].upper() in ("DATETIME", "DATE"):
                            __rangeValue = etl.getRangeDate(self.Delta)
                            self.Delta["start_value"] = __rangeValue[0]
                            self.Delta["end_value"] = __rangeValue[1]
                            self.Delta["scopo"] = __rangeValue[2]
                        elif self.Delta["type"].upper() == "HOUR":
                            ...
                        elif self.Delta["type"].upper() == "MINUTE":
                            ...
                        elif self.Delta["type"].upper() == "NUMERIC":
                            __rangeValue = etl.getNumericRangeValue(self.Delta)
                    elif self.TipoCarga.upper() == "ESTATICA":
                        ...
                    else:
                        # Full
                        self.Delta["start_value"] = None
                        self.Delta["end_value"] = None
                        self.Delta["scopo"] = None
                    #endregion



                    #region Identificando se o tipo de objeto é um "Table" ou "Query"
                    log.setLogEvent(content=f"""Obtendo a query para extração!""", level=lvl.INFO)
                    if self.Origem["tipo_objeto"].upper() == "QUERY":
                        self.QUERY = par.getParameter(cols=["VAL_PARAMETRO"], cols_where=["NOM_PARAMETRO"], cols_value=[self.Origem["name"]])[0]["VAL_PARAMETRO"]
                        self.QUERY = etl.getQueryExtract(obj=self.Parameters, name=self.TableName, conn=con, qry=self.QUERY)
                    else:
                        self.QUERY = etl.getQueryExtract(obj=self.Parameters, name=self.TableName, conn=con)
                    log.setLogEvent(content=f"""Definindo PLACEHOLDERS!""", level=lvl.INFO)
                    if row == 0:
                        self.PLACEHOLDER = False
                    else:
                        self.PLACEHOLDER = row #self.setPlaceHolders(self.QUERY, row)

                    # -----------------------------------------------------
                    log.setLogEvent(content=f"""Iniciando Extração dos dados!""", level=lvl.INFO)
                    self.getExtractCursor()
                    # -----------------------------------------------------

                log.setLogEvent(content=f"""Fechando conexão!""", level=lvl.INFO)
                con.CONNECTION.close()
                #endregion
            #endregion

            #region Finalizando o processo
            self.End_Date = dt.datetime.now()
            self.Resumo["execucao"]["datahora_termino"] = self.End_Date.strftime(dtu.MILLISECONDS_FORMAT_PYTHON)
            self.Resumo["execucao"]["tempo_decorrido"] = f"""{(self.End_Date - self.START_DATE)}"""
            #endregion

            # region SAVE PARAMETERS
            log.setLogEvent(content=f"""Salvando parametros!""", level=lvl.INFO)
            par.setSaveParameters(par=self.Parameters)
            # endregion

            # region PURGE FILES
            # este looping se repete apenas para controlar o expurgo de arquivos
            log.setLogEvent(content=f"""Eliminando arquivos antigos para este processo!""", level=lvl.INFO)
            for self.TableName in self.Parameters["Objetos_Candidatos"]:
                if self.TableName != 'HASH':
                    x = self.Parameters["Objetos_Candidatos"][self.TableName]["destino"]
                    #self.Destino = self.Parameters["Objetos_Candidatos"][self.TableName]["destino"]
                    __dtPurge = self.getDatePurge(self.Destino["expurgo"])
                    __regexinclude = f"""{self.NameProcess}-{self.TableName}.*.(csv|json|xlsx|xls|parquet|avro|txt)"""
                    __regexexclude = ""
                    __minutosexpurgo =  gen.iif(self.Destino["expurgo"]["type"].upper()=="DAYS", self.Destino["expurgo"]["value"] * 1440, self.Destino["expurgo"]["value"])
                    __abspath = etl.getPathFilesRoot(path_base=self.Paths["path_base"],
                                                     platform=so.OSINFO["so_platform"],
                                                     path_file=self.Paths[self.Destino["local_destino"]]
                                                     )
                    etl.setPurge(path=__abspath,
                                 regex_include=__regexinclude,
                                 regex_exclude=__regexexclude,
                                 minutos=__minutosexpurgo
                                 )
            # endregion

        except Exception as error:
            msg = error
            result = gen.getError(error)
            log.setLogEvent(
                content=f"""Erro na linha: {result["line"]}, Tipo de erro: {result["error_type"]}, mensagem: {msg}""",
                level=lvl.ERROR)
        finally:
            # region Enviando EMAIL´s
            log.setLogEvent(content=f"""Enviando EMAIL!""", level=lvl.INFO)
            __hashProcess = par.getParameter(cols=["HASH"], cols_where=["NOM_PROJETO", "TIPO_PARAMETRO"],
                                             cols_value=[self.NameProcess, "Topico"])
            emails = par.getEmailProcesso(__hashProcess[0]["HASH"])
            # endregion
            log.setEnd()
            return result

    # ---------------------------------
    def getDatePurge(self, expurgo: dict):
        msg, result = None, True
        try:
            __now = dt.datetime.now()
            if expurgo["type"].upper() == "DIAS":
                result = __now - dt.timedelta(days=expurgo["value"])
            elif expurgo["type"].upper() == "MINUTOS":
                result = __now - dt.timedelta(minutes=expurgo["value"])
            else:
                result = __now - dt.timedelta(days=10)
        except Exception as error:
            msg = error
            result = gen.getError(error)
            log.setLogEvent(
                content=f"""Erro na linha: {result["line"]}, Tipo de erro: {result["error_type"]}, mensagem: {result["error_msg"]}""",
                level=lvl.ERROR)
        finally:
            return result

    # ---------------------------------
    # quanditade de parametros tem que ser revista
    def getExtractCursor(self):
        msg, result = None, True
        try:

            #region abrindo o cursor
            log.setLogEvent(content=f"""Criando cursor com os dados de origem!""", level=lvl.INFO)
            cur = self.CONNECTION.cursor()
            if self.PLACEHOLDER:
                cur.execute(self.QUERY, self.PLACEHOLDER)
            else:
                cur.execute(self.QUERY)
            #endregion

            #region SLICE
            __sliceValue = gen.iif(not self.Slice["page"], 50000, self.Slice["page"])
            __sliceDynamic = gen.iif(not self.Slice["dynamic"], "S", self.Slice["dynamic"])
            __sliceMemory = gen.iif(not self.Slice["memory"], 32000, self.Slice["memory"])
            log.setLogEvent(content=f"""Slice definido para: {__sliceValue}!""", level=lvl.INFO)
            #endregion

            # region Loop sobre o cursor
            __sequencia = 0
            while True:
                __sequencia += 1
                rows = cur.fetchmany(__sliceValue)
                if not rows:
                    break
                log.setLogEvent(content=f"""Sequencia: {__sequencia}!""", level=lvl.INFO)

                #region gerando a(s) arquivo(s)
                log.setLogEvent(content=f"""Iniciando geracao do arquivo para a sequencia!""", level=lvl.INFO)
                __df = pd.DataFrame(rows, columns=etl.getColumnsCursor(cur))

                # if __df.get("DAT_FIM_VIGENCIA"):
                #     __df["DAT_FIM_VIGENCIA"] = __df["DAT_FIM_VIGENCIA"].astype(str)

                __basefilename = etl.setFileName(file=self.Destino, resumo=self.Resumo, paths=self.Paths, args={"process":self.NameProcess, "objname":self.TableName, "sequencia":__sequencia, "rowprequery": self.RowIterator})
                __fileListZip = []

                if "csv" in self.Destino["tipo_arquivo"]:
                    __filename = __basefilename + ".csv"
                    csv.ExportDataFrame(df=__df,file_name=__filename, index=False, sep=";")
                    __fileListZip.append(__filename)
                if "txt" in self.Destino["tipo_arquivo"]:
                    __filename = __basefilename + ".txt"
                    txt.ExportDataFrame(df=__df, file_name=__filename, index=False, sep=";")
                    __fileListZip.append(__filename)
                if "json" in self.Destino["tipo_arquivo"]:
                    __filename = __basefilename + ".json"
                    jsn.ExportDataFrame(df=__df, file_name=__filename, index=False, date_format=dtu.DATETIME_FORMAT_PYTHON)
                    __fileListZip.append(__filename)
                if "xlsx" in self.Destino["tipo_arquivo"]:
                    __filename = __basefilename + ".xlsx"
                    __fileListZip.append(__filename)
                if "parquet" in self.Destino["tipo_arquivo"]:
                    __filename = __basefilename + ".parquet"
                    __fileListZip.append(__filename)
                if "avro" in self.Destino["tipo_arquivo"]:
                    __filename = __basefilename + ".avro"
                    __fileListZip.append(__filename)
                #endregion

                #region ZIPFILE
                if self.Destino["zip"]["flg_ativo"] == "S":
                    __l = self.Paths[self.Destino["local_destino"]]
                    __z = self.Paths["zip_files"]
                    __sep = self.Destino["separador"]["valor"]
                    __bs = __basefilename.split(__sep)
                    __zipfilename = f"""{__bs[0].replace(__l, __z)}{__sep}{self.Resumo["identificacao"]["ultimo_lote"]:06d}.zip"""
                    __action = gen.iif(self.Destino["zip"]["flg_exclui"] == "S", zip.DELETE, zip.NOTHING)
                    zip.zip(files=__fileListZip, zipfile=__zipfilename, modo=zip.APPEND, action=__action)
                #endregion

                #region analisando o chunk
                if __sliceDynamic.upper() == "S":
                    __size = sys.getsizeof(rows[0])
                    __sliceValue = int((__sliceMemory/__size)*1000)
                    if __sliceValue < len(rows):
                        __sliceValue=len(rows)
                #endregion
            #endregion

            etl.close_cursor(cur)
        except Exception as error:
            msg = error
            result = gen.getError(error)
            log.setLogEvent(
                content=f"""Erro na linha: {result["line"]}, Tipo de erro: {result["error_type"]}, mensagem: {msg}""",
                level=lvl.ERROR)
        finally:
            return result

    # ---------------------------------
    def getIterator(self, iterator):
        """
        Resolve como sera a iteração conforme os parametros do objeto que esta
        sendo processado
        :param iterator: Sempre devera ser um STR podendo ser um numero ou uma string
        :return:
        Ex.: "$$QueryEmpresa" ou "1" ou "20". Não aceita "1A"
        Se for uma query a ser extraida a mesma sera identificada e executada, retornando
        uma query que sera executada e montara uma lista de dados.
        """
        msg, result = None, True
        try:
            if gen.is_valid_int(iterator):
                if isinstance(iterator, str):
                    iterator = int(iterator)
                result = list(range(0, iterator))
            elif isinstance(iterator, str):
                __qry = par.getParameter(cols=["VAL_PARAMETRO"], cols_where=["NOM_PARAMETRO"], cols_value=[iterator])[0]["VAL_PARAMETRO"]
                __qryText = etl.getQueryExtract(obj=self.Parameters, name=self.TableName, conn=con.CONNECTION, qry=__qry)
                cur = con.CONNECTION.cursor()
                cur.execute(__qryText)
                result = sql.CursorToDict(cur)
            else:
                raise Exception(f"Iterator tem que obrigatoriamente ser um INT, STR")
        except Exception as error:
            msg = error
            result = gen.getError(error)
            log.setLogEvent(content=f"""Erro na linha: {result["line"]}, Tipo de erro: {result["error_type"]}, mensagem: {result["error_msg"]}""", level=lvl.ERROR)
        finally:
            return result

    # ---------------------------------
    def setPlaceHolders(self, stmt: str, filters) -> dict:
        """
        Montar um conjunto de placeholders
        :param stmt: Query a ser analisada
        :param filters:
        :return:
        """
        msg, result = None, {}
        try:
            __text = None
            keys = filters.split(",")
            for index, key in enumerate(keys):
                if self.DataBaseConnection["database"].upper()  == "SQLALCHEMY":
                    __text = f""":{key}"""
                elif self.DataBaseConnection["database"].upper() == "MYSQL":
                    __text = f"""%({key})s"""
                elif self.DataBaseConnection["database"].upper() == "ORACLE":
                    __text = f""":{key}"""
                __size = len(__text) + 1
                __dummy = stmt.find(__text)
                if __dummy > 0:
                    result = keys[index]
        except Exception as error:
            msg = error
            result = gen.getError(error)
            log.setLogEvent(
                content=f"""Erro na linha: {result["line"]}, Tipo de erro: {result["error_type"]}, mensagem: {result["error_msg"]}""",
                level=lvl.ERROR)
        finally:
            return result

    def getWhereQuery(self, qry, novo_where):
        msg, result = None, None
        try:
            match = re.search(r"\bWHERE\b(.*?)(\bGROUP\b|\bORDER\b|\bFETCH\b|$)", qry, re.IGNORECASE | re.DOTALL)
            if match:
                # Substitui a cláusula WHERE inteira pela nova
                parte_antes = qry[:match.start(1)]
                parte_depois = qry[match.end(1):]
                result = f"{parte_antes} {novo_where} {parte_depois}"
            else:
                # Não havia WHERE — adiciona antes do ORDER/GROUP/FETCH ou no fim
                insert_pos = re.search(r"\bGROUP\b|\bORDER\b|\bFETCH\b", qry, re.IGNORECASE)
                if insert_pos:
                    result = qry[:insert_pos.start()] + f" WHERE {novo_where} " + qry[insert_pos.start():]
                else:
                    nova_query = qry.strip() + f" WHERE {novo_where}"
        except Exception as error:
            msg = error
            result = gen.getError(error)
            log.setLogEvent(
                content=f"""Erro na linha: {result["line"]}, Tipo de erro: {result["error_type"]}, mensagem: {result["error_msg"]}""",
                level=lvl.ERROR)
        finally:
            return result

    #region NOVAS PROPRIEDADES GETTER´s e SETTER´s
    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, value):
        self._start_date = value

    @property
    def End_Date(self):
        return self._End_Date

    @End_Date.setter
    def End_Date(self, value):
        self._End_Date = value

    @property
    def NameProcess(self: str):
        return self._NameProcess

    @NameProcess.setter
    def NameProcess(self, value) -> str:
        self._NameProcess = value

    @property
    def Parameters(self) -> dict:
        return self._Parameters

    @Parameters.setter
    def Parameters(self, value: dict):
        self._Parameters = value

    @property
    def Paths(self) -> dict:
        return self.Parameters["Paths"]

    @Paths.setter
    def Paths(self, value: dict):
        self.Parameters["Paths"] = value

    @property
    def Schedule(self) -> dict:
        return self.Parameters["Schedule"]

    @Schedule.setter
    def Schedule(self, value: dict):
        self.Parameters["Schedule"] = value

    @property
    def Resumo(self) -> dict:
        return self.Parameters["Resumo"]

    @Resumo.setter
    def Resumo(self, value: dict):
        self._Resumo = value

    @property
    def Obj(self) -> dict:
        return self.Parameters["Objetos_Candidatos"]

    @Obj.setter
    def Obj(self, value: dict):
        self.Parameters["Objetos_Candidatos"] = value
        #self._Obj = value

    @property
    def TableName(self) -> str:
        return self._TableName

    @TableName.setter
    def TableName(self, value: str):
        self._TableName = value

    @property
    def TableId(self) -> dict:
        return self.Obj[self.TableName]["identificacao"]

    @TableId.setter
    def TableId(self, value: dict):
        self.Obj[self.TableName]["identificacao"] = value

    @property
    def Webhook(self) -> dict:
        return self.Obj[self.TableName]["webhook"]

    @Webhook.setter
    def Webhook(self, value: dict):
        self.Obj[self.TableName]["webhook"] = value

    @property
    def Origem(self) -> dict:
        return self.Obj[self.TableName]["origem"]

    @Origem.setter
    def Origem(self, value: dict):
        self.Obj[self.TableName]["origem"] = value

    @property
    def Estrategia(self) -> dict:
        return self.Obj[self.TableName]["estrategia"]

    @Estrategia.setter
    def Estrategia(self, value: dict):
        self.Obj[self.TableName]["estrategia"] = value

    @property
    def Filters(self) -> dict:
        return self.Obj[self.TableName]["filters"]

    @Filters.setter
    def Filters(self, value: dict):
        self.Obj[self.TableName]["filters"] = value

    @property
    def Destino(self) -> dict:
        return self.Obj[self.TableName]["destino"]

    @Destino.setter
    def Destino(self, value: dict):
        self.Obj[self.TableName]["destino"] = value

    @property
    def Delta(self) -> dict:
        return self.Estrategia["delta"]

    @Delta.setter
    def Delta(self, value: dict):
        self.Estrategia["delta"] = value

    @property
    def Slice(self) -> dict:
        return self.Estrategia["slice"]

    @Slice.setter
    def Slice(self, value: dict):
        self.Estrategia["slice"] = value

    @property
    def Iterator(self):
        # o Iterator pode retornar tanto um INT como um STR
        # por isso não foi tipado o retorno
        return self._Iterator

    @Iterator.setter
    def Iterator(self, value):
        # o Iterator pode popular tanto um INT como um STR
        # por isso não foi tipado a entrada
        self._Iterator = value

    @property
    def TokenName(self) -> str:
        # Nome do token de conexao
        return self.Origem["token"]

    @TokenName.setter
    def TokenName(self, value: str):
        # Nome do token de conexao
        self.Origem["token"] = value

    @property
    def TokenDataBase(self) -> str:
        # Token de conexao criptografado
        value = par.getParameter(cols=["VAL_PARAMETRO"], cols_where=["NOM_PARAMETRO"], cols_value=[self.TokenName])[0]["VAL_PARAMETRO"]
        if not isinstance(value, str):
            # consistindo se a coluna não é um STR (tipo BLOB oracle)
            value = str(value)
        return value

    @property
    def DataBaseConnection(self) -> dict:
        # string de conexao descriptografada
        value = fernet.decrypt(self.TokenDataBase)
        value = json.loads(value)
        value["password"] = fernet.decrypt(value["password"])
        return value

    @property
    def TipoCarga(self) -> str:
        return self.Estrategia["tipo_carga"]
        #return self._TipoCarga

    @TipoCarga.setter
    def TipoCarga(self, value: str):
        self.Estrategia["tipo_carga"] = value
    #endregion

    @property
    def RowIterator(self):
        return self._RowIterator

    @RowIterator.setter
    def RowIterator(self, value):
        self._RowIterator = value

    @property
    def PLACEHOLDER(self):
        return self._PLACEHOLDER

    @PLACEHOLDER.setter
    def PLACEHOLDER(self, value):
        self._PLACEHOLDER = value

    @property
    def CONNECTION(self):
        return self._CONNECTION

    @CONNECTION.setter
    def CONNECTION(self, value):
        self._CONNECTION = value

    @property
    def CONNECTION_IS_VALID(self):
        return self._CONNECTION_IS_VALID

    @CONNECTION_IS_VALID.setter
    def CONNECTION_IS_VALID(self, value):
        self._CONNECTION_IS_VALID = value

    @property
    def DATABASE_ERROR(self):
        return self._DATABASE_ERROR

    @DATABASE_ERROR.setter
    def DATABASE_ERROR(self, value):
        self._DATABASE_ERROR = value

    @property
    def NOME_DATABASE(self):
        return self._NOME_DATABASE

    @NOME_DATABASE.setter
    def NOME_DATABASE(self, value):
        self._NOME_DATABASE = value

    @property
    def DATABASE_DRIVER(self):
        return self._DATABASE_DRIVER

    @DATABASE_DRIVER.setter
    def DATABASE_DRIVER(self, value):
        self._DATABASE_DRIVER = value

    #region PROPRIEDADES INICIAIS
    @property
    def ERROR(self):
        return self._error

    @property
    def TOKEN(self):
        return fernet.TOKEN
    #endregion

    @property
    def QUERY(self):
        return self._QUERY

    @QUERY.setter
    def QUERY(self, value):
        self._QUERY = value

    @property
    def DATABASE(self):
        return self.__database

    @DATABASE.setter
    def DATABASE(self, value):
        self.__database = value


if __name__ == "__main__":
    x = EXTRACT()
    # process_name = "MULTIMAGEM_PETROPOLIS_RECEITA"
    # rst = x.Execute(process_name)
    # process_name = "MovimentoDiarioDivisaoMarcaRDI"
    # rst = x.Execute(process_name)
    process_name = "INTEGRADOR_HOSP_INDICADORES"
    rst = x.Execute(process_name)
    print(rst)