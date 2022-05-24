
#include <algorithm>

#include <stdio.h>
#include <stdexcept>
#include <type_traits>
#include <string>
#include "json/json.h"
#include "json_parser.h"

#include "base64/base64.h"

#include "policies.h"

#include "debug.h"

#include "debug.h"

namespace ock
{
  JsonReader::JsonReader( ustring msg )
  {
    root = json_parse( msg.data( ), msg.size( ) );
    if( !root )
    {
      throw std::runtime_error( "Cannot parse json" );
    }
  }

  JsonReader::~JsonReader( )
  {
    free( root );
  }

  struct json_value_s* JsonReader::at_key( const string& key, struct json_value_s* value ) const
  {
    if( !value || value->type != json_type_object )
    {
      throw std::runtime_error( "Parsing non-object as object" );
    }

    auto object = ( struct json_object_s* ) value->payload;
    for( auto p = object->start; p; p = p->next )
    {
      auto name = ( ( json_string_s* )p->name )->string;

      if( strcmp( key.c_str( ), name ) == 0 )
      {
        return p->value;
      }
    }
    return NULL;
  }

  string JsonReader::as_string( struct json_value_s* value ) const
  {
    if( !value || value->type != json_type_string )
    {
      throw std::runtime_error( "Parsing non-string as string" );
    }

    auto s = (struct json_string_s*)value->payload;
    return string( s->string, s->string_size );
  }

  int JsonReader::as_int( struct json_value_s* value ) const
  {
    if( !value || value->type != json_type_number )
    {
      throw std::runtime_error( "Parsing non-string as string" );
    }

    auto n = (struct json_number_s*)value->payload;
    return std::stoi( string( n->number, n->number_size ) );
  }

  std::vector< struct json_value_s* > JsonReader::as_vector( struct json_value_s* value ) const
  {
    if( !value || value->type != json_type_array )
    {
      throw std::runtime_error( "Parsing non-array as array" );
    }

    std::vector< struct json_value_s* > v;

    auto array = ( struct json_array_s* )value->payload;
    for( auto p = array->start; p; p = p->next )
    {
      v.push_back( p->value );
    }

    return v;
  }

  string JsonReader::get( const string& key, const string& automatic, struct json_value_s* value ) const
  {
    auto var = at_key( key, ( value ) ? value : root );
    if( var != NULL )
    {
      return as_string( var );
    }
    else if( var == NULL && automatic.size( ) > 0 )
    {
      return to_string( automatic );
    }
    else
    {
      throw std::runtime_error( "Property " + key + " not found!" );
    }
  }

  int JsonReader::get_int( const string& key, int automatic, struct json_value_s* value ) const
  {
    auto var = at_key( key, ( value ) ? value : root );
    if( var != NULL )
    {
      return as_int( var );
    }
    else if( var == NULL )
    {
      return automatic;
    }
    else
    {
      throw std::runtime_error( "Property " + key + " not found!" );
    }
  }

}
