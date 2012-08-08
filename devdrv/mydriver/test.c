
#include<stdio.h>
#include<sys/types.h>
#include<sys/stat.h>
#include<fcntl.h>

int main(void)
{
    int fd;
    int i;
    char *buf="we love duanduan! god bless our family!\n";
    char buf1[22];

    fd = open("/dev/myDriver",O_RDWR); 
    if (fd == -1)
    {
        printf("Can't open file \n");
        exit(-1);
    }

    write(fd,buf,22);
    read(fd,buf1,22);

    printf("\n");
    for(i=0; i<22; i++)
        printf("%c",buf1[i]);
    printf("\n");

    close(fd);
    return 0;
}
