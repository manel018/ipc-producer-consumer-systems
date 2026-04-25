#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <string.h>
#include <time.h>
#include <math.h>

#define BUFFER_SIZE 20  // Tamanho fixo para representação do número
#define NUMERO_PARADA 0  // Número que indica término

// Função para gerar o próximo número conforme a sequência N_i = N_{i-1} + Delta
// Onde Delta é um valor aleatório entre 1 e 100
int gerar_proximo_numero(int anterior) {
    if (anterior == 0) {
        return 1;  // N0 = 1
    }
    
    int delta = (rand() % 100) + 1;  // Delta entre 1 e 100
    return anterior + delta;
}

// Função para verificar se um número é primo
int eh_primo(int numero) {
    if (numero <= 1) return 0;
    if (numero == 2) return 1;
    if (numero % 2 == 0) return 0;
    
    int limite = (int)sqrt(numero);
    for (int i = 3; i <= limite; i += 2) {
        if (numero % i == 0) return 0;
    }
    return 1;
}

// Função do processo produtor
void produtor(int write_fd, int quantidade) {
    int numero_atual = 1;
    int delta = 0;
    char buffer[BUFFER_SIZE];
    
    printf("[Produtor] Iniciando produção de %d números...\n", quantidade);
    
    for (int i = 0; i < quantidade; i++) {
        // Converter número para string de tamanho fixo
        snprintf(buffer, BUFFER_SIZE, "%019d", numero_atual);
        
        // Escrever no pipe
        if (write(write_fd, buffer, BUFFER_SIZE) == -1) {
            perror("[Produtor] Erro ao escrever no pipe");
            exit(1);
        }
        
        printf("[Produtor] Enviado: %d (Delta = %d)\n", 
               numero_atual, 
               delta
            );
        
        // Gerar próximo número
        delta = rand() % 100 + 1;
        numero_atual += delta;

        // Pequena pausa para simular produção mais realista
        usleep(10000);  // 10ms
    }
    
    // Enviar número 0 para sinalizar término
    snprintf(buffer, BUFFER_SIZE, "%019d", NUMERO_PARADA);
    write(write_fd, buffer, BUFFER_SIZE);
    printf("[Produtor] Enviado sinal de término (0)\n");
    
    close(write_fd);
    printf("[Produtor] Finalizado.\n");
}

// Função do processo consumidor
void consumidor(int read_fd) {
    char buffer[BUFFER_SIZE];
    int numero;
    int total_recebidos = 0;
    int primos_encontrados = 0;
    
    printf("[Consumidor] Iniciando consumo...\n");
    
    while (1) {
        // Ler do pipe
        ssize_t bytes_read = read(read_fd, buffer, BUFFER_SIZE);
        
        if (bytes_read == -1) {
            perror("[Consumidor] Erro ao ler do pipe");
            exit(1);
        }
        
        if (bytes_read == 0) {
            printf("[Consumidor] Pipe fechado pelo produtor.\n");
            break;
        }
        
        // Converter string para número
        numero = atoi(buffer);
        total_recebidos++;
        
        if (numero == NUMERO_PARADA) {
            printf("[Consumidor] Sinal de término recebido.\n");
            break;
        }
        
        // Verificar se é primo
        if (eh_primo(numero)) {
            printf("[Consumidor] %d é PRIMO!\n", numero);
            primos_encontrados++;
        } else {
            printf("[Consumidor] %d não é primo.\n", numero);
        }
    }
    
    close(read_fd);
    printf("[Consumidor] Finalizado. Total recebidos: %d, Primos encontrados: %d\n", 
           total_recebidos, primos_encontrados);
}

int main(int argc, char *argv[]) {
    int pipe_fd[2];
    pid_t pid;
    int quantidade;
    
    // Verificar argumentos
    if (argc != 2) {
        fprintf(stderr, "Uso: %s <quantidade_de_numeros>\n", argv[0]);
        fprintf(stderr, "Exemplo: %s 1000\n", argv[0]);
        exit(1);
    }
    
    quantidade = atoi(argv[1]);
    if (quantidade <= 0) {
        fprintf(stderr, "Quantidade deve ser um número positivo.\n");
        exit(1);
    }
    
    // Inicializar gerador de números aleatórios
    srand(time(NULL));
    
    // Criar pipe
    if (pipe(pipe_fd) == -1) {
        perror("Erro ao criar pipe");
        exit(1);
    }
    
    // Criar processo filho via fork
    pid = fork();
    
    if (pid == -1) {
        perror("Erro ao criar processo filho");
        exit(1);
    }
    
    if (pid == 0) {
        // Processo filho - Consumidor
        close(pipe_fd[1]);  // Fechar extremidade de escrita
        consumidor(pipe_fd[0]);
    } else {
        // Processo pai - Produtor
        close(pipe_fd[0]);  // Fechar extremidade de leitura
        produtor(pipe_fd[1], quantidade);
        
        // Aguardar processo filho terminar
        wait(NULL);
        printf("[Main] Processo filho finalizado.\n");
    }
    
    return 0;
}