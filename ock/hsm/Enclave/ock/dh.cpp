#include "dh.h"

#include <openssl/rsa.h>
#include <openssl/pem.h>
#include <openssl/evp.h>

#include <stdexcept>
#include <algorithm>

#include "debug.h"


namespace ock
{
  std::tuple< std::string, std::string > DH::create_key_pair( int bits )
  {
    EVP_PKEY_CTX *pctx, *kctx;
  	EVP_PKEY *pkey = NULL, *params = NULL;

    if(NULL == (params = EVP_PKEY_new()))
    {
      throw std::runtime_error( "EVP_PKEY_new" );
    }
    if(1 != EVP_PKEY_set1_DH(params,DH_get_2048_256()))
    {
      throw std::runtime_error( "EVP_PKEY_set1_DH" );
    }

    /* Create context for the key generation */
    if(!(kctx = EVP_PKEY_CTX_new(params, NULL)))
    {
      throw std::runtime_error( "EVP_PKEY_CTX_new" );
    }

    /* Generate a new key */
    if(1 != EVP_PKEY_keygen_init(kctx))
    {
      throw std::runtime_error( "EVP_PKEY_keygen_init" );
    }
    if(1 != EVP_PKEY_keygen(kctx, &pkey))
    {
      throw std::runtime_error( "EVP_PKEY_keygen" );
    }

    BIO *bio_public = NULL, *bio_private = NULL;

    bio_public = BIO_new( BIO_s_mem( ) );
    if( 1 != PEM_write_bio_PUBKEY( bio_public, pkey ) )
    {
      throw std::runtime_error( "PEM_write_bio_RSAPublicKey" );
    }

    bio_private = BIO_new( BIO_s_mem( ) );
    if( 1 != PEM_write_bio_PrivateKey( bio_private, pkey, NULL, NULL, 0, NULL, NULL ) )
    {
      throw std::runtime_error( "PEM_write_bio_RSAPrivateKey" );
    }

    auto private_len = BIO_pending( bio_private );
    std::string private_key( private_len + 1, 0 );
    BIO_read( bio_private, &private_key[ 0 ], private_len );

    auto public_len = BIO_pending( bio_public );
    std::string public_key( public_len + 1, 0 );
    BIO_read( bio_public, &public_key[ 0 ], public_len );

    debug("DH GEN DONE %s \n %s !\n", private_key.c_str(), public_key.c_str());

    BIO_free_all( bio_private );
    BIO_free_all( bio_public );
    EVP_PKEY_free( pkey );
    EVP_PKEY_free( params );
    EVP_PKEY_CTX_free( pctx );
    EVP_PKEY_CTX_free( kctx );

    return { private_key, public_key };
  }

  ustring DH::derive_secret( const string& my_privkey, const string& pubkey )
  {
    EVP_PKEY_CTX *ctx;
    // unsigned char *skey;
    size_t skeylen;
    EVP_PKEY *pkey, *peerkey;
    /* NB: assumes pkey, peerkey have been already set up */

    BIO* bio = BIO_new( BIO_s_mem( ) );
    int bio_len = BIO_write(bio, my_privkey.data(), my_privkey.size());
    pkey = PEM_read_bio_PrivateKey(bio, NULL, NULL, NULL );

    BIO* bio_p = BIO_new( BIO_s_mem( ) );
    int bio_p_len = BIO_write(bio_p, pubkey.data( ), pubkey.size( ) );
    peerkey = PEM_read_bio_PUBKEY( bio_p, NULL, NULL, NULL );

    ctx = EVP_PKEY_CTX_new(pkey, NULL);
    if (!ctx)
    {
      throw std::runtime_error( "EVP_PKEY_CTX_new" );
    }
    if (EVP_PKEY_derive_init(ctx) <= 0)
    {
      throw std::runtime_error( "EVP_PKEY_derive_init" );
    }
    if (EVP_PKEY_derive_set_peer(ctx, peerkey) <= 0)
    {
      throw std::runtime_error( "EVP_PKEY_derive_set_peer" );
    }

    /* Determine buffer length */
    if (EVP_PKEY_derive(ctx, NULL, &skeylen) <= 0)
    {
      throw std::runtime_error( "EVP_PKEY_derive" );
    }

    ustring skey(skeylen, 0 );


    if (EVP_PKEY_derive(ctx, &skey[0], &skeylen) <= 0)
    {
      throw std::runtime_error( "EVP_PKEY_derive" );
    }

    BIO_free_all( bio );
    BIO_free_all( bio_p );
    EVP_PKEY_free( pkey );
    EVP_PKEY_free( peerkey );
    EVP_PKEY_CTX_free( ctx );


    /* Shared secret is skey bytes written to buffer skey */
    // debug("SHARED: %s\n", skey.c_str());

    return skey;
  }
}
