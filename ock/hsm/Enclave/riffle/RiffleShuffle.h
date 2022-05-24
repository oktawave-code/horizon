//
// Created by felippo on 8/28/18.
//
using namespace std;
#include <cstring>
#include <inttypes.h>
#include "openssl/sha.h"
#ifndef CRIFFLE_RIFFLESHUFFLE_H
#define CRIFFLE_RIFFLESHUFFLE_H

#include <string>


class RiffleShuffle {
    private:
        uint8_t salt;
        int pepper;
        int N;
        int Nhalf;
        int lambda;
        const char* algorithm;
        SHA256_CTX digest;
        const char hexTable[16]  = {'0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f'};

    public:
        void init(int, const char[]);
        string result;
        string scramble(std::string , std::string , int);
        string sha256(const std::string);
        bool isSet(std::string, int);
        string saltedChoices(int, int, std::string);
        string getHash();

    private: char hashString(uint8_t);
};

#endif //CRIFFLE_RIFFLESHUFFLE_H
