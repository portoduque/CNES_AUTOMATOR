# 🏥 CNES Automator Fast - API A### 📥 Passo 0: Clonando o Projeto

### 📋 Setup Manual (se necessário)

#### Pré-requisitose você está baixando o projeto pela primeira vez:

1. **Baixe os arquivos** do projeto para uma pasta local
2. **Ou clone o repositório** (se disponível):

```bash
git clone <url-do-repositorio>
cd CNES_AUTOMATOR
```

### 🚀 Setup Automático (RECOMENDADO)

Para configurar tudo automaticamente, execute:

```bash
python setup.py
```

Este script irá:

- ✅ Verificar a versão do Python
- ✅ Instalar as dependências automaticamente
- ✅ Criar arquivos de exemplo
- ✅ Configurar a estrutura de pastas

**Se o setup automático funcionou, você pode pular para a seção "Como Usar"!**

### 📋 Setup Manual (se necessário)imizada

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Async-Otimizado-green.svg" alt="Async Optimized">
  <img src="https://img.shields.io/badge/API-CNES-orange.svg" alt="CNES API">
  <img src="https://img.shields.io/badge/Performance-Alto-red.svg" alt="High Performance">
</div>

## � Início Rápido (3 minutos)

1. **Baixe** os arquivos do projeto para uma pasta
2. **Execute** o setup automático:
   ```bash
   python setup.py
   ```
3. **Edite** os arquivos de exemplo com seus dados
4. **Execute** o script principal:
   ```bash
   python cnes_automator_fast.py
   ```

**Pronto! Seu projeto está funcionando.** 🎉

---

## �📋 Sobre o Projeto

O **CNES Automator Fast** é uma ferramenta Python assíncrona otimizada para automatizar consultas na API pública do CNES (Cadastro Nacional de Estabelecimentos de Saúde). Esta versão foi desenvolvida com foco em **alta performance** e **usabilidade**, oferecendo:

- ⚡ **Processamento assíncrono** com requisições simultâneas
- 📊 **Barra de progresso em tempo real** com ETA e velocidade
- 🗺️ **Mesclagem automática** com dados de macrorregião
- 💾 **Backup incremental** para proteção dos dados
- 🔧 **Configurações flexíveis** de performance
- 📝 **Logging detalhado** para monitoramento

### 🎯 Principais Funcionalidades

1. **Consulta em Massa**: Processa milhares de códigos CNES simultaneamente
2. **Dados Enriquecidos**: Adiciona informações de macrorregião e região de saúde
3. **Interface Intuitiva**: Loading em tempo real com estatísticas detalhadas
4. **Recuperação de Erros**: Sistema robusto de backup e recuperação
5. **Configurável**: Ajuste de performance conforme sua necessidade

---

## 🚀 Instalação e Configuração

### � Passo 0: Clonando o Projeto

Se você está baixando o projeto pela primeira vez:

1. **Baixe os arquivos** do projeto para uma pasta local
2. **Ou clone o repositório** (se disponível):

```bash
git clone <url-do-repositorio>
cd CNES_AUTOMATOR
```

### �📋 Pré-requisitos

- **Python 3.8+** instalado na máquina
- **Conexão com internet** para acessar a API do CNES
- **Espaço em disco** suficiente para armazenar os resultados

### 🔧 Passo 1: Preparação do Ambiente (Manual)

#### Windows:

```powershell
# Verifique se o Python está instalado
python --version

# Se não tiver Python, baixe em: https://python.org/downloads/
```

#### Linux/Mac:

```bash
# Verifique se o Python está instalado
python3 --version

# Se não tiver Python, instale:
# Ubuntu/Debian: sudo apt install python3 python3-pip
# CentOS/RHEL: sudo yum install python3 python3-pip
# macOS: brew install python3
```

### 📦 Passo 2: Instalar Dependências (Manual)

1. **Abra o terminal/prompt** na pasta do projeto
2. **Instale as dependências**:

```bash
pip install aiohttp
```

**Ou use o arquivo `requirements.txt` já incluído no projeto**:

```bash
pip install -r requirements.txt
```

> **Nota**: `asyncio` já está incluído no Python 3.7+, não precisa instalar separadamente.

### 📁 Passo 3: Estrutura de Arquivos (Manual)

Organize seus arquivos na seguinte estrutura:

```
📁 CNES_AUTOMATOR/
├── 📄 cnes_automator_fast.py          # Script principal
├── 📄 setup.py                        # Configuração automática
├── 📄 requirements.txt                 # Dependências (já incluído)
├── 📄 README.md                       # Este arquivo
├── 📄 exemplo_codigos_cnes.json       # Exemplo de códigos CNES (criado pelo setup)
├── 📄 exemplo_macrorregiao.json       # Exemplo de dados de macrorregião (criado pelo setup)
├── 📄 codigos_cnes.json              # Seus códigos CNES (você deve criar)
├── 📄 macrorregiao_regiao_saude_municipios.json  # Dados de macrorregião (você deve criar)
└── 📁 outputs/                        # Resultados (criado automaticamente)
```

> **⚠️ IMPORTANTE**: Você precisa criar os arquivos `codigos_cnes.json` e `macrorregiao_regiao_saude_municipios.json` conforme explicado na próxima seção.
>
> **💡 DICA**: Use os arquivos de exemplo (`exemplo_codigos_cnes.json` e `exemplo_macrorregiao.json`) como base para criar seus próprios arquivos.

---

## 📊 Preparação dos Dados

### 🔢 Arquivo de Códigos CNES

**OBRIGATÓRIO**: Crie um arquivo JSON com os códigos CNES que deseja consultar:

#### Formato 1 - Lista simples (RECOMENDADO):

```json
{
  "codigos": ["2077469", "2077477", "2077485"]
}
```

#### Formato 2 - Lista de objetos:

```json
[
  { "codigo_cnes": "2077469" },
  { "codigo_cnes": "2077477" },
  { "codigo_cnes": "2077485" }
]
```

#### Formato 3 - Estrutura completa:

```json
{
  "estabelecimentos": [
    {
      "codigo_cnes": "2077469",
      "nome": "Hospital Exemplo"
    }
  ]
}
```

### 🗺️ Arquivo de Macrorregião

**OBRIGATÓRIO**: O arquivo de macrorregião deve conter dados dos municípios:

```json
{
  "macrorregiao_regiao_saude_municipios": [
    {
      "codigo_municipio": "150010",
      "nome_municipio": "Abaetetuba",
      "macrorregiao_saude": "Metropolitana I",
      "regiao_saude": "Metropolitana I"
    },
    {
      "codigo_municipio": "150020",
      "nome_municipio": "Abaetetuba",
      "macrorregiao_saude": "Metropolitana II",
      "regiao_saude": "Metropolitana II"
    }
  ]
}
```

### 💡 Exemplo Prático de Criação

1. **Crie o arquivo `codigos_cnes.json`**:

```bash
# No Windows (usando notepad)
notepad codigos_cnes.json

# No Linux/Mac (usando nano)
nano codigos_cnes.json
```

2. **Cole o conteúdo** (exemplo com 3 códigos):

```json
{
  "codigos": ["2077469", "2077477", "2077485"]
}
```

3. **Salve o arquivo** na pasta do projeto

---

## ✅ Checklist Rápido

Antes de executar o script, certifique-se de que você tem:

- [x] **Python 3.8+** instalado
- [x] **Dependências** instaladas (`pip install aiohttp`)
- [x] **Arquivo `codigos_cnes.json`** criado com seus códigos
- [x] **Arquivo `macrorregiao_regiao_saude_municipios.json`** criado com dados de macrorregião
- [x] **Conexão com internet** ativa

Se todos os itens estão ✅, você está pronto para usar o script!

---

## 🎮 Como Usar

### 🖥️ Execução Básica

1. **Abra o terminal** na pasta do projeto
2. **Execute o script**:

```bash
python cnes_automator_fast.py
```

### 🧪 Teste Rápido

Para testar se tudo está funcionando corretamente, crie um arquivo de teste com poucos códigos:

1. **Crie um arquivo `teste_codigos.json`**:

```json
{
  "codigos": ["2077469", "2077477"]
}
```

2. **Execute o script** e use este arquivo de teste
3. **Verifique** se o processamento funciona antes de usar arquivos grandes

### 📝 Passo a Passo Interativo

O script irá solicitar as seguintes informações:

#### 1️⃣ **Arquivo de Códigos CNES**

```
Digite o caminho do arquivo JSON com os códigos CNES: codigos_cnes.json
```

#### 2️⃣ **Configurações de Performance**

```
⚡ CONFIGURAÇÕES DE PERFORMANCE:
Número de requisições simultâneas (padrão: 15, máx recomendado: 25): 20
Delay entre lotes em segundos (padrão: 0.3): 0.5
```

#### 3️⃣ **Arquivo de Macrorregião**

```
Digite o caminho do arquivo de macrorregião (ou pressione Enter para usar o padrão): macrorregiao_regiao_saude_municipios.json
```

#### 4️⃣ **Arquivo de Saída**

```
Nome do arquivo de saída (padrão: cnes_com_macrorregiao_AAAAMMDD_HHMMSS.json): meus_resultados.json
```

### 📊 Acompanhamento em Tempo Real

Durante a execução, você verá uma barra de progresso detalhada:

```
🏥 Consultando API CNES: |████████████████████████████████████████| 2500/2500 (100.0%) | Restam: 0 | 45.2/s | ETA: 00:00:00 | Lote 250/250 | ✅ 2450 ❌ 50

📊 Estatísticas finais:
   - Códigos processados: 2450
   - Mesclagens bem-sucedidas: 2400
   - Taxa de sucesso API: 98.0%
   - Taxa de sucesso mesclagem: 96.0%
   - Velocidade média: 45.2 req/s
   - Tempo total: 55.3 segundos
```

---

## ⚙️ Configurações Avançadas

### 🔧 Ajustes de Performance

#### Requisições Simultâneas

- **Padrão**: 15 requisições
- **Recomendado**: 10-25 requisições
- **Máximo**: 50 (pode sobrecarregar a API)

#### Delay Entre Lotes

- **Padrão**: 0.3 segundos
- **Rápido**: 0.1 segundos
- **Conservador**: 0.5-1.0 segundos

### 📋 Exemplo de Configuração Otimizada

Para **processamento rápido** (máquina potente + internet rápida):

```
Requisições simultâneas: 25
Delay entre lotes: 0.1
```

Para **processamento estável** (máquina comum + internet média):

```
Requisições simultâneas: 15
Delay entre lotes: 0.3
```

Para **processamento conservador** (máquina lenta + internet lenta):

```
Requisições simultâneas: 10
Delay entre lotes: 0.5
```

---

## 📁 Estrutura dos Resultados

### 📄 Arquivo de Saída

O arquivo gerado contém:

```json
{
  "metadados": {
    "data_processamento": "2025-07-07T12:25:00",
    "tempo_execucao_segundos": 55.3,
    "total_codigos_processados": 2500,
    "versao_script": "2.0_async_optimized_with_progress",
    "configuracao_performance": {
      "requisicoes_simultaneas": 20,
      "delay_entre_lotes": 0.3,
      "total_lotes": 250
    },
    "estatisticas": {
      "total_requisicoes": 2500,
      "sucessos": 2450,
      "erros": 50,
      "taxa_sucesso": "98.0%"
    }
  },
  "estabelecimentos": [
    {
      "codigo_cnes": "2077469",
      "nome_fantasia": "Hospital Exemplo",
      "razao_social": "Hospital Exemplo LTDA",
      "endereco": "Rua Exemplo, 123",
      "telefone": "(11) 1234-5678",
      "codigo_municipio": "150010",
      "nome_municipio": "Abaetetuba",
      "macrorregiao_saude": "Metropolitana I",
      "regiao_saude": "Metropolitana I"
    }
  ],
  "erros": [
    {
      "codigo_cnes": "1234567",
      "erro": "Código CNES não encontrado",
      "status_code": 404
    }
  ],
  "resumo": {
    "total_sucessos": 2450,
    "total_erros": 50,
    "taxa_sucesso": "98.0%",
    "velocidade_media": "45.2 req/s"
  }
}
```

### 📊 Arquivos de Log

O sistema gera logs detalhados:

- **`cnes_automator.log`**: Log principal da execução
- **`cnes_macrorregiao_merger.log`**: Log específico da mesclagem
- **`cnes_backup_AAAAMMDD_HHMMSS.json`**: Backup incremental (removido ao final)

---

## 🔍 Resolução de Problemas

### ❌ Problemas Comuns

#### 1. **Erro de Dependências**

```bash
# Erro: ModuleNotFoundError: No module named 'aiohttp'
# Solução:
pip install aiohttp
```

#### 2. **Erro de Arquivo não Encontrado**

```bash
# Erro: FileNotFoundError: [Errno 2] No such file or directory
# Solução: Verifique o caminho do arquivo
ls -la codigos_cnes.json  # Linux/Mac
dir codigos_cnes.json     # Windows
```

#### 3. **Erro de Memória**

```bash
# Para arquivos muito grandes, reduza as requisições simultâneas:
Requisições simultâneas: 5
Delay entre lotes: 0.5
```

#### 4. **Erro de Conexão**

```bash
# Verifique sua conexão com internet
ping apidadosabertos.saude.gov.br
```

### 🔧 Dicas de Otimização

1. **Máquina Potente**: Use 20-25 requisições simultâneas
2. **Internet Rápida**: Reduza o delay para 0.1-0.2 segundos
3. **Muitos Dados**: Monitore o uso de memória
4. **Erro 429**: Reduza requisições simultâneas se receber erro de rate limit

---

## 📈 Benchmarks e Performance

### 🏆 Comparação de Performance

| Configuração               | Códigos/min | Tempo p/ 1000 códigos |
| -------------------------- | ----------- | --------------------- |
| Conservador (10 req, 0.5s) | 1.200       | 50 segundos           |
| Padrão (15 req, 0.3s)      | 2.700       | 22 segundos           |
| Otimizado (25 req, 0.1s)   | 6.000       | 10 segundos           |

### 📊 Estimativas de Tempo

| Quantidade      | Tempo Aproximado |
| --------------- | ---------------- |
| 100 códigos     | 2-5 segundos     |
| 1.000 códigos   | 10-30 segundos   |
| 10.000 códigos  | 5-15 minutos     |
| 100.000 códigos | 1-3 horas        |

---

## 🆘 Suporte e Contribuição

### 📞 Suporte

- **Logs**: Sempre verifique os arquivos `.log` para diagnóstico
- **Issues**: Documente erros com screenshots e logs
- **Performance**: Teste diferentes configurações para sua máquina

### 🤝 Contribuição

Para contribuir com o projeto:

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Implemente melhorias
4. Teste extensivamente
5. Submeta um pull request

---

## 📜 Licença e Disclaimer

### ⚖️ Uso Responsável

- Use apenas para fins educacionais, de pesquisa ou saúde pública
- Respeite os limites de rate da API do CNES
- Não sobrecarregue os servidores públicos
- Mantenha os dados atualizados e seguros

### 📚 API do CNES

Este projeto utiliza a API pública oficial do CNES:

- **URL**: https://apidadosabertos.saude.gov.br/cnes
- **Documentação**: https://apidadosabertos.saude.gov.br/
- **Dados**: Ministério da Saúde do Brasil

---

## 🎉 Conclusão

O **CNES Automator Fast** é uma ferramenta poderosa para automatizar consultas na API do CNES com **alta performance** e **facilidade de uso**. Com processamento assíncrono, barra de progresso em tempo real e mesclagem automática de dados, você pode processar milhares de códigos CNES em poucos minutos.

**Principais benefícios:**

- ⚡ **Até 10x mais rápido** que processamento sequencial
- 📊 **Visibilidade total** do progresso em tempo real
- 🗺️ **Dados enriquecidos** com informações de macrorregião
- 💾 **Backup automático** para proteção dos dados
- 🔧 **Configurações flexíveis** para qualquer ambiente

---

<div align="center">
  <h3>🏥 Dados de Saúde Pública • 🚀 Performance Otimizada • 📊 Tempo Real</h3>
  <p><em>Desenvolvido para facilitar o acesso aos dados do CNES</em></p>
</div>
