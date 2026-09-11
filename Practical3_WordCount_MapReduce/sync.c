#include <stdio.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

int main()
{
    struct stat src, dst;

    if(stat("input.txt",&src)!=0)
    {
        perror("input");
        return 1;
    }

    if(stat("backup.txt",&dst)!=0 || src.st_mtime > dst.st_mtime)
    {
        int in=open("input.txt",O_RDONLY);
        int out=open("backup.txt",O_WRONLY|O_CREAT|O_TRUNC,0644);

        char buf[1024];
        int n;

        while((n=read(in,buf,sizeof(buf)))>0)
            write(out,buf,n);

        close(in);
        close(out);

        printf("Backup updated.\n");
    }
    else
    {
        printf("Backup already up to date.\n");
    }

    return 0;
}
