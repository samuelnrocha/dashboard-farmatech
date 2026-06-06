import os
import json
import pandas as pd
from datetime import datetime
import oracledb
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# --- MODELOS DE DOMÍNIO ---
class Propriedade:
    def __init__(self, nome: str, area_total: float, localizacao: str, tipo_solo: str, id_prop=None):
        self.id = id_prop
        self.nome = nome
        self.area_total = area_total
        self.localizacao = localizacao
        self.tipo_solo = tipo_solo
        self.colheitas = []

    def adicionar_colheita(self, colheita):
        self.colheitas.append(colheita)

    def obter_total_colheitas(self):
        return len(self.colheitas)

    def obter_area_total_colhida(self):
        return sum(colheita.area_colhida for colheita in self.colheitas)

    def obter_quantidade_total_colhida(self):
        return sum(colheita.quantidade_colhida for colheita in self.colheitas)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "area_total": self.area_total,
            "localizacao": self.localizacao,
            "tipo_solo": self.tipo_solo,
            "colheitas": [c.to_dict() for c in self.colheitas]
        }

    @classmethod
    def from_dict(cls, d):
        prop = cls(d["nome"], d["area_total"], d["localizacao"], d["tipo_solo"], d.get("id"))
        if "colheitas" in d:
            for col_dict in d["colheitas"]:
                prop.adicionar_colheita(Colheita.from_dict(col_dict))
        return prop


class Colheita:
    def __init__(self, data: str, area_colhida: float, quantidade_colhida: float, tipo_colheita: str, id_col=None, produtividade=None, percentual_perda=None):
        self.id = id_col
        self.data = data
        self.area_colhida = area_colhida
        self.quantidade_colhida = quantidade_colhida
        self.tipo_colheita = tipo_colheita
        self._produtividade = produtividade
        self.percentual_perda = percentual_perda

    @property
    def produtividade(self):
        if self._produtividade is not None:
            return self._produtividade
        if self.area_colhida > 0:
            return round(self.quantidade_colhida / self.area_colhida, 2)
        return 0.0

    def to_dict(self):
        return {
            "id": self.id,
            "data": self.data,
            "area_colhida": self.area_colhida,
            "quantidade_colhida": self.quantidade_colhida,
            "tipo_colheita": self.tipo_colheita,
            "produtividade": self.produtividade,
            "percentual_perda": self.percentual_perda
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            d["data"],
            d["area_colhida"],
            d["quantidade_colhida"],
            d["tipo_colheita"],
            d.get("id"),
            d.get("produtividade"),
            d.get("percentual_perda")
        )


# --- REGRAS DE PERDA DE SOLO (Fase 2) ---
PRODUTIVIDADE_ESPERADA_POR_SOLO = {
    'latossolo vermelho': 95.0,
    'latossolo vermelho-amarelo': 88.0,
    'nitossolo': 92.0,
    'argissolo': 78.0,
    'cambissolo': 75.0,
    'neossolo quartzarênico': 65.0,
    'neossolo litólico': 58.0,
    'planossolo': 62.0,
    'gleissolo': 55.0,
    'vertissolo': 82.0,
    'organossolo': 70.0,
    'outros': 75.0
}

def obter_produtividade_esperada(tipo_solo):
    return PRODUTIVIDADE_ESPERADA_POR_SOLO.get(tipo_solo.lower().strip(), 75.0)

def calcular_perda(produtividade_real, produtividade_esperada):
    if produtividade_esperada <= 0:
        return 0.0
    if produtividade_real >= produtividade_esperada:
        return 0.0
    perda = ((produtividade_esperada - produtividade_real) / produtividade_esperada) * 100
    return round(perda, 2)

def classificar_perda(percentual):
    if percentual <= 5.0:
        return "Baixa"
    elif percentual <= 10.0:
        return "Média"
    elif percentual <= 15.0:
        return "Alta"
    else:
        return "Crítica"


# --- SERVIÇO DE CONEXÃO E PERSISTÊNCIA ---
class SMPCService:
    def __init__(self):
        self.db_host = os.getenv("ORACLE_HOST", "localhost")
        self.db_port = os.getenv("ORACLE_PORT", "1521")
        self.db_service = os.getenv("ORACLE_SERVICE", "ORCL")
        self.db_user = os.getenv("ORACLE_USER", "root")
        self.db_password = os.getenv("ORACLE_PASSWORD", "root")
        self.fallback_file = "smpc_fallback_data.json"
        
        # Testar conexão inicial
        self.db_online = self._test_connection()
        if self.db_online:
            self._criar_tabelas_se_necessario()

    def _test_connection(self):
        if not self.db_user or not self.db_password:
            return False
        try:
            dsn = f"{self.db_host}:{self.db_port}/{self.db_service}"
            # Tenta conectar no modo Thin do oracledb (não requer client local)
            conn = oracledb.connect(user=self.db_user, password=self.db_password, dsn=dsn)
            conn.close()
            return True
        except Exception:
            return False

    def _criar_tabelas_se_necessario(self):
        dsn = f"{self.db_host}:{self.db_port}/{self.db_service}"
        try:
            conn = oracledb.connect(user=self.db_user, password=self.db_password, dsn=dsn)
            cursor = conn.cursor()
            
            # Tabela Propriedades
            cursor.execute("""
                BEGIN
                    EXECUTE IMMEDIATE 'CREATE TABLE propriedades (
                        id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                        nome VARCHAR2(100) NOT NULL UNIQUE,
                        area_total NUMBER(10,2) NOT NULL,
                        localizacao VARCHAR2(200) NOT NULL,
                        tipo_solo VARCHAR2(50) NOT NULL,
                        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )';
                EXCEPTION WHEN OTHERS THEN IF SQLCODE != -955 THEN RAISE; END IF;
                END;
            """)
            
            # Tabela Colheitas
            cursor.execute("""
                BEGIN
                    EXECUTE IMMEDIATE 'CREATE TABLE colheitas (
                        id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                        propriedade_id NUMBER NOT NULL,
                        data_colheita DATE NOT NULL,
                        area_colhida NUMBER(10,2) NOT NULL,
                        quantidade_colhida NUMBER(10,2) NOT NULL,
                        tipo_colheita VARCHAR2(20) NOT NULL,
                        produtividade NUMBER(10,2),
                        percentual_perda NUMBER(5,2),
                        data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT fk_colheita_propriedade FOREIGN KEY (propriedade_id) REFERENCES propriedades(id) ON DELETE CASCADE
                    )';
                EXCEPTION WHEN OTHERS THEN IF SQLCODE != -955 THEN RAISE; END IF;
                END;
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print("Erro ao inicializar tabelas Oracle:", e)

    def obter_conexao(self):
        dsn = f"{self.db_host}:{self.db_port}/{self.db_service}"
        return oracledb.connect(user=self.db_user, password=self.db_password, dsn=dsn)

    # --- CRUD PROPRIEDADE ---
    def cadastrar_propriedade(self, nome, area_total, localizacao, tipo_solo):
        if self.db_online:
            try:
                conn = self.obter_conexao()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO propriedades (nome, area_total, localizacao, tipo_solo)
                    VALUES (:nome, :area_total, :localizacao, :tipo_solo)
                """, {"nome": nome, "area_total": area_total, "localizacao": localizacao, "tipo_solo": tipo_solo})
                conn.commit()
                cursor.close()
                conn.close()
                return True, "Propriedade cadastrada com sucesso no banco Oracle!"
            except Exception as e:
                return False, f"Erro ao cadastrar no banco Oracle: {e}"
        else:
            # Fallback local
            propriedades = self.listar_propriedades_locais()
            if any(p.nome.lower() == nome.lower() for p in propriedades):
                return False, "Erro: Já existe uma propriedade com este nome."
            
            nova_prop = Propriedade(nome, area_total, localizacao, tipo_solo, len(propriedades) + 1)
            propriedades.append(nova_prop)
            self.salvar_propriedades_locais(propriedades)
            return True, "Propriedade cadastrada com sucesso no armazenamento local (Fallback DB Offline)."

    def listar_propriedades(self):
        if self.db_online:
            try:
                conn = self.obter_conexao()
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome, area_total, localizacao, tipo_solo FROM propriedades ORDER BY nome")
                rows = cursor.fetchall()
                
                propriedades = []
                for row in rows:
                    prop = Propriedade(row[1], float(row[2]), row[3], row[4], int(row[0]))
                    # Carregar colheitas dela
                    cursor.execute("""
                        SELECT id, TO_CHAR(data_colheita, 'DD/MM/YYYY'), area_colhida, quantidade_colhida, 
                               tipo_colheita, produtividade, percentual_perda 
                        FROM colheitas WHERE propriedade_id = :prop_id
                    """, {"prop_id": prop.id})
                    col_rows = cursor.fetchall()
                    for col_row in col_rows:
                        colheita = Colheita(
                            col_row[1], float(col_row[2]), float(col_row[3]), col_row[4],
                            int(col_row[0]), float(col_row[5]), float(col_row[6])
                        )
                        prop.adicionar_colheita(colheita)
                    propriedades.append(prop)
                
                cursor.close()
                conn.close()
                return propriedades
            except Exception as e:
                print("Erro ao listar propriedades Oracle:", e)
                return self.listar_propriedades_locais()
        else:
            return self.listar_propriedades_locais()

    # --- CRUD COLHEITAS ---
    def cadastrar_colheita(self, propriedade_id, data_str, area_colhida, quantidade_colhida, tipo_colheita, tipo_solo):
        # Calcular produtividade e perda
        prod_real = round(quantidade_colhida / area_colhida, 2) if area_colhida > 0 else 0.0
        prod_esperada = obter_produtividade_esperada(tipo_solo)
        perda_pct = calcular_perda(prod_real, prod_esperada)
        
        if self.db_online:
            try:
                conn = self.obter_conexao()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO colheitas (propriedade_id, data_colheita, area_colhida, quantidade_colhida, 
                                          tipo_colheita, produtividade, percentual_perda)
                    VALUES (:propriedade_id, TO_DATE(:data_col, 'DD/MM/YYYY'), :area_col, :qtd_col, :tipo, :prod, :perda)
                """, {
                    "propriedade_id": propriedade_id,
                    "data_col": data_str,
                    "area_col": area_colhida,
                    "qtd_col": quantidade_colhida,
                    "tipo": tipo_colheita,
                    "prod": prod_real,
                    "perda": perda_pct
                })
                conn.commit()
                cursor.close()
                conn.close()
                return True, "Colheita registrada com sucesso no banco Oracle!"
            except Exception as e:
                return False, f"Erro ao registrar colheita no Oracle: {e}"
        else:
            # Fallback
            propriedades = self.listar_propriedades_locais()
            prop = next((p for p in propriedades if p.id == propriedade_id), None)
            if not prop:
                return False, "Erro: Propriedade não localizada."
                
            nova_col = Colheita(data_str, area_colhida, quantidade_colhida, tipo_colheita, len(prop.colheitas) + 1, prod_real, perda_pct)
            prop.adicionar_colheita(nova_col)
            self.salvar_propriedades_locais(propriedades)
            return True, "Colheita registrada com sucesso no armazenamento local (Fallback Offline)."

    # --- METODOS LOCAIS (JSON FALLBACK) ---
    def listar_propriedades_locais(self):
        if not os.path.exists(self.fallback_file):
            return []
        try:
            with open(self.fallback_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [Propriedade.from_dict(p) for p in data]
        except Exception as e:
            print("Erro ao carregar dados locais:", e)
            return []

    def salvar_propriedades_locais(self, propriedades):
        try:
            with open(self.fallback_file, "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in propriedades], f, indent=4, ensure_ascii=False)
        except Exception as e:
            print("Erro ao salvar dados locais:", e)

    # --- BACKUP & RESTAURAÇÃO ---
    def exportar_backup(self, filepath):
        """
        Gera um backup completo das propriedades e colheitas em JSON
        """
        propriedades = self.listar_propriedades()
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in propriedades], f, indent=4, ensure_ascii=False)
            return True, f"Backup exportado com sucesso para `{filepath}`!"
        except Exception as e:
            return False, f"Erro ao gerar backup: {e}"

    def restaurar_backup(self, json_data_str):
        """
        Restaura os dados de propriedades e colheitas a partir de uma string JSON
        """
        try:
            data = json.loads(json_data_str)
            propriedades_novas = [Propriedade.from_dict(p) for p in data]
            
            if self.db_online:
                conn = self.obter_conexao()
                cursor = conn.cursor()
                # Limpar tabelas atuais
                cursor.execute("DELETE FROM colheitas")
                cursor.execute("DELETE FROM propriedades")
                
                # Inserir recuperados
                for prop in propriedades_novas:
                    cursor.execute("""
                        INSERT INTO propriedades (nome, area_total, localizacao, tipo_solo)
                        VALUES (:nome, :area_total, :localizacao, :tipo_solo)
                    """, {"nome": prop.nome, "area_total": prop.area_total, "localizacao": prop.localizacao, "tipo_solo": prop.tipo_solo})
                    
                    # Obter o novo ID gerado
                    cursor.execute("SELECT id FROM propriedades WHERE nome = :nome", {"nome": prop.nome})
                    new_prop_id = cursor.fetchone()[0]
                    
                    for col in prop.colheitas:
                        cursor.execute("""
                            INSERT INTO colheitas (propriedade_id, data_colheita, area_colhida, quantidade_colhida, 
                                                  tipo_colheita, produtividade, percentual_perda)
                            VALUES (:propriedade_id, TO_DATE(:data_col, 'DD/MM/YYYY'), :area_col, :qtd_col, :tipo, :prod, :perda)
                        """, {
                            "propriedade_id": new_prop_id,
                            "data_col": col.data,
                            "area_col": col.area_colhida,
                            "qtd_col": col.quantidade_colhida,
                            "tipo": col.tipo_colheita,
                            "prod": col.produtividade,
                            "perda": col.percentual_perda
                        })
                conn.commit()
                cursor.close()
                conn.close()
                return True, "Dados restaurados com sucesso no banco de dados Oracle!"
            else:
                # Restaurar localmente
                # Re-indexar IDs
                for idx_p, prop in enumerate(propriedades_novas, start=1):
                    prop.id = idx_p
                    for idx_c, col in enumerate(prop.colheitas, start=1):
                        col.id = idx_c
                self.salvar_propriedades_locais(propriedades_novas)
                return True, "Dados restaurados com sucesso no armazenamento local de fallback!"
        except Exception as e:
            return False, f"Erro ao restaurar backup: {e}"
