#include "helper.h"
#include <cstring>
#include <ctime>
#include <cstdio>
#include <sys/types.h>
#include <sys/stat.h>
#ifndef S_ISREG
#define	S_ISREG(m)	(((m) & S_IFMT) == S_IFREG)
#endif
#ifndef S_ISDIR
#define	S_ISDIR(m)	(((m) & S_IFMT) == S_IFDIR)
#endif

#include <fstream>
#include <regex>

//clamps value between 0 and 255
uint8_t clamp(int32_t val)
{
	if (val < 0) {
		return 0;
	}
	if (val > 255) {
		return 255;
	}
	return (uint8_t)val;
}

std::string base36(int val)
{
	if (val < 0) {
		return std::string("-") + base36(-val);
	}
	if (val / 36 == 0) {
		if (val < 10) {
			char x = '0' + val;
			return std::string(&x, 1);
		}
		char x = 'a' + (val - 10);
		return std::string(&x, 1);
	}
	return base36(val / 36) + base36(val % 36);
}

int base10(const std::string& val)
{
	return std::stoi(val);
	//return atoi(val.c_str());
	/*
	//printf("Turning %s into ", val);
	int res = 0;
	bool neg = false;
	if (*val == '-') {
		neg = true;
		++val;
	}
	for (;;) {
		if (*val >= '0' && *val <= '9') {
			res = res * 36 + (*val++ - '0');
			continue;
		}
		if (*val >= 'a' && *val <= 'z') {
			res = res * 36 + 10 + (*val++ - 'a');
			continue;
		}
		if (*val >= 'A' && *val <= 'Z') {
			res = res * 36 + 10 + (*val++ - 'A');
			continue;
		}
		break;
	}
	if (neg) {
		res *= -1;
	}
	//printf("%d\n", res);
	return res;
	*/
}

void printProgress(const size_t current, const size_t max)
{
	static float lastp = -10;
	static time_t lastt = 0;
	if (current == 0) { // Reset
		lastp = -10;
		lastt = 0;
	}
	time_t now = time(NULL);
	if (now > lastt || current == max) {
		float proc = (float(current) / float(max)) * 100.0f;
		if (proc > lastp + 0.99f || current == max) {
			// Keep user updated but don't spam the console
			printf("[%.2f%%]\r", proc);
			fflush(stdout);
			lastt = now;
			lastp = proc;
		}
	}
}

bool fileExists(const std::string& strFilename)
{
	if (strFilename.empty()) return false;
	std::ifstream f(strFilename);
	return f.good();

	/*
	struct stat stFileInfo;
	int ret;
	ret = stat(strFilename, &stFileInfo);
	if(ret == 0) {
		return S_ISREG(stFileInfo.st_mode);
	}
	return false;
	*/
}

bool dirExists(const std::string& strFilename)
{
	struct stat stFileInfo;
	int ret;
	ret = stat(strFilename.c_str(), &stFileInfo);
	if(ret == 0) {
		return S_ISDIR(stFileInfo.st_mode);
	}
	return false;
}

bool isNumeric(const std::string& str)
{
	return std::regex_match(str, std::regex("[(-|+)|][0-9]+"));
}

bool isAlphaWorld(const std::string& path)
{
	std::string pathToFile = path + "/level.dat";
	return fileExists(pathToFile);
}

bool strEndsWith(std::string const &fullString, std::string const &ending) {
	if (fullString.length() >= ending.length()) {
		return (0 == fullString.compare(fullString.length() - ending.length(), ending.length(), ending));
	}
	else {
		return false;
	}
}

std::vector<std::string> strSplit(const std::string &s, char delim) {
	std::vector<std::string> elems;
	strSplit(s, delim, std::back_inserter(elems));
	return elems;
}

size_t getZahl(const std::vector<uint64_t>& arr, const size_t index, const size_t lengthOfOne) {
	const size_t maxObj = (arr.size() * numBits<uint64_t>()) / lengthOfOne;
	if (maxObj <= index)
		throw std::out_of_range("out of range");

	size_t startBit = index * lengthOfOne;
	size_t endBit = (startBit + lengthOfOne) - 1;
	if ((startBit / numBits<uint64_t>()) != (endBit / numBits<uint64_t>())) {
		size_t bitsLow = ((index + 1) * lengthOfOne) - startBit - 1;
		size_t bitsUp = lengthOfOne - bitsLow;

		uint64_t lowByte = arr[startBit / numBits<uint64_t>()];
		uint64_t upByte = arr[endBit / numBits<uint64_t>()];
		upByte &= ~(~0 << bitsUp);
		upByte = upByte << bitsLow;

		//lowByte &= ~0 << bitsLow;
		lowByte = lowByte >> (numBits<uint64_t>() - bitsLow);

		return static_cast<size_t>(upByte | lowByte);
	}
	else {
		//on same index in arr
		uint64_t val = arr[startBit / numBits<uint64_t>()];
		const auto m = ((startBit / numBits<uint64_t>()) * numBits<uint64_t>());
		val = val >> (startBit - m);
		val &= ~(~0 << lengthOfOne);
		return static_cast<size_t>(val);
	}

}