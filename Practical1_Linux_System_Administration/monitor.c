#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/utsname.h>
#include <sys/sysinfo.h>

void display_proc_file(const char *filename)
{
    FILE *fp;
    char line[256];

    fp = fopen(filename, "r");

    if (fp == NULL)
    {
        perror("Error opening file");
        return;
    }

    while (fgets(line, sizeof(line), fp))
    {
        printf("%s", line);
    }

    fclose(fp);
}

int main()
{
    struct utsname info;
    struct sysinfo mem;

    printf("\n========== SYSTEM CALL INFORMATION ==========\n");

    printf("PID          : %d\n", getpid());
    printf("PPID         : %d\n", getppid());
    printf("UID          : %d\n", getuid());
    printf("GID          : %d\n", getgid());

    if (uname(&info) == -1)
    {
        perror("uname");
        return 1;
    }

    printf("\nHostname     : %s\n", info.nodename);
    printf("Kernel       : %s\n", info.release);

    if (sysinfo(&mem) == -1)
    {
        perror("sysinfo");
        return 1;
    }

    printf("\nUptime       : %ld seconds\n", mem.uptime);
    printf("Total RAM    : %lu MB\n", mem.totalram / (1024 * 1024));
    printf("Free RAM     : %lu MB\n", mem.freeram / (1024 * 1024));
    printf("Swap Memory  : %lu MB\n", mem.totalswap / (1024 * 1024));

    printf("\n=============================================\n");

    printf("\n========== /proc/self/status ==========\n");
    display_proc_file("/proc/self/status");

    printf("\n========== /proc/version ==========\n");
    display_proc_file("/proc/version");

    printf("\n========== /proc/meminfo ==========\n");
    display_proc_file("/proc/meminfo");

    printf("\n========== /proc/uptime ==========\n");
    display_proc_file("/proc/uptime");

    return 0;
}
