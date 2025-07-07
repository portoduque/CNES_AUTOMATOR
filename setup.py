#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup automático para CNES Automator Fast
Este script configura automaticamente o ambiente para uso do CNES Automator
"""

import os
import subprocess
import sys
import json

def verificar_python():
    """Verifica se o Python está na versão adequada"""
    print("🔍 Verificando versão do Python...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ é necessário. Versão atual:", sys.version)
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    return True

def instalar_dependencias():
    """Instala as dependências necessárias"""
    print("\n📦 Instalando dependências...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp>=3.8.0"])
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências")
        return False

def criar_arquivos_exemplo():
    """Cria arquivos de exemplo se não existirem"""
    print("\n📁 Criando arquivos de exemplo...")
    
    # Exemplo de códigos CNES
    if not os.path.exists("exemplo_codigos_cnes.json"):
        exemplo_codigos = {
            "codigos": [
                "2077469",
                "2077477", 
                "2077485",
                "2077493",
                "2077507"
            ]
        }
        with open("exemplo_codigos_cnes.json", "w", encoding="utf-8") as f:
            json.dump(exemplo_codigos, f, ensure_ascii=False, indent=2)
        print("✅ Criado: exemplo_codigos_cnes.json")
    
    # Exemplo de macrorregião
    if not os.path.exists("exemplo_macrorregiao.json"):
        exemplo_macro = {
            "macrorregiao_regiao_saude_municipios": [
                {
                    "codigo_municipio": "150010",
                    "nome_municipio": "Abaetetuba",
                    "uf": "PA",
                    "macrorregiao_saude": "Metropolitana I",
                    "regiao_saude": "Metropolitana I"
                },
                {
                    "codigo_municipio": "150020",
                    "nome_municipio": "Acarí",
                    "uf": "PA",
                    "macrorregiao_saude": "Metropolitana II",
                    "regiao_saude": "Metropolitana II"
                }
            ]
        }
        with open("exemplo_macrorregiao.json", "w", encoding="utf-8") as f:
            json.dump(exemplo_macro, f, ensure_ascii=False, indent=2)
        print("✅ Criado: exemplo_macrorregiao.json")

def verificar_arquivos():
    """Verifica se os arquivos principais existem"""
    print("\n🔍 Verificando arquivos...")
    
    arquivos_obrigatorios = [
        "cnes_automator_fast.py",
        "requirements.txt"
    ]
    
    todos_ok = True
    for arquivo in arquivos_obrigatorios:
        if os.path.exists(arquivo):
            print(f"✅ {arquivo}")
        else:
            print(f"❌ {arquivo} não encontrado")
            todos_ok = False
    
    return todos_ok

def main():
    """Função principal do setup"""
    print("🏥 CNES AUTOMATOR FAST - SETUP AUTOMÁTICO")
    print("=" * 50)
    
    # Verifica Python
    if not verificar_python():
        print("\n❌ Setup falhou: Python inadequado")
        return
    
    # Verifica arquivos
    if not verificar_arquivos():
        print("\n❌ Setup falhou: Arquivos principais não encontrados")
        return
    
    # Instala dependências
    if not instalar_dependencias():
        print("\n❌ Setup falhou: Erro na instalação de dependências")
        return
    
    # Cria arquivos de exemplo
    criar_arquivos_exemplo()
    
    # Cria pasta de outputs
    if not os.path.exists("outputs"):
        os.makedirs("outputs")
        print("✅ Criada pasta: outputs/")
    
    print("\n🎉 SETUP CONCLUÍDO COM SUCESSO!")
    print("=" * 50)
    print("📋 Próximos passos:")
    print("1. Edite o arquivo 'exemplo_codigos_cnes.json' com seus códigos CNES")
    print("2. Edite o arquivo 'exemplo_macrorregiao.json' com seus dados de macrorregião")
    print("3. Execute: python cnes_automator_fast.py")
    print("4. Use os arquivos de exemplo quando solicitado")
    print("\n🚀 Projeto pronto para uso!")

if __name__ == "__main__":
    main()
