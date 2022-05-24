#ifndef __OCK_POLICIES_H__
#define __OCK_POLICIES_H__

#include <string>

#include "types.h"
#include "json_parser.h"
#include <vector>

namespace ock
{
  struct AliasAction
  {
    string action;
    string ip;
  };

  struct AliasPolicy
  {
    std::vector< string > action;
    string access;
    string expires;

    AliasPolicy( const std::vector< string >& a, const string& b, const string& c ): action( a ), access( b ), expires( c ) { }
    AliasPolicy( ) { }
    AliasPolicy( const JsonReader& jr, struct json_value_s* root );
  };

  string to_string( const AliasPolicy& policy );


  class PoliciesManager
  {
  public:

    void set_alias_policy( const Key& key, const AliasPolicy& policy );

    void verify_alias_action( const Key& key, const AliasAction& action );


    AliasPolicy get_alias_policy( const Key& key_id );

  };
}

#endif
