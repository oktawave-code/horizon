#ifndef __OCK_ECDSA_H__
#define __OCK_ECDSA_H__

#include <tuple>
#include "types.h"

namespace ock
{
  class AesGCM
  {
  public:
    static ciphertext_t encrypt(
      const aes256key_t& aes_key,
      const std::string& plaintext,
      const std::string& aad
    );

    static std::string decrypt(
      const aes256key_t& aes_key,
      const ciphertext_t& ciphertxt,
      const std::string& aad
    );

    static ciphertext_t to_cipher( const std::string& msg );
    static ciphertext_t to_cipher( const uint8_t* msg, uint32_t len );
  };
}
#endif
