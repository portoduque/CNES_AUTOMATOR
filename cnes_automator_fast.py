#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automatizador da API CNES - VERSÃO ASSÍNCRONA OTIMIZADA COM LOADING

Este script automatiza o consumo da API pública do CNES para obter dados
detalhados de estabelecimentos de saúde usando seus códigos CNES específicos.

OTIMIZAÇÕES IMPLEMENTADAS:
- Processamento assíncrono com requisições simultâneas
- Sistema de loading em tempo real com ETA
- Pool de conexões otimizado
- Backup incremental dos dados

Autor: Script Automatizado
Data: 2025
API: https://apidadosabertos.saude.gov.br/cnes/estabelecimentos/{codigo_cnes}
"""

import json
import asyncio
import aiohttp
import time
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import logging
import sys

# Configuração de logging para acompanhar o progresso
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cnes_automator.log'),
        logging.StreamHandler()
    ]
)

class ProgressTracker:
    """
    Classe para rastrear e exibir progresso em tempo real - VERSÃO APRIMORADA
    """
    
    def __init__(self, total_items: int, description: str = "Processando"):
        self.total_items = total_items
        self.processed_items = 0
        self.description = description
        self.start_time = time.time()
        self.last_update = 0
        self.success_count = 0
        self.error_count = 0
        self.last_rates = []  # Para calcular velocidade média dos últimos segundos
        
    def update(self, processed: int, current_batch: int = None, total_batches: int = None, 
               success_count: int = None, error_count: int = None):
        """
        Atualiza o progresso e exibe informações detalhadas
        """
        self.processed_items = processed
        current_time = time.time()
        
        # Atualiza contadores se fornecidos
        if success_count is not None:
            self.success_count = success_count
        if error_count is not None:
            self.error_count = error_count
        
        # Atualiza a cada 0.3 segundos para feedback mais frequente
        if current_time - self.last_update < 0.3 and processed < self.total_items:
            return
            
        self.last_update = current_time
        
        # Calcula estatísticas
        elapsed_time = current_time - self.start_time
        remaining_items = self.total_items - processed
        
        if elapsed_time > 0:
            current_rate = processed / elapsed_time
            
            # Mantém histórico das últimas 10 medições para velocidade mais estável
            self.last_rates.append(current_rate)
            if len(self.last_rates) > 10:
                self.last_rates.pop(0)
            
            # Velocidade média das últimas medições
            avg_rate = sum(self.last_rates) / len(self.last_rates)
            
            if avg_rate > 0:
                eta_seconds = remaining_items / avg_rate
                eta = str(timedelta(seconds=int(eta_seconds)))
            else:
                eta = "Calculando..."
        else:
            avg_rate = 0
            eta = "Calculando..."
        
        # Calcula porcentagem
        percentage = (processed / self.total_items) * 100
        
        # Cria barra de progresso mais detalhada
        bar_length = 40
        filled_length = int(bar_length * processed // self.total_items)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # Formata informações do lote se fornecidas
        batch_info = ""
        if current_batch is not None and total_batches is not None:
            batch_info = f" | Lote {current_batch}/{total_batches}"
        
        # Informações de sucesso/erro
        status_info = ""
        if self.success_count > 0 or self.error_count > 0:
            status_info = f" | ✅ {self.success_count} ❌ {self.error_count}"
        
        # Estimativa de tempo formatada
        eta_display = eta if eta != "Calculando..." else "⏳ Calc..."
        
        # Monta a linha de progresso detalhada
        progress_line = (
            f"\r{self.description}: |{bar}| "
            f"{processed:,}/{self.total_items:,} ({percentage:.1f}%) "
            f"| Restam: {remaining_items:,} | {avg_rate:.1f}/s | ETA: {eta_display}{batch_info}{status_info}"
        )
        
        # Limita o tamanho da linha para evitar problemas no terminal
        if len(progress_line) > 120:
            progress_line = progress_line[:117] + "..."
        
        # Exibe o progresso
        sys.stdout.write(progress_line)
        sys.stdout.flush()
        
        # Se terminou, pula linha
        if processed >= self.total_items:
            print()  # Nova linha no final
    
    def finish(self):
        """
        Finaliza o progresso com estatísticas detalhadas
        """
        elapsed_time = time.time() - self.start_time
        rate = self.total_items / elapsed_time if elapsed_time > 0 else 0
        
        print(f"\n✅ {self.description} concluído!")
        print(f"📊 Total processado: {self.total_items:,}")
        print(f"⏱️ Tempo total: {elapsed_time:.1f}s ({timedelta(seconds=int(elapsed_time))})")
        print(f"⚡ Velocidade média: {rate:.1f} req/s")
        
        if self.success_count > 0 or self.error_count > 0:
            success_rate = (self.success_count / self.total_items) * 100 if self.total_items > 0 else 0
            print(f"✅ Sucessos: {self.success_count:,} ({success_rate:.1f}%)")
            print(f"❌ Erros: {self.error_count:,} ({100-success_rate:.1f}%)")
        
        print("-" * 50)

class DateTimeEncoder(json.JSONEncoder):
    """
    Encoder customizado para serializar objetos datetime
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class CNESAPIAutomator:
    """
    Classe principal para automatizar consultas na API CNES - VERSÃO ASSÍNCRONA OTIMIZADA
    """
    
    def __init__(self, concurrent_requests: int = 10, delay_between_batches: float = 0.5):
        """
        Inicializa o automatizador assíncrono
        
        Args:
            concurrent_requests (int): Número de requisições simultâneas (padrão: 10)
            delay_between_batches (float): Tempo de espera entre lotes (padrão: 0.5s)
        """
        self.base_url = "https://apidadosabertos.saude.gov.br/cnes/estabelecimentos"
        self.concurrent_requests = concurrent_requests
        self.delay_between_batches = delay_between_batches
        
        # Headers para as requisições
        self.headers = {
            'User-Agent': 'CNES-Automator/2.0-AsyncOptimized-WithProgress',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Estatísticas da execução
        self.stats = {
            'total_requisicoes': 0,
            'sucessos': 0,
            'erros': 0,
            'codigos_invalidos': 0,
            'erros_conexao': 0,
            'inicio_execucao': None,
            'fim_execucao': None
        }

    def carregar_codigos_cnes(self, arquivo_entrada: str) -> List[str]:
        """
        Carrega a lista de códigos CNES de um arquivo JSON
        
        Args:
            arquivo_entrada (str): Caminho para o arquivo JSON com os códigos
            
        Returns:
            List[str]: Lista de códigos CNES
        """
        logging.info(f"📂 Carregando códigos CNES do arquivo: {arquivo_entrada}")
        
        try:
            with open(arquivo_entrada, 'r', encoding='utf-8') as arquivo:
                dados = json.load(arquivo)
            
            # Extrai os códigos CNES do arquivo
            codigos = []
            
            # Se for uma lista de objetos com campo 'codigo_cnes'
            if isinstance(dados, list):
                for item in dados:
                    if isinstance(item, dict) and 'codigo_cnes' in item:
                        codigos.append(str(item['codigo_cnes']))
                    elif isinstance(item, (str, int)):
                        codigos.append(str(item))
            
            # Se for um objeto com campo 'estabelecimentos'
            elif isinstance(dados, dict):
                if 'estabelecimentos' in dados:
                    for estabelecimento in dados['estabelecimentos']:
                        if 'codigo_cnes' in estabelecimento:
                            codigos.append(str(estabelecimento['codigo_cnes']))
                elif 'codigo_cnes' in dados:
                    codigos.append(str(dados['codigo_cnes']))
                elif 'codigos' in dados:
                    codigos.extend([str(codigo) for codigo in dados['codigos']])
            
            # Remove duplicatas e códigos vazios
            codigos = list(set([codigo for codigo in codigos if codigo.strip()]))
            
            logging.info(f"✅ Carregados {len(codigos)} códigos CNES únicos")
            
            if not codigos:
                raise ValueError("Nenhum código CNES válido encontrado no arquivo")
            
            return codigos
            
        except Exception as e:
            logging.error(f"❌ Erro ao carregar arquivo: {e}")
            raise

    async def consultar_estabelecimento_async(self, session: aiohttp.ClientSession, codigo_cnes: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Consulta um estabelecimento específico na API CNES de forma assíncrona
        
        Args:
            session (aiohttp.ClientSession): Sessão HTTP assíncrona
            codigo_cnes (str): Código CNES do estabelecimento
            
        Returns:
            Tuple[bool, Dict]: (sucesso, dados_ou_erro)
        """
        url = f"{self.base_url}/{codigo_cnes}"
        
        try:
            # Incrementa contador de requisições
            self.stats['total_requisicoes'] += 1
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    try:
                        dados = await response.json()
                        
                        # Adiciona metadados ao estabelecimento
                        if isinstance(dados, dict):
                            dados['_metadata'] = {
                                'consultado_em': datetime.now().isoformat(),
                                'codigo_cnes_consultado': codigo_cnes,
                                'url_consultada': url
                            }
                        
                        self.stats['sucessos'] += 1
                        return True, dados
                        
                    except Exception as json_error:
                        erro = {
                            'codigo_cnes': codigo_cnes,
                            'erro': 'Resposta não é um JSON válido',
                            'status_code': response.status,
                            'detalhes': str(json_error)
                        }
                        self.stats['erros'] += 1
                        return False, erro
                        
                elif response.status == 404:
                    erro = {
                        'codigo_cnes': codigo_cnes,
                        'erro': 'Código CNES não encontrado',
                        'status_code': 404,
                        'url_consultada': url
                    }
                    self.stats['codigos_invalidos'] += 1
                    return False, erro
                    
                else:
                    erro = {
                        'codigo_cnes': codigo_cnes,
                        'erro': f'Erro HTTP {response.status}',
                        'status_code': response.status,
                        'url_consultada': url
                    }
                    self.stats['erros'] += 1
                    return False, erro
                    
        except asyncio.TimeoutError:
            erro = {
                'codigo_cnes': codigo_cnes,
                'erro': 'Timeout na requisição',
                'detalhes': 'A requisição demorou mais que 15 segundos',
                'url_consultada': url
            }
            self.stats['erros_conexao'] += 1
            return False, erro
            
        except Exception as e:
            erro = {
                'codigo_cnes': codigo_cnes,
                'erro': 'Erro inesperado',
                'detalhes': str(e),
                'url_consultada': url
            }
            self.stats['erros'] += 1
            return False, erro

    async def processar_lote_codigos(self, session: aiohttp.ClientSession, codigos_lote: List[str]) -> List[Tuple[bool, Dict[str, Any]]]:
        """
        Processa um lote de códigos CNES de forma assíncrona
        """
        tarefas = []
        for codigo in codigos_lote:
            tarefa = self.consultar_estabelecimento_async(session, codigo)
            tarefas.append(tarefa)
        
        # Executa todas as tarefas do lote simultaneamente
        resultados = await asyncio.gather(*tarefas, return_exceptions=True)
        
        # Processa exceções
        resultados_limpos = []
        for i, resultado in enumerate(resultados):
            if isinstance(resultado, Exception):
                erro = {
                    'codigo_cnes': codigos_lote[i],
                    'erro': 'Exceção durante processamento',
                    'detalhes': str(resultado)
                }
                resultados_limpos.append((False, erro))
            else:
                resultados_limpos.append(resultado)
        
        return resultados_limpos

    def salvar_backup_incremental(self, estabelecimentos: List[Dict], erros: List[Dict], arquivo_backup: str):
        """
        Salva backup incremental dos dados durante o processamento
        """
        try:
            dados_backup = {
                'timestamp_backup': datetime.now().isoformat(),
                'estabelecimentos_processados': len(estabelecimentos),
                'erros_encontrados': len(erros),
                'estabelecimentos': estabelecimentos,
                'erros': erros
            }
            
            with open(arquivo_backup, 'w', encoding='utf-8') as arquivo:
                json.dump(dados_backup, arquivo, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
                
        except Exception as e:
            logging.warning(f"⚠️ Erro ao salvar backup: {e}")

    async def processar_lista_codigos(self, codigos_cnes: List[str]) -> Dict[str, Any]:
        """
        Processa uma lista de códigos CNES de forma assíncrona otimizada com loading em tempo real
        
        Args:
            codigos_cnes (List[str]): Lista de códigos CNES para consultar
            
        Returns:
            Dict[str, Any]: Dados consolidados com estabelecimentos e erros
        """
        # Exibe informações iniciais detalhadas
        print("=" * 60)
        print("🚀 CNES AUTOMATOR - PROCESSAMENTO ASSÍNCRONO OTIMIZADO")
        print("=" * 60)
        print(f"📋 Total de códigos CNES: {len(codigos_cnes):,}")
        print(f"⚡ Requisições simultâneas: {self.concurrent_requests}")
        print(f"⏱️ Delay entre lotes: {self.delay_between_batches}s")
        
        # Calcula estimativa inicial
        estimativa_tempo = len(codigos_cnes) / (self.concurrent_requests * (1/self.delay_between_batches))
        print(f"🔮 Tempo estimado: ~{estimativa_tempo:.1f}s ({timedelta(seconds=int(estimativa_tempo))})")
        
        # Divide os códigos em lotes
        lotes = []
        for i in range(0, len(codigos_cnes), self.concurrent_requests):
            lote = codigos_cnes[i:i + self.concurrent_requests]
            lotes.append(lote)
        
        print(f"📦 Dividido em {len(lotes)} lotes")
        print("=" * 60)
        
        logging.info(f"🚀 Iniciando processamento assíncrono de {len(codigos_cnes)} códigos CNES")
        logging.info(f"⚡ Configuração: {self.concurrent_requests} requisições simultâneas")
        
        self.stats['inicio_execucao'] = datetime.now().isoformat()
        
        # Estruturas para armazenar resultados
        estabelecimentos_validos = []
        erros_encontrados = []
        
        # Arquivo de backup incremental
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_backup = f"cnes_backup_{timestamp}.json"
        
        logging.info(f"📦 Dividido em {len(lotes)} lotes para processamento")
        
        # Inicializa o tracker de progresso
        progress_tracker = ProgressTracker(len(codigos_cnes), "🏥 Consultando API CNES")
        
        # Configurações do connector para otimização
        connector = aiohttp.TCPConnector(
            limit=self.concurrent_requests + 5,  # Pool de conexões
            limit_per_host=self.concurrent_requests,
            ttl_dns_cache=300,  # Cache DNS por 5 minutos
            use_dns_cache=True,
        )
        
        # Timeout personalizado
        timeout = aiohttp.ClientTimeout(total=15, connect=5)
        
        try:
            async with aiohttp.ClientSession(
                headers=self.headers,
                connector=connector,
                timeout=timeout
            ) as session:
                
                for i, lote in enumerate(lotes, 1):
                    # Processa o lote
                    resultados_lote = await self.processar_lote_codigos(session, lote)
                    
                    # Processa os resultados
                    for j, (sucesso, resultado) in enumerate(resultados_lote):
                        if sucesso:
                            if isinstance(resultado, dict) and '_metadata' in resultado:
                                resultado['_metadata']['indice_processamento'] = (i-1) * self.concurrent_requests + j + 1
                            estabelecimentos_validos.append(resultado)
                        else:
                            erros_encontrados.append(resultado)
                    
                    # Atualiza o progresso com informações detalhadas
                    processados = min(i * self.concurrent_requests, len(codigos_cnes))
                    progress_tracker.update(
                        processed=processados, 
                        current_batch=i, 
                        total_batches=len(lotes),
                        success_count=len(estabelecimentos_validos),
                        error_count=len(erros_encontrados)
                    )
                    
                    # Salva backup a cada 5 lotes
                    if i % 5 == 0:
                        self.salvar_backup_incremental(estabelecimentos_validos, erros_encontrados, arquivo_backup)
                    
                    # Pausa entre lotes (exceto no último)
                    if i < len(lotes):
                        await asyncio.sleep(self.delay_between_batches)
        
        except Exception as e:
            logging.error(f"❌ Erro durante sessão assíncrona: {e}")
            raise
        
        finally:
            # Fecha o connector
            await connector.close()
        
        # Finaliza o progresso
        progress_tracker.finish()
        
        self.stats['fim_execucao'] = datetime.now().isoformat()
        
        # Calcula tempo de execução
        inicio = datetime.fromisoformat(self.stats['inicio_execucao'])
        fim = datetime.fromisoformat(self.stats['fim_execucao'])
        tempo_execucao = (fim - inicio).total_seconds()
        
        # Consolida os resultados finais
        resultado_consolidado = {
            'metadados': {
                'data_processamento': self.stats['fim_execucao'],
                'tempo_execucao_segundos': tempo_execucao,
                'fonte_api': self.base_url,
                'total_codigos_processados': len(codigos_cnes),
                'versao_script': '2.0_async_optimized_with_progress',
                'configuracao_performance': {
                    'requisicoes_simultaneas': self.concurrent_requests,
                    'delay_entre_lotes': self.delay_between_batches,
                    'total_lotes': len(lotes)
                },
                'estatisticas': self.stats.copy()
            },
            'estabelecimentos': estabelecimentos_validos,
            'erros': erros_encontrados,
            'resumo': {
                'total_sucessos': len(estabelecimentos_validos),
                'total_erros': len(erros_encontrados),
                'taxa_sucesso': f"{(len(estabelecimentos_validos)/len(codigos_cnes)*100):.1f}%" if codigos_cnes else "0%",
                'velocidade_media': f"{len(codigos_cnes)/tempo_execucao:.1f} req/s" if tempo_execucao > 0 else "N/A"
            }
        }
        
        logging.info(f"✅ Processamento assíncrono concluído!")
        logging.info(f"📈 Sucessos: {len(estabelecimentos_validos)}")
        logging.info(f"❌ Erros: {len(erros_encontrados)}")
        logging.info(f"📊 Taxa de sucesso: {resultado_consolidado['resumo']['taxa_sucesso']}")
        logging.info(f"⚡ Velocidade média: {resultado_consolidado['resumo']['velocidade_media']}")
        logging.info(f"⏱️ Tempo total: {tempo_execucao:.1f} segundos")
        
        # Remove arquivo de backup se processamento foi bem-sucedido
        try:
            if os.path.exists(arquivo_backup):
                os.remove(arquivo_backup)
                logging.info(f"🗑️ Backup temporário removido: {arquivo_backup}")
        except:
            pass
        
        return resultado_consolidado

    def salvar_resultados(self, dados: Dict[str, Any], arquivo_saida: str):
        """
        Salva os resultados consolidados em um arquivo JSON com validação
        
        Args:
            dados (Dict[str, Any]): Dados consolidados para salvar
            arquivo_saida (str): Caminho do arquivo de saída
        """
        try:
            logging.info(f"💾 Salvando resultados em: {arquivo_saida}")
            
            # Primeiro, valida se os dados podem ser serializados
            json_string = json.dumps(dados, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
            
            # Salva o arquivo
            with open(arquivo_saida, 'w', encoding='utf-8') as arquivo:
                arquivo.write(json_string)
            
            # Verifica se o arquivo foi salvo corretamente
            tamanho_arquivo = os.path.getsize(arquivo_saida)
            
            # Testa se o arquivo pode ser lido de volta
            with open(arquivo_saida, 'r', encoding='utf-8') as arquivo:
                dados_verificacao = json.load(arquivo)
            
            logging.info(f"✅ Arquivo salvo e verificado com sucesso!")
            logging.info(f"📁 Tamanho: {tamanho_arquivo:,} bytes")
            logging.info(f"📊 Estabelecimentos salvos: {len(dados_verificacao.get('estabelecimentos', []))}")
            logging.info(f"❌ Erros salvos: {len(dados_verificacao.get('erros', []))}")
            
        except Exception as e:
            logging.error(f"❌ Erro ao salvar arquivo: {e}")
            
            # Tenta salvar um arquivo de emergência sem formatação
            try:
                arquivo_emergencia = arquivo_saida.replace('.json', '_emergencia.json')
                with open(arquivo_emergencia, 'w', encoding='utf-8') as arquivo:
                    json.dump(dados, arquivo, ensure_ascii=False, cls=DateTimeEncoder)
                logging.info(f"💾 Arquivo de emergência salvo: {arquivo_emergencia}")
            except Exception as e2:
                logging.error(f"❌ Falhou também no arquivo de emergência: {e2}")
            
            raise

class CNESMacrorregiaeMerger:
    """
    Classe para mesclar dados de macrorregião com dados das unidades de saúde
    """
    
    def __init__(self, arquivo_macrorregiao: str):
        """
        Inicializa o merger com o arquivo de macrorregiões
        
        Args:
            arquivo_macrorregiao (str): Caminho para o arquivo JSON com dados de macrorregião
        """
        self.arquivo_macrorregiao = arquivo_macrorregiao
        self.dados_macrorregiao = {}
        self.carregar_dados_macrorregiao()
        
        # Configurar logging específico para merger
        self.logger = logging.getLogger('CNESMacrorregiaeMerger')
        handler = logging.FileHandler('cnes_macrorregiao_merger.log')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def carregar_dados_macrorregiao(self):
        """
        Carrega os dados de macrorregião do arquivo JSON e cria índice por código de município
        """
        try:
            logging.info(f"📂 Carregando dados de macrorregião de: {self.arquivo_macrorregiao}")
            
            with open(self.arquivo_macrorregiao, 'r', encoding='utf-8') as arquivo:
                dados = json.load(arquivo)
            
            # Verifica se a estrutura contém o campo esperado
            if 'macrorregiao_regiao_saude_municipios' in dados:
                lista_municipios = dados['macrorregiao_regiao_saude_municipios']
            elif isinstance(dados, list):
                lista_municipios = dados
            else:
                raise ValueError("Estrutura do arquivo de macrorregião não reconhecida")
            
            # Cria índice por código de município para busca rápida
            for item in lista_municipios:
                codigo_municipio = str(item.get('codigo_municipio', ''))
                if codigo_municipio:
                    self.dados_macrorregiao[codigo_municipio] = {
                        'codigo_regiao_pais': item.get('codigo_regiao_pais'),
                        'regiao_pais': item.get('regiao_pais'),
                        'codigo_uf': item.get('codigo_uf'),
                        'uf': item.get('uf'),
                        'codigo_macrorregiao_saude': item.get('codigo_macrorregiao_saude'),
                        'macrorregiao_saude': item.get('macrorregiao_saude'),
                        'codigo_regiao_saude': item.get('codigo_regiao_saude'),
                        'regiao_saude': item.get('regiao_saude'),
                        'municipio': item.get('municipio'),
                        'populacao_estimada_ibge_2022': item.get('populacao_estimada_ibge_2022')
                    }
            
            logging.info(f"✅ Carregados dados de {len(self.dados_macrorregiao)} municípios")
            
        except Exception as e:
            logging.error(f"❌ Erro ao carregar dados de macrorregião: {e}")
            raise
    
    def mesclar_dados_unidade(self, unidade_saude: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mescla os dados de uma unidade de saúde com os dados de macrorregião
        
        Args:
            unidade_saude (Dict[str, Any]): Dados da unidade de saúde obtidos da API
            
        Returns:
            Dict[str, Any]: Unidade de saúde com dados de macrorregião mesclados
        """
        # Cria uma cópia da unidade para não modificar o original
        unidade_mesclada = unidade_saude.copy()
        
        # Remove o campo _metadata se existir (não incluir no resultado final)
        if '_metadata' in unidade_mesclada:
            del unidade_mesclada['_metadata']
        
        # Extrai o código do município da unidade de saúde
        codigo_municipio = str(unidade_saude.get('codigo_municipio', ''))
        
        if codigo_municipio and codigo_municipio in self.dados_macrorregiao:
            # Obtém os dados de macrorregião
            dados_macro_originais = self.dados_macrorregiao[codigo_municipio]
            
            # Cria uma cópia dos dados de macrorregião para evitar duplicações
            dados_macro_limpos = dados_macro_originais.copy()
            
            # Remove campos duplicados que já existem no estabelecimento
            # O codigo_uf já está presente no estabelecimento, não precisa duplicar
            if 'codigo_uf' in dados_macro_limpos:
                del dados_macro_limpos['codigo_uf']
            
            # Adiciona os dados de macrorregião limpos em uma seção específica
            unidade_mesclada['dados_macrorregiao'] = dados_macro_limpos
            
            self.logger.info(f"✅ Mesclagem bem-sucedida para código município: {codigo_municipio}")
            
        else:
            # Caso não encontre o código do município
            unidade_mesclada['dados_macrorregiao'] = None
            
            self.logger.warning(f"⚠️ Código município não encontrado: {codigo_municipio}")
        
        return unidade_mesclada
    
    def mesclar_arquivo_resultados(self, arquivo_entrada: str, arquivo_saida: str):
        """
        Mescla um arquivo completo de resultados da API CNES com dados de macrorregião
        
        Args:
            arquivo_entrada (str): Caminho para o arquivo JSON com resultados da API CNES
            arquivo_saida (str): Caminho para salvar o arquivo mesclado
        """
        try:
            logging.info(f"🔄 Iniciando mesclagem de arquivo: {arquivo_entrada}")
            
            # Carrega os dados do arquivo de entrada
            with open(arquivo_entrada, 'r', encoding='utf-8') as arquivo:
                dados_entrada = json.load(arquivo)
            
            # Verifica se é um arquivo de resultados do automatizador
            if 'estabelecimentos' in dados_entrada:
                estabelecimentos = dados_entrada['estabelecimentos']
            elif isinstance(dados_entrada, list):
                estabelecimentos = dados_entrada
            else:
                raise ValueError("Estrutura do arquivo de entrada não reconhecida")
            
            # Estatísticas da mesclagem
            stats_mesclagem = {
                'total_unidades': len(estabelecimentos),
                'mesclagens_bem_sucedidas': 0,
                'mesclagens_falharam': 0,
                'codigos_municipio_nao_encontrados': []
            }
            
            # Inicializa tracker de progresso para mesclagem
            progress_tracker = ProgressTracker(len(estabelecimentos), "🗺️ Mesclando macrorregião")
            
            # Processa cada estabelecimento
            estabelecimentos_mesclados = []
            for i, estabelecimento in enumerate(estabelecimentos, 1):
                # Mescla os dados
                estabelecimento_mesclado = self.mesclar_dados_unidade(estabelecimento)
                
                # Atualiza estatísticas
                if estabelecimento_mesclado.get('dados_macrorregiao') is not None:
                    stats_mesclagem['mesclagens_bem_sucedidas'] += 1
                else:
                    stats_mesclagem['mesclagens_falharam'] += 1
                    codigo_municipio = str(estabelecimento.get('codigo_municipio', ''))
                    if codigo_municipio:
                        stats_mesclagem['codigos_municipio_nao_encontrados'].append(codigo_municipio)
                
                estabelecimentos_mesclados.append(estabelecimento_mesclado)
                
                # Atualiza progresso a cada 50 estabelecimentos
                if i % 50 == 0 or i == len(estabelecimentos):
                    progress_tracker.update(i)
            
            # Finaliza progresso
            progress_tracker.finish()
            
            # Prepara dados de saída
            dados_saida = {
                'metadados_mesclagem': {
                    'data_mesclagem': datetime.now().isoformat(),
                    'arquivo_entrada': arquivo_entrada,
                    'arquivo_macrorregiao': self.arquivo_macrorregiao,
                    'versao_merger': '1.0_with_progress',
                    'estatisticas': stats_mesclagem
                },
                'estabelecimentos_com_macrorregiao': estabelecimentos_mesclados
            }
            
            # Preserva metadados originais se existirem
            if 'metadados' in dados_entrada:
                dados_saida['metadados_originais'] = dados_entrada['metadados']
            
            # Preserva erros originais se existirem
            if 'erros' in dados_entrada:
                dados_saida['erros_originais'] = dados_entrada['erros']
            
            # Salva o arquivo mesclado
            with open(arquivo_saida, 'w', encoding='utf-8') as arquivo:
                json.dump(dados_saida, arquivo, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
            
            # Verifica se o arquivo foi salvo corretamente
            tamanho_arquivo = os.path.getsize(arquivo_saida)
            
            logging.info(f"✅ Mesclagem concluída com sucesso!")
            logging.info(f"📁 Arquivo mesclado salvo: {arquivo_saida}")
            logging.info(f"📊 Tamanho do arquivo: {tamanho_arquivo:,} bytes")
            logging.info(f"🏥 Total de unidades processadas: {stats_mesclagem['total_unidades']}")
            logging.info(f"✅ Mesclagens bem-sucedidas: {stats_mesclagem['mesclagens_bem_sucedidas']}")
            logging.info(f"❌ Mesclagens falharam: {stats_mesclagem['mesclagens_falharam']}")
            logging.info(f"📈 Taxa de sucesso: {(stats_mesclagem['mesclagens_bem_sucedidas']/stats_mesclagem['total_unidades']*100):.1f}%")
            
            return dados_saida
            
        except Exception as e:
            logging.error(f"❌ Erro durante mesclagem: {e}")
            raise

def main():
    """
    Função principal do script - Processamento integrado ASSÍNCRONO de códigos CNES com mesclagem de macrorregião
    """
    print("🏥 AUTOMATIZADOR DA API CNES - VERSÃO ASSÍNCRONA OTIMIZADA")
    print("🔗 Consulta detalhada por código de estabelecimento")
    print("🛠️ Correções: Processamento paralelo, otimizações de velocidade")
    print("🗺️ FUNCIONALIDADE: Processamento rápido e mesclagem com dados de macrorregião")
    print("⚡ NOVO: Requisições simultâneas com loading em tempo real!")
    print("📊 NOVO: Barra de progresso, ETA e velocidade em tempo real!")
    print("=" * 80)
    
    # Solicita arquivo de entrada
    arquivo_entrada = input("\nDigite o caminho do arquivo JSON com os códigos CNES: ").strip()
    
    if not os.path.exists(arquivo_entrada):
        print(f"❌ Arquivo não encontrado: {arquivo_entrada}")
        return
    
    # Configurações de performance
    print("\n⚡ CONFIGURAÇÕES DE PERFORMANCE:")
    concurrent_str = input("Número de requisições simultâneas (padrão: 15, máx recomendado: 25): ").strip()
    concurrent_requests = int(concurrent_str) if concurrent_str else 15
    
    delay_str = input("Delay entre lotes em segundos (padrão: 0.3): ").strip()
    delay_between_batches = float(delay_str) if delay_str else 0.3
    
    # Validação das configurações
    if concurrent_requests > 25:
        print("⚠️ Aviso: Mais de 25 requisições simultâneas pode sobrecarregar a API")
        confirma_config = input("Deseja continuar mesmo assim? (s/n): ").strip().lower()
        if confirma_config != 's':
            concurrent_requests = 15
            print("✅ Configuração ajustada para 15 requisições simultâneas")
    
    # Verifica arquivo de macrorregião
    arquivo_macrorregiao = input("\nDigite o caminho do arquivo de macrorregião (ou pressione Enter para usar o padrão): ").strip()
    
    if not arquivo_macrorregiao:
        caminhos_padrao = [
            'macrorregiao_regiao_saude_municipios.json',
            '../macrorregiao_regiao_saude_municipios.json',
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'macrorregiao_regiao_saude_municipios.json')
        ]
        
        for caminho in caminhos_padrao:
            if os.path.exists(caminho):
                arquivo_macrorregiao = caminho
                break
        
        if not arquivo_macrorregiao:
            print("❌ Arquivo de macrorregião não encontrado. Especifique o caminho completo.")
            return
    
    if not os.path.exists(arquivo_macrorregiao):
        print(f"❌ Arquivo de macrorregião não encontrado: {arquivo_macrorregiao}")
        return
    
    async def processar_async():
        try:
            # Inicializa o automatizador assíncrono
            automatizador = CNESAPIAutomator(
                concurrent_requests=concurrent_requests,
                delay_between_batches=delay_between_batches
            )
            
            # Carrega os códigos CNES
            codigos = automatizador.carregar_codigos_cnes(arquivo_entrada)
            
            # Calcula tempo estimado (muito mais rápido agora!)
            tempo_estimado = (len(codigos) / concurrent_requests) * delay_between_batches
            tempo_estimado += len(codigos) * 0.1  # Overhead estimado por requisição
            
            # Confirma antes de processar
            print(f"\n📋 Encontrados {len(codigos)} códigos CNES para processar")
            print(f"⚡ Configuração: {concurrent_requests} requisições simultâneas")
            print(f"⏱️ Tempo estimado: {tempo_estimado:.1f} segundos ({tempo_estimado/60:.1f} minutos)")
            print(f"🚀 Velocidade estimada: ~{len(codigos)/tempo_estimado:.1f} requisições/segundo")
            
            confirma = input("\nDeseja continuar? (s/n): ").strip().lower()
            
            if confirma == 's':
                print(f"\n🚀 Iniciando processamento assíncrono otimizado...")
                print(f"📊 Loading em tempo real com ETA ativado!")
                print()
                
                # Processa os códigos de forma assíncrona
                resultados = await automatizador.processar_lista_codigos(codigos)
                
                # Salva os resultados iniciais
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                arquivo_intermediario = f"cnes_resultados_temp_{timestamp}.json"
                automatizador.salvar_resultados(resultados, arquivo_intermediario)
                
                print(f"\n✅ Processamento da API concluído!")
                print(f"🔄 Iniciando mesclagem com dados de macrorregião...")
                print()
                
                # Inicializa o merger
                merger = CNESMacrorregiaeMerger(arquivo_macrorregiao)
                
                # Executa a mesclagem
                arquivo_final = f"cnes_com_macrorregiao_{timestamp}.json"
                resultado_final = merger.mesclar_arquivo_resultados(arquivo_intermediario, arquivo_final)
                
                # Remove arquivo intermediário
                try:
                    os.remove(arquivo_intermediario)
                    print(f"🗑️ Arquivo temporário removido: {arquivo_intermediario}")
                except:
                    pass
                
                print(f"\n🎉 Processamento e mesclagem concluídos!")
                print(f"📁 Arquivo final: {arquivo_final}")
                
                # Mostra estatísticas finais
                stats_api = resultados['resumo']
                stats_mesclagem = resultado_final['metadados_mesclagem']['estatisticas']
                
                print(f"\n📊 Estatísticas finais:")
                print(f"   - Códigos processados: {stats_api['total_sucessos']}")
                print(f"   - Mesclagens bem-sucedidas: {stats_mesclagem['mesclagens_bem_sucedidas']}")
                print(f"   - Taxa de sucesso API: {stats_api['taxa_sucesso']}")
                print(f"   - Taxa de sucesso mesclagem: {(stats_mesclagem['mesclagens_bem_sucedidas']/stats_mesclagem['total_unidades']*100):.1f}%")
                print(f"   - Velocidade média: {stats_api['velocidade_media']}")
                print(f"   - Tempo total: {resultados['metadados']['tempo_execucao_segundos']:.1f} segundos")
                
        except Exception as e:
            logging.error(f"❌ Erro durante processamento integrado assíncrono: {e}")
            print(f"❌ Erro: {e}")
    
    # Executa o processamento assíncrono
    try:
        asyncio.run(processar_async())
    except KeyboardInterrupt:
        print("\n❌ Processamento interrompido pelo usuário")
    except Exception as e:
        logging.error(f"❌ Erro ao executar processamento assíncrono: {e}")
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
