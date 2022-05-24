//
// Created by felippo on 8/28/18.
//
using namespace std;
#include <cmath>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <cstring>
#include <vector>

#include "RiffleShuffle.h"

namespace
{
  constexpr char hexmap[] = {'0', '1', '2', '3', '4', '5', '6', '7',
                             '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'};

  string to_hex( uint8_t* buffer, uint32_t len )
  {
    string s( len * 2, ' ' );
    for( int i = 0; i < len; ++i )
    {
      s[2 * i]     = hexmap[(buffer[i] & 0xF0) >> 4];
      s[2 * i + 1] = hexmap[buffer[i] & 0x0F];
    }
    return s;
  }
}

/*!
 * A method that initializes RiffleShuffle object i.e., it allocates memory for the computation graph
 * @param N defines the size of the graph (number of vertices in each layer)
 * @param algorithm defines the algorithm that is used for hashing -- in the current version only SHA-256 is supported
 */
void RiffleShuffle::init(int N, const char * algorithm) {
    //if (N < 256)
      //  N = 256;

    if (N % 2 != 0)
        N++;

    this->N = N;
    this->Nhalf = (int) N/2;

    this->lambda = 2 * (int) ceil(log2(N));
    this->pepper = 1;

    this->algorithm = "SHA-256";
    string result = "";
    SHA256_Init(&this->digest);
}

/*!
 * Method checks if for a given string \arr, a bit at position \bit is set to 1
 * @param arr an input string
 * @param bit a position of a bit
 * @return a value equal to 0/1 depending on the value of the querried bit
 */
bool RiffleShuffle::isSet(string  arr, int bit) {
    int bitIndex = (int) bit / 8;
    int bitPosition = bit % 8;
    return ((arr[bitIndex] >> bitPosition) & 0x1) == 1;
}

/*!
 * Method returns sha256 value of a str
 * @param str input string
 * @return string representing sha256
 */
string RiffleShuffle::sha256(const string str) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256_CTX sha256;
    SHA256_Init(&sha256);
    SHA256_Update(&sha256, str.c_str(), str.size());
    SHA256_Final(hash, &sha256);
    return to_hex( hash, SHA256_DIGEST_LENGTH );
}

/*!
 * Method that for a given \layer, \round number and \salt computes string that is later used to build a graph
 * @param layer an integer that is the layer number
 * @param round an integer that tells which lever of the graph's layer we compute
 * @param salt
 * @return a string of hex of length at least \N bits
 */
string RiffleShuffle::saltedChoices(int layer, int round, string salt) {
    int numberOfBlocks = (int) (ceil(this->N/256));

    string choices;

    for (int i=0; i <= numberOfBlocks; i++) {
        string saltChoices;
        saltChoices = "RSfree:" + to_string(this->N) + ":" + to_string(this->pepper) + ":" +  to_string(layer) + ":" +  to_string(round) + ":" + salt + ":" + to_string(numberOfBlocks) + ":" + to_string(i);
        choices = sha256(saltChoices);
    }

    return choices;
}

/**
 * Main method that computes a \password on a stack of \pepper graphs that depend on the value of \salt
 * This version is a non-SST based RiffleScrambler the graph is generated online, layer by layer and depends only on the graph size: N and salt
 * @param password a user password to be hashed
 * @param salt a string from which
 * @param pepper a number of graphs that are stacked together (for non-SST version actual number of layers is increased by 2)
 * @return a string that corresponds to the value of the final vertex of the graph.
 */
string RiffleShuffle::scramble(string password, string salt, int pepper) {
    if (this->pepper < pepper)
        this->pepper = pepper;

    this->pepper += 2;


    vector <string> bufferOld(this->N);
    vector <string> bufferNew(this->N);

    //initialization of the buffer:
    string initVal = password + ":" + salt;
    bufferOld[0] = sha256(initVal);
    for (int i = 1; i < this->N; i++) {
        string stringToHash;
        stringToHash =  "RSfreeInit:" + to_string(this->N) + ":" +  to_string(this->pepper) +  ":0:" + to_string(i) + ":" + bufferOld[i-1];
        bufferOld[i] = sha256(stringToHash);
    }


    vector <int> leftParents(this->N);
    vector <int> rightParents(this->N);

    //actual RiffleScrambler computation
    //outer loop
    for (int layer = 0; layer < this->pepper; layer++) {
        //inner loop
        for (int round = 0; round < this->lambda; round++) {

            int leftCounter = 0;

            string choices = saltedChoices(layer, round, salt);
            //cout << "choices: " << choices << endl;

            //first pass to learn how many zeros we have
            for (int i = 0; i < this->N; i++) {
                if (!isSet(choices, i))
                    leftCounter++;
            }

            int noOfZeros = leftCounter;
            int noOfOnes = this->N - leftCounter;

            leftCounter = 0;
            int rightCounter = 0;

            //buffer loop
            for (int i = 0; i < this->N; i++) {
                if (!isSet(choices, i)) {
                    leftParents[leftCounter] = i;
                    rightParents[noOfOnes + leftCounter] = i;
                    leftCounter++;
                } else {
                    leftParents[noOfZeros + rightCounter] = i;
                    rightParents[rightCounter] = i;
                    rightCounter++;
                }
            }


            //compute values at the next level:
            for (int i = 0; i < this->N; i++) {
                string toNewHash;
                toNewHash = bufferOld[leftParents[i]] + bufferOld[rightParents[i]];

                bufferNew[i] = sha256(toNewHash);
            }

            for (int i = 0; i < this->N; i++) {
                bufferOld[i] = bufferNew[i];
            }
        }
    }

    this->result = bufferNew[((this->N)-1)];
    return bufferNew[((this->N)-1)];
}

/*!
 * A method that returns the value of computed hash
 * @return
 */
string RiffleShuffle::getHash() {
    return this->result;
}
