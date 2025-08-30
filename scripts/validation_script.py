#!/usr/bin/env python3
# scripts/validate_examples.py
"""
Script de validação automática dos Examples do SmartSearchHUB.

Executa todos os examples em sequência e valida os resultados.
Útil para CI/CD e validação rápida de mudanças.

Uso:
    python scripts/validate_examples.py
    python scripts/validate_examples.py --skip-auth
    python scripts/validate_examples.py --folder-id 1AbCdEf
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple


class ExamplesValidator:
    """Validador automático dos examples."""

    def __init__(self, skip_auth: bool = False, folder_id: str = None):
        self.skip_auth = skip_auth
        self.folder_id = folder_id or os.getenv("GDRIVE_TEST_FOLDER")
        self.project_root = Path(__file__).parent.parent
        self.results = []

    def run_validation(self) -> bool:
        """Executa validação completa dos examples."""
        print("🚀 VALIDAÇÃO AUTOMÁTICA DOS EXAMPLES")
        print("=" * 60)

        # Pré-requisitos
        if not self._check_prerequisites():
            return False

        # Configurar ambiente
        self._setup_environment()

        # Executar testes
        tests = [
            ("01_auth_test", "Teste de Autenticação", []),
            ("02_list_basic", "Listagem Básica", ["GDRIVE_TEST_FOLDER"]),
            ("03_extract_html", "Extração de Conteúdo", ["GDRIVE_TEST_FOLDER"])
        ]

        for test_id, test_name, required_env in tests:
            if self.skip_auth and test_id == "01_auth_test":
                print(f"⏭️  Pulando {test_name} (--skip-auth)")
                continue

            success = self._run_example_test(test_id, test_name, required_env)
            if not success:
                print(f"❌ Falha em {test_name} - interrompendo validação")
                break

        # Relatório final
        return self._generate_report()

    def _check_prerequisites(self) -> bool:
        """Verifica pré-requisitos para executar os testes."""
        print("🔍 Verificando pré-requisitos...")

        # Verifica diretório do projeto
        if not self.project_root.exists():
            print("❌ Diretório do projeto não encontrado")
            return False

        # Verifica estrutura de examples
        examples_dir = self.project_root / "examples"
        if not examples_dir.exists():
            print("❌ Diretório examples/ não encontrado")
            return False

        # Verifica módulos essenciais
        required_files = [
            "examples/__main__.py",
            "examples/common/auth_manager.py",
            "examples/common/content_extractor.py",
            "examples/gdrive/__main__.py"
        ]

        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                print(f"❌ Arquivo obrigatório não encontrado: {file_path}")
                return False

        print("✅ Pré-requisitos verificados")
        return True

    def _setup_environment(self):
        """Configura variáveis de ambiente para os testes."""
        print("⚙️  Configurando ambiente de teste...")

        # Define pasta de teste se fornecida
        if self.folder_id:
            os.environ["GDRIVE_TEST_FOLDER"] = self.folder_id
            print(f"📂 Pasta de teste: {self.folder_id}")

        # Configurações de teste
        os.environ["GDRIVE_MAX_FILES"] = "3"  # Poucos arquivos para testes rápidos
        os.environ["GDRIVE_PREVIEW_LENGTH"] = "100"  # Preview curto
        os.environ["GDRIVE_INTERACTIVE"] = "true"  # Permite interação se necessário

    def _run_example_test(self, test_id: str, test_name: str, required_env: List[str]) -> bool:
        """Executa um example específico e valida resultado."""
        print(f"\n🧪 Executando: {test_name}")
        print("-" * 40)

        # Verifica variáveis de ambiente obrigatórias
        for env_var in required_env:
            if not os.getenv(env_var):
                print(f"❌ Variável de ambiente obrigatória não definida: {env_var}")
                return False

        # Executa o example
        cmd = [sys.executable, "-m", f"examples.gdrive.{test_id}"]
        
        try:
            start_time = time.time()
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60  # Timeout de 1 minuto por test
            )
            
            duration = time.time() - start_time

            # Analisa resultado
            success = result.returncode == 0
            
            # Registra resultado
            self.results.append({
                'test_id': test_id,
                'test_name': test_name,
                'success': success,
                'duration': duration,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            })

            if success:
                print(f"✅ {test_name} executado com sucesso ({duration:.1f}s)")
                
                # Validações específicas por teste
                if test_id == "01_auth_test":
                    if "TESTE DE AUTENTICAÇÃO CONCLUÍDO COM SUCESSO" in result.stdout:
                        print("   ✅ Autenticação validada")
                    else:
                        print("   ⚠️  Autenticação pode ter falhado")

                elif test_id == "02_list_basic":
                    if "LISTAGEM CONCLUÍDA COM SUCESSO" in result.stdout:
                        print("   ✅ Listagem validada")
                    else:
                        print("   ⚠️  Listagem pode ter falhado")

                elif test_id == "03_extract_html":
                    if "EXTRAÇÃO CONCLUÍDA COM SUCESSO" in result.stdout:
                        print("   ✅ Extração validada")
                    else:
                        print("   ⚠️  Extração pode ter falhado")

            else:
                print(f"❌ {test_name} falhou (código {result.returncode})")
                if result.stderr:
                    print(f"   Erro: {result.stderr[:200]}...")

            return success

        except subprocess.TimeoutExpired:
            print(f"⏰ {test_name} excedeu timeout de 60s")
            self.results.append({
                'test_id': test_id,
                'test_name': test_name,
                'success': False,
                'duration': 60,
                'returncode': -1,
                'error': 'Timeout'
            })
            return False

        except Exception as e:
            print(f"💥 Erro inesperado em {test_name}: {e}")
            self.results.append({
                'test_id': test_id,
                'test_name': test_name,
                'success': False,
                'duration': 0,
                'error': str(e)
            })
            return False

    def _generate_report(self) -> bool:
        """Gera relatório final da validação."""
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO FINAL DE VALIDAÇÃO")
        print("=" * 60)

        successful = [r for r in self.results if r['success']]
        failed = [r for r in self.results if not r['success']]

        print(f"✅ Sucessos: {len(successful)}/{len(self.results)}")
        print(f"❌ Falhas: {len(failed)}")

        if successful:
            print(f"\n🎉 Tests bem-sucedidos:")
            for result in successful:
                print(f"   ✅ {result['test_name']} ({result['duration']:.1f}s)")

        if failed:
            print(f"\n💥 Tests com falha:")
            for result in failed:
                error_info = result.get('error', f"código {result['returncode']}")
                print(f"   ❌ {result['test_name']} - {error_info}")

        # Validação geral
        all_passed = len(failed) == 0
        
        if all_passed:
            print(f"\n🎉 VALIDAÇÃO COMPLETA: TODOS OS EXAMPLES FUNCIONANDO!")
            print("✅ O refactor dos Examples foi bem-sucedido")
            print("🚀 Pronto para partir para Fase 2: Examples Avançados")
        else:
            print(f"\n⚠️  VALIDAÇÃO PARCIAL: {len(failed)} falha(s) encontrada(s)")
            print("🔧 Revise as configurações e dependências")

        return all_passed

    def save_report(self, output_file: str = None):
        """Salva relatório detalhado em arquivo."""
        if not output_file:
            output_file = self.project_root / "validation_report.txt"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("RELATÓRIO DE VALIDAÇÃO DOS EXAMPLES\n")
            f.write("=" * 50 + "\n\n")

            for result in self.results:
                f.write(f"Test: {result['test_name']} ({result['test_id']})\n")
                f.write(f"Status: {'✅ Sucesso' if result['success'] else '❌ Falha'}\n")
                f.write(f"Duração: {result.get('duration', 0):.1f}s\n")
                
                if not result['success']:
                    f.write(f"Erro: {result.get('error', 'N/A')}\n")
                    if 'stderr' in result and result['stderr']:
                        f.write(f"Stderr: {result['stderr']}\n")

                f.write("\n" + "-" * 30 + "\n\n")

        print(f"📄 Relatório salvo em: {output_file}")


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Validador automático dos Examples do SmartSearchHUB"
    )
    
    parser.add_argument(
        "--skip-auth",
        action="store_true",
        help="Pula teste de autenticação"
    )
    
    parser.add_argument(
        "--folder-id",
        help="ID da pasta do Google Drive para teste"
    )
    
    parser.add_argument(
        "--save-report",
        help="Salva relatório em arquivo"
    )
    
    args = parser.parse_args()

    # Executa validação
    validator = ExamplesValidator(
        skip_auth=args.skip_auth,
        folder_id=args.folder_id
    )
    
    success = validator.run_validation()

    # Salva relatório se solicitado
    if args.save_report:
        validator.save_report(args.save_report)

    # Exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()