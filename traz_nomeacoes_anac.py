# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 08:40:50 2021

Exemplo
data = '31-03-2021'

@author: paulo
"""

import requests, json, bs4
from datetime import datetime


# Formato data 'dd-mm-aaaa' ; 
def main(data:str=''):
    
    header_req = {
    'Accept' : '*/*',
    'DNT': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
    'X-Requested-With':'XMLHttpRequest'
    }
    
    def pega_fonte(data:str='', secao:str='2'):
        
        if not data: data = datetime.now().strftime("%d-%m-%Y")
        
        res = requests.get('https://www.in.gov.br/leiturajornal?data={}&secao=do{}#daypicker'.format(
        data, secao),
        headers=header_req)
    
        res.raise_for_status()
    
        info_json = res.text.find('<script id="params" type="application/json">')
        info_json = res.text[info_json + len('<script id="params" type="application/json">'):].strip()
        info_json = info_json[:info_json.find('</script>')].strip()
        
        return json.loads(info_json) 
    

    def seleciona_anac(jsonArray):
        anac = [dic for dic in jsonArray if 'Aviação' in dic['hierarchyStr'] and dic['artType'] == 'Portaria']
        
        return ['https://www.in.gov.br/web/dou/-/{}'.format(dic['urlTitle']) for dic in anac]
    
    
    def baixa_normas(urls):
        textos, tudo_ok = [], True
        for url in urls:        
            res = requests.get(url)
            
            if res.status_code != requests.codes.ok: tudo_ok = False
            
            sopa = bs4.BeautifulSoup(res.text, 'html.parser')
            textos.append(sopa.find("div", {"class":"texto-dou"}).text.strip()) 
            
        return textos, tudo_ok
    
    
    def corta_texto_interesse(textos_completos):
        
        termos= ['DESIGNAR', 'NOMEAR', 'EXONERAR', 'DISPENSAR']
        
        textos_selecionados = []
        
        for texto in textos_completos:
            if ' cargo ' not in texto.lower(): continue
            
            for termo in termos:
                corte = texto.upper().find(termo)
                
                if corte > 0: 
                    textos_selecionados.append(texto[corte:])
                    break
                
        return textos_selecionados
    
    
    def escreve_txt(textos_selecionados):
        textos_selecionados = '\n-------------------\n'.join(textos_selecionados)
        relatorio_txt = open('nomeacoes.txt', 'w')
        relatorio_txt.write(textos_selecionados)
        relatorio_txt.close()

               
    info_json = pega_fonte(data)
    
    urls = seleciona_anac(jsonArray = info_json['jsonArray'])
    
    textos_completos_anac, tudo_ok = baixa_normas(urls)
    
    textos_selecionados = corta_texto_interesse(textos_completos_anac)
    
    if not tudo_ok: print('\nHOUVERAM ERROS NA EXECUÇÃO, CONSIDERE EXECUTAR NOVAMENTE!')
    
    if textos_selecionados:
        print('\nN LOCALIZADAS:', len(textos_selecionados))
        escreve_txt(textos_selecionados)
    else:
        print('\nNENHUMA LOCALIZADA!')
        
    
            

