This repo is a collection of very small programs, usually only one file.

## switchVsIfElse ##

And now, is it better to use a big switch or a big if else (yes that's ugly, but still....) ? 

On htis script, there are 11 "case", not including the default. The script will 
iterate over a large number of values and almost always reach the default, which 
should be the best case for the if/Else statements, because the branch prediction 
will be always right.


Next step: try the average case with fewer default.
    
    $ g++ --std=c++11 test.cpp -O3 -Wall                                                                                                                                   
    $ time ./a.out  10000000 25                                                                                                                                            
    Average duration of bigSwitch: 16.1334ms.
    Average duration of bigIfElse: 59.891ms.
    A Switch is 26% as long as a IfElse

I tried to get into the good practice  by restarting the benchmarking loop until 
I have enough data (5s.). 

Question: How does the branch prediction handle a large number of if/Else ? Does it still works ?


For more information, see: 
* http://en.wikipedia.org/wiki/Switch_statement#Compilation
* http://en.wikipedia.org/wiki/Branch_predictor
* Machine code : http://741MHz.github.io

## memoryAccessPattern

Is there any difference in speed if you acces a big array randomly or sequentially ?
Isn't the main memory of your computer called _Random Access Memory_ ?

Compile this in Release mode under Visual C++ 2013. 

I'll make the MakeFile as soon as i cant find an install of linux with gcc-4.9 (ubuntu is still 4.8) !

    stdCreate Data: 187ms.
    Create offsetAccess: 56ms.
    Find Max: 2ms.
    data.size=100000000, offsetAccess.size=1000000, max(offsetAccess)=99999927
    Pure random access: 16 ms.
    Pure random access: 17 ms.
    Pure random access: 17 ms.
    Pure random access: 16 ms.
    Pure random access: 15 ms.
    Pure random access: 16 ms.
    Pure random access: 15 ms.
    Pure random access: 16 ms.
    Pure random access: 15 ms.
    Pure random access: 15 ms.
    Pure random access: 16 ms.
    Pure random access: 16 ms.
    Pure random access: 15 ms.
    Pure random access: 15 ms.
    Pure random access: 16 ms.
    Pure random access: 15 ms.
    Pure random access: 16 ms.
    Pure random access: 17 ms.
    Pure random access: 16 ms.
    Pure random access: 17 ms.
    Sort: 86 ms.
    Pseudo sequential access: 9 ms.
    Pseudo sequential access: 9 ms.
    Pseudo sequential access: 9 ms.
    Pseudo sequential access: 9 ms.
    Pseudo sequential access: 9 ms.
    Pseudo sequential access: 10 ms.
    Pseudo sequential access: 9 ms.
    Pseudo sequential access: 9 ms.
    Pseudo sequential access: 10 ms.
    Pseudo sequential access: 9 ms.
    Pseudo sequential access: 9 ms.
    Pseudo sequential access: 9 ms.
    Pseudo sequential access: 8 ms.
    Pseudo sequential access: 9 ms.
    Pseudo sequential access: 9 ms.
    Pseudo sequential access: 9 ms.
    Pseudo sequential access: 9 ms.
    Pseudo sequential access: 8 ms.
    Pseudo sequential access: 9 ms.
    Pseudo sequential access: 9 ms.
    Sort (reversed): 15 ms.
    Pseudo sequential access (reversed): 9 ms.
    Pseudo sequential access (reversed): 9 ms.
    Pseudo sequential access (reversed): 8 ms.
    Pseudo sequential access (reversed): 9 ms.
    Pseudo sequential access (reversed): 10 ms.
    Pseudo sequential access (reversed): 9 ms.
    Pseudo sequential access (reversed): 12 ms.
    Pseudo sequential access (reversed): 12 ms.
    Pseudo sequential access (reversed): 9 ms.
    Pseudo sequential access (reversed): 9 ms.
    Pseudo sequential access (reversed): 9 ms.
    Pseudo sequential access (reversed): 9 ms.
    Pseudo sequential access (reversed): 9 ms.
    Pseudo sequential access (reversed): 9 ms.
    Pseudo sequential access (reversed): 9 ms.
    Pseudo sequential access (reversed): 9 ms.
    Pseudo sequential access (reversed): 9 ms.
    Pseudo sequential access (reversed): 9 ms.
    Pseudo sequential access (reversed): 9 ms.
    Pseudo sequential access (reversed): 9 ms.
    
    Total time random: 317ms (mean: 15ms)
    Total time sequential: 180ms (mean: 9ms)
    Total time sequential reversed: 186ms (mean: 9ms)
    Performance (sequential/random): 0.567823
