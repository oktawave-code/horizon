#ifndef __OCK_RSA_H__
#define __OCK_RSA_H__


#include "types.h"

namespace ock
{
  class Rsa
  {
  public:
    static std::tuple< std::string, std::string > create_key_pair( int bits );
  };

  class RsaOaep
  {
  public:
    static ustring encrypt( const string& public_key, const ustring& plaintext );
    static ustring decrypt( const string& private_key, const ustring& encrypt );
  };

  class RsaEvp
  {
  public:
    static ustring encrypt( const string& public_key, const ustring& plaintext );
    static ustring decrypt( const string& private_key, const ustring& ciphertext );
  };

  class RsaSig
  {
  public:
    static ustring sign( const string& private_key, const ustring& msg );
    static bool verify( const string& public_key, const ustring& msg, const ustring& signature );
  };
}
#endif
