#include <string>

#include "/opt/intel/sgxsdk/include/sgx_urts.h"
#include "enclave_u.h"
#include "/opt/intel/sgxsdk/include/sgx_uae_service.h"


#include "stdio.h"
#include <stdlib.h>
#include "string.h"
#include "inttypes.h"
#include <unistd.h>
//#include "../Enclave/enclave_t.h"

#define BUFLEN 2048
#define SGX_AESGCM_MAC_SIZE 16
#define SGX_AESGCM_IV_SIZE 12

#define ENCLAVE_FILE "enclave.signed.so"


/* OCall functions */
void ocall_print_string(const char *str)
{
    /* Proxy/Bridge will check the length and null-terminate
     * the input string to prevent buffer overflow.
     */
    printf("%s", str);
}

/* Setup enclave */
sgx_enclave_id_t eid = 0;
//rwlock_t lock_eid;
//struct sealed_buf_t sealed_buf;
sgx_launch_token_t token = { 0 };
int token_updated = 0;



extern "C" {

  //int create_enclave(const char* file_name, uint64_t* eid)
    int create_enclave(const char* file_name, sgx_enclave_id_t *eid)
    {
        int result;
        uint64_t geid;
        result =  sgx_create_enclave(file_name, SGX_DEBUG_FLAG, &token, &token_updated, eid, NULL);
        geid = (unsigned long int) eid;
        printf("enclave id: %" PRIu64 "\n", geid);
        FILE *fp;
        //std::string fullPath = "/mnt/shared/" + name;
        //const char *st = "x%u" + (long unsigned int) eid + "\n";
        fp = fopen("/mnt/shared/global_eid.txt", "w+");
        fprintf(fp, "%" PRIu64 "\n", geid);
        //fputs("This is testing for fputs...\n", fp);
        fclose(fp);
        printf("enclave id saved\n");


        //string f( eid.size() * 2, 0 );
        //std::copy_n( eid, eid.size(), f.begin() );
        //std::copy_n( secret_2.begin(), secret_2.size(), f.begin() + secret_1.size() );
        //write_file( "enclaveID.txt", std::to_string((unsigned long int) eid));
        //const char *st = (long unsigned int) eid + "asd" ;
        //ocall_print_string(st);
        //ocall_print_string("it's OK. EPID: %d");
        return result;
    }

  int destroy_enclave()
  {
        printf("Destroy enclave\n");
        FILE *fp;
        uint64_t geid = 0;
        //unsigned long int eid = 0;
        char str[30];
        fp = fopen("/mnt/shared/global_eid.txt", "r");
        if (fp == NULL) {
            perror("Error opening file");
            return(-1);
        }

        if (fgets(str, 30, fp) != NULL) {
            geid = std::stoul(str, 0, 10);
        }
        printf("Trying to destroy eid: %" PRIu64 "\n", geid);
        fclose(fp);


        //eid = (sgx_enclave_id_t) geid;
        sgx_status_t status = sgx_destroy_enclave(geid);
          if (status == SGX_SUCCESS) {
              printf("Enclave successfully destroyed\n");
          }

          if (status == SGX_ERROR_INVALID_ENCLAVE_ID) {
              printf("Enclave already destroyed\n");
          }

        return 0;
  }

  int invoke(
    uint64_t eid, int *status,
    uint32_t operation,
    uint8_t* input,
    uint32_t input_len,
    const char* ip,
    uint8_t* output,
    uint32_t* output_len)
  {
    return ecall_invoke(
      eid, status,
      operation,
      input, input_len,
      ip,
      output, output_len
    );
  }

  int epid(
          uint64_t eid, int *status,
          uint32_t operation,
          uint8_t* input,
          uint32_t input_len,
          const char* ip,
          uint8_t* output,
          uint32_t* output_len) {
      uint32_t p_extended_epid_group_id = 0;
      sgx_status_t status_sgx;
      status_sgx = sgx_get_extended_epid_group_id(&p_extended_epid_group_id);
      //std::string resp = "error";


      if (status_sgx == SGX_SUCCESS) {
          //resp =  "success:" + p_extended_epid_group_id;
          const char *st = p_extended_epid_group_id + "asd" ;
          ocall_print_string(st);
          ocall_print_string("it's OK. EPID: %d");
      } else {
          ocall_print_string("it's not OK");
      }

      return p_extended_epid_group_id;

  }

void write_file( std::string name, std::string content )
{
    std::string fullPath = "/mnt/shared/" + name;
    auto g = fopen( fullPath.c_str(), "w+" );
    fwrite(content.data(), 1, content.size(), g);
    fflush(g);
    fclose(g);
}



// int create_key(
  //   uint64_t eid, int *status,
  //   const char *access_token,
  //   uint8_t *key_id,
  //   uint8_t *token)
  // {
  //   return ecall_create_key(
  //     eid, status,
  //     access_token,
  //     key_id,
  //     token
  //   );
  // }
//
// int create_alias(
//     uint64_t eid, int *status,
//     uint8_t *key_id,
//     uint8_t *key_token,
//     const char *alias,
//     const char *action,
//     uint8_t *alias_token)
//   {
//     return ecall_create_alias(
//       eid, status,
//       key_id,
//       Keyoken,
//       alias,
//       action,
//       alias_token
//     );
//   }
//
//   int encrypt_aes256_gcm(
//     uint64_t eid, int* status,
//     uint8_t *key_id,
//     const char *alias,
//     uint8_t *token,
//     uint8_t *plaintext, uint32_t plaintext_len,
//     uint8_t *aad, uint32_t aad_len,
//     uint8_t *ciphertext,
//     uint8_t *iv, uint8_t *tag)
//   {
//
//     return ecall_encrypt_aes256_gcm(
//       eid, status,
//       key_id,
//       alias,
//       token,
//       plaintext, plaintext_len,
//       aad, aad_len,
//       ciphertext,
//       iv, tag
//     );
//   }
//
//   int decrypt_aes256_gcm(
//     uint64_t eid, int* status,
//     uint8_t *key_id,
//     const char *alias,
//     uint8_t *token,
//     uint8_t *ciphertext, uint32_t ciphertext_len,
//     uint8_t *aad, uint32_t aad_len,
//     uint8_t *plaintext,
//     uint8_t *iv, uint8_t *tag)
//   {
//
//     return ecall_decrypt_aes256_gcm(
//       eid, status,
//       key_id,
//       alias,
//       token,
//       ciphertext, ciphertext_len,
//       aad, aad_len,
//       plaintext,
//       iv, tag
//     );
//   }
}
