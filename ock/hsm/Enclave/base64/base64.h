//
//  base64 encoding and decoding with C++.
//  Version: 1.01.00
//

#ifndef BASE64_H_C0CE2A47_D10E_42C9_A27C_C883944E704A
#define BASE64_H_C0CE2A47_D10E_42C9_A27C_C883944E704A

#include <string>

namespace b64
{
  typedef std::basic_string<unsigned char> ustring;
  using std::string;

  string encode( const ustring& us);
  string encode( unsigned char const*, unsigned int len );
  ustring decode( const string& s );
}

#endif /* BASE64_H_C0CE2A47_D10E_42C9_A27C_C883944E704A */
