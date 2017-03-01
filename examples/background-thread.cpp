
//-----------------------------------------------------------------------------------------------100
/// @file background-thread.cpp
/// @author Susanne van den Elsen
/// @date 2017
//--------------------------------------------------------------------------------------------------

#include <chrono>
#include <iostream>
#include <thread>

//--------------------------------------------------------------------------------------------------

class manager
{
public:
   
   manager()
   {
      // pthread_mutex_init(&m_mutex, nullptr);
   }
   
   ~manager()
   {
      cancel_thread();
   }
   
   void cancel_thread()
   {
      if (m_background_thread.joinable())
      {
         m_background_thread.join();
      }
   }

   void run_thread()
   {
      // if (pthread_mutex_trylock(&m_mutex))
      if (!m_mutex.try_lock())
      {
         std::cout << "[manager]\tbackground thread already running" << std::endl;
         return;
      }
      
      cancel_thread();
      
      std::cout << "[manager]\tstarting background thread" << std::endl;
      m_background_thread = std::thread([this]
         {
            // pthread_mutex_lock(&m_mutex);
            m_mutex.lock();
            std::cout << "[background_thread]\tHello World!" << std::endl; 
            // pthread_mutex_unlock(&m_mutex);
            m_mutex.unlock();
         }
      );
      
      m_mutex.unlock();
      // pthread_mutex_unlock(m_mutex);
   }
   
private:
   
   std::thread m_background_thread;
   std::mutex m_mutex;

}; // end class manager

//--------------------------------------------------------------------------------------------------

int main()
{
   using namespace std::chrono_literals;
   
   manager m;
   m.run_thread();
   // std::this_thread::sleep_for(1s);
   m.run_thread();

   return 0;
}

//--------------------------------------------------------------------------------------------------
