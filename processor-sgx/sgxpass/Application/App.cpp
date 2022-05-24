// CryptoTestingApp.cpp : Defines the entry point for the console application.
//

#include <string.h>

#include "sgx_urts.h"
#include "enclave_u.h"

#include "stdio.h"
#include "stdlib.h"
#include "string.h"

#define BUFLEN 2048
#define SGX_AESGCM_MAC_SIZE 16
#define SGX_AESGCM_IV_SIZE 12

#define ENCLAVE_FILE "enclave.signed.so"


/* Setup enclave */
sgx_enclave_id_t eid;
sgx_launch_token_t token = { 0 };
int token_updated = 0;


extern "C" {

  int create_enclave(const char* file_name, uint64_t* eid)
  {
    return sgx_create_enclave(file_name, SGX_DEBUG_FLAG, &token, &token_updated, eid, NULL);
  }

  int pass_through(uint64_t eid, char* msg, uint32_t length)
  {
    printf("APP %s\n", msg);
    return ecall_pass(eid, (uint8_t*)msg, length);
  }
}
