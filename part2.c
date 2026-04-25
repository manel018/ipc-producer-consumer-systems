// produtor_consumidor.c
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <semaphore.h>
#include <time.h>
#include <math.h>
#include <unistd.h>
#include <errno.h>
#include <sys/stat.h>
#include <sys/types.h>

#define MAX_N 1000
#define MAX_THREADS 100
#define M 100000  // 10^5 Número total de itens a processar
#define MAXRAND 10000000  // 10^7
#define RUNS 10  // Número de execuções para cada configuração
#define OUTPUT_ROOT "analysis/part2"
#define OUTPUT_DATA_DIR "analysis/part2/data"
#define OUTPUT_PLOTS_DIR "analysis/part2/plots"

// Estrutura para o buffer compartilhado
typedef struct {
    int buffer[MAX_N];
    int size;           // Tamanho do buffer (N)
    int in;             // Índice de inserção
    int out;            // Índice de remoção
    int count;          // Número atual de itens no buffer
    int producers_done; // Indica que não haverá mais produção
    int* occupancy;     // Array para registrar ocupação
    int occupancy_size; // Tamanho do array de ocupação
    int occupancy_idx;  // Índice atual no array de ocupação
} SharedBuffer;

// Estrutura para argumentos das threads
typedef struct {
    SharedBuffer* shared;
    int thread_id;
    int run_id;
    int buffer_size;
    int num_producers;
    int num_consumers;
    int type;  // 0 = produtor, 1 = consumidor
    int* total_produced;
    int* total_consumed;
    sem_t* mutex;
    sem_t* empty;
    sem_t* full;
} ThreadArgs;

// Variáveis globais para controle
pthread_mutex_t print_mutex = PTHREAD_MUTEX_INITIALIZER;
int running = 1;

typedef struct {
    long long total;
    long long current;
    int last_percent;
    int current_n;
    int active;
} ProgressState;

static pthread_mutex_t progress_mutex = PTHREAD_MUTEX_INITIALIZER;
static ProgressState progress_state = {0, 0, -1, 0, 0};

static void progress_init_for_n(int n, long long total_items) {
    pthread_mutex_lock(&progress_mutex);
    progress_state.total = total_items;
    progress_state.current = 0;
    progress_state.last_percent = -1;
    progress_state.current_n = n;
    progress_state.active = 1;
    pthread_mutex_unlock(&progress_mutex);
}

static void progress_add(long long delta) {
    const int bar_width = 40;

    pthread_mutex_lock(&progress_mutex);
    if (!progress_state.active || progress_state.total <= 0) {
        pthread_mutex_unlock(&progress_mutex);
        return;
    }

    progress_state.current += delta;
    if (progress_state.current > progress_state.total) {
        progress_state.current = progress_state.total;
    }

    int percent = (int)((progress_state.current * 100) / progress_state.total);
    if (percent != progress_state.last_percent || progress_state.current == progress_state.total) {
        int filled = (percent * bar_width) / 100;
        printf("\rN=%d [", progress_state.current_n);
        for (int i = 0; i < bar_width; i++) {
            putchar(i < filled ? '#' : '-');
        }
        printf("] %3d%% (%lld/%lld)", percent, progress_state.current, progress_state.total);
        fflush(stdout);
        progress_state.last_percent = percent;
    }

    pthread_mutex_unlock(&progress_mutex);
}

static void progress_finish_for_n(void) {
    pthread_mutex_lock(&progress_mutex);
    if (progress_state.active) {
        progress_state.current = progress_state.total;
        pthread_mutex_unlock(&progress_mutex);
        progress_add(0);
        pthread_mutex_lock(&progress_mutex);
        putchar('\n');
        fflush(stdout);
        progress_state.active = 0;
    }
    pthread_mutex_unlock(&progress_mutex);
}

static void ensure_directory(const char* path) {
    if (mkdir(path, 0777) != 0 && errno != EEXIST) {
        perror(path);
    }
}

static void ensure_output_directories(void) {
    ensure_directory("analysis");
    ensure_directory(OUTPUT_ROOT);
    ensure_directory(OUTPUT_DATA_DIR);
    ensure_directory(OUTPUT_PLOTS_DIR);
}

// Função para verificar se um número é primo
int is_prime(int numero) {
    if (numero <= 1) return 0;
    if (numero == 2) return 1;
    if (numero % 2 == 0) return 0;
    
    int limite = (int)sqrt(numero);
    for (int i = 3; i <= limite; i += 2) {
        if (numero % i == 0) return 0;
    }
    return 1;
}

// Função para registrar ocupação do buffer
void record_occupancy(SharedBuffer* shared) {
    if (shared->occupancy_idx < shared->occupancy_size) {
        shared->occupancy[shared->occupancy_idx++] = shared->count;
    }
}

// Função da thread produtora
void* producer(void* arg) {
    ThreadArgs* args = (ThreadArgs*)arg;
    SharedBuffer* shared = args->shared;
    int* total_produced = args->total_produced;
    sem_t* mutex = args->mutex;
    sem_t* empty = args->empty;
    sem_t* full = args->full;
    
    while (1) {
        // Verificar se já produzimos todos os itens
        int current_total;
        sem_wait(mutex);
        current_total = *total_produced;
        sem_post(mutex);

        if (current_total >= M) {
            break;
        }
        
        // Gerar número aleatório entre 1 e MAXRAND
        int number = (rand() % MAXRAND) + 1;
        
        // Aguardar buffer vazio disponível
        sem_wait(empty);
        
        // Entrar na região crítica
        sem_wait(mutex);
        
        // Verificar novamente se ainda precisa produzir
        if (*total_produced >= M) {
            sem_post(mutex);
            sem_post(empty);
            break;
        }
        
        // Produzir no buffer
        shared->buffer[shared->in] = number;
        shared->in = (shared->in + 1) % shared->size;
        shared->count++;
        (*total_produced)++;

        // Registrar ocupação
        record_occupancy(shared);
        
        // Sair da região crítica
        sem_post(mutex);
        
        // Sinalizar que há um item disponível
        sem_post(full);
        
        // Pequeno delay para simular trabalho
        // usleep(1);
    }
    
    return NULL;
}

// Função da thread consumidora
void* consumer(void* arg) {
    ThreadArgs* args = (ThreadArgs*)arg;
    SharedBuffer* shared = args->shared;
    int* total_consumed = args->total_consumed;
    sem_t* mutex = args->mutex;
    sem_t* empty = args->empty;
    sem_t* full = args->full;
    
    while (1) {
        // Verificar se já consumimos todos os itens
        int current_total;
        sem_wait(mutex);
        current_total = *total_consumed;
        sem_post(mutex);

        if (current_total >= M) {
            break;
        }
        
        // Aguardar buffer cheio disponível
        sem_wait(full);
        
        // Entrar na região crítica
        sem_wait(mutex);
        
        // Verificar novamente
        if (*total_consumed >= M || (shared->producers_done && shared->count == 0)) {
            sem_post(mutex);
            sem_post(full);
            break;
        }
        
        // Consumir do buffer
        int number = shared->buffer[shared->out];
        shared->out = (shared->out + 1) % shared->size;
        shared->count--;
        (*total_consumed)++;
        
        // Registrar ocupação
        record_occupancy(shared);
        
        // Sair da região crítica
        sem_post(mutex);

        // Atualizar barra de progresso global do N atual.
        progress_add(1);
        
        // Sinalizar que há um espaço vazio
        sem_post(empty);
        
        // Mantém o custo computacional do consumidor
        int prime = is_prime(number);

        (void)prime;
    }
    
    return NULL;
}

// Função para executar uma configuração específica
double run_simulation(int N, int Np, int Nc, int run) {
    SharedBuffer shared;
    pthread_t producers[MAX_THREADS], consumers[MAX_THREADS];
    ThreadArgs prod_args[MAX_THREADS], cons_args[MAX_THREADS];
    sem_t mutex, empty, full;

    ensure_output_directories();
    
    // Inicializar buffer compartilhado
    shared.size = N;
    shared.in = 0;
    shared.out = 0;
    shared.count = 0;
    shared.producers_done = 0;
    shared.occupancy_size = M * 2; // Espaço para todas as operações
    shared.occupancy = (int*)malloc(shared.occupancy_size * sizeof(int));
    shared.occupancy_idx = 0;
    
    // Inicializar semáforos
    sem_init(&mutex, 0, 1);
    sem_init(&empty, 0, N);
    sem_init(&full, 0, 0);
    
    // Contadores totais
    int total_produced = 0;
    int total_consumed = 0;
    
    // Criar threads produtoras
    for (int i = 0; i < Np; i++) {
        prod_args[i].shared = &shared;
        prod_args[i].thread_id = i;
        prod_args[i].run_id = run;
        prod_args[i].buffer_size = N;
        prod_args[i].num_producers = Np;
        prod_args[i].num_consumers = Nc;
        prod_args[i].type = 0;
        prod_args[i].total_produced = &total_produced;
        prod_args[i].total_consumed = &total_consumed;
        prod_args[i].mutex = &mutex;
        prod_args[i].empty = &empty;
        prod_args[i].full = &full;
        pthread_create(&producers[i], NULL, producer, &prod_args[i]);
    }
    
    // Criar threads consumidoras
    for (int i = 0; i < Nc; i++) {
        cons_args[i].shared = &shared;
        cons_args[i].thread_id = i;
        cons_args[i].run_id = run;
        cons_args[i].buffer_size = N;
        cons_args[i].num_producers = Np;
        cons_args[i].num_consumers = Nc;
        cons_args[i].type = 1;
        cons_args[i].total_produced = &total_produced;
        cons_args[i].total_consumed = &total_consumed;
        cons_args[i].mutex = &mutex;
        cons_args[i].empty = &empty;
        cons_args[i].full = &full;
        pthread_create(&consumers[i], NULL, consumer, &cons_args[i]);
    }
    
    // Aguardar todas as threads terminarem
    for (int i = 0; i < Np; i++) {
        pthread_join(producers[i], NULL);
    }

    // Sinalizar que não haverá mais produção e acordar consumidores bloqueados.
    sem_wait(&mutex);
    shared.producers_done = 1;
    sem_post(&mutex);
    for (int i = 0; i < Nc; i++) {
        sem_post(&full);
    }

    for (int i = 0; i < Nc; i++) {
        pthread_join(consumers[i], NULL);
    }
    
    // Salvar dados de ocupação em arquivo
    char filename[256];
    snprintf(filename, sizeof(filename), "%s/occupancy_N%d_P%d_C%d.txt", OUTPUT_DATA_DIR, N, Np, Nc);
    FILE* fp = fopen(filename, "w");
    if (fp) {
        for (int i = 0; i < shared.occupancy_idx; i++) {
            fprintf(fp, "%d\n", shared.occupancy[i]);
        }
        fclose(fp);
    } else {
        fprintf(stderr, "Erro ao abrir arquivo para escrita: %s\n", filename);
    }
    
    // Limpeza
    sem_destroy(&mutex);
    sem_destroy(&empty);
    sem_destroy(&full);
    free(shared.occupancy);
    
    return 0.0; // Retornar tempo real seria medido externamente
}

// Função para medir tempo de execução
double measure_time(int N, int Np, int Nc, int runs) {
    struct timespec start, end;
    double total_time = 0;
    
    for (int r = 0; r < runs; r++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        run_simulation(N, Np, Nc, r);
        clock_gettime(CLOCK_MONOTONIC, &end);
        
        double time_taken = (end.tv_sec - start.tv_sec) + 
                            (end.tv_nsec - start.tv_nsec) / 1e9;
        total_time += time_taken;
    }
    
    return total_time / runs;
}

int main() {
    srand(time(NULL));
    ensure_output_directories();

    // printf("tempo médio: %.4f segundos\n", measure_time(10, 1, 4, 10));
    
    int N_values[] = {1, 10, 100, 1000};
    int combinations[][2] = {
        {1, 1}, {1, 2}, {1, 4}, {1, 8},
        {2, 1}, {4, 1}, {8, 1}
    };

    int num_combinations = sizeof(combinations) / sizeof(combinations[0]);
    int runs = RUNS;

    char times_filename[256];
    snprintf(times_filename, sizeof(times_filename), "%s/execution_times.csv", OUTPUT_DATA_DIR);

    FILE* times_fp = fopen(times_filename, "w");
    if (!times_fp) {
        fprintf(stderr, "Erro ao abrir %s para escrita.\n", times_filename);
        return 1;
    }
    fprintf(times_fp, "N,Produtores,Consumidores,TempoMedio\n");
    
    printf("=== PRODUTOR-CONSUMIDOR COM SEMAFOROS ===\n");
    printf("Total de itens a processar: %d\n", M);
    printf("Número de execuções por configuração: %d\n\n", runs);
    
    // Para cada N
    for (int n_idx = 0; n_idx < 4; n_idx++) {
        int N = N_values[n_idx];
        long long total_items_for_n = (long long)num_combinations * runs * M;

        printf("\n=== N = %d ===\n", N);
        progress_init_for_n(N, total_items_for_n);
        
        // Para cada combinação de threads
        for (int c = 0; c < num_combinations; c++) {
            int Np = combinations[c][0];
            int Nc = combinations[c][1];

            double avg_time = measure_time(N, Np, Nc, runs);

            fprintf(times_fp, "%d,%d,%d,%.9f\n", N, Np, Nc, avg_time);
        }

        progress_finish_for_n();
    }

    fclose(times_fp);
    
    printf("\n=== EXPERIMENTO CONCLUÍDO ===\n");
    printf("Arquivos de ocupação gerados para cada configuração.\n");
    
    return 0;
}