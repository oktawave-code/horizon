#include "types.h"
#include "base64/base64.h"

#include <algorithm>
#include <stdexcept>
#include <vector>
#include <string>

namespace
{
  std::vector< std::string > string_split( const std::string& str, char delim )
  {
    std::vector< std::string > cont;
    size_t current, previous = 0;

    current = str.find( delim );
    while( current != std::string::npos )
    {
      cont.push_back( str.substr( previous, current - previous ) );
      previous = current + 1;
      current = str.find( delim, previous );
    }
    cont.push_back( str.substr( previous, current - previous ) );

    return cont;
  }

  ock::keynumber_t convert_number( const std::string& s )
  {
    ock::keynumber_t a;
    *( ( uint64_t* )a.data( ) ) = stoull( s );
    return a;
  }

  constexpr char hexmap[] = {'0', '1', '2', '3', '4', '5', '6', '7',
                             '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'};
}

namespace ock
{
  EncryptionMode::EncryptionMode( const string& s )
  {
    if( s == "AES-GCM" ) value = EncryptionMode::AES_GCM;
    else if( s == "AES-CTR" ) value = EncryptionMode::AES_CTR;
    else if( s == "RSA-OAEP" ) value = EncryptionMode::RSA_OAEP;
    else if( s == "RSA-EVP" ) value = EncryptionMode::RSA_EVP;
    else if( s == "RSA-SHA256" ) value = EncryptionMode::RSA_SHA256;
    else if( s == "SHA-256" ) value = EncryptionMode::SHA256;
    else if( s == "RIFFLE" ) value = EncryptionMode::RIFFLE;
    else throw std::runtime_error( "Unknown encryption mode: " + s );
  }

  KeyFamily::KeyFamily( const string& s )
  {
    if( s == "AES" ) value = KeyFamily::Symmetric;
    else if( s == "RSA" ) value = KeyFamily::RSA;
    else if( s == "DH" ) value = KeyFamily::DH;
    else throw std::runtime_error( "Unknown key family: " + s );
  }

  Key::Key( const string& s )
  {
    auto parts = string_split( s, ':' );

    if( parts.size( ) != 4 )
    {
      throw std::runtime_error( "Invalid key format" );
    }

    number = convert_number( parts[ 1 ] );
    family = KeyFamily( parts[ 2 ] );
    alias = parts[ 3 ];
  }

  Token::Token( const std::string& s )
  {
    for( size_t i = 0, j = 0; j < size( ); i += 2, j++ )
    {
      while( s[i] == '-') i++;
      (*this)[j] = (s[i] % 32 + 9) % 25 * 16 + (s[i+1] % 32 + 9) % 25;
    }
  }

  string to_string( const Key& key )
  {
    auto s = "ock:" + to_string( key.number ) + ":" + to_string( key.family ) + ":" + key.alias;
    return s;
  }

  string to_string( const keynumber_t& number )
  {
    auto num = *( ( uint64_t* ) number.data( ) );
    return std::to_string( num );
  }

  string to_string( const KeyFamily& family )
  {
    if( family.value == KeyFamily::Symmetric ) return "AES";
    if( family.value == KeyFamily::RSA ) return "RSA";
    if( family.value == KeyFamily::DH ) return "DH";
  }

  string to_string( const Token& token )
  {
    string s( token.size( ) * 2 + 4, ' ' );
    for( int i = 0, j = 0; i < token.size( ); ++i )
    {
      if( i == 5 || i == 7 || i ==  9 || i == 11 )
      {
        s[ 2 * i + j ] = '-';
        j++;
      }

      s[2 * i + j]     = hexmap[(token[i] & 0xF0) >> 4];
      s[2 * i + 1 + j] = hexmap[token[i] & 0x0F];
    }
    return s;
  }

  string to_string( const string& s )
  {
    return s;
  }

  string to_string( const ustring& s )
  {
    return b64::encode( s );
  }

}
