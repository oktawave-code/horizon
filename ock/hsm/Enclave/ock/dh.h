#ifndef __OCK_DH_H__
#define __OCK_DH_H__

#include "types.h"

namespace ock
{
  class DH
  {
  public:
    static std::tuple< std::string, std::string > create_key_pair( int bits );

    static ustring derive_secret( const string& my_privkey, const string& pubkey );
  };
}
#endif
