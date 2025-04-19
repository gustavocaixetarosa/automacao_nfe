from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import csv 
import sys
from datetime import datetime

def registrar_erro(arquivo_log, linha, motivo):
    """Registra erros em um arquivo de log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(arquivo_log, 'a', encoding='utf-8') as log:
        log.write(f"[{timestamp}] ERRO - {motivo}\n")
        log.write(f"Dados da linha: {linha}\n")
        log.write("-" * 50 + "\n")

driver = webdriver.Chrome()

site_prefeitura = "https://patrocinio.simplissweb.com.br/contrib/Inicio"
cnpj = '01.075.692/0001-08'
senha = 10203040

driver.get(site_prefeitura)

campo_cnpj = driver.find_element(By.ID, 'Login_UserName')
campo_cnpj.send_keys(cnpj)

campo_senha = driver.find_element(By.NAME, 'Login.Password')
campo_senha.send_keys(senha)

entrar = driver.find_element(By.CLASS_NAME, 'btn-primary')
entrar.send_keys(Keys.RETURN)

arquivo_csv = sys.argv[1]

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
arquivo_log = f"log_processamento_{timestamp}.txt"

# Inicializar arquivo de log
with open(arquivo_log, 'w', encoding='utf-8') as log:
    log.write(f"Log de processamento iniciado em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    log.write("=" * 50 + "\n\n")

# Contadores para estatísticas
total = 0
processados = 0
falhas = 0


with open(arquivo_csv, 'r', encoding='utf-8') as arquivo:
    leitor_csv = csv.DictReader(arquivo)
    
    for linha in leitor_csv:

        emitir_nfe = 'https://patrocinio.simplissweb.com.br/contrib/AspAccess/Index?id=nfse/emitir_nfse.aspx'

        time.sleep(5)

        total += 1
        valor_total = linha['valor_total'] + '00'
        cpf_cliente = linha['cpf']
        nome_cliente = linha['nome_cliente']

        campos_vazios = []
        if not nome_cliente.strip():
            campos_vazios.append("nome")
        if not valor_total.strip():
            campos_vazios.append("valor")
        if not cpf_cliente.strip():
            campos_vazios.append("CPF")
            
        # Se há campos vazios, registrar e pular
        if campos_vazios:
            motivo = f"Campos vazios: {', '.join(campos_vazios)} - Cliente: {nome_cliente}"
            print(f"AVISO: {motivo}. Pulando este cliente.")
            registrar_erro(arquivo_log, linha, motivo)
            falhas += 1
            continue

        print(f"Processando cliente: {nome_cliente}")

        driver.get(emitir_nfe)


        wait = WebDriverWait(driver, 10)

        iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe)

        cnae_id = 'ctl00_ContentPlaceHolder1_ddl_Cnae'
        atividade_id = 'ctl00_ContentPlaceHolder1_ddl_Atividade'

        cnae_element_raw = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "select[id*='ctl00_ContentPlaceHolder1_ddl_Cnae'][name*='ctl00$ContentPlaceHolder1$ddl_Cnae']"))
        )

        # Cria o Select a partir do elemento
        cnae_element = Select(cnae_element_raw)
        cnae_element.select_by_value('859901')

        # Agora espera o elemento ser recriado (ficar "obsoleto")
        wait.until(EC.staleness_of(cnae_element_raw))

        driver.switch_to.default_content()
        iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe)

        atividade_element_raw = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "select[id*='ctl00_ContentPlaceHolder1_ddl_Atividade'][name*='ctl00$ContentPlaceHolder1$ddl_Atividade']"))
        )

        # Usa o raw para criar o Select
        atividade_element = Select(atividade_element_raw)
        atividade_element.select_by_value("8.02")

        # Aguarda a atualização da página (espera o elemento sumir)
        print("→ Aguardando atualização do DOM após Atividade")
        wait.until(EC.staleness_of(atividade_element_raw))

        driver.switch_to.default_content()
        driver.switch_to.frame(iframe)

        mensagem_discriminacao = 'CNH AVISTA'
        mensagem_descricao = 'PACOTE PARCIAL'


        discriminacao = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_txt_Discriminacao"))
        )

        discriminacao.send_keys(mensagem_discriminacao)


        descricao = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_txt_Descricao"))
        )

        descricao.clear()
        descricao.send_keys("PACOTE PARCIAL")

        campo_valor = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_txt_Valor"))
        )

        # Limpa e insere o valor desejado
        campo_valor.clear()
        campo_valor.send_keys(valor_total)


        #Clicka no check
        botao_adicionar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_ibtn_Adicao"))
        )

        botao_adicionar.click()

        # Aguarda a atualização do DOM após a interação
        wait.until(EC.staleness_of(botao_adicionar))

        driver.switch_to.default_content()
        driver.switch_to.frame(iframe)

        botao_avancar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_btn_Avancar_Tomador"))
        )
        botao_avancar.click()

        try:
            radio_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_rbl_Tipo_Tomador_1"))
            )
            print("Elemento radio button encontrado!")
            radio_button.click()
        except Exception as e:
            print(f"Erro ao encontrar o radio button: {e}")
            # Debugar o conteúdo do iframe
            print("HTML do iframe atual:")
            print(driver.page_source[:500])  # Mostra os primeiros 500 caracteres para debug




        campo_cpf = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_txt_Cpf"))
        )
        campo_cpf.clear()
        campo_cpf.send_keys(cpf_cliente)

        campo_nome = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_txt_Razao_Social"))
        )
        campo_nome.clear()
        campo_nome.send_keys(nome_cliente)

        segundo_avancar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_btn_Avancar"))
        )

        # Rola até o botão para garantir que está visível
        driver.execute_script("arguments[0].scrollIntoView(true);", segundo_avancar)
        time.sleep(0.5)  # Pequena pausa após a rolagem

        # Clica no botão
        segundo_avancar.click()

        botao_conclusao = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_btn_Avanvar_Conclusao"))
        )

        # Rola até o botão para garantir que está visível
        driver.execute_script("arguments[0].scrollIntoView(true);", botao_conclusao)
        time.sleep(0.5)  # Pequena pausa após a rolagem

        # Clica no botão
        botao_conclusao.click()

        botao_emitir = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_btn_Salvar"))
        )

        # Rola até o botão para garantir que está visível
        driver.execute_script("arguments[0].scrollIntoView(true);", botao_emitir)
        time.sleep(0.5)  # Pequena pausa após a rolagem

        # Clica no botão
        botao_emitir.click()
        processados += 1
        time.sleep(5)

    time.sleep(5)

    time.sleep(10)
        
        
    driver.quit()

    with open(arquivo_log, 'a', encoding='utf-8') as log:
        log.write("\n" + "=" * 50 + "\n")
        log.write(f"Processamento concluído em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write(f"Total de registros: {total}\n")
        log.write(f"Processados com sucesso: {processados}\n")
        log.write(f"Falhas: {falhas}\n")
        
    print(f"\nProcessamento concluído. Verifique o arquivo '{arquivo_log}' para detalhes sobre as falhas.")


