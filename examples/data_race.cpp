
#include <thread>

//------------------------------------------------------------------

void thread1(std::mutex& m, int& x, int& y)
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

void thread2(std::mutex& m, int& x, int& y, int& z)
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
    
   std::thread t1(thread1, std::ref(m), std::ref(x), std::ref(y));
   std::thread t2(thread2, std::ref(m), std::ref(x), std::ref(y), std::ref(z));
             
   t1.join();
   t2.join();
    
   return 0;
}

//------------------------------------------------------------------
