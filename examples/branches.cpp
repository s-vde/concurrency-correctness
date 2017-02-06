
#include <iostream>
#include <pthread.h>

int x = 0;
int y = 0;
int z = 0;

void* thread1(void* args)
{
    if (x == 1)
    {
        y = 1;
    }
//    y = 1;
    pthread_exit(0);
}

void* thread2(void* args)
{
    x = 1;
    z = x + y;
    pthread_exit(0);
}

int main()
{
    pthread_t t1, t2;
    pthread_create(&t1, 0, thread1, 0);
    pthread_create(&t2, 0, thread2, 0);
    
    pthread_join(t1, 0);
    pthread_join(t2, 0);
   
    std::cout << "result=" << z << "\n";
   
    return 0;
}