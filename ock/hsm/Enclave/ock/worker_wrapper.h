
#ifndef __OCK_WORKER_WRAPPER_H_
#define __OCK_WORKER_WRAPPER_H_

#include <tuple>
#include <exception>

#include "worker.h"
#include "types.h"
#include "json_parser.h"


namespace ock
{
  class WorkerWrapper
  {
  private:
    Worker worker;

  public:

    std::tuple< string, int> init_secrets( const JsonReader& json, const char* ip);
    std::tuple< string, int > create_key( const JsonReader& json, const char* ip );
    std::tuple< string, int > import_key( const JsonReader& json, const char* ip );
    std::tuple< string, int > create_alias( const JsonReader& json, const char* ip );
    std::tuple< string, int > encrypt( const JsonReader& json, const char* ip );
    std::tuple< string, int > decrypt( const JsonReader& json, const char* ip );
    std::tuple< string, int > sign( const JsonReader& json, const char* ip );
    std::tuple< string, int > verify( const JsonReader& json, const char* ip );
    std::tuple< string, int > digest( const JsonReader& json, const char* ip );
    std::tuple< string, int > shared_secret( const JsonReader& json, const char* ip );
    std::tuple< string, int > get_public_key( const JsonReader& json, const char* ip );
    std::tuple< string, int > random( const JsonReader& json, const char* ip );
    std::tuple< string, int > manage( const JsonReader& json, const char* ip );
    std::tuple< string, int > get_epid( const JsonReader& json, const char* ip );
    std::tuple< string, int > error( const std::exception& re );
  };
}

#endif
