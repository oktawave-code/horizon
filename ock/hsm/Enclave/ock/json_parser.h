#ifndef __OCK_JSON_PARSER_H__
#define __OCK_JSON_PARSER_H__

#include <tuple>
#include <vector>
#include "types.h"
#include <string>

#include "json/json.h"


namespace ock
{
  class JsonObjectBuilder
  {
  private:
    string buffer = { };

  public:
    template< typename T >
    JsonObjectBuilder& add( const string& key, const T& value )
    {
      auto kv = "\"" + key + "\": " + to_string( value );
      buffer = ( buffer.size( ) > 0 ) ? buffer + ", " + kv : kv;
      return *this;
    }

    template< typename T >
    JsonObjectBuilder& add_string( const string& key, const T& value )
    {
      return add( key, "\"" + to_string( value ) + "\"" );
    }

    string build( )
    {
      return "{" + buffer +"}";
    }
  };

  class JsonArrayBuilder
  {
  private:
    string buffer = { };

  public:
    template< typename T >
    JsonArrayBuilder& add( const T& value )
    {
      auto kv = to_string( value );
      buffer = ( buffer.size( ) > 0 ) ? buffer + ", " + kv : kv;
      return *this;
    }

    template< typename T >
    JsonArrayBuilder& add_string( const T& value )
    {
      return add( "\"" + to_string( value ) + "\"" );
    }

    string build( )
    {
      return "[" + buffer +"]";
    }
  };


  class JsonReader
  {
  public:
    struct json_value_s* root;

    JsonReader( ustring );
    ~JsonReader( );

    string get( const string& key, const string& automatic = "", struct json_value_s* value = NULL ) const;
    int get_int( const string& key, int automatic = 0, struct json_value_s* value = NULL ) const;
    std::vector< struct json_value_s* > as_vector( struct json_value_s* value ) const;
    string as_string( struct json_value_s* value ) const;
    int as_int( struct json_value_s* value ) const;
    struct json_value_s* at_key( const string& key, struct json_value_s* value ) const;

    template< typename T >
    T get( const string& key, const string& automatic = "", struct json_value_s* value = NULL ) const
    {
      return T( get( key, automatic, value ) );
    }
  };
}
#endif
