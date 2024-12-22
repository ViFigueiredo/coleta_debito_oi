from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuração do driver
driver = webdriver.Firefox()

try:
    driver.get('https://www.oi.com.br/minha-oi/codigo-de-barras/')

    wait = WebDriverWait(driver, 10)
    
    # Aguardar visibilidade e rolar até o campo CPF
    cpf_input = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="cpf_cliente"]')))
    driver.execute_script("arguments[0].scrollIntoView(true);", cpf_input)
    
    # Preencher o campo CPF
    cpf_input.send_keys('06259146515')
    
    # Aguardar visibilidade do botão e clicar nele
    btn_emitir = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btn_emitir-codigo-de-barras"]')))
    # driver.execute_script("arguments[0].scrollIntoView(true);", btn_emitir)
    btn_emitir.click()
    
    # Aguardar pelo valor de débito
    debit_element = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div/main/div[1]/div/div/div[5]/div/div[2]/div[1]/div[1]/div[1]/div/div/div[1]/h3')))
    debit_value = debit_element.text
    
    if debit_value:
        print(f"Valor de débito encontrado: {debit_value}")
    else:
        print("Nenhum valor de débito encontrado.")

except Exception as e:
    print(f"Ocorreu um erro: {e}")
    driver.save_screenshot('screenshot.png')  # Salva uma captura de tela para debug

finally:
    driver.quit()
