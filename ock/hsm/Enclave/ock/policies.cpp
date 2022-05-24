#include "policies.h"

#include <algorithm>
#include <stdexcept>
#include <cstring>

#include "json_parser.h"

#include "sgx_tprotected_fs.h"
#include "base64/base64.h"

#include "debug.h"


namespace
{
  void write_file( std::string name, std::string content )
  {
    std::string fullPath = "/mnt/shared/policies/" + name;
    auto g = sgx_fopen_auto_key( fullPath.c_str(), "w+" );
    sgx_fwrite(content.data(), 1, content.size(), g);
    sgx_fflush(g);
    sgx_fclose(g);
  }

  std::string read_file( std::string name )
  {
    std::string fullPath = "/mnt/shared/policies/" + name;
    auto g = sgx_fopen_auto_key( fullPath.c_str(), "r+" );

    std::string content;
    char buff[512];
    size_t len = 0;
    while( (len = sgx_fread(buff, 1, 512, g) ) > 0)
    {
      content  = content + std::string(buff, len);
    }
    sgx_fclose(g);

    return content;
  }
}


namespace ock
{
  AliasPolicy::AliasPolicy( const JsonReader& jr, struct json_value_s* policy_root )
  {
    if( policy_root != NULL )
    {
      access = jr.get< string >( "AllowedIp", "*", policy_root );
      expires = jr.get< string >( "ExpirationDate", "Never", policy_root );

      auto action_root = jr.at_key( "Action", policy_root );
      if( action_root )
      {
        auto json_action = jr.as_vector( action_root );
        for( auto a : json_action )
        {
          auto s = jr.as_string( a );
          if( s == "ock:Encrypt" || s == "ock:Decrypt" || s == "ock:Sign" || s == "ock:Verify" || s == "ock:DH" || s == "ock:Info")
          {
            action.push_back( jr.as_string( a ) );
          }
          else
          {
            throw std::runtime_error( "Unknown policy action - wtf: " + s );
          }
        }

        if( action.size() == 0 )
        {
          throw std::runtime_error( "Action list cannot be empty" );
        }
      }
      else
      {
        action = { "ock:Encrypt", "ock:Info", "ock:Verify" };
      }
    }
    else
    {
      access = "*";
      expires = "Never";
      action = { "ock:Encrypt", "ock:Info", "ock:Verify" };
    }

  }


  void PoliciesManager::set_alias_policy( const Key& key, const AliasPolicy& alias_policy )
  {
    auto dkey = to_string( key.number ) + ":" + key.alias.substr(6);
    auto s = to_string( alias_policy );

    write_file( dkey + ".policy", s );
  }

  AliasPolicy PoliciesManager::get_alias_policy( const Key& key )
  {
    if( key.alias == "key" )
    {
      throw std::runtime_error( "Asking for alias policy of master key" );
    }

    auto dkey = to_string( key.number ) + ":" + key.alias.substr(6);
    auto ss = read_file( dkey + ".policy" );
    ustring s(ss.begin(), ss.end());

    JsonReader json( s );
    AliasPolicy alias_policy( json, json.root );

    return alias_policy;
  }


  void PoliciesManager::verify_alias_action( const Key& key, const AliasAction& action )
  {
    bool policyVerified = false;
    bool accessVerified = false;
    auto policy = get_alias_policy( key );

    for( const auto& a : policy.action )
    {
      if( a == action.action )
      {
        policyVerified = true;
      }
    }

    if (policy.access == "*" || policy.access == action.ip) {
       accessVerified = true;
    }

    if (accessVerified && policyVerified) {
      return;
    }

    if (accessVerified && !policyVerified) {
            throw std::runtime_error("Action " + action.action + " is not allowed for this key");
    }
    if (!accessVerified && !policyVerified) {
          throw std::runtime_error("Nothing is allowed for this key");
      }
    if (!accessVerified && policyVerified) {
          throw std::runtime_error("Action " + action.action + " is allowed but not from this IP: " + action.ip + " (but from " + policy.access + ").");
      }

       //"Action ock:Encrypt is allowed but not from this IP: * (but from 127.0.0.1)."}
  }


  string to_string( const AliasPolicy& policy )
  {
    auto actions = JsonArrayBuilder();
    for( const string& a : policy.action )
    {
      actions.add_string( a );
    }

    auto job = JsonObjectBuilder( );
    auto s = job.add_string( "AllowedIp", policy.access ) \
                .add_string( "ExpirationDate", policy.expires ) \
                .add( "Action", actions.build() ).build();

    return s;

  }

}
