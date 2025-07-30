#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <errno.h>
#include <sys/stat.h> // Для stat (проверка существования файла)
#include <android/log.h> // Для Android logging
#include <pthread.h> // Для многопоточности (опционально, но лучше для продакшена)
#include <signal.h> // Для обработки сигналов

#define LOG_TAG "CustomAgent"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)
#define LOGD(...) __android_log_print(ANDROID_LOG_DEBUG, LOG_TAG, __VA_ARGS__) // Добавим Debug логи

#define DEFAULT_PORT 6000
#define BUFFER_SIZE 4096 // Размер буфера для чтения команд и отправки мелких ответов
#define MAX_SHELL_OUTPUT_SIZE (1024 * 1024) // Максимальный размер вывода shell команды (1MB)
#define NEWLINE_MARKER '|' // Маркер для замены \n в SHELL выводе

// Глобальный флаг завершения работы
volatile sig_atomic_t keep_running = 1;

// Обработчик сигналов для чистого завершения
void sig_handler(int sig) {
    LOGI("Received signal %d, shutting down...", sig);
    keep_running = 0;
}

// Функция для отправки ответа клиенту
void send_response(int client_sock, const char *response) {
    if (client_sock < 0 || response == NULL) return;
    // Убедимся, что ответ заканчивается на \n
    size_t len = strlen(response);
    char *full_response = NULL;
    if (len > 0 && response[len-1] == '\n') {
        full_response = strdup(response);
    } else {
        full_response = malloc(len + 2); // +1 для \n, +1 для \0
        if (full_response) {
            strcpy(full_response, response);
            full_response[len] = '\n';
            full_response[len+1] = '\0';
        }
    }

    if (full_response) {
        // Добавляем логгирование отправляемого ответа (убираем \n для лога)
        char log_resp[BUFFER_SIZE];
        strncpy(log_resp, full_response, BUFFER_SIZE - 1);
        log_resp[BUFFER_SIZE - 1] = '\0';
        if (strlen(log_resp) > 0 && log_resp[strlen(log_resp)-1] == '\n') {
             log_resp[strlen(log_resp)-1] = '\0';
        }
        LOGD("Sending response: %s", log_resp);

        if (send(client_sock, full_response, strlen(full_response), 0) < 0) {
            LOGE("Error sending response to client: %s", strerror(errno));
        }
        free(full_response);
    } else {
        LOGE("Failed to allocate memory for response.");
        // Можно попытаться отправить ERROR, но сокет может быть уже проблемным
        send(client_sock, "ERROR internal error\n", strlen("ERROR internal error\n"), 0);
    }
}

// Функция для выполнения shell команды
// ВАЖНО: КРАЙНЕ НЕБЕЗОПАСНО! Нужна санитизация 'command' или переход на execvp/posix_spawn
char* run_shell_command(const char *command) {
    LOGI("Running shell command: %s", command);
    char buffer[512]; // Буфер для чтения строк из popen
    char *result = NULL;
    size_t result_size = 0;
    FILE *fp;

    // Ограничиваем размер вывода, чтобы не исчерпать память
    result = malloc(1); // Начальный пустой буфер
    if (result == NULL) {
         LOGE("Memory allocation failed for shell output");
         return strdup("ERROR memory allocation failed");
    }
    result[0] = '\0'; // Пустая строка

    fp = popen(command, "r");
    if (fp == NULL) {
        LOGE("Failed to run command '%s': %s", command, strerror(errno));
        free(result);
        return strdup("ERROR popen failed");
    }

    // Читаем вывод команды построчно
    while (fgets(buffer, sizeof(buffer), fp) != NULL) {
        size_t chunk_len = strlen(buffer);
        // Проверяем, не превысит ли добавление следующего куска лимит
        if (result_size + chunk_len >= MAX_SHELL_OUTPUT_SIZE) {
             LOGE("Shell output exceeded max size (%d bytes)", MAX_SHELL_OUTPUT_SIZE);
             // Пытаемся отправить частичный результат или ошибку
             char* temp = realloc(result, result_size + 1); // Убеждаемся, что есть место для \0
             if (temp) {
                  result = temp;
                  result[result_size] = '\0'; // Обрезаем
                  // Добавляем маркер обрезки, если нужно
             }
             // Закрываем popen и выходим
             pclose(fp);
             // Возвращаем ошибку или частичный результат с маркером
             char* truncated_msg = strdup("ERROR output truncated\n");
             if (result) free(result);
             return truncated_msg;
        }

        // Заменяем \n на маркер, КРОМЕ ПОСЛЕДНЕГО \n в строке от fgets (если он есть)
        // fgets оставляет \n в конце строки. Мы хотим заменить \n внутри вывода, но
        // сохранить структуру строк для последующей замены маркера обратно на \n клиентом.
        // Простейший способ: заменить ВСЕ \n из fgets на маркер. Клиент заменит их обратно.
        for (size_t i = 0; i < chunk_len; ++i) {
            if (buffer[i] == '\n') {
                buffer[i] = NEWLINE_MARKER;
            }
        }

        // Расширяем буфер и копируем данные
        char* temp = realloc(result, result_size + chunk_len + 1); // +1 для \0
        if (temp == NULL) {
             LOGE("Memory allocation failed reading command output");
             free(result);
             pclose(fp);
             return strdup("ERROR memory allocation failed");
        }
        result = temp;
        strcpy(result + result_size, buffer);
        result_size += chunk_len;
    }

    // Добавляем null-терминатор в конец результата
    if (result) result[result_size] = '\0';


    // Проверяем статус завершения popen
    int status = pclose(fp);
    if (status == -1) {
         LOGE("Error closing popen stream: %s", strerror(errno));
         // Если pclose завершился с ошибкой, возможно, команда не выполнилась успешно.
         // Это может быть индикатором ошибки команды, даже если был stdout.
         // В реальном агенте нужно анализировать WEXITSTATUS(status) и WIFEXITED(status)
         // В этом простом примере игнорируем статус закрытия, если получили хоть какой-то вывод.
    }

    if (result == NULL || result_size == 0) {
        // Если команда ничего не вывела или result_size 0
        // Если pclose показал ошибку, возможно, тут надо вернуть ошибку?
        // Для простоты: если вывода нет, возвращаем пустую строку
        free(result); // Освобождаем начальный пустой буфер
        return strdup("");
    }

    LOGD("Shell command output collected (size %zu)", result_size);
    return result; // Вызывающий должен освободить эту память
}

// Функция для выполнения shell команды 'am start'
// ВАЖНО: НЕБЕЗОПАСНО! Нужна санитизация component_name
void run_am_start(const char* component_name, int client_sock) {
    if (component_name == NULL || strlen(component_name) == 0) {
        send_response(client_sock, "ERROR START_APP requires component name");
        return;
    }
    LOGI("Running am start -n %s", component_name);
    char shell_cmd[BUFFER_SIZE + 32]; // Достаточно для "am start -n " + component_name
    // ВАЖНО: Тут ДОЛЖНА БЫТЬ САНИТИЗАЦИЯ component_name!
    snprintf(shell_cmd, sizeof(shell_cmd), "am start -n %s 2>&1", component_name); // Перенаправляем stderr в stdout

    char *output = run_shell_command(shell_cmd); // Используем нашу функцию shell
    if (output) {
        // Простая проверка вывода 'am start'
        // adb shell am start возвращает 0 даже при ошибках, если синтаксис команды верен.
        // Ошибки типа Activity not found, Permission denied и т.п. выводятся в stdout/stderr.
        // Ищем известные маркеры ошибок.
        if (strstr(output, "Error:") != NULL || strstr(output, "Exception") != NULL || strstr(output, "Failed to") != NULL) {
             char err_resp[MAX_SHELL_OUTPUT_SIZE + 64]; // ERROR + сообщение + \n
             snprintf(err_resp, sizeof(err_resp), "ERROR failed to start app: %s", output);
             // Заменяем \n в ошибке на маркер, чтобы ответ был однострочным по протоколу
             for (size_t i = 0; i < strlen(err_resp); ++i) {
                 if (err_resp[i] == '\n') err_resp[i] = NEWLINE_MARKER;
             }
             send_response(client_sock, err_resp);
        } else {
            send_response(client_sock, "OK"); // Считаем, что успешно, если нет явных ошибок в выводе
        }
        free(output);
    } else {
         send_response(client_sock, "ERROR failed to execute am start command");
    }
}

// Функция для проверки существования файла
// ВАЖНО: НЕБЕЗОПАСНО! Нужна санитизация file_path
void check_file_exists(const char* file_path, int client_sock) {
    if (file_path == NULL || strlen(file_path) == 0) {
        send_response(client_sock, "ERROR EXIST_FILE requires file path");
        return;
    }
     // ВАЖНО: Тут ДОЛЖНА БЫТЬ САНИТИЗАЦИЯ file_path!
    struct stat st;
    if (stat(file_path, &st) == 0) {
        send_response(client_sock, "OK true");
    } else {
        if (errno == ENOENT) {
            send_response(client_sock, "OK false");
        } else {
            LOGE("Error checking file %s: %s", file_path, strerror(errno));
            char err_resp[BUFFER_SIZE];
            snprintf(err_resp, sizeof(err_resp), "ERROR checking file: %s", strerror(errno));
            send_response(client_sock, err_resp);
        }
    }
}


void *client_handler(void *socket_desc) {
    // Получаем дескриптор сокета
    int client_sock = *(int*)socket_desc;
    free(socket_desc); // Освобождаем выделенную память

    char buffer[BUFFER_SIZE];
    int read_size;

    // Устанавливаем небольшой таймаут чтения для клиента
    struct timeval tv;
    tv.tv_sec = 30; // Например, 30 секунд
    tv.tv_usec = 0;
    setsockopt(client_sock, SOL_SOCKET, SO_RCVTIMEO, (const char*)&tv, sizeof tv);


    LOGI("Client handler started for socket %d", client_sock);

    // Обработка команд от клиента
    while(keep_running && (read_size = recv(client_sock, buffer, BUFFER_SIZE - 1, 0)) > 0) {
        buffer[read_size] = '\0'; // Null-terminate whatever we received

        // Обработка частичных команд - если команда пришла не полностью (нет \n)
        // Этот простой агент не умеет обрабатывать команды по частям.
        // Он предполагает, что каждая команда приходит целиком и заканчивается \n.
        // Если \n нет в конце буфера, это проблема протокола или частичное чтение.
        // Для надежности нужно буферизовать ввод и обрабатывать команды посимвольно до \n.
        // В этом простом примере предполагаем, что read() получает всю команду до \n.
        // Если вы используете sendall() в клиенте с \n, это часто работает.

        // Убираем \n в конце, если есть
        if (read_size > 0 && buffer[read_size - 1] == '\n') {
            buffer[read_size - 1] = '\0';
        }
        // Убираем \r, если есть (для совместимости с Windows клиентами)
        if (read_size > 1 && buffer[read_size - 2] == '\r') {
             buffer[read_size - 2] = '\0';
        }

        LOGI("Received command: %s", buffer);

        // Парсинг команды - очень примитивный, небезопасный!
        char *command = strtok(buffer, " ");
        char *arg = strtok(NULL, ""); // Все остальное как один аргумент

        if (command == NULL || strlen(command) == 0) {
            send_response(client_sock, "ERROR empty command");
            continue; // Пропускаем пустые команды
        }

        // Обработка команд
        if (strcmp(command, "GET_SDK") == 0) {
            char* sdk_output = run_shell_command("getprop ro.build.version.sdk");
             if (sdk_output && strncmp(sdk_output, "ERROR", 5) != 0 && strlen(sdk_output) > 0) {
                char response[BUFFER_SIZE]; // Используем BUFFER_SIZE для ответа
                snprintf(response, sizeof(response), "OK %s", sdk_output); // Не добавляем \n, это сделает send_response
                send_response(client_sock, response);
             } else {
                send_response(client_sock, "ERROR could not get SDK version");
             }
             if (sdk_output) free(sdk_output); // Освобождаем память

        } else if (strcmp(command, "START_APP") == 0) {
            run_am_start(arg, client_sock); // Передаем остаток строки как аргумент component_name

        } else if (strcmp(command, "EXIST_FILE") == 0) {
             check_file_exists(arg, client_sock); // Передаем остаток строки как аргумент file_path

        } else if (strcmp(command, "SHELL") == 0) {
             if (arg) {
                 // Выполняем shell команду
                 char* shell_output = run_shell_command(arg);
                 if (shell_output) {
                     if (strncmp(shell_output, "ERROR", 5) == 0) {
                         // run_shell_command вернула ошибку
                         send_response(client_sock, shell_output); // Включает "ERROR ..."
                     } else {
                          // Успех. shell_output уже содержит замененные \n на NEWLINE_MARKER
                          // и не содержит финального \n, так как run_shell_command его удаляет.
                          char response[MAX_SHELL_OUTPUT_SIZE + 64]; // OK + output + \n
                          snprintf(response, sizeof(response), "OK %s", shell_output);
                          send_response(client_sock, response);
                     }
                     free(shell_output);
                 } else {
                      send_response(client_sock, "ERROR shell command execution failed");
                 }
             } else {
                  send_response(client_sock, "ERROR SHELL command requires an argument");
             }

        } else if (strcmp(command, "EXIT") == 0) {
            LOGI("Client requested EXIT for socket %d", client_sock);
            send_response(client_sock, "OK bye"); // Отправляем подтверждение
            break; // Выходим из цикла обработки команд
        }
        else {
            LOGE("Unknown command: %s", command);
            send_response(client_sock, "ERROR Unknown command");
        }
    } // Конец цикла обработки команд

    if (read_size == 0) {
        LOGI("Client disconnected from socket %d", client_sock);
    } else if (read_size < 0) {
        if (errno == EWOULDBLOCK || errno == EAGAIN) {
             LOGI("Client read timeout on socket %d", client_sock);
        } else {
             LOGE("Read error on socket %d: %s", client_sock, strerror(errno));
        }
    }

    // Закрываем сокет клиента
    close(client_sock);
    LOGI("Client handler for socket %d finished", client_sock);

    // В многопоточной версии поток завершится здесь.
    // В однопоточной (как в main ниже) это не используется как поток.
    return NULL;
}


int main() {
    int server_fd, client_sock;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);

    LOGI("Custom Agent Starting...");

    // Установка обработчиков сигналов для чистого завершения
    signal(SIGINT, sig_handler);  // Ctrl+C
    signal(SIGTERM, sig_handler); // Команда kill

    // Создание сокета
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        LOGE("Socket creation failed: %s", strerror(errno));
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    // Установка опций сокета (переиспользование адреса и порта)
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt))) {
        LOGE("setsockopt failed: %s", strerror(errno));
        perror("setsockopt");
        close(server_fd);
        exit(EXIT_FAILURE);
    }
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY; // Слушаем на всех интерфейсах (0.0.0.0)
    address.sin_port = htons(DEFAULT_PORT);

    // Привязка сокета
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        LOGE("Bind failed on port %d: %s", DEFAULT_PORT, strerror(errno));
        perror("bind failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    // Прослушивание входящих соединений (максимум 3 в очереди)
    if (listen(server_fd, 3) < 0) {
        LOGE("Listen failed: %s", strerror(errno));
        perror("listen");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    LOGI("Agent listening on port %d", DEFAULT_PORT);

    // Главный цикл ожидания соединений
    while (keep_running) {
        LOGI("Waiting for new connection...");

        // Устанавливаем таймаут на accept, чтобы main цикл мог проверить keep_running
        struct timeval tv_accept;
        tv_accept.tv_sec = 1; // Проверять флаг каждую секунду
        tv_accept.tv_usec = 0;
        setsockopt(server_fd, SOL_SOCKET, SO_RCVTIMEO, (const char*)&tv_accept, sizeof tv_accept);

        // Принятие соединения
        client_sock = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen);

        if (client_sock < 0) {
            if (errno == EWOULDBLOCK || errno == EAGAIN) {
                // Таймаут accept, продолжаем цикл для проверки keep_running
                continue;
            }
            if (errno == EINTR) {
                // Прервано сигналом, выходим из цикла
                LOGI("Accept interrupted by signal.");
                break;
            }
            LOGE("Accept failed: %s", strerror(errno));
            perror("accept");
            // Не критическая ошибка, продолжаем ждать
            continue;
        }

        // Если соединение принято
        char client_ip[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &address.sin_addr, client_ip, INET_ADDRSTRLEN);
        LOGI("Connection accepted from %s:%d (socket %d)", client_ip, ntohs(address.sin_port), client_sock);

        // --- Обработка клиента ---
        // В этом простом примере обрабатываем клиента в главном потоке.
        // Для продакшена следует создавать новый поток или использовать неблокирующий ввод/вывод.
        // pthread_t sniffer_thread;
        // int *new_sock = malloc(sizeof(int));
        // *new_sock = client_sock;
        // if( pthread_create( &sniffer_thread , NULL ,  client_handler , (void*) new_sock) < 0)
        // {
        //     LOGE("Could not create thread for client %d", client_sock);
        //     perror("could not create thread");
        //     close(client_sock); // Закрываем соединение, если поток не создан
        //     continue;
        // }
        // pthread_detach(sniffer_thread); // Не ждем завершения потока

        // Однопоточная обработка (просто вызываем функцию)
        // Внимание: Это блокирует основной цикл, пока клиент не отключится!
        int temp_sock = client_sock; // Передаем копию дескриптора
        client_handler((void*)&temp_sock); // sock_desc тут не освобождается, т.к. не malloc
        // Дескриптор закрывается внутри client_handler
        // Однопоточный вариант:
        // client_handler(&client_sock); // sock_desc тут не освобождается, т.к. не malloc

    } // Конец главного цикла ожидания соединений

    LOGI("Agent shutting down.");
    close(server_fd);
    LOGI("Agent finished.");
    return 0;
}