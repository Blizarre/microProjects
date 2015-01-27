#include <iostream>
#include <array>
#include <memory>
#include <random>
#include <chrono>
#include <stdexcept>
#include <string>

// This structure represent the content of a "data type" that will be stored in the big array.
struct Payload {
	size_t data;
};

// Create an array of size SD of Payload, where the Payload's data has a value of "Offset + 10".
// The array must be created on the heap because the stack may not be able to hold all the data.
// SD: Size of the Data array
template<size_t SD>
std::unique_ptr<std::array<Payload, SD> > createData()
{
	auto ret = std::make_unique<std::array<Payload, SD> >();
	for (size_t counter = 0; counter < ret->size(); counter++)
	{
		// fill the data with a value easy to check
		(*ret)[counter].data = counter + 10;
	}
	return ret;
};

// Create an array on the heap with values from minValue to maxValue. 
// return a unique_ptr to this array.
// T: Type of the data from the array (the random generator will generate only unsigned int)
// SR: Size of the array of Random values.
template<typename T, size_t SR>
std::unique_ptr<std::array<T, SR> > createRndAccessData(T minValue, T maxValue)
{
	auto ret = std::make_unique<std::array<T, SR> >();
	std::uniform_int<T> uniform(minValue, maxValue);
	std::minstd_rand generator;

	std::for_each(ret->begin(), ret->end(), [&uniform, &generator](T & val) { val = uniform(generator); });
	return ret;
}

// This class is used to print message at particular points in the code with the time elapsed since the last call
class TimePoints
{
public:
	TimePoints() {
		m_checkPoint = m_clock.now();
	}

	// Reset the timer to "now"
	void reset()
	{
		m_checkPoint = m_clock.now();
	}

	// Print the time elapsed since the last call to reset() or checkPoint(). The message must contains the string "{TIME}"
	// That will be replaced by the time in milliseconds.
	// Return the time elapsed in ms
	long long checkPoint(char* message)
	{
		std::string strMsg = std::string(message);
		return checkPoint(strMsg);
	}

	// Print the time elapsed since the last call to reset() or checkPoint(). The message must contains the string "{TIME}"
	// That will be replaced by the time in milliseconds
	// Return the time elapsed in ms
	long long checkPoint(std::string& message)
	{
		std::string placeholder = "{TIME}";
		auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(m_clock.now() - m_checkPoint).count();
		auto position = message.find(placeholder);
		if (position == message.npos)
			throw std::invalid_argument("message should contain {TIME}");

		std::cout << message.replace(position, placeholder.size(), std::to_string(duration)) << std::endl;
		reset();
		return duration;
	}

protected:
	std::chrono::steady_clock m_clock;
	std::chrono::steady_clock::time_point m_checkPoint;
};

// This class will access the elements of "data" using the positions stored in elementPosition. 
// To make sure the compiler will not remove the data, a check is performed every time to make sure that the data
// is the one that has been stored at this particular location.
template <size_t SR, size_t SD>
void accessElementsOfArray(const std::array<size_t, SR>& elementPosition, const std::array<Payload, SD>& data)
{
	for (const size_t& pos : elementPosition)
	{
		// a simple check to make sure the compiler will not remove everything
		if (data[pos].data != pos + 10)
			throw std::bad_exception("What ?");
	}
};


void main()
{
	TimePoints tp;
	const size_t dataSize(100000000);
	const size_t accessSize(1000000);

	long long randomAccess(0), sequentialAccess(0), sequentialAccessReversed(0);
	const int nbReplay(20);

	auto data = createData<dataSize>();
	tp.checkPoint("Create Data: {TIME}ms.");

	auto offsetAccess = createRndAccessData<size_t, accessSize>(0, dataSize);
	tp.checkPoint("Create offsetAccess: {TIME}ms.");

	auto max = *std::max_element(offsetAccess->begin(), offsetAccess->end());
	tp.checkPoint("Find Max: {TIME}ms.");

	std::cout << "data.size=" << data->size() << ", offsetAccess.size=" << offsetAccess->size() << ", max(offsetAccess)=" << max << std::endl;

	tp.reset();

	for (int i = 0; i < nbReplay; i++)
	{
		accessElementsOfArray(*offsetAccess, *data);
		randomAccess += tp.checkPoint("Pure random access: {TIME} ms.");
	}

	std::sort(offsetAccess->begin(), offsetAccess->end(), [](size_t& a, size_t& b) { return a < b; });

	tp.checkPoint("Sort: {TIME} ms.");

	for (int i = 0; i < nbReplay; i++)
	{
		accessElementsOfArray(*offsetAccess, *data);
		sequentialAccess += tp.checkPoint("Pseudo sequential access: {TIME} ms.");
	}

	std::sort(offsetAccess->begin(), offsetAccess->end(), [](size_t& a, size_t& b) { return a > b; });

	tp.checkPoint("Sort (reversed): {TIME} ms.");

	for (int i = 0; i < nbReplay; i++)
	{
		accessElementsOfArray(*offsetAccess, *data);
		sequentialAccessReversed += tp.checkPoint("Pseudo sequential access (reversed): {TIME} ms.");
	}


	std::cout << std::endl;
	std::cout << "Total time random: " << randomAccess << "ms (mean: " << randomAccess / nbReplay << "ms)" << std::endl;
	std::cout << "Total time sequential: " << sequentialAccess << "ms (mean: " << sequentialAccess / nbReplay << "ms)" << std::endl;
	std::cout << "Total time sequential reversed: " << sequentialAccessReversed << "ms (mean: " << sequentialAccessReversed / nbReplay << "ms)" << std::endl;
	std::cout << "Performance (sequential/random): " << static_cast<float>(sequentialAccess) / randomAccess;
}
