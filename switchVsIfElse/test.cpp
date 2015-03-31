#include <iostream>
#include <string>
#include <chrono>

void startBenchmark(const int nbIterations, int val);
void printUsage(std::string & exeName);
int bigSwitch(int a);
int bigIfElse(int a);

int bigSwitch(int a) {
    int value;
    
    switch(a) {
        case 0: 
            value = 1;
            break;

        case 11: 
            value = 2;
            break;            
                
        case 22: 
            value = 3;
            break;
        
        case 33: 
            value = 5;
            break;
        
        case 44: 
            value = 8;
            break;
        
        case 55: 
            value = 13;
            break;
            
        case 66: 
            value = 21;
            break;
        
        case 77: 
            value = 34;
            break;
            
        case 88: 
            value = 55;
            break;
            
        case 99: 
            value = 89;
            break;
            
        case 110: 
            value = 144;
            break;
            
        default:
            value = -1;
    }
    return value;
}


int bigIfElse(int a) {
    int value;
    
    if(a == 0) { 
            value = 1;
    }
    else if(a==11) { 
            value = 2;
    } 
    else if(a==22){
            value = 3;
    }
    else if(a==33) {
            value = 5;
    }
    else if(a==44) {
            value = 8;
    }
    else if(a==55) { 
            value = 13;
    }
    else if(a==66) { 
            value = 21;
    }
    else if(a==77) {
            value = 34;
    }
    else if(a==88) {
            value = 55;
    }
    else if(a==99) {
            value = 89;
    }
    else if(a==110) {
            value = 144;
    }
    else {
            value = -1;
    }
    return value;
}




void printUsage(std::string & exeName) {
    std::cout << "usage:" <<std::endl << "\t" << exeName << " <numberOfIteration> <startingValue>" << std::endl;;
}




int main(const int argc, const char * argv[]) {
    int nbIter, startVal;
    std::string exeName = argv[0];
    
    if(argc != 3) {
        printUsage(exeName);
        return 1;
    }
    
    try {
        nbIter = std::stoi(argv[1]);
        startVal = std::stoi(argv[2]);
    } catch(...) {
        std::cout << "Error during argument conversion" << std::endl;
        printUsage(exeName);
        return 2;
    }
    
    startBenchmark(nbIter, startVal);

    return 0;
}


// Small helper class
class SimpleChrono {

public:
    
    void start() {
        m_start = std::chrono::steady_clock::now();
    }
    
    void end() {
        m_end = std::chrono::steady_clock::now();
    }
    
    double elapsedMs() const {
        millisecDuration duration = std::chrono::duration_cast<millisecDuration>(m_end - m_start);
        return duration.count();
    }
    
protected:

    typedef std::chrono::duration<double, std::milli> millisecDuration;
    std::chrono::time_point<std::chrono::steady_clock> m_start, m_end;
};


void startBenchmark(const int nbIterations, int val) {
    SimpleChrono s;

    s.start();
    for(int i = 0; i < nbIterations; i++) {
        val += bigSwitch(i%110);
    }
    s.end();
    std::cout << "duration of bigSwitch: " << s.elapsedMs() << "ms." <<std::endl;
    
    s.start();
    for(int i = 0; i < nbIterations; i++) {
        val += bigIfElse(i%110);
    }
    s.end();
    std::cout << "duration of bigIfElse: " << s.elapsedMs() << "ms." <<std::endl;

    std::cout << "end value " << val << std::endl;
    
    
}