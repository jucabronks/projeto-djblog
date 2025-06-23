#!/usr/bin/env python3
"""
Script para testar fontes RSS e verificar se estão funcionando

Uso:
    python scripts/test_fontes.py
    python scripts/test_fontes.py --nicho tecnologia
    python scripts/test_fontes.py --verbose
"""

import os
import sys
import argparse
import feedparser
import requests
from datetime import datetime, UTC
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import setup_logging, buscar_fontes, validar_url
from config import config

logger = setup_logging()

class RSSFeedTester:
    """Classe para testar fontes RSS"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = {
            "total": 0,
            "working": 0,
            "broken": 0,
            "details": []
        }
    
    def test_url_accessibility(self, url: str) -> bool:
        """
        Testa se uma URL é acessível
        
        Args:
            url: URL para testar
            
        Returns:
            True se acessível
        """
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            return response.status_code < 400
        except Exception as e:
            if self.verbose:
                logger.debug(f"URL inacessível: {url} - {e}")
            return False
    
    def test_rss_feed(self, feed_url: str, source_name: str) -> Dict[str, Any]:
        """
        Testa um feed RSS específico
        
        Args:
            feed_url: URL do feed RSS
            source_name: Nome da fonte
            
        Returns:
            Dicionário com resultados do teste
        """
        result = {
            "name": source_name,
            "url": feed_url,
            "accessible": False,
            "valid_rss": False,
            "entries_count": 0,
            "last_entry_date": None,
            "error": None,
            "status": "unknown"
        }
        
        try:
            # Testa acessibilidade da URL
            if not self.test_url_accessibility(feed_url):
                result["error"] = "URL inacessível"
                result["status"] = "broken"
                return result
            
            result["accessible"] = True
            
            # Testa parse do RSS
            feed = feedparser.parse(feed_url)
            
            if hasattr(feed, 'bozo') and feed.bozo:
                result["error"] = "Feed malformado"
                result["status"] = "broken"
                return result
            
            if not feed.entries:
                result["error"] = "Feed sem entradas"
                result["status"] = "broken"
                return result
            
            result["valid_rss"] = True
            result["entries_count"] = len(feed.entries)
            
            # Verifica data da última entrada
            if feed.entries:
                last_entry = feed.entries[0]
                if hasattr(last_entry, 'published_parsed') and last_entry.published_parsed:
                    result["last_entry_date"] = datetime(*last_entry.published_parsed[:6])
            
            result["status"] = "working"
            
        except Exception as e:
            result["error"] = str(e)
            result["status"] = "broken"
        
        return result
    
    def test_all_sources(self, nicho: Optional[str] = None) -> Dict[str, Any]:
        """
        Testa todas as fontes ou fontes de um nicho específico
        
        Args:
            nicho: Nicho específico para testar (opcional)
            
        Returns:
            Dicionário com resultados dos testes
        """
        logger.info(f"Testando fontes RSS{' para nicho: ' + nicho if nicho else ''}")
        
        try:
            # Busca fontes
            fontes = buscar_fontes(nicho=nicho, ativo=True)
            
            if not fontes:
                logger.warning(f"Nenhuma fonte encontrada{' para nicho: ' + nicho if nicho else ''}")
                return self.results
            
            logger.info(f"Encontradas {len(fontes)} fontes para teste")
            
            # Testa cada fonte
            for fonte in fontes:
                if not fonte.get("rss"):
                    logger.warning(f"Fonte sem RSS: {fonte['name']}")
                    continue
                
                result = self.test_rss_feed(fonte["rss"], fonte["name"])
                self.results["details"].append(result)
                self.results["total"] += 1
                
                if result["status"] == "working":
                    self.results["working"] += 1
                    logger.info(f"✅ {fonte['name']}: {result['entries_count']} entradas")
                else:
                    self.results["broken"] += 1
                    logger.error(f"❌ {fonte['name']}: {result['error']}")
                
                if self.verbose:
                    logger.info(f"  URL: {fonte['rss']}")
                    if result["last_entry_date"]:
                        logger.info(f"  Última entrada: {result['last_entry_date']}")
            
            # Estatísticas finais
            success_rate = (self.results["working"] / self.results["total"]) * 100 if self.results["total"] > 0 else 0
            logger.info(f"\n📊 Estatísticas:")
            logger.info(f"  Total: {self.results['total']}")
            logger.info(f"  Funcionando: {self.results['working']}")
            logger.info(f"  Quebradas: {self.results['broken']}")
            logger.info(f"  Taxa de sucesso: {success_rate:.1f}%")
            
            return self.results
            
        except Exception as e:
            logger.error(f"Erro ao testar fontes: {e}")
            return self.results
    
    def generate_report(self) -> str:
        """
        Gera relatório detalhado dos testes
        
        Returns:
            String com relatório formatado
        """
        report = []
        report.append("=" * 60)
        report.append("RELATÓRIO DE TESTE DE FONTES RSS")
        report.append("=" * 60)
        report.append(f"Data: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report.append(f"Total testado: {self.results['total']}")
        report.append(f"Funcionando: {self.results['working']}")
        report.append(f"Quebradas: {self.results['broken']}")
        
        success_rate = (self.results["working"] / self.results["total"]) * 100 if self.results["total"] > 0 else 0
        report.append(f"Taxa de sucesso: {success_rate:.1f}%")
        report.append("")
        
        # Fontes funcionando
        working_sources = [r for r in self.results["details"] if r["status"] == "working"]
        if working_sources:
            report.append("✅ FONTES FUNCIONANDO:")
            for result in working_sources:
                report.append(f"  • {result['name']}")
                report.append(f"    URL: {result['url']}")
                report.append(f"    Entradas: {result['entries_count']}")
                if result["last_entry_date"]:
                    report.append(f"    Última entrada: {result['last_entry_date']}")
                report.append("")
        
        # Fontes quebradas
        broken_sources = [r for r in self.results["details"] if r["status"] == "broken"]
        if broken_sources:
            report.append("❌ FONTES QUEBRADAS:")
            for result in broken_sources:
                report.append(f"  • {result['name']}")
                report.append(f"    URL: {result['url']}")
                report.append(f"    Erro: {result['error']}")
                report.append("")
        
        return "\n".join(report)

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Testa fontes RSS")
    parser.add_argument("--nicho", help="Nicho específico para testar")
    parser.add_argument("--verbose", "-v", action="store_true", help="Modo verboso")
    parser.add_argument("--report", "-r", action="store_true", help="Gerar relatório detalhado")
    
    args = parser.parse_args()
    
    # Valida variáveis de ambiente
    if not os.environ.get("MONGO_URI"):
        logger.error("MONGO_URI não configurada")
        sys.exit(1)
    
    # Inicializa tester
    tester = RSSFeedTester(verbose=args.verbose)
    
    # Executa testes
    results = tester.test_all_sources(nicho=args.nicho)
    
    # Gera relatório se solicitado
    if args.report:
        report = tester.generate_report()
        print(report)
        
        # Salva relatório em arquivo
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        filename = f"rss_test_report_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        logger.info(f"Relatório salvo em: {filename}")
    
    # Retorna código de saída baseado nos resultados
    if results["broken"] > 0:
        logger.warning(f"Encontradas {results['broken']} fontes quebradas")
        sys.exit(1)
    else:
        logger.info("Todas as fontes estão funcionando!")
        sys.exit(0)

if __name__ == "__main__":
    main() 