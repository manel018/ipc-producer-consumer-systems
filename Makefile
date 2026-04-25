CC = gcc
CFLAGS = -Wall -Wextra -O2 -pthread
LDLIBS = -lm

# Executáveis
TARGET_PART1 = part1
TARGET_PART2 = part2

# Arquivos fonte
SOURCE_PART1 = part1.c
SOURCE_PART2 = part2.c

# Alvos principais
all: $(TARGET_PART1) $(TARGET_PART2)

# Compilação da Parte 1
$(TARGET_PART1): $(SOURCE_PART1)
	$(CC) $(CFLAGS) -o $(TARGET_PART1) $(SOURCE_PART1) $(LDLIBS)

# Compilação da Parte 2
$(TARGET_PART2): $(SOURCE_PART2)
	$(CC) $(CFLAGS) -o $(TARGET_PART2) $(SOURCE_PART2) $(LDLIBS)

# Limpeza
clean:
	rm -f $(TARGET_PART1) $(TARGET_PART2)

clean-data: clean
	rm -rf analysis/part2/data

clean-plots: clean
	rm -rf analysis/part2/plots

clean-part1:
	rm -f $(TARGET_PART1)

clean-part2:
	rm -f $(TARGET_PART2)

clean-all: clean clean-data clean-plots

# Execução da Parte 1
run-part1: $(TARGET_PART1)
	./$(TARGET_PART1) 20

# Execução da Parte 2
run-part2: $(TARGET_PART2)
	./$(TARGET_PART2)

# Execução completa de todos os experimentos
run-all: $(TARGET_PART1) $(TARGET_PART2)
	@echo "=========================="
	@echo "=== Executando Parte 1 ==="
	@echo "=========================="
	@echo "Valor de teste: 20 números"
	./$(TARGET_PART1) 20
	@echo "=========================="
	@echo "=== Executando Parte 2 ==="
	@echo "=========================="
	./$(TARGET_PART2)
	@echo "\n=== Experimentos completos executados ==="
	@$(MAKE) analyze

# Testes
test-part1: $(TARGET_PART1)
	@echo "=== Teste Parte 1 com 10 números ==="
	./$(TARGET_PART1) 10
	@echo "\n=== Teste Parte 1 com 30 números ==="
	./$(TARGET_PART1) 30

# Análise Python (requer python3 com matplotlib e numpy)
analyze: $(TARGET_PART2)
	@echo "=== Executando script de análise Python ==="
	@echo "\n=== Preparando ambiente Python local (venv) ==="
	@test -d venv || python3 -m venv venv
	@VENV_PY=venv/bin/python; \
	if "$$VENV_PY" -c "import matplotlib, numpy, scipy" >/dev/null 2>&1; then \
		echo "=== Ambiente Python já configurado ==="; \
	else \
		echo "=== Instalando dependências Python no venv ==="; \
		"$$VENV_PY" -m pip install --upgrade pip && \
		"$$VENV_PY" -m pip install -r requirements.txt; \
	fi; \
	echo "\n=== Gerando gráficos com Python ===" && \
	"$$VENV_PY" part2-analysis.py

# Help
help:
	@echo "=== Makefile para Trabalho Prático 1 ==="
	@echo ""
	@echo "Alvos disponíveis:"
	@echo "  make              - Compila Parte 1 e Parte 2"
	@echo "  make run-part1    - Executa Parte 1 (padrão: 20 números)"
	@echo "  make test-part1   - Teste rápido da Parte 1"
	@echo "  make run-part2    - Executa Parte 2 (todos experimentos)"
	@echo "  make run-all      - Executa Parte 1 e Parte 2"
	@echo "  make analyze      - Gera gráficos Python dos dados da Parte 2"
	@echo "  make clean        - Remove todos executáveis"
	@echo "  make clean-data   - Remove dados gerados pela Parte 2"
	@echo "  make clean-plots  - Remove gráficos gerados pela Parte 2"
	@echo "  make clean-part1  - Remove executáveis apenas da Parte 1"
	@echo "  make clean-part2  - Remove executáveis apenas da Parte 2"
	@echo "  make clean-all    - Remove todos os arquivos gerados"
	@echo "  make help         - Mostra esta ajuda"
	@echo ""
	@echo "Observações:"
	@echo "  - A Parte 2 gera arquivos em analysis/part2/data"
	@echo "  - Os gráficos vão para analysis/part2/plots"
	@echo "  - Dependências Python em requirements.txt"
	@echo "  - Execute 'make analyze' após rodar os experimentos"

.PHONY: all clean clean-data clean-plots clean-part1 clean-part2 clean-all run-part1 run-part2 run-all test-part1 analyze help