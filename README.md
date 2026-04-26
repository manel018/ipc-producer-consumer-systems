# Sistemas IPC Produtor-Consumidor

Projeto que explora mecanismos de Comunicação entre Processos (IPC) e técnicas de sincronização por meio de duas implementações de produtor-consumidor:

1. **Produtor-Consumidor com Pipes**: comunicação entre processos usando pipes anônimos
2. **Produtor-Consumidor com Semáforos**: implementação multithread com memória compartilhada


## Estrutura do Repositório

```
├── .gitignore   
├── Makefile                       # Scripts de build e execução    
├── README.md                      # Este arquivo
├── analysis/                      # Pasta criada ao executar os experimentos da Parte 2
│   └── part2/
│       ├── data/
│       │   ├── execution_times.csv   # Tempos de execução para todas as combinações
│       │   └── occupancy_*.txt       # Traços de ocupação do buffer
│       └── plots/                    # Gráficos gerados                  
├── part1.c                        # Implementação com pipes
├── part2-analysis.py              # Script para gerar gráficos a partir dos dados da Parte 2
├── part2.c                        # Implementação com semáforos
└── requirements.txt               # Dependências do projeto
```

## Compilação

```bash
make              # Compila todos os programas
```

## Execução
Executa a parte 1 com um número específico de inteiros como argumento:

```bash
./part1 <numero_de_inteiros>    # Executa a Parte 1

# ou usando o Makefile com uma variável do número de inteiros a processar

make run-part1 NUM=1000          # Executa a Parte 1 com 1000 inteiros, por exemplo
```

Executar a parte 2 para rodar todos os experimentos e gerar os dados:

```bash
./part2                     # Executa os experimentos da Parte 2

# ou usando o Makefile

make run-part2              # Executa os experimentos da Parte 2
```

Isso executará todas as combinações de threads produtoras/consumidoras e tamanhos de buffer, gravando os resultados na pasta `analysis/part2/data/`.

Depois, gere os gráficos a partir dos dados da Parte 2:

```bash
make analyze      # Gera gráficos de análise na pasta 'analysis/part2/plots/'
```

🔎  Abra os gráficos gerados em **`analysis/part2/plots/`** e analise os resultados.

Por fim, você pode limpar os binários compilados e os dados/gráficos de análise:

```bash
make clean        # Remove apenas os binários compilados
make clean-all    # Remove binários e todos os dados/gráficos de análise
```


## Parte 1: Produtor-Consumidor com Pipes

Implementação com dois processos na qual produtor e consumidor se comunicam por pipes anônimos. O produtor gera sequências de inteiros que o consumidor valida quanto à primalidade.

⚠️ Este programa recebe um argumento de linha de comando que especifica quantos inteiros produzir/consumir, permitindo testes flexíveis

### Principais Detalhes de Implementação

- Ambos os processos (pai e filho) acessam as duas extremidades do pipe após o `fork()`
- **Crítico**: os números são convertidos para strings de tamanho fixo (20 bytes) antes de serem escritos no pipe
- E/S de tamanho fixo evita fragmentação de mensagens e garante comunicação confiável


## Parte 2: Produtor-Consumidor com Semáforos

Uma implementação multithread que usa memória compartilhada e semáforos para sincronização entre múltiplas threads produtoras e consumidoras.

Este programa é composto por duas partes: 
1. lógica principal em `part2.c` 
2. análise/plotagem em `part2-analysis.py`. 

O programa principal executa experimentos com várias configurações de produtores, consumidores e tamanhos de buffer, enquanto o script python  de análise gera visualizações a partir dos dados coletados.

### Arquitetura

- **Memória Compartilhada**: vetor com N posições inteiras
- **Produtores** (threads $Np$): geram inteiros aleatórios (1 a $10^7$) e escrevem em posições vazias
- **Consumidores** (threads $Nc$): leem inteiros de posições preenchidas e verificam primalidade

### Sincronização

- **Semáforo Mutex**: protege o acesso à memória compartilhada (evita condições de corrida)
- **Semáforos Contadores**: coordenam as condições de buffer cheio/vazio
  - Produtores esperam quando o buffer está cheio
  - Consumidores esperam quando o buffer está vazio

### Parâmetros do Estudo de Caso

- **Objetivo**: processar $M = 10^5$ números antes da finalização
- **Tamanhos de buffer**: $N \in \{1, 10, 100, 1000\}$
- **Combinações de threads**: $(Np, Nc) \in \{(1,1), (1,2), (1,4), (1,8), (2,1), (4,1), (8,1)\}$

### Análise e Gráficos

- **Tempo de Execução**: tempo total para processar $M$ números em cada configuração
- **Ocupação do Buffer**: série temporal da ocupação do buffer durante a execução
- **Mapas de Calor**: ocupação média do buffer entre configurações para cada $N$

