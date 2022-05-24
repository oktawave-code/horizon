#ifndef __OCK_AES_H__
#define __OCK_AES_H__

#include <tuple>
#include "types.h"
#include "base64/base64.h"

namespace ock
{
  class AesGcm
  {
  public:
    static const size_t iv_size = 12;
    static const size_t tag_size = 16;
  };

  struct AesGcmDecrypt;

  struct AesGcmEncrypt
  {
    ustring plaintext;
  public:

    AesGcmEncrypt( ) { }
    AesGcmEncrypt( const string& s ) : plaintext( s.begin( ), s.end( ) ) { }
    AesGcmEncrypt( const ustring& us ) : plaintext( us ) { }

    AesGcmDecrypt encrypt( const aes256key_t& aes_key, const ustring& aad );
  };
  string to_string( const AesGcmEncrypt& enc );

  struct AesGcmDecrypt
  {
    ustring ciphertext;
    ustring iv;
    ustring tag;

  public:
    AesGcmDecrypt( ) { }
    AesGcmDecrypt( const string& s ) : AesGcmDecrypt( b64::decode( s ) ) { }
    AesGcmDecrypt( const ustring& us );
    AesGcmDecrypt( const unsigned char* in, size_t len );
    AesGcmDecrypt( const ustring& a, const ustring& b, const ustring& c ) : ciphertext( a ), iv( b ), tag( c ) { }

    AesGcmEncrypt decrypt( const aes256key_t& aes_key, const ustring& aad );
  };
  string to_string( const AesGcmDecrypt& dec );
}
#endif
