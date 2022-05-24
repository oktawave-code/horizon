#include "/opt/intel/sgxsdk/include/sgx_trts.h"
#include "/opt/intel/sgxsdk/include/sgx_tcrypto.h"

#include "stdlib.h"
#include <memory>
#include <algorithm>

#include <stdexcept>
#include <tuple>

#include "worker.h"
#include "kdf.h"
#include "types.h"
#include "aes.h"
#include "rsa.h"
#include "dh.h"
//#include "attestation.h"

//#include "/opt/intel/sgxsdk/include/sgx_ukey_exchange.h"
//#include "/opt/intel/sgxsdk/include/sgx_tprotected_fs.h"
//#include "/opt/intel/sgxsdk/include/sgx_uae_service.h"
//#include "/opt/intel/sgxsdk/include/sgx_ukey_exchange.h"
//#include "/opt/intel/sgxsdk/include/sgx_urts.h"



#include <openssl/evp.h>
#include "riffle/RiffleShuffle.h"

#include "debug.h"

namespace
{
  constexpr char hexmap[] = {'0', '1', '2', '3', '4', '5', '6', '7',
                             '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'};

  string to_hex( uint8_t* buffer, uint32_t len )
  {
    string s( len * 2, ' ' );
    for( int i = 0; i < len; ++i )
    {
      s[2 * i]     = hexmap[(buffer[i] & 0xF0) >> 4];
      s[2 * i + 1] = hexmap[buffer[i] & 0x0F];
    }
    return s;
  }
}


namespace ock
{
  Worker::Worker()
  {
    // TODO get key from master
    // TODO derive kdf_secret from masters
    secret_t secret_1 = {0}, secret_2 = {0};
    sgx_read_rand( secret_1.data( ), secret_1.size( ) );
    sgx_read_rand( secret_2.data( ), secret_2.size( ) );

    // Initialize
    kdf = std::unique_ptr< KDF >( new KDF( std::move( secret_1 ), std::move( secret_2 ) ) );
    policies = std::unique_ptr< PoliciesManager >( new PoliciesManager( ) );
  }


  std::tuple< Key, Token >
  Worker::create_key(
    const string& access_token,
    const KeyFamily& key_family,
    const char* ip)
  {
    // TODO Verify oktawave access token
    // TODO: Write to db - policies and id

    Key key{ { 0 }, "key", key_family };
    sgx_read_rand( key.number.data( ), key.number.size( ) );

    auto token = kdf->get_key_token( key );

    kdf->create_key( key );

    return { key, token };
  }

    std::tuple< Key, Token >
    Worker::import_key(
            const string& access_token,
            const KeyFamily& key_family,
            const string& private_key,
            const string& public_key,
            const char* ip)
    {
      // TODO Verify oktawave access token
      // TODO: Write to db - policies and id

      Key key{ { 0 }, "key", key_family };
      sgx_read_rand( key.number.data( ), key.number.size( ) );

      auto token = kdf->get_key_token( key );

      kdf->import_key( key, private_key, public_key );

      return { key, token };
    }

  std::tuple< Key, Token, AliasPolicy >Worker::create_alias(
    const Key& key,
    const Token& token,
    const string& alias,
    const AliasPolicy& policy,
    const char* ip )
  {
    if( kdf->get_key_token( key ) != token ) {
      throw std::runtime_error( "Invalid access token!" );
    }
    // TODO Verify permission from db
    // TODO if alias does not yet exist
    // TODO: Set policies


    Key alias_key { key.number , "alias/" + alias, key.family };
    auto alias_token = kdf->get_key_token( alias_key );

    policies->set_alias_policy( alias_key, policy );

    return { alias_key, alias_token, policy };
  }

  bool Worker::verify_action_access( const Key& key, const Token& token, const AliasAction& action)
  {
    if( kdf->get_key_token( key ) != token ) {
      throw std::runtime_error( "Invalid access token!" );
    }
    if( key.alias == "key" ) {
      throw std::runtime_error( "Usage of master key verboten" );
    }

    policies->verify_alias_action( key, action);

    return true;
  }

  ustring Worker::encrypt(
    const Key& key,
    const Token& alias_token,
    const ustring& plaintext,
    const EncryptionMode& mode, const char* ip )
  {
      if( kdf->get_key_token( key ) != alias_token ) {
          throw std::runtime_error( "Invalid access token!" );
      }
      if( key.alias == "key" ) {
          throw std::runtime_error( "Usage of master key verboten" );
      }

      verify_action_access( key, alias_token, { "ock:Encrypt", ip });

    switch( mode.value )
    {
      case EncryptionMode::AES_GCM:
      {
        auto aes_key = kdf->get_aes_key( key );
        ustring aad = {};
        auto c = AesGcmEncrypt( plaintext ).encrypt( aes_key, aad );
        return c.ciphertext + c.iv + c.tag;
      }
      case EncryptionMode::RSA_OAEP:
      {
        auto rsa_pubkey = kdf->get_rsa_pubkey( key );
        auto c = RsaOaep::encrypt( rsa_pubkey, plaintext );
        return c;
      }
      case EncryptionMode::RSA_EVP:
      {
        auto rsa_pubkey = kdf->get_rsa_pubkey( key );
        auto c = RsaEvp::encrypt( rsa_pubkey, plaintext );
        return c;
      }
    }

    return {0};
  }


  ustring Worker::decrypt(
    const Key& key,
    const Token& alias_token,
    const ustring& ciphertext_blob,
    const EncryptionMode& mode, const char* ip )
  {
    if( kdf->get_key_token( key ) != alias_token ) {
      throw std::runtime_error( "Invalid access token!" );
    }
    if( key.alias == "key" ) {
      throw std::runtime_error( "Usage of master key verboten" );
    }

    policies->verify_alias_action( key, { "ock:Decrypt", ip } );


    switch( mode.value )
    {
      case EncryptionMode::AES_GCM:
      {
        auto aes_key = kdf->get_aes_key( key );
        ustring aad = {};
        auto c = AesGcmDecrypt( ciphertext_blob ).decrypt( aes_key, aad );
        return c.plaintext;
      }
      case EncryptionMode::RSA_OAEP:
      {
        auto rsa_privkey = kdf->get_rsa_privkey( key );
        auto c = RsaOaep::decrypt( rsa_privkey, ciphertext_blob );
        return c;
      }
      case EncryptionMode::RSA_EVP:
      {
        auto rsa_privkey = kdf->get_rsa_privkey( key );
        auto c = RsaEvp::decrypt( rsa_privkey, ciphertext_blob );
        return c;
      }
    }

    return {0};
  }

  ustring Worker::sign(
    const Key& key,
    const Token& alias_token,
    const ustring& msg,
    const EncryptionMode& mode, const char* ip )
  {
    if( kdf->get_key_token( key ) != alias_token ) {
      throw std::runtime_error( "Invalid access token!" );
    }
    if( key.alias == "key" ) {
      throw std::runtime_error( "Usage of master key verboten" );
    }

    //policies->verify_alias_action( key, { "ock:Encrypt", "*" } );

    policies->verify_alias_action( key, { "ock:Sign", ip});

    switch( mode.value )
    {
      case EncryptionMode::RSA_SHA256:
      {
        auto rsa_privkey = kdf->get_rsa_privkey( key );
        auto c = RsaSig::sign( rsa_privkey, msg );
        return c;
      }
    }

    return {0};
  }


  bool Worker::verify(
    const Key& key,
    const Token& alias_token,
    const ustring& msg,
    const ustring& signature,
    const EncryptionMode& mode,
    const char* ip)
  {
    if( kdf->get_key_token( key ) != alias_token ) {
      throw std::runtime_error( "Invalid access token!" );
    }
    if( key.alias == "key" ) {
      throw std::runtime_error( "Usage of master key verboten" );
    }

    policies->verify_alias_action( key, { "ock:Verify", ip } );

    switch( mode.value )
    {
      case EncryptionMode::RSA_SHA256:
      {
        auto rsa_pubkey = kdf->get_rsa_pubkey( key );
        auto c = RsaSig::verify( rsa_pubkey, msg, signature );
        return c;
      }
    }

    return {0};
  }

  string Worker::digest(
    const Key& key,
    const Token& alias_token,
    const string& msg,
    const EncryptionMode& mode,
    const char* ip)
  {
    if( kdf->get_key_token( key ) != alias_token ) {
      throw std::runtime_error( "Invalid access token!" );
    }
    if( key.alias == "key" ) {
      throw std::runtime_error( "Usage of master key verboten" );
    }

    policies->verify_alias_action( key, { "ock:Digest", ip } );

    switch( mode.value )
    {
      case EncryptionMode::SHA256:
      {
        uint32_t key_len;
        string buffer( SHA256_DIGEST_LENGTH, 0 );

        EVP_MD_CTX* context = EVP_MD_CTX_new( );
        EVP_DigestInit_ex( context, EVP_sha256( ), NULL );
        EVP_DigestUpdate( context, (uint8_t*) &msg[0], msg.size( ) );
        EVP_DigestFinal_ex( context, (uint8_t*) &buffer[0], &key_len );
        EVP_MD_CTX_free( context );

        return to_hex( (uint8_t*) &buffer[0], buffer.size() );
      }
      case EncryptionMode::RIFFLE:
      {
        RiffleShuffle x;
        x.init( 256, "SHA-256" );
        auto aes_key = kdf->get_aes_key( key );
        auto salt = to_hex( (uint8_t*) &aes_key[0], aes_key.size());
        x.scramble( msg, salt, 1 ); // Pass, salt <- input
        return x.getHash( );
      }
    }
  }

  string Worker::shared_secret(
    const Key& key,
    const Token& alias_token,
    const string& public_key,
    const char* ip)
  {
    verify_action_access( key, alias_token, { "ock:Sign", ip });

    auto dh_privkey = kdf->get_dh_privkey( key );
    auto c = DH::derive_secret( dh_privkey, public_key );
    return to_hex( &c[0], c.size() );
  }

  string Worker::get_public_key(
    const Key& key,
    const Token& alias_token,
    const char* ip)
  {
    verify_action_access( key, alias_token, { "ock:Info", ip });

    string pubKey;
    if (key.family == KeyFamily::DH) {
      pubKey = kdf->get_dh_pubkey(key);
    }
    else {
      if (key.family.RSA) {
        pubKey = kdf->get_rsa_pubkey(key);
      } else {
        throw std::runtime_error("Showing public key is not possible");
      }
    }

    return pubKey;
  }


  ustring Worker::random(
    const Key& key,
    const Token& alias_token,
    const int length,
    const char* ip)
  {
    if( kdf->get_key_token( key ) != alias_token ) {
      throw std::runtime_error( "Invalid access token!" );
    }
    if( key.alias == "key" ) {
      throw std::runtime_error( "Usage of master key verboten" );
    }

    policies->verify_alias_action( key, { "ock:GetRandom", ip } );

    if( length < 1 )
    {
      throw std::runtime_error( "Length < 1" );
    }

    ustring buffer( length, 0 );
    sgx_read_rand( &buffer[0], buffer.size( ) );

    return buffer;
  }

  string Worker::get_epid(const char *ip) {
      uint32_t p_extended_epid_group_id = 0;
      sgx_status_t status;
      //  = "as";
      string resp = "error";
//      status = sgx_get_extended_epid_group_id(&p_extended_epid_group_id);
      //status = sgx_get_extended_epid_group_id(&p_extended_epid_group_id);


    //  if (status == SGX_SUCCESS) {
  //        resp =  "success:" + p_extended_epid_group_id;
//      }

      return resp;
  }

}
