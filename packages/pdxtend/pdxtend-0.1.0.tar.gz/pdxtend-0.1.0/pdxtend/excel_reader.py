import pandas as pd
import os
import json


class LeitorExcel:
    def __init__(self, arquivo_config='config.json'):
        self._dados = None
        self._caminho = None
        self._aba = None
        self.arquivo_config = arquivo_config
        self._carregar_configuracoes()

        # Verifica se as configurações salvas são válidas
        if not self._configuracoes_validas():
            self._forcar_dados_validos()

    @property
    def dados(self):
        if self._dados is None:
            self.carregar_arquivo()
        return self._dados

    def _carregar_configuracoes(self):
        """Lê o caminho e a aba do arquivo config.json, ou cria um vazio se não existir"""
        if os.path.exists(self.arquivo_config):
            with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self._caminho = config.get('caminho')
                self._aba = config.get('aba')
                # print(f"Arquivo carregado do JSON: {self._caminho}, {self._aba}")  # Verificação para garantir que está funcionando
        else:
            self.salvar_configuracoes()  # Cria o arquivo se não existir

    def salvar_configuracoes(self):
        """Salva o caminho e aba no arquivo config.json"""
        config = {
            'caminho': self._caminho,
            'aba': self._aba
        }
        with open(self.arquivo_config, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

    def _verificar_caminho_valido(self, caminho: str) -> str:
        """Verifica se o caminho do arquivo Excel é válido e retorna a engine apropriada"""
        try:
            # Verifica se o arquivo é .xlsb
            if caminho.endswith('.xlsb'):
                pd.read_excel(caminho, engine='pyxlsb')
                return 'pyxlsb'
            # Verifica se o arquivo é .xlsx ou .xlsm
            elif caminho.endswith(('.xlsx', '.xlsm')):
                pd.read_excel(caminho, engine='openpyxl')
                return 'openpyxl'
            else:
                return None
        except Exception:
            return None

    def _verificar_aba_valida(self, caminho: str, aba: str, engine: str) -> bool:
        """Verificar se a sheet fornecida existe no arquivo Excel"""
        try:
            xls = pd.ExcelFile(caminho, engine=engine)
            return aba in xls.sheet_names
        except Exception:
            return False

    def _forcar_dados_validos(self):
        """Loop interativo até que caminho e sheet válidos sejam fornecidos"""
        while True:
            # Verifica se o caminho está definido e existe no sistema
            if not self._caminho or not os.path.exists(self._caminho):
                self._caminho = input("Insira o caminho de um arquivo Excel válido (.xlsb, .xlsx, .xlsm): ").strip()
                if not os.path.exists(self._caminho):
                    print("❌ Caminho não encontrado. Tente novamente.")
                    self._caminho = None
                    continue

            # Verifica se o arquivo tem uma extensão suportada e é carregável
            engine = self._verificar_caminho_valido(self._caminho)
            if not engine:
                print("❌ Arquivo inválido ou formato não suportado. Tente novamente.")
                self._caminho = None
                continue

            # Verifica se a aba é válida
            if not self._aba or not self._verificar_aba_valida(self._caminho, self._aba, engine):
                try:
                    xls = pd.ExcelFile(self._caminho, engine=engine)
                    print(f"\nSheets disponíveis: {', '.join(xls.sheet_names)}")
                    self._aba = input("Insira o nome de uma sheet válida: ").strip()
                    continue
                except Exception as e:
                    print(f"Erro ao tentar ler o arquivo: {e}")
                    self._caminho = None  # Reinicia o processo
                    self._aba = None
                    continue

            # Se tudo estiver válido, salva e sai do loop
            self.salvar_configuracoes()
            print("✅ Caminho e sheet válidos definidos.")
            break

    def carregar_arquivo(self, caminho: str = None, aba: str = None) -> pd.DataFrame:
        """Carrega um arquivo Excel e retorna um DataFrame."""
        if caminho:
            self._caminho = caminho
        if aba:
            self._aba = aba

        if not self._caminho:
            raise ValueError("Nenhum caminho de arquivo fornecido.")

        # Verifica o caminho e obtém a engine
        engine = self._verificar_caminho_valido(self._caminho)
        if not engine:
            raise ValueError("Arquivo inválido ou formato não suportado.")

        # Carrega o arquivo com a engine determinada
        # noinspection PyTypeChecker
        self._dados = pd.read_excel(self._caminho, sheet_name=self._aba, engine=engine)

        return self._dados

    def new_path(self, perguntar: bool = True):
        """Pergunta ao usuário se deseja alterar o caminho do arquivo"""
        if self._caminho and perguntar:
            while True:
                resposta = input(
                    f'Já existe um arquivo carregado: {self._caminho}. Deseja carregar outro? (s/n): '
                ).strip().lower()

                if resposta == 's':
                    while True:
                        novo_caminho = input('Insira um novo caminho: ').strip()
                        # Verifica o novo caminho
                        engine = self._verificar_caminho_valido(novo_caminho)
                        if engine:
                            self._caminho = novo_caminho
                            self._dados = None
                            self.salvar_configuracoes()  # Salva no JSON
                            print("✅ Novo caminho definido com sucesso!")
                            break
                        else:
                            print("❌ Caminho ou formato inválido. Tente novamente.\n")
                    break

                elif resposta == 'n':
                    print('Mantendo o caminho anterior.')
                    break
                else:
                    print('Insira um valor válido [s/n]')

    def new_sheet(self):
        """Permite ao usuário trocar a aba atual"""
        engine = self._verificar_caminho_valido(self._caminho)
        if not engine:
            print("❌ O caminho atual é inválido. Use 'new_path()' para definir um novo.")
            return

        try:
            xls = pd.ExcelFile(self._caminho, engine=engine)
            print(f"\nAbas disponíveis: {', '.join(xls.sheet_names)}")
            while True:
                nova_aba = input("Insira o nome da nova aba: ").strip()
                if nova_aba in xls.sheet_names:
                    self._aba = nova_aba
                    self._dados = None
                    self.salvar_configuracoes()
                    print("✅ Aba alterada com sucesso!")
                    break
                else:
                    print("❌ Aba não encontrada. Tente novamente.")
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")

    def _configuracoes_validas(self) -> bool:
        """Verifica se o caminho e a aba existentes são válidos"""
        if not self._caminho or not os.path.exists(self._caminho):
            return False

        engine = self._verificar_caminho_valido(self._caminho)
        if not engine:
            return False

        if not self._aba or not self._verificar_aba_valida(self._caminho, self._aba, engine):
            return False

        return True