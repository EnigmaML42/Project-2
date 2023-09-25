import csv
import os
import re
import time
import html5lib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.support.expected_conditions import element_to_be_clickable
from selenium.common.exceptions import NoAlertPresentException



class UniversityScraper:

    default_data = {
    'Mantenedora': 'null',
    'CNPJ': 'null',
    'Natureza Jurídica': 'null',
    'Representante Legal': 'null',
    'Nome da IES - Sigla': 'null',
    'Situação': 'null',
    'Endereço': 'null',
    'Nº': 'null',
    'Complemento': 'null',
    'CEP': 'null',
    'Bairro': 'null',
    'Município': 'null',
    'UF': 'null',
    'Telefone': 'null',
    'Fax': 'null',
    'Acadêmica': 'null',
    'Sítio': 'null',
    'Administrativa': 'null',
    'Principal': 'null',
    'Tipo de Credenciamento': 'null',
    'Organização Academica': 'null',
    'Categoria Administrativa': 'null',
    'Motivo':'null'
}

    estado_foco = "PR"

    fieldnames = [
    "Mantenedora", "CNPJ", "Natureza Jurídica", "Representante Legal", 
    "Nome da IES - Sigla", "Situação", "Endereço", "Nº", "Complemento", 
    "CEP", "Bairro", "Município", "UF", "Telefone", "Fax", "Acadêmica", 
    "Sítio", "Administrativa", "Principal", "Tipo de Credenciamento", 
    "Organização Academica", "Categoria Administrativa", "Motivo"
    ]

    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--start-maximized")

    def setup_driver(self):
        driver = webdriver.Chrome(options=self.chrome_options)
        driver.implicitly_wait(10)
        #print(f"[DEBUG] Após inicialização em setup_driver: {type(driver)}")  # Log de depuração adicionado
        return driver

    def navigate_to_site(self, driver, url):
        driver.get(url)
        time.sleep(5)

    def validar_html(self, html):
        try:
            # Parse o HTML usando html5lib
            document = html5lib.parse(html)
            return True, "HTML é válido!"
        except Exception as e:
            return False, f"Erro ao validar o HTML: {str(e)}"

    def select_options(self, driver):
        estado_dropdown = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.ID, 'sel_sg_uf')))
        estado_dropdown.click()
        estado_opcao = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, f'//option[@value="{self.estado_foco}"]')))
        estado_opcao.click()
        time.sleep(3)
        checkbox_value_5 = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, "//input[@id='consulta_avancada_chk_tp_natureza_gn' and @value='5']")))
        checkbox_value_5.click()
        time.sleep(2)
        checkbox_value_4 = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, "//input[@id='consulta_avancada_chk_tp_natureza_gn' and @value='4']")))
        checkbox_value_4.click()
        time.sleep(4)

        # Clicar no botão "Pesquisar"
        botao_pesquisar = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[@type='submit' and @value='Pesquisar']")))
        botao_pesquisar.click()

        # Aguarde um pouco para garantir que a página tenha carregado completamente
        time.sleep(5)


    def click_icons(self, driver):
        MAX_ATTEMPTS = 5  # Defina o número máximo de tentativas
        attempts = 0

        while attempts < MAX_ATTEMPTS:
            try:
                # Tente localizar os ícones
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//img[@src='/emec/img/icones/icone_lupa.gif' and @title='Visualizar Detalhes da IES']")))
                
                # Se os ícones forem encontrados, saia do loop
                break
            except TimeoutException:
                # Se os ícones não forem encontrados, faça um refresh e reinicie o preenchimento do formulário
                driver.refresh()
                self.select_options(driver)
                attempts += 1
            except UnexpectedAlertPresentException:
                # Trate alertas inesperados
                try:
                    alert = driver.switch_to.alert
                    print(f"Alerta detectado: {alert.text}")
                    alert.dismiss()  # ou alert.accept() se você quiser aceitar o alerta
                except NoAlertPresentException:
                    print("Tentou fechar o alerta, mas ele já havia desaparecido.")

        if attempts == MAX_ATTEMPTS:
            print("Número máximo de tentativas atingido. Não foi possível encontrar os ícones.")

    def switch_to_desired_iframe(self, driver):
        # Espera até que o elemento desejado esteja presente no iframe
        #WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'MANTENEDORA')]")))
        iframe_wrapper = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'tabIframeWrapper')))
        iframe = iframe_wrapper.find_element(By.NAME, 'tabIframe2')
        #print(f"[DEBUG] Tentando mudar para iframe: {iframe}")  # Log de depuração adicionado
        driver.switch_to.frame(iframe)
        #print(f"[DEBUG] Mudou para iframe: {iframe}")  # Log de depuração adicionado

    def save_iframe_content(self, driver, filename, estado_sigla=None):
        if estado_sigla is None:
            estado_sigla = self.estado_foco
        current_time = datetime.now().strftime('%Y%m%d%H%M%S')
        filename_with_timestamp = f"{current_time}_{estado_sigla}_{filename}"
        with open(filename_with_timestamp, 'w', encoding='utf-8') as file:
            file.write(driver.page_source)
        return driver.page_source
        
    def switch_to_new_window(self, driver, main_window_handle):
        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
        for handle in driver.window_handles:
            if handle != main_window_handle:
                driver.switch_to.window(handle)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                break

    def close_all_secondary_windows(self, driver, main_window_handle):
        if not isinstance(driver, webdriver.Chrome):
            #print(f"[DEBUG] close_all_secondary_windows: driver é do tipo {type(driver)}")
            return
        
        """Fecha todas as janelas secundárias e retorna o foco para a janela principal."""
        for handle in driver.window_handles:
            if handle != main_window_handle:
                driver.switch_to.window(handle)
                    
                # Tratar possíveis alertas antes de fechar a janela
                try:
                    alert = driver.switch_to.alert
                    alert.accept()
                    print("Alerta detectado e aceito.")
                except:
                    print("Nenhum alerta detectado.")
                    
                driver.close()
                print(f"Janela secundária {handle} fechada.")

        # Retorna o foco para a janela principal
        driver.switch_to.window(main_window_handle)

        print("Foco retornado para a janela principal.")

    def open_csv_file(self, filename, estado_sigla=None):
        if estado_sigla is None:
            estado_sigla = self.estado_foco
        current_time = datetime.now().strftime('%Y%m%d%H%M%S')
        filename_with_timestamp = f"{current_time}_{estado_sigla}_{filename}"
        csvfile = open(filename_with_timestamp, 'a', newline='', encoding='utf-8')
        fieldnames = self.fieldnames
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if os.path.getsize(filename_with_timestamp) == 0:
            writer.writeheader()
        return csvfile, writer, filename_with_timestamp


    def close_csv_file(self, csvfile):
        csvfile.close()

    def click_on_icon(self, driver, icone):
        try:
            icone.click()
        except:
            driver.execute_script("arguments[0].click();", icone)
        
    def process_icon(self, index, driver, icone, writer, main_window_handle):
        """Processa um único ícone, extrai os dados e escreve no CSV."""
        print(f"Processando ícone {index}...")  # Registro adicionado

        self.click_on_icon(driver, icone)
        self.switch_to_new_window(driver, main_window_handle)

        time.sleep(3)

        self.switch_to_desired_iframe(driver)

        html_content = self.save_iframe_content(driver, f"iframe_content_{index}.html")

        # Validar o HTML fornecido
        html_valido = self.validar_html(html_content)

        # Se o HTML for válido, extrair as informações
        if html_valido:
            resultado = self.extrair_informacoes(html_content)
            campos_extraidos = list(resultado.keys())

            # Comparar campos extraídos com fieldnames esperados
            fieldnames = self.fieldnames
            resultado_comparacao = self.comparar_campos_com_fieldnames(campos_extraidos, fieldnames)

            # Avaliar os resultados da comparação
            if resultado_comparacao["campos_faltantes"] or resultado_comparacao["campos_extras"]:
                print(f"Discrepâncias detectadas para o ícone {index}:")
                print("Campos faltantes:", resultado_comparacao["campos_faltantes"])
                print("Campos extras:", resultado_comparacao["campos_extras"])

            data = self.default_data.copy()
            data.update(resultado)
            writer.writerow(data)
        else:
            print("Falhou durante extração")

        self.close_all_secondary_windows(driver, main_window_handle)
        driver.switch_to.window(main_window_handle)

    def extract_and_write_details(self, driver, writer):
        main_window_handle = driver.current_window_handle
        index = 0

        # Localize TODOS os ícones uma vez
        icones = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, "//img[@src='/emec/img/icones/icone_lupa.gif' and @title='Visualizar Detalhes da IES']")))
        
        while True:
            try:
                # Se todos os ícones já foram processados, saia do loop
                if index >= len(icones):
                    break

                # Processa o ícone atual
                icone = icones[index]
                self.process_icon(index, driver, icone, writer, main_window_handle)
                index += 1  # Incrementar o índice após processar com sucesso
            except TimeoutException:
                # Se o ícone não for encontrado, saia do loop
                break
            finally:
                self.close_all_secondary_windows(driver, main_window_handle)
                driver.switch_to.window(main_window_handle)


    def tratar_dados(self, dados: str, fieldnames: list) -> dict:
        # Dividir os dados em linhas
        linhas = dados.split("\n")
        
        # Inicializar um dicionário vazio para armazenar os pares chave-valor
        resultado = {}
        chave_atual = None
        valor_temp = []

        # Iterar sobre a lista de linhas
        for linha in linhas:
            linha = linha.strip()  # Limpar a linha
            
            # Verificar se a linha contém alguma das chaves do conjunto finito
            is_fieldname = any([fieldname in linha for fieldname in fieldnames])
            
            if is_fieldname:
                # Se já tivermos uma chave atual, adicione ao resultado
                if chave_atual:
                    resultado[chave_atual] = " ".join(valor_temp).strip()
                    valor_temp = []
                # Identificar qual chave está contida na linha
                chave_atual = next((fieldname for fieldname in fieldnames if fieldname in linha), None)
            else:
                valor_temp.append(linha)

        # Adicionar o último par chave-valor ao resultado
        if chave_atual:
            resultado[chave_atual] = " ".join(valor_temp).strip()

        return resultado
        

    def comparar_campos_com_fieldnames(self, campos_extraidos: list, fieldnames: list) -> dict:
        campos_faltantes = set(fieldnames) - set(campos_extraidos)
        campos_extras = set(campos_extraidos) - set(fieldnames)

        resultado = {
            "campos_faltantes": list(campos_faltantes),
            "campos_extras": list(campos_extras)
        }

        return resultado

    def extrair_informacoes(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extrair informações de toda a tabela
        dados_brutos = soup.select(".avalTabCampos .avalLinhaCampos")
        textos = [elemento.text.strip() for elemento in dados_brutos]

        # Inicializar um dicionário vazio para armazenar os pares chave-valor
        resultado = {}

        # Processar cada texto individualmente
        for texto in textos:
            # Atualizar o dicionário resultado com os pares chave-valor do texto atual
            resultado_atual = self.tratar_dados(texto, self.fieldnames)
            resultado.update(resultado_atual)

        return resultado

    def select_pagination_option(self, driver):
        try:
            # Espera até que o elemento esteja visível e clicável
            pagination_dropdown = WebDriverWait(driver, 10).until(element_to_be_clickable((By.ID, 'paginationItemCountItemdiv_listar_consulta_avancada')))
            pagination_dropdown.click()
            option_300 = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//option[@data-valor="300"]')))
            option_300.click()
            time.sleep(5)
        except TimeoutException:
            print("Dropdown de paginação não encontrado. Continuando sem alterar a opção de paginação.")



    def main(self):
        driver = self.setup_driver()
        self.navigate_to_site(driver, 'https://emec.mec.gov.br/emec')
        self.select_options(driver)
        self.click_icons(driver)

        # Verificar se o Select de paginação está presente
        try:
            pagination_dropdown = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.ID, 'paginationItemCountItemdiv_listar_consulta_avancada')))
            # Se estiver presente, selecione 300 resultados por página
            self.select_pagination_option(driver)
            # Aguarde a tabela ser carregada (adicionando um tempo de espera explícito para garantir que a tabela seja carregada)
            time.sleep(5)
        except TimeoutException:
            print("Dropdown de paginação não encontrado. Continuando sem alterar a opção de paginação.")

        csvfile, writer, filename_with_timestamp = self.open_csv_file('universidades.csv')
        default_data = self.default_data.copy()

        # Lógica de repetição para lidar com possíveis erros intermitentes
        max_retries = 3
        retries = 0
        while retries < max_retries:
            try:
                self.extract_and_write_details(driver, writer)
                print("Extração bem-sucedida!")  # Adicionado log de sucesso
                break
            except Exception as e:
                print(f"Erro na extração: {e}")
                retries += 1
                if retries < max_retries:
                    print(f"Tentando novamente ({retries}/{max_retries})...")
                else:
                    print("Número máximo de tentativas atingido. Encerrando o programa.")
                    writer.writerow(self.default_data)
                    break

        self.close_csv_file(csvfile)
        print(f"Os dados foram salvos em: {filename_with_timestamp}")
        driver.quit()


if __name__ == "__main__":
    scraper = UniversityScraper()
    scraper.main()

