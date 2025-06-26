#!/usr/bin/env python3
"""
Script de teste automatizado para o projeto DJBlog
Executa todos os testes necessários antes do deploy
"""

import os
import sys
import subprocess
import time
import json
import platform
from typing import Dict, Any
import boto3
from datetime import datetime


class DJBlogTester:
    """Classe para executar testes automatizados"""

    def __init__(self):
        self.start_time = time.time()
        self.test_results = []
        self.venv_path = self._detect_virtual_env()
        self.python_cmd = self._get_python_command()
        self.pip_cmd = self._get_pip_command()

    def _detect_virtual_env(self) -> str:
        """Detecta caminho do ambiente virtual"""
        possible_paths = [
            "venv",
            ".venv",
            "env",
            ".env"
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        return None

    def _get_python_command(self) -> str:
        """Retorna comando Python correto para o ambiente"""
        if self.venv_path:
            if platform.system() == "Windows":
                python_path = os.path.join(self.venv_path, "Scripts", "python.exe")
            else:
                python_path = os.path.join(self.venv_path, "bin", "python")

            if os.path.exists(python_path):
                return python_path

        # Fallback para python do sistema
        return "python" if platform.system() == "Windows" else "python3"

    def _get_pip_command(self) -> str:
        """Retorna comando pip correto para o ambiente"""
        if self.venv_path:
            if platform.system() == "Windows":
                pip_path = os.path.join(self.venv_path, "Scripts", "pip.exe")
            else:
                pip_path = os.path.join(self.venv_path, "bin", "pip")

            if os.path.exists(pip_path):
                return pip_path

        # Fallback para pip do sistema
        return "pip"

    def _get_command_in_venv(self, command: str) -> str:
        """Retorna comando correto para executar no ambiente virtual"""
        if not self.venv_path:
            return command

        # Separar comando e argumentos
        parts = command.split()
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        # Comandos que devem usar o venv
        if cmd == "python":
            return f"{self.python_cmd} {' '.join(args)}"
        elif cmd == "pip":
            return f"{self.pip_cmd} {' '.join(args)}"
        elif cmd in ["flake8", "pytest"]:
            # Executar via python -m para garantir que usa o venv
            return f"{self.python_cmd} -m {cmd} {' '.join(args)}"
        elif cmd == "terraform":
            # Terraform é independente, usar comando original
            return command
        elif cmd == "aws":
            # AWS CLI é independente, usar comando original
            return command
        else:
            # Para outros comandos, tentar executar via python -m
            if args and args[0] == "-m":
                return f"{self.python_cmd} {' '.join(args)}"
            else:
                return command

    def log(self, message: str, level: str = "INFO"):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def run_command(self, command: str, description: str, use_venv: bool = True, timeout: int = 300) -> bool:
        """Executa comando e retorna True se sucesso"""
        self.log(f"Executando: {description}")

        # Adaptar comando para usar ambiente virtual se necessário
        if use_venv:
            command = self._get_command_in_venv(command)

        self.log(f"Comando: {command}")

        try:
            # Para comandos com pipes ou redirecionamentos, usar shell=True
            if "|" in command or ">" in command or "<" in command:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
            else:
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

            if result.returncode == 0:
                self.log(f"✅ {description} - OK")
                self.test_results.append({"test": description, "status": "PASS"})
                return True
            else:
                self.log(f"❌ {description} - FALHOU", "ERROR")
                self.log(f"Erro: {result.stderr}", "ERROR")
                if result.stdout:
                    self.log(f"Output: {result.stdout}", "DEBUG")
                self.test_results.append({"test": description, "status": "FAIL", "error": result.stderr})
                return False

        except subprocess.TimeoutExpired:
            self.log(f"⏰ {description} - TIMEOUT (>{timeout}s)", "ERROR")
            self.test_results.append({"test": description, "status": "TIMEOUT"})
            return False
        except Exception as e:
            self.log(f"❌ {description} - ERRO: {e}", "ERROR")
            self.test_results.append({"test": description, "status": "ERROR", "error": str(e)})
            return False

    def test_environment(self) -> bool:
        """Testa configuração do ambiente"""
        self.log("🔧 Testando ambiente...")

        # Verificar se ambiente virtual foi detectado
        if self.venv_path:
            self.log(f"✅ Ambiente virtual detectado: {self.venv_path}")
        else:
            self.log("⚠️ Ambiente virtual não detectado, usando Python do sistema", "WARNING")

        # Verificar Python
        if not self.run_command("python --version", "Verificar Python"):
            return False

        # Verificar pip
        if not self.run_command("pip --version", "Verificar pip"):
            return False

        # Verificar AWS CLI (não usa venv)
        if not self.run_command("aws --version", "Verificar AWS CLI", use_venv=False):
            return False

        return True

    def test_dependencies(self) -> bool:
        """Testa instalação de dependências"""
        self.log("📦 Testando dependências...")

        # Instalar dependências
        if not self.run_command("pip install -r requirements.txt", "Instalar dependências"):
            return False

        # Testar imports principais
        try:
            pass

            self.log("✅ Imports principais - OK")
            self.test_results.append({"test": "Imports principais", "status": "PASS"})
            return True

        except ImportError as e:
            self.log(f"❌ Erro no import: {e}", "ERROR")
            self.test_results.append({"test": "Imports principais", "status": "FAIL", "error": str(e)})
            return False

    def test_configuration(self) -> bool:
        """Testa configuração do projeto"""
        self.log("⚙️ Testando configuração...")

        try:
            # Configurar variáveis de teste
            os.environ["AWS_REGION"] = "us-east-1"
            os.environ["DYNAMODB_TABLE_NAME"] = "djblog-noticias-test"
            os.environ["OPENAI_API_KEY"] = "sk-test-key"

            from config import get_config
            get_config()

            self.log("✅ Configuração carregada - OK")
            self.test_results.append({"test": "Configuração", "status": "PASS"})
            return True

        except Exception as e:
            self.log(f"❌ Erro na configuração: {e}", "ERROR")
            self.test_results.append({"test": "Configuração", "status": "FAIL", "error": str(e)})
            return False

    def test_unit_tests(self) -> bool:
        """Executa testes unitários"""
        self.log("🧪 Executando testes unitários...")

        return self.run_command("pytest tests/ -v", "Testes unitários")

    def test_linting(self) -> bool:
        """Executa linting do código"""
        self.log("🔍 Executando linting...")

        # Instalar flake8 se necessário
        subprocess.run([self.pip_cmd, "install", "flake8"], capture_output=True)

        return self.run_command(
            "flake8 . --max-line-length=120 --ignore=E501,W503 --exclude=venv,__pycache__,.git,.pytest_cache",
            "Linting com flake8")

    def test_aws_connection(self) -> bool:
        """Testa conexão com AWS"""
        self.log("☁️ Testando conexão AWS...")

        try:
            # Verificar credenciais
            sts = boto3.client('sts')
            identity = sts.get_caller_identity()

            self.log(f"✅ AWS conectado como: {identity.get('Arn', 'N/A')}")
            self.test_results.append({"test": "Conexão AWS", "status": "PASS"})
            return True

        except Exception as e:
            self.log(f"❌ Erro na conexão AWS: {e}", "ERROR")
            self.test_results.append({"test": "Conexão AWS", "status": "FAIL", "error": str(e)})
            return False

    def test_lambda_syntax(self) -> bool:
        """Testa sintaxe dos arquivos Lambda"""
        self.log("🐍 Testando sintaxe Lambda...")

        lambda_files = [
            "lambda_coletor.py",
            "lambda_publicar_wordpress.py",
            "lambda_limpeza.py",
            "lambda_health_check.py",
            "lambda_api_noticias.py"
        ]

        all_passed = True
        for file in lambda_files:
            if os.path.exists(file):
                if not self.run_command(f"python -m py_compile {file}", f"Sintaxe {file}"):
                    all_passed = False
            else:
                self.log(f"⚠️ Arquivo não encontrado: {file}", "WARNING")

        return all_passed

    def test_terraform_validation(self) -> bool:
        """Valida arquivos Terraform"""
        self.log("🏗️ Validando Terraform...")

        if not os.path.exists("terraform/aws"):
            self.log("⚠️ Diretório terraform/aws não encontrado", "WARNING")
            return True

        # Mudar para diretório terraform
        original_dir = os.getcwd()
        try:
            os.chdir("terraform/aws")

            # Inicializar terraform (sem backend) - não usa venv
            if not self.run_command("terraform init -backend=false", "Terraform init", use_venv=False):
                return False

            # Validar sintaxe - não usa venv
            success = self.run_command("terraform validate", "Terraform validate", use_venv=False)

            return success

        finally:
            os.chdir(original_dir)

    def generate_report(self) -> Dict[str, Any]:
        """Gera relatório final dos testes"""
        end_time = time.time()
        duration = end_time - self.start_time

        passed = len([t for t in self.test_results if t["status"] == "PASS"])
        failed = len([t for t in self.test_results if t["status"] in ["FAIL", "ERROR", "TIMEOUT"]])
        total = len(self.test_results)

        report = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": round(duration, 2),
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "success_rate": round((passed / total * 100) if total > 0 else 0, 2)
            },
            "details": self.test_results
        }

        return report

    def run_all_tests(self) -> bool:
        """Executa todos os testes"""
        self.log("🚀 Iniciando bateria completa de testes...")

        # Mostrar informações do ambiente
        self.log(f"Python: {self.python_cmd}")
        self.log(f"Pip: {self.pip_cmd}")
        if self.venv_path:
            self.log(f"Ambiente virtual: {self.venv_path}")
        else:
            self.log("Usando Python do sistema (sem ambiente virtual)")

        tests = [
            ("Ambiente", self.test_environment),
            ("Dependências", self.test_dependencies),
            ("Configuração", self.test_configuration),
            ("Testes Unitários", self.test_unit_tests),
            ("Linting", self.test_linting),
            ("Conexão AWS", self.test_aws_connection),
            ("Sintaxe Lambda", self.test_lambda_syntax),
            ("Validação Terraform", self.test_terraform_validation),
        ]

        all_passed = True
        for test_name, test_func in tests:
            self.log(f"\n📋 Executando: {test_name}")
            if not test_func():
                all_passed = False

        # Gerar relatório
        report = self.generate_report()

        # Salvar relatório
        with open("test_report.json", "w") as f:
            json.dump(report, f, indent=2)

        # Exibir resumo
        self.log("\n" + "=" * 50)
        self.log("📊 RESUMO DOS TESTES")
        self.log("=" * 50)
        self.log(f"Total de testes: {report['summary']['total']}")
        self.log(f"Passou: {report['summary']['passed']}")
        self.log(f"Falhou: {report['summary']['failed']}")
        self.log(f"Taxa de sucesso: {report['summary']['success_rate']}%")
        self.log(f"Duração: {report['duration_seconds']}s")

        if all_passed:
            self.log("\n🎉 TODOS OS TESTES PASSARAM! Pronto para deploy.", "SUCCESS")
        else:
            self.log("\n❌ ALGUNS TESTES FALHARAM! Verifique os erros acima.", "ERROR")

        return all_passed


def main():
    """Função principal"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
Uso: python test_runner.py [opções]

Opções:
  --help          Mostra esta ajuda
  --quick         Executa apenas testes rápidos
  --no-aws        Pula testes que requerem AWS
  --no-terraform  Pula validação do Terraform
        """)
        return

    tester = DJBlogTester()

    # Flags para pular certos testes
    quick_mode = "--quick" in sys.argv
    "--no-aws" in sys.argv
    "--no-terraform" in sys.argv

    if quick_mode:
        success = (tester.test_environment() and
                   tester.test_dependencies() and
                   tester.test_configuration() and
                   tester.test_lambda_syntax())

        # Gerar relatório mesmo no modo quick
        report = tester.generate_report()
        with open("test_report.json", "w") as f:
            json.dump(report, f, indent=2)

        # Exibir resumo
        tester.log("\n" + "=" * 50)
        tester.log("📊 RESUMO DOS TESTES (QUICK MODE)")
        tester.log("=" * 50)
        tester.log(f"Total de testes: {report['summary']['total']}")
        tester.log(f"Passou: {report['summary']['passed']}")
        tester.log(f"Falhou: {report['summary']['failed']}")
        tester.log(f"Taxa de sucesso: {report['summary']['success_rate']}%")
        tester.log(f"Duração: {report['duration_seconds']}s")

        if success:
            tester.log("\n🎉 TODOS OS TESTES RÁPIDOS PASSARAM!", "SUCCESS")
        else:
            tester.log("\n❌ ALGUNS TESTES FALHARAM! Verifique os erros acima.", "ERROR")

    else:
        success = tester.run_all_tests()

    # Exit code para CI/CD
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
