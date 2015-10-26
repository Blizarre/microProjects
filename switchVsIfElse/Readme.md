# switchVsIfElse #

Is it better to use a big switch or a big if else (yes that's ugly, but still....) ? 

On this script, there are 11 "case", not including the default. The script will 
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
* Machine code : http://741mhz.com/switch/
