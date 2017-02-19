
#include <thread>

int main()
{
    int x, y, z;
    std::mutex m;
    
    std::thread t1([&m, &x, &y]
    {
        m.lock();
        int x_local = x;
        m.unlock();
        if (x_local == 0)
        {
            y = 1;                  // datarace: line 23
        }
    });
    
    std::thread t2([&m, &x, &y, &z]
    {
        m.lock();
        x = 1;
        m.unlock();
        z = x + y;                  // datarace: line 16
    });
                   
    t1.join();
    t2.join();
    
    return 0;
}
