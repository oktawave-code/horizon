#include "enclave_t.h"

#include <stdio.h>      /* vsnprintf */
#include <string>
#include <algorithm>
#include <exception>

#include "ock/types.h"
#include "ock/worker_wrapper.h"
#include "ock/aes.h"
#include "ock/json_parser.h"

using ock::ustring;
using std::string;

// ------------------- OCALLS -------------------
void printf(const char *fmt, ...)
{
    char buf[BUFSIZ] = {'\0'};
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(buf, BUFSIZ, fmt, ap);
    va_end(ap);
    ocall_print_string(buf);
}

// ------------------- ECALLS -------------------
ock::WorkerWrapper ww;

namespace
{
  int pack( string response, uint8_t* output, uint32_t* output_len )
  {
    auto cipher = ock::AesGcmEncrypt( response ).encrypt( { 0 }, { } );

    auto out = cipher.ciphertext + cipher.iv + cipher.tag;
    std::copy_n( out.begin( ), out.size( ), output );
    *output_len = out.size( );
  }
}

// TODO Buffer check
const uint32_t BUFFER_SIZE = 8192;

std::tuple< string, int > execute_operation( uint32_t operation, const ock::JsonReader& json, const char* ip )
{
  switch( operation )
  {
    case 1: // CREATE_KEY
      return ww.create_key( json, ip );
    case 2: // CREATE_ALIAS
      return ww.create_alias( json, ip );
    case 3: // ENCRYPT
      return ww.encrypt( json, ip );
    case 4: // DECRYPT
      return ww.decrypt( json, ip );
    case 5: // SIGN
      return ww.sign( json, ip );
    case 6: // VERIFY
      return ww.verify( json, ip );
    case 7: // DIGEST
      return ww.digest( json, ip );
    case 8: // RANDOM
      return ww.random( json, ip );
    case 9: // MANAGE
      return ww.manage( json, ip );
    case 10: // shared_secret
      return ww.shared_secret( json, ip );
    case 11: // shared_secret
      return ww.get_public_key( json, ip );
    case 12: // import key
      return ww.import_key(json, ip);
    case 101: // get_epid
      return ww.get_epid(json, ip);

  }
}

int ecall_invoke(
  uint32_t operation,
  uint8_t* input, uint32_t input_len,
  const char* ip,
  uint8_t* output, uint32_t* output_len )
{
  int return_code;
  string response;

  try
  {
    // 1. Unpack
    // auto plaintext = ock::AesGcmDecrypt( input, input_len ).decrypt( { 0 }, { } ); // TALOS failure
    // 2. Parse to Json
    auto plaintext = ustring( input, input_len );
    printf("json: %s", plaintext.c_str() );
    auto json = ock::JsonReader( plaintext );
    printf("Input size: %d\n", input_len );
    printf("Input size: %d\n", operation );
    printf("Ip: %s\n", ip);
    // 3. Execute operation
    std::tie( response, return_code ) = execute_operation( operation, json, ip );
  }
  catch( const std::exception& re )
  {
    // 4! Report errors
    std::tie( response, return_code ) = ww.error( re );
  }
  // 4. Pack
  // pack( response, output, output_len );
  std::copy_n( response.begin( ), response.size( ), output );
  *output_len = response.size( );

  printf("Output size: %d\n", *output_len);

  return return_code;
}
