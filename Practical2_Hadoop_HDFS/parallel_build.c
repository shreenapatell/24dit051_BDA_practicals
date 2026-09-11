#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main()
{
    pid_t c1, c2;

    c1 = fork();

    if(c1 == 0)
    {
        printf("Compiling file1...\n");
        sleep(2);
        printf("file1 compiled.\n");
        exit(0);
    }

    c2 = fork();

    if(c2 == 0)
    {
        printf("Compiling file2...\n");
        sleep(3);
        printf("file2 compiled.\n");
        exit(0);
    }

    wait(NULL);
    wait(NULL);

    printf("\nLinking files...\n");
    sleep(1);
    printf("Build completed successfully.\n");

    return 0;
}

