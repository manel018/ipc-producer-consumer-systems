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

# Execução da Parte 1
run-part1: $(TARGET_PART1)
	./$(TARGET_PART1) 20

run-part1-test: $(TARGET_PART1)
	@echo "=== Teste Parte 1 com 10 números ==="
	./$(TARGET_PART1) 10
	@echo "\n=== Teste Parte 1 com 30 números ==="
	./$(TARGET_PART1) 30

# Execução da Parte 2
run-part2: $(TARGET_PART2)
	./$(TARGET_PART2)

run-part2-quick: $(TARGET_PART2)
	@echo "=== Execução rápida da Parte 2 (apenas M=1000 para teste) ==="
	# Versão modificada para teste rápido - alterar M na constante do código
	./$(TARGET_PART2)

# Execução completa de todos os experimentos
run-all: $(TARGET_PART1) $(TARGET_PART2)
	@echo "=== Executando Parte 1 ==="
	./$(TARGET_PART1) 20
	@echo "\n=== Executando Parte 2 ==="
	./$(TARGET_PART2)

# Testes
test: test-part1

test-part1: $(TARGET_PART1)
	@echo "=== Teste Parte 1 com 10 números ==="
	./$(TARGET_PART1) 10
	@echo "\n=== Teste Parte 1 com 30 números ==="
	./$(TARGET_PART1) 30


# Análise Python (requer python3 com matplotlib e numpy)
analyze: $(TARGET_PART2)
	@echo "=== Executando experimentos para análise ==="
	./$(TARGET_PART2)
	@echo "\n=== Preparando ambiente Python local (venv) ==="
	@test -d venv || python3 -m venv venv
	@. venv/bin/activate && \
		python3 -m pip install --upgrade pip && \
		python3 -m pip install matplotlib numpy scipy && \
		echo "\n=== Gerando gráficos com Python ===" && \
		python3 part2-analysis.py

# Help
help:
	@echo "=== Makefile para Trabalho Prático 1 ==="
	@echo ""
	@echo "Alvos disponíveis:"
	@echo "  make              - Compila Parte 1 e Parte 2"
	@echo "  make run-part1    - Executa Parte 1 (padrão: 20 números)"
	@echo "  make run-part2    - Executa Parte 2 (todos experimentos)"
	@echo "  make run-all      - Executa Parte 1 e Parte 2"
	@echo "  make test         - Executa testes da Parte 1 e Parte 2"
	@echo "  make test-part1   - Teste rápido da Parte 1"
	@echo "  make analyze      - Executa Parte 2 e gera gráficos Python"
	@echo "  make clean        - Remove todos executáveis e dados"
	@echo "  make clean-part1  - Remove apenas Parte 1"
	@echo "  make clean-part2  - Remove apenas Parte 2"
	@echo "  make help         - Mostra esta ajuda"
	@echo ""
	@echo "Observações:"
	@echo "  - A Parte 2 gera arquivos em analysis/part2/data"
	@echo "  - Os gráficos vão para analysis/part2/plots"
	@echo "  - Para análise gráfica, instale: pip install matplotlib numpy"
	@echo "  - Execute 'make analyze' após rodar os experimentos"

.PHONY: all clean clean-part1 clean-part2 run-part1 run-part1-test run-part2 run-part2-quick run-all test test-part1 analyze help