#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

int main()
{
    int source, destination;
    char buffer[1024];
    ssize_t bytesRead;
    struct stat fileInfo;

    source = open("input.txt", O_RDONLY);

    if(source == -1)
    {
        perror("Error opening source file");
        return 1;
    }

    destination = open("output.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);

    if(destination == -1)
    {
        perror("Error creating output file");
        close(source);
        return 1;
    }

    while((bytesRead = read(source, buffer, sizeof(buffer))) > 0)
    {
        write(destination, buffer, bytesRead);
    }

    if(stat("input.txt", &fileInfo) == 0)
    {
        printf("File Size : %ld bytes\n", fileInfo.st_size);
        printf("Permissions : %o\n", fileInfo.st_mode & 0777);
    }

    close(source);
    close(destination);

    printf("\nFile copied successfully.\n");

    return 0;
}
