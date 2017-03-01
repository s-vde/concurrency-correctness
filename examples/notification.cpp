
#include <array>
#include <numeric>
#include <thread>

//--------------------------------------------------------------------------------------------------

bool done = false;

int thread1(std::array<int,2>& a)
{
   while (!done)
   {
      // wait
   }
   return std::accumulate(a.begin(), a.end(), 0);
}

//--------------------------------------------------------------------------------------------------

void thread2(std::array<int,2>& a)
{
   for (auto& element : a)
   {
      ++element;
   }
   done = true;
}

//--------------------------------------------------------------------------------------------------

int main()
{
   std::array<int,2> a{ 0, 0 };
   
   std::thread t1(thread1, std::ref(a));
   std::thread t2(thread2, std::ref(a));
   
   t1.join();
   t2.join();
   
   return 0;
}

//--------------------------------------------------------------------------------------------------
