#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>

int main()
{
    int fd;
    char ch;

    fd = open("input.txt", O_RDONLY);

    if(fd == -1)
    {
        perror("open");
        return 1;
    }

    lseek(fd, 10, SEEK_SET);

    read(fd, &ch, 1);

    printf("Character at position 10: %c\n", ch);

    close(fd);

    return 0;
}
