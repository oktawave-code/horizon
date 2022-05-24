
#ifndef __OCK_TYPES__
#define __OCK_TYPES__

#include <array>
#include <string>
#include <tuple>

namespace ock
{
  // String = readable || Ustring = bytes
  typedef std::basic_string<unsigned char> ustring;
  using std::string;


  // ----------------- KEY -----------------
  struct EncryptionMode
  {
    static const uint8_t AES_GCM = 1;
    static const uint8_t AES_CTR = 2;
    static const uint8_t RSA_OAEP = 5;
    static const uint8_t RSA_EVP = 6;
    static const uint8_t RSA_SHA256 = 7;
    static const uint8_t SHA256 = 10;
    static const uint8_t RIFFLE = 11;
    static const uint8_t Unknown = 0;

    uint8_t value;

    EncryptionMode( uint8_t a ) : value( a ) { }
    EncryptionMode( ) : value( EncryptionMode::Unknown ) { }
    EncryptionMode( const string& s );
  };
  inline bool operator==(const EncryptionMode& lhs, const uint8_t rhs ){ return lhs.value == rhs; }

  struct KeyFamily
  {
    static const uint8_t Symmetric = 1;
    static const uint8_t RSA = 2;
    static const uint8_t DH = 3;
    static const uint8_t Unknown = 0;

    uint8_t value;

    KeyFamily( uint8_t a ) : value( a ) { }
    KeyFamily( ) : value( KeyFamily::Unknown ) { }
    KeyFamily( const string& s );
  };
  inline bool operator==(const KeyFamily& lhs, const uint8_t rhs ){ return lhs.value == rhs; }

  typedef std::array< uint8_t, 8 > keynumber_t;
  struct Key
  {
    keynumber_t number;
    std::string alias;
    KeyFamily family;

    Key( const keynumber_t& a, const std::string& b, const KeyFamily& c ): number( a ), alias( b ), family( c ) {}
    Key( ){ }
    Key( const std::string& s );
  };

  // ---------------- TOKEN ----------------
  struct Token : std::array< uint8_t, 16 >
  {
    Token( ){ }
    Token( const std::string& s);
  };

  // --------------- SECRETS ---------------
  typedef std::array< uint8_t, 32 > secret_t ;
  typedef std::array< uint8_t, 32 > aes256key_t;

  // ---------------- STRING ---------------
  std::string to_string( const Key& key );
  std::string to_string( const keynumber_t& number );
  // std::string to_string( const key_family& family );
  std::string to_string( const KeyFamily& family );
  std::string to_string( const Token& token );
  std::string to_string( const std::string& s );
  std::string to_string( const ustring& s );
  // std::string to_string( bool s );
}

#endif
