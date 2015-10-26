# memoryAccessPattern

Is there any difference in speed if you acces a big array randomly or sequentially ?
Isn't the main memory of your computer called _Random Access Memory_ ?

Compile this in Release mode under Visual C++ 2013. 

I'll make the MakeFile as soon as i can find an install of linux with gcc-4.9 for c++11.

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
