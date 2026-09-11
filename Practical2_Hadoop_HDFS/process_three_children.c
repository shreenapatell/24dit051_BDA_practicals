#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main()
{
    pid_t pid;

    for(int i = 0; i < 3; i++)
    {
        pid = fork();

        if(pid == 0)
        {
            printf("\nChild %d\n", i + 1);

            if(i == 0)
                execl("/bin/ls", "ls", "-l", NULL);
            else if(i == 1)
                execl("/bin/pwd", "pwd", NULL);
            else
                execl("/bin/date", "date", NULL);

            perror("exec failed");
            exit(1);
        }
    }

    while(wait(NULL) > 0);

    printf("\nAll child processes completed.\n");

    return 0;
}
