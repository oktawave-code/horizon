#ifndef __OCK_TOKENS_H__
#define __OCK_TOKENS_H__

#include <string>

#include "types.h"

namespace ock
{
  class KDF
  {
  private:
    secret_t secret_1;
    secret_t secret_2;

  public:
    KDF( secret_t&& secret_1, secret_t&& secret_2 );

    Token get_key_token( const Key& key );

    aes256key_t get_aes_key( const Key& key );

    string get_rsa_pubkey( const Key& key );

    string get_rsa_privkey( const Key& key );

    string get_dh_privkey( const Key& key );
    string get_dh_pubkey( const Key& key );

    aes256key_t get_ecdsa_key( const Key& key );

    void create_key( const Key& key );
    void import_key( const Key& key, const string& private_key, const string& public_key );
  };
}

#endif
