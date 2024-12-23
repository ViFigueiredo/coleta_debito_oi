from selenium import webdriver  # type: ignore
from selenium.webdriver.common.by import By  # type: ignore
from selenium.webdriver.support.ui import WebDriverWait  # type: ignore
from selenium.webdriver.support import expected_conditions as EC  # type: ignore
from dotenv import load_dotenv  # type: ignore
import pyodbc  # type: ignore
import os  # type: ignore
import re  # type: ignore

load_dotenv()  # Carrega as variáveis do arquivo .env

# Configuração do SQL Server
db_server = os.getenv('db_server')
db_username = os.getenv('db_username')
db_password = os.getenv('db_password')
db_name = os.getenv('db_name')
db_table1 = 'coletados'
db_table2 = 'CPF_OI'

# Verificar se as variáveis de ambiente foram carregadas corretamente
if not all([db_server, db_username, db_password, db_name]):
    print("Erro: Falta de configuração no arquivo .env")
    exit(1)

# Conexão com o SQL Server
conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={db_server};DATABASE={db_name};UID={db_username};PWD={db_password}')
cursor = conn.cursor()

def coletar(cpf_value):
    driver = webdriver.Firefox()  # Configuração do driver

    try:
        url = 'https://www.oi.com.br/minha-oi/codigo-de-barras/'
        driver.get(url)

        wait = WebDriverWait(driver, 10)

        # Aguardar visibilidade e rolar até o campo CPF
        xpath_cpf = '//*[@id="cpf_cliente"]'
        cpf_input = wait.until(EC.visibility_of_element_located((By.XPATH, xpath_cpf)))
        driver.execute_script("arguments[0].scrollIntoView(true);", cpf_input)

        # Preencher o campo CPF
        cpf_input.send_keys(cpf_value)

        # Aguardar visibilidade do botão e clicar nele
        xpath_botao = '//*[@id="btn_emitir-codigo-de-barras"]'
        btn_emitir = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_botao)))
        btn_emitir.click()

        # Aguardar pelo valor de débito
        xpath_debito = '/html/body/div[1]/div/div/main/div[1]/div/div/div[6]/div/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/h3'
        debit_element = wait.until(EC.visibility_of_element_located((By.XPATH, xpath_debito)))

        if debit_element:
            valor = re.search(r'[\d,.]+', debit_element.text)
            
            if valor:
                debit_value = float(valor.group().replace(',', '.'))
                print(f"Valor de débito encontrado: {debit_value}")
                values = (cpf_value, debit_value)
                cursor.execute(f"""INSERT INTO {db_table1} (cpf, debito) VALUES (?,?)""", values)
                conn.commit()
            else:
                print("Nenhum valor de débito encontrado.")
                return "Nenhum valor de débito encontrado."
        else:
            print("Nenhum valor de débito encontrado.")
            return "Nenhum valor de débito encontrado."
    except pyodbc.DataError as e:
        print(f"\nErro ao tentar inserir os dados na tabela '{db_table1}'")
        print(f"Detalhes do erro: {e}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        driver.save_screenshot('screenshot.png')  # Salva uma captura de tela para debug
    finally:
        driver.quit()

def numeros_cpf():
    try:
        cursor.execute(f"SELECT cpf FROM {db_table2}")
        lista_cpfs = cursor.fetchall()
        
        for cpf in lista_cpfs:
            print(f'Dados para o CPF: {cpf[0]}')
            coletar(cpf[0])  # Passa o valor do CPF para a função coletar

        cursor.execute(f"SELECT COUNT(*) FROM {db_table2}")
        total = cursor.fetchone()[0]
        print(f"Total de registros na tabela '{db_table2}': {total}")
        return total    
    except Exception as e:
        print(f"Erro ao buscar CPFs: {e}")
    finally:
        cursor.close()
        conn.close()  # Fecha a conexão com o banco de dados

# Chamar a função para iniciar a coleta
# numeros_cpf()
