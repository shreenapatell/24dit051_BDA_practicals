#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main()
{
    pid_t pid;

    printf("Parent Process Started\n");
    printf("Parent PID : %d\n", getpid());

    pid = fork();

    if (pid < 0)
    {
        perror("fork failed");
        return 1;
    }

    if (pid == 0)
    {
        printf("\n--- Child Process ---\n");
        printf("Child PID  : %d\n", getpid());
        printf("Parent PID : %d\n", getppid());

        printf("\nExecuting 'ls' using exec()...\n");

        execl("/bin/pwd", "pwd", NULL);

        perror("exec failed");
        exit(1);
    }
    else
    {
        wait(NULL);

        printf("\nChild process completed.\n");
        printf("Parent exiting.\n");
    }

    return 0;
}
