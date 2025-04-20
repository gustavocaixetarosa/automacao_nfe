import csv
import sys 
import pandas as pd
import xml.etree.ElementTree as ET
import datetime

def tratar_linha(linha):
    linha_boa = []
    for celula in linha:
        if celula != "":
            linha_boa.append(celula)
    linha_reduzida = [elemento.strip() for elemento in linha_boa]

    queremos = [0, 2, 3, 10]

    linha_ideal = []
    
    for i, celula in enumerate(linha_reduzida):
        if i in queremos:
            if i == 2:
                celula = celula.split('-')[0]
            linha_ideal.append(celula)

    return linha_ideal

def extrair_linhas(original):
    dados = []

    with open(original) as arquivo:
        is_baixa = False
        
        arquivo_csv = csv.reader(arquivo, delimiter=',')

        for linha in arquivo_csv:
            if linha and len(linha) > 0:
                primeiro_elemento = linha[0].strip()

                if primeiro_elemento.startswith('82-BAIXA'):
                    is_baixa = True
                    continue 
                elif primeiro_elemento.startswith('215-LIQUIDAÇÃO') or primeiro_elemento.startswith('68-LIQUIDAÇÃO') or primeiro_elemento.startswith('58-LIQUIDAÇÃO'):
                    is_baixa = False

                if not is_baixa:
                    if primeiro_elemento.isupper() and not primeiro_elemento[0].isdigit():
                        linha_tratada = tratar_linha(linha)
                        dados.append(linha_tratada)

    return dados

def escreve_arquivo(dados, cabecalho, end_arquivo_original):
    csv_tratado = 'sicoob/ok_' + end_arquivo_original.split('/')[1] + '.csv'

    with open(csv_tratado, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        writer.writerow(cabecalho)
        
        writer.writerows(dados)

    return csv_tratado

def processar_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    clientes = []
    codigo = None
    cpf = None
    nome = None  
    
    for table in root.findall('.//Table1'):
        text1 = table.findtext('TEXT1', '').strip()
        text3 = table.findtext('TEXT3', '').strip()
        text8 = table.findtext('TEXTO8', '').strip()
        text19 = table.findtext('TEXTO19', '').strip()
        
        if text1.startswith("Código"):
            codigo = text1.replace("Código", "").strip()
        
        if text1 == "Nome do Cliente:" and text8:
            nome = text8.strip()
        
        if text3.startswith('CPF:') and text19:
            cpf = text19.strip()
            if codigo and nome and cpf:
                cliente = {
                    'codigo': codigo,
                    'nome': nome,
                    'cpf': cpf.replace('.', '').replace('-', '')
                }
                clientes.append(cliente)
                # Reiniciar variáveis para o próximo cliente
                codigo = None
                nome = None
                cpf = None
    
    return pd.DataFrame(clientes)

if __name__ == "__main__":
    sicoob_csv = sys.argv[1]
    assuncao_xml = sys.argv[2]

    dados = extrair_linhas(sicoob_csv)

    cabecalho = ['nome_cliente', 'codigo_cliente', 'data_pagamento', 'valor_total', 'descricao']
    csv_tratado = escreve_arquivo(dados, cabecalho, sicoob_csv)

    df_xml = processar_xml(assuncao_xml)
    df_csv = pd.read_csv(csv_tratado)

    df_csv['codigo_cliente'] = df_csv['codigo_cliente'].astype(str)
    df_xml['codigo'] = df_xml['codigo'].astype(str)

    df_merged = pd.merge(df_csv, df_xml, left_on='codigo_cliente', right_on='codigo', how='left')
    df_merged.drop(columns=['codigo', 'nome', 'data_pagamento'], inplace=True)
    print(df_merged)

    hoje = datetime.date.today()
    nome_resultado = 'resultados/' + str(hoje) + '.csv'

    df_merged.to_csv(nome_resultado, index=False, encoding='utf-8')


