#include "/opt/intel/sgxsdk/include/sgx_tcrypto.h"

#include <algorithm>
#include <stdexcept>
#include <string>
#include <tuple>


#include <openssl/sha.h>
#include <openssl/evp.h>
#include <openssl/err.h>

#include "kdf.h"

#include "rsa.h"
#include "dh.h"

#include "debug.h"

#include "/opt/intel/sgxsdk/include/sgx_tprotected_fs.h"
#include "/opt/intel/sgxsdk/include/sgx_tcrypto.h"
#include "/opt/intel/sgxsdk/include/sgx_utils.h"




namespace
{
  template< typename T, typename... S >
  T hash_sha256( S... args )
  {
    const size_t nargs = sizeof...( args );
    const void* data[ nargs ] = { ( args.data( ) )... };
    size_t size[ nargs ] = { ( args.size( ) )... };

    uint32_t key_len;
    uint8_t buffer[32];

    EVP_MD_CTX* context = EVP_MD_CTX_new( );
    EVP_DigestInit_ex( context, EVP_sha256( ), NULL );
    for( int i = 0; i < nargs; i++ )
      EVP_DigestUpdate( context, data[ i ], size[ i ] );
    EVP_DigestFinal_ex( context, buffer, &key_len );
    EVP_MD_CTX_free( context );

    T t;
    std::copy_n( buffer, t.size( ), t.begin( ) );
    return t;
  }

  void write_file( std::string name, std::string content )
  {
    std::string fullPath = "/mnt/shared/" + name;
    auto g = sgx_fopen_auto_key( fullPath.c_str(), "w+" );
    sgx_fwrite(content.data(), 1, content.size(), g);
    sgx_fflush(g);
    sgx_fclose(g);
  }

  std::string read_file( std::string name )
  {
    std::string fullPath = "/mnt/shared/" + name;
    auto g = sgx_fopen_auto_key( fullPath.c_str(), "r+" );

    if( g == NULL )
    {
      throw std::runtime_error( "sgx_fopen_auto_key error" );
    }

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
  KDF::KDF( secret_t&& secret_1, secret_t&& secret_2 )
  {
    try
    {
      auto f = read_file( "secret.keys" );
      std::copy_n( f.begin( ), secret_1.size( ), secret_1.begin( ) );
      std::copy_n( f.begin( ) + secret_1.size(), secret_2.size( ), secret_2.begin( ) );

      debug("Reading old:\n");
      for (int i = 0; i < secret_1.size(); i++ )
      {
        debug("%x", secret_1[i]);
      }
      debug("\n");
      for (int i = 0; i < secret_2.size(); i++ )
      {
        debug("%x", secret_2[i]);
      }
      debug("\n");

    }
    catch( const std::runtime_error& e )
    {
      debug( "Initializing KDF at random\n" );


      string f( secret_1.size() * 2, 0 );
      std::copy_n( secret_1.begin(), secret_1.size(), f.begin() );
      std::copy_n( secret_2.begin(), secret_2.size(), f.begin() + secret_1.size() );

      debug("Writing new:\n");
      for (int i = 0; i < secret_1.size(); i++ )
      {
        debug("%x", secret_1[i]);
      }
      debug("\n");
      for (int i = 0; i < secret_2.size(); i++ )
      {
        debug("%x", secret_2[i]);
      }
      debug("\n");

      write_file( "secret.keys", f );


      /**
       * TODO: new way of generating keys
       */
       /*
      const sgx_key_request_t *key_request;
      sgx_key_128bit_t *key;
      const sgx_aes_gcm_128bit_key_t *p_key;

      sgx_status_t result;
      result = sgx_get_key(*key_request, *key);
        */

    }
  }

  Token KDF::get_key_token( const Key& key )
  {
    return hash_sha256< Token >( secret_1, std::string(":key_token:"), secret_2, key.number, key.alias );
  }

  aes256key_t KDF::get_aes_key( const Key& key )
  {
    return hash_sha256< aes256key_t >( secret_1, std::string(":aes_key:"), secret_2, key.number );
  }

  aes256key_t KDF::get_ecdsa_key( const Key& key )
  {
    return hash_sha256< aes256key_t >( secret_1, std::string(":ecdsa_key:"), secret_2, key.number );
  }

  void KDF::create_key( const Key& key )
  {
    if( key.family == KeyFamily::RSA )
    {
      auto rsa = Rsa::create_key_pair( 3072 );
      auto dkey = to_string( key.number );

      write_file( dkey + ".pem", std::get< 0 >(rsa) );
      write_file( dkey + ".pub", std::get< 1 >(rsa) );
    }
    if( key.family == KeyFamily::DH )
    {
      auto dh = DH::create_key_pair( 3072 );
      auto rsa = DH::derive_secret( std::get< 0 >(dh), std::get< 1 >(dh) );
      auto dkey = to_string( key.number );

      write_file( dkey + ".pem", std::get< 0 >(dh) );
      write_file( dkey + ".pub", std::get< 1 >(dh) );
    }

  }

    void KDF::import_key( const Key& key, const string& private_key, const string& public_key )
    {
      if( key.family == KeyFamily::RSA )
      {
        //auto rsa = Rsa::create_key_pair( 3072 );
        auto dkey = to_string( key.number );
        //auto rsa = std::tuple({private_key, public_key});
        //std::tuple<std::string, std::string> rsa;


        //write_file( dkey + ".pem", std::get< 0 >(rsa) );
        write_file(dkey + ".pem", private_key);
        //write_file( dkey + ".pub", std::get< 1 >(rsa) );
        write_file(dkey + ".pub", public_key);
      }
      if( key.family == KeyFamily::DH )
      {
        auto dh = DH::create_key_pair( 3072 );
        auto rsa = DH::derive_secret( std::get< 0 >(dh), std::get< 1 >(dh) );
        auto dkey = to_string( key.number );

        write_file( dkey + ".pem", std::get< 0 >(dh) );
        write_file( dkey + ".pub", std::get< 1 >(dh) );
      }

    }

  string KDF::get_rsa_pubkey( const Key& key )
  {
    return read_file( to_string( key.number ) + ".pub" );
  }

  string KDF::get_rsa_privkey( const Key& key )
  {
    return read_file( to_string( key.number ) + ".pem" );
  }

  string KDF::get_dh_privkey( const Key& key )
  {
    return read_file( to_string( key.number ) + ".pem" );
  }

  string KDF::get_dh_pubkey( const Key& key )
  {
    return read_file( to_string( key.number ) + ".pub" );
  }

}
