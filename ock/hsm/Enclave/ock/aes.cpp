#include <openssl/ec.h>
#include <openssl/bn.h>
#include <openssl/rsa.h>
#include <openssl/evp.h>
#include <openssl/err.h>
#include <openssl/rand.h>
#include <openssl/sha.h>

#include <stdexcept>
#include "sgx_trts.h"
#include "base64/base64.h"
#include "aes.h"

namespace ock
{
  AesGcmDecrypt AesGcmEncrypt::encrypt( const aes256key_t& aes_key, const ustring& aad )
  {
    ustring iv( AesGcm::iv_size, 0 );
    ustring tag( AesGcm::tag_size, 0 );
    ustring ciphertext( plaintext.size( ), 0 );
    int len;

    /* Create and initialise the context */
    EVP_CIPHER_CTX* ctx;
    if( !( ctx = EVP_CIPHER_CTX_new( ) ) )
    {
      throw std::runtime_error( "1" );
    }

    /* Initialise the encryption operation. */
    if( 1 != EVP_EncryptInit_ex( ctx, EVP_aes_256_gcm( ), NULL, NULL, NULL ) )
    {
      throw std::runtime_error( "2" );
    }

    /* Set IV length if default 12 bytes (96 bits) is not appropriate */
    if(1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, iv.size( ), NULL) )
    {
      throw std::runtime_error( "3" );
    }

    /* Initialise key and IV */
    sgx_read_rand( (uint8_t*) iv.data( ), iv.size( ) );
    if( 1 != EVP_EncryptInit_ex( ctx, NULL, NULL, aes_key.data( ), iv.data( ) ) )
    {
      throw std::runtime_error( "4" );
    }

    /* Provide any AAD data. This can be called zero or more times as
     * required
     */
    if( aad.size( ) > 0 ) {
      if( 1 != EVP_EncryptUpdate( ctx, NULL, &len, (uint8_t*)aad.data( ), aad.size( ) ) )
      {
        throw std::runtime_error( "5" );
      }
    }

    /* Provide the message to be encrypted, and obtain the encrypted output.
     * EVP_EncryptUpdate can be called multiple times if necessary
     */
    if( 1 != EVP_EncryptUpdate( ctx, (uint8_t*)ciphertext.data( ), &len,(uint8_t*) plaintext.data( ), plaintext.size( ) ) )
    {
      throw std::runtime_error( "6" );
    }

    /* Finalise the encryption. Normally ciphertext bytes may be written at
     * this stage, but this does not occur in GCM mode
     */
    if( 1 != EVP_EncryptFinal_ex( ctx, (uint8_t*)ciphertext.data( ) + len, &len ) )
    {
      throw std::runtime_error( "7" );
    }

    /* Get the tag */
    if( 1 != EVP_CIPHER_CTX_ctrl( ctx, EVP_CTRL_GCM_GET_TAG, tag.size( ), (void*)tag.data( ) ) )
    {
      throw std::runtime_error( "8" );
    }

    /* Clean up */
    EVP_CIPHER_CTX_free( ctx );

    return { ciphertext, iv, tag };
  }

  AesGcmEncrypt AesGcmDecrypt::decrypt( const aes256key_t& aes_key, const ustring& aad )
  {
    // auto ciphertext = ;
    // iv_t iv;
    // tag_t tag;
    // std::tie( ciphertext, iv, tag ) = ciphertxt;
    ustring plaintext( ciphertext.size( ), 0);

    int len;

    /* Create and initialise the context */
    EVP_CIPHER_CTX *ctx;
    if( !( ctx = EVP_CIPHER_CTX_new( ) ) )
    {
      throw std::runtime_error( "1" );
    }

    /* Initialise the decryption operation. */
    if( !EVP_DecryptInit_ex( ctx, EVP_aes_256_gcm( ), NULL, NULL, NULL ) )
    {
      throw std::runtime_error( "2" );
    }

    /* Set IV length. Not necessary if this is 12 bytes (96 bits) */
    // int iv_len = 12;
    if( !EVP_CIPHER_CTX_ctrl( ctx, EVP_CTRL_GCM_SET_IVLEN, iv.size( ), NULL ) )
    {
      throw std::runtime_error( "3" );
    }

    /* Initialise key and IV */
    // uint8_t * key = secret_key_1;
    if( !EVP_DecryptInit_ex( ctx, NULL, NULL, aes_key.data( ), iv.data( ) ) )
    {
      throw std::runtime_error( "4" );
    }

    /* Provide any AAD data. This can be called zero or more times as
     * required
     */
    if( aad.size( ) > 0 )
    {
      if( !EVP_DecryptUpdate( ctx, NULL, &len, (uint8_t*)aad.data( ), aad.size( ) ) )
      {
        throw std::runtime_error( "5" );
      }
    }

    /* Provide the message to be decrypted, and obtain the plaintext output.
     * EVP_DecryptUpdate can be called multiple times if necessary
     */
    if( !EVP_DecryptUpdate( ctx, (uint8_t*)plaintext.data( ), &len, (uint8_t*)ciphertext.data( ), ciphertext.size( ) ) )
    {
      throw std::runtime_error( "6" );
    }

    /* Set expected tag value. Works in OpenSSL 1.0.1d and later */
    if( !EVP_CIPHER_CTX_ctrl( ctx, EVP_CTRL_GCM_SET_TAG, tag.size( ), (void*)tag.data( ) ) )
    {
      throw std::runtime_error( "7" );
    }

    /* Finalise the decryption. A positive return value indicates success,
     * anything else is a failure - the plaintext is not trustworthy.
     */
    int ret = EVP_DecryptFinal_ex( ctx, (uint8_t*)plaintext.data( ) + len, &len );

    /* Clean up */
    EVP_CIPHER_CTX_free( ctx );

    if( ret > 0 )
    {
      /* Success */
      return { plaintext };
    }
    else
    {
      /* Verify failed */
      throw std::runtime_error( "AES decryption failed" );
    }
  }


  AesGcmDecrypt::AesGcmDecrypt( const ustring& us )
  {
    ciphertext = us.substr( 0, us.size( ) - AesGcm::tag_size -  AesGcm::iv_size );
    iv = us.substr( ciphertext.size( ), AesGcm::iv_size );
    tag = us.substr( ciphertext.size( ) + AesGcm::iv_size, AesGcm::tag_size );
  }

  AesGcmDecrypt::AesGcmDecrypt( const uint8_t* ptr, size_t len )
  {
    ciphertext = ustring( ptr, len - AesGcm::tag_size -  AesGcm::iv_size );
    iv = ustring( ptr + ciphertext.size( ), AesGcm::iv_size );
    tag = ustring( ptr + ciphertext.size( ) + AesGcm::iv_size, AesGcm::tag_size );
  }

  string to_string( const AesGcmDecrypt& c )
  {
    return b64::encode( c.ciphertext + c.iv + c.tag );
  }

  string to_string( const AesGcmEncrypt& p )
  {
    return b64::encode( p.plaintext );
  }
}
