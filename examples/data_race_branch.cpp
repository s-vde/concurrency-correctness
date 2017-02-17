
#include <thread>

int main()
{
    int x, y, z;
    
    std::thread t1([&y]
    {
        if (x == 1)                 // datarace: line 18
        {
            y = 1;                  // datarace: line 19
        }
    });
    
    std::thread t2([&x, &y, &z]
    {
        x = 1;                      // datarace: line 10
        z = x + y;                  // datarace: line 18, 19
    });
                   
    t1.join();
    t2.join();
    
    return 0;
}
