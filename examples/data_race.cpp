
#include <thread>

//------------------------------------------------------------------

void thread0(std::mutex& m, int& x, int& y)
{
   // m.lock();
   int x_local = x;
   // m.unlock();
   if (x_local == 1)          // datarace: line 23
   {
      y = 1;                  // datarace: line 25
   }
   pthread_exit(0);
}

//------------------------------------------------------------------

void thread1(std::mutex& m, int& x, int& y, int& z)
{
   // m.lock();
   x = 1;                     // datarace: line 9
   // m.unlock();
   z = x + y;                 // datarace: line 13
   pthread_exit(0);
}

//------------------------------------------------------------------

int main()
{
   int x, y, z;
   std::mutex m;
    
   std::thread t0(thread0, std::ref(m), std::ref(x), std::ref(y));
   std::thread t1(thread1, std::ref(m), std::ref(x), std::ref(y), std::ref(z));
             
   t0.join();
   t1.join();
    
   return 0;
}

//------------------------------------------------------------------
