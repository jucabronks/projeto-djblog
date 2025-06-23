#!/usr/bin/env python3
"""
Script de Monitoramento do Projeto VM
Verifica se todas as Lambdas estão funcionando corretamente
"""

import boto3
import json
import time
from datetime import datetime, timedelta, UTC
import requests
from pymongo import MongoClient
import os

class ProjetoVMMonitor:
    def __init__(self):
        self.lambda_client = boto3.client('lambda', region_name='us-east-1')
        self.cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
        self.logs = boto3.client('logs', region_name='us-east-1')
        
        # Configurações
        self.functions = [
            'coletor-noticias',
            'publicador-noticias', 
            'limpeza-noticias',
            'health-check-fontes'
        ]
        
        self.mongo_uri = os.getenv('MONGO_URI', '')
        
    def check_lambda_functions(self):
        """Verifica se todas as Lambda functions existem"""
        print("🔍 Verificando Lambda Functions...")
        
        for func_name in self.functions:
            try:
                response = self.lambda_client.get_function(FunctionName=func_name)
                print(f"✅ {func_name}: OK")
                print(f"   - Runtime: {response['Configuration']['Runtime']}")
                print(f"   - Memory: {response['Configuration']['MemorySize']}MB")
                print(f"   - Timeout: {response['Configuration']['Timeout']}s")
            except Exception as e:
                print(f"❌ {func_name}: ERRO - {e}")
                
    def check_eventbridge_rules(self):
        """Verifica se as regras do EventBridge estão configuradas"""
        print("\n🔍 Verificando EventBridge Rules...")
        
        events = boto3.client('events', region_name='us-east-1')
        
        rules = [
            'coleta-diaria',
            'publicacao-diaria', 
            'limpeza-semanal',
            'coletor-batch',
            'resumidor',
            'publicador-manha',
            'health-check-schedule'
        ]
        
        for rule_name in rules:
            try:
                response = events.describe_rule(Name=rule_name)
                print(f"✅ {rule_name}: OK")
                print(f"   - Schedule: {response.get('ScheduleExpression', 'N/A')}")
            except Exception as e:
                print(f"❌ {rule_name}: ERRO - {e}")
                
    def check_recent_executions(self):
        """Verifica execuções recentes das Lambdas"""
        print("\n🔍 Verificando Execuções Recentes...")
        
        end_time = datetime.now(UTC)
        start_time = end_time - timedelta(hours=24)
        
        for func_name in self.functions:
            try:
                # Verificar métricas do CloudWatch
                response = self.cloudwatch.get_metric_statistics(
                    Namespace='AWS/Lambda',
                    MetricName='Invocations',
                    Dimensions=[{'Name': 'FunctionName', 'Value': func_name}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=3600,
                    Statistics=['Sum']
                )
                
                total_invocations = sum(point['Sum'] for point in response['Datapoints'])
                print(f"📊 {func_name}: {total_invocations} invocações nas últimas 24h")
                
                # Verificar erros
                error_response = self.cloudwatch.get_metric_statistics(
                    Namespace='AWS/Lambda',
                    MetricName='Errors',
                    Dimensions=[{'Name': 'FunctionName', 'Value': func_name}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=3600,
                    Statistics=['Sum']
                )
                
                total_errors = sum(point['Sum'] for point in error_response['Datapoints'])
                if total_errors > 0:
                    print(f"⚠️  {func_name}: {total_errors} erros nas últimas 24h")
                else:
                    print(f"✅ {func_name}: Sem erros nas últimas 24h")
                    
            except Exception as e:
                print(f"❌ Erro ao verificar {func_name}: {e}")
                
    def check_mongodb_connection(self):
        """Verifica conexão com MongoDB Atlas"""
        print("\n🔍 Verificando Conexão MongoDB...")
        
        if not self.mongo_uri:
            print("⚠️  MONGO_URI não configurado")
            return
            
        try:
            client = MongoClient(self.mongo_uri)
            db = client.get_default_database()
            
            # Verificar se as coleções existem
            collections = db.list_collection_names()
            expected_collections = ['fontes_noticias', 'noticias_coletadas']
            
            for collection in expected_collections:
                if collection in collections:
                    count = db[collection].count_documents({})
                    print(f"✅ {collection}: {count} documentos")
                else:
                    print(f"⚠️  {collection}: Não encontrada")
                    
            client.close()
            
        except Exception as e:
            print(f"❌ Erro na conexão MongoDB: {e}")
            
    def check_sns_topic(self):
        """Verifica se o tópico SNS está configurado"""
        print("\n🔍 Verificando SNS Topic...")
        
        try:
            sns = boto3.client('sns', region_name='us-east-1')
            response = sns.list_topics()
            
            topic_found = False
            for topic in response['Topics']:
                if 'lambda-error-notifications' in topic['TopicArn']:
                    print(f"✅ SNS Topic: {topic['TopicArn']}")
                    topic_found = True
                    break
                    
            if not topic_found:
                print("⚠️  SNS Topic não encontrado")
                
        except Exception as e:
            print(f"❌ Erro ao verificar SNS: {e}")
            
    def test_lambda_invocation(self):
        """Testa invocação manual das Lambdas"""
        print("\n🧪 Testando Invocação Manual...")
        
        test_functions = ['health-check-fontes']  # Começar com a mais simples
        
        for func_name in test_functions:
            try:
                print(f"🔧 Testando {func_name}...")
                response = self.lambda_client.invoke(
                    FunctionName=func_name,
                    InvocationType='RequestResponse',
                    Payload=json.dumps({})
                )
                
                if response['StatusCode'] == 200:
                    print(f"✅ {func_name}: Teste bem-sucedido")
                else:
                    print(f"❌ {func_name}: Status {response['StatusCode']}")
                    
            except Exception as e:
                print(f"❌ Erro ao testar {func_name}: {e}")
                
    def generate_report(self):
        """Gera relatório completo"""
        print("=" * 60)
        print("📋 RELATÓRIO DE MONITORAMENTO - PROJETO VM")
        print("=" * 60)
        print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        self.check_lambda_functions()
        self.check_eventbridge_rules()
        self.check_recent_executions()
        self.check_mongodb_connection()
        self.check_sns_topic()
        self.test_lambda_invocation()
        
        print("\n" + "=" * 60)
        print("✅ Verificação concluída!")
        print("📧 Verifique seu email para alertas SNS")
        print("🔍 Monitore no CloudWatch para mais detalhes")
        print("=" * 60)

def main():
    monitor = ProjetoVMMonitor()
    monitor.generate_report()

if __name__ == "__main__":
    main() 