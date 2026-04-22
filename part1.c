#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <time.h>
#include <sys/types.h>

#define MSG_SIZE 20

// Função para verificar se número é primo
int is_prime(int n) {
    if (n <= 1) return 0;
    if (n == 2) return 1;
    if (n % 2 == 0) return 0;

    for (int i = 3; i * i <= n; i += 2) {
        if (n % i == 0)
            return 0;
    }
    return 1;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Uso: %s <quantidade>\n", argv[0]);
        return 1;
    }

    int qtd = atoi(argv[1]);

    int pipefd[2];
    pipe(pipefd);

    pid_t pid = fork();

    if (pid < 0) {
        perror("fork");
        return 1;
    }

    // =========================
    // CONSUMIDOR (FILHO)
    // =========================
    if (pid == 0) {
        close(pipefd[1]); // fecha escrita

        char buffer[MSG_SIZE];

        while (1) {
            read(pipefd[0], buffer, MSG_SIZE);

            int num = atoi(buffer);

            if (num == 0) break;

            if (is_prime(num))
                printf("[Consumidor] %d é primo\n", num);
            else
                printf("[Consumidor] %d NÃO é primo\n", num);
        }

        close(pipefd[0]);
    }

    // =========================
    // PRODUTOR (PAI)
    // =========================
    else {
        close(pipefd[0]); // fecha leitura

        srand(time(NULL));

        int current = 1;
        char buffer[MSG_SIZE];

        for (int i = 0; i < qtd; i++) {
            int delta = rand() % 100 + 1;
            current += delta;

            snprintf(buffer, MSG_SIZE, "%d", current);
            write(pipefd[1], buffer, MSG_SIZE);
        }

        // envia 0 para encerrar
        snprintf(buffer, MSG_SIZE, "%d", 0);
        write(pipefd[1], buffer, MSG_SIZE);

        close(pipefd[1]);
    }

    return 0;
}