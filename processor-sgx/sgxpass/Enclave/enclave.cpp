#include "enclave_t.h"

#include "sgx_trts.h"
#include "sgx_tcrypto.h"
#include "stdlib.h"
#include <string.h>
#include <map>

#include <stdarg.h>
#include <stdio.h>      /* vsnprintf */
#include <ctype.h>

void ecall_pass(uint8_t *p, uint32_t length)
{
  uint8_t key[16] = {0};
  uint8_t ctr[16] = {0};
  uint8_t ctr2[16] = {0};

  sgx_aes_ctr_decrypt((sgx_aes_ctr_128bit_key_t *)key, p, length, ctr, 1, p);
  // Magic happens here...


  for (int i = 0; i < length; i++)
  {
    p[i] = toupper(p[i]);
  }


  // Magic ends here ...
  sgx_aes_ctr_encrypt((sgx_aes_ctr_128bit_key_t *)key, p, length, ctr2, 1, p);
}
