
//-----------------------------------------------------------------------------------------------100
/// @file dining-philosophers.c
/// @details Classic scenario where a number of philosophers are at a dining table. After thinking
/// for a while each philosopher tries to eat their spaghetti. For that they need two forks: the
/// one to their left, and the one to their right. Each of the forks can be held by one philosopher
/// at a time.
/// @note This program has a potential deadlock.
/// @author Susanne van den Elsen
/// @date 2017
//--------------------------------------------------------------------------------------------------

#include <pthread.h>
#include <array>

//--------------------------------------------------------------------------------------------------

struct fork
{
    fork()
    {
        pthread_mutex_init(&m_mutex, NULL);
    }
    
    void take_up()
    {
        pthread_mutex_lock(&m_mutex);
    }
    
    void put_down()
    {
        pthread_mutex_unlock(&m_mutex);
    }
    
private:
    
    pthread_mutex_t m_mutex;
    
}; // end struct fork

//--------------------------------------------------------------------------------------------------

std::array<fork,NR_THREADS> forks;
std::array<unsigned int,NR_THREADS> nr_meals;

//--------------------------------------------------------------------------------------------------

/// @brief Philosopher thread start routine

void* philosopher(void* args)
{
    int id = *(int*) args;
    int left = id;
    int right = (id+1) % NR_THREADS;
    
    forks[left].take_up();
    forks[right].take_up();
    ++nr_meals[id];
    forks[right].put_down();
    forks[left].put_down();

    pthread_exit(0); 
} 

//--------------------------------------------------------------------------------------------------

int main()
{
    pthread_t phils[NR_THREADS];
	int pid[NR_THREADS];
    
    // initialize
    for (int i = 0; i < NR_THREADS; ++i)
    {
    	pid[i] = i;
    	forks[i] = fork();
    	nr_meals[i] = 0;
    }
    
    // spawn philosopher threads
    for (int i = 0; i < NR_THREADS; ++i)
    {
        pthread_create(phils + i, 0, philosopher, pid + i);
    }
    
    // join philosopher threads
    for (int i = 0; i < NR_THREADS; ++i)
    {
        pthread_join(phils[i], NULL);
    }
    
    return(0); 
}

//--------------------------------------------------------------------------------------------------
