
#include "rsa.h"

#include <openssl/rsa.h>
#include <openssl/pem.h>
#include <openssl/evp.h>

#include <stdexcept>
#include <algorithm>

#include "debug.h"


namespace ock
{
  std::tuple< std::string, std::string > Rsa::create_key_pair( int bits )
  {
    int             ret = 0;
    RSA             *r = NULL;
    BIGNUM          *bne = NULL;
    BIO             *bio_public = NULL, *bio_private = NULL;

    // int             bits = 3072;
    unsigned long   e = RSA_F4;

    // 1. generate rsa key
    bne = BN_new( );
    if( 1 != BN_set_word( bne, e ) )
    {
      throw std::runtime_error( "BN_set_word" );
    }

    r = RSA_new( );
    if( 1 != RSA_generate_key_ex (r, bits, bne, NULL ) )
    {
      throw std::runtime_error( "RSA_generate_key_ex" );
    }

    // 2. save public key
    bio_public = BIO_new( BIO_s_mem( ) );
    if( 1 != PEM_write_bio_RSAPublicKey( bio_public, r ) )
    {
      throw std::runtime_error( "PEM_write_bio_RSAPublicKey" );
    }

    // 3. save private key
    bio_private = BIO_new( BIO_s_mem( ) );
    if( 1 != PEM_write_bio_RSAPrivateKey( bio_private, r, NULL, NULL, 0, NULL, NULL ) )
    {
      throw std::runtime_error( "PEM_write_bio_RSAPrivateKey" );
    }

    // 4. extract to string
    auto private_len = BIO_pending( bio_private );
    std::string private_key( private_len + 1, 0 );
    BIO_read( bio_private, &private_key[ 0 ], private_len );

    auto public_len = BIO_pending( bio_public );
    std::string public_key( public_len + 1, 0 );
    BIO_read( bio_public, &public_key[ 0 ], public_len );

    // 5. free
    BIO_free_all( bio_public );
    BIO_free_all( bio_private );
    RSA_free( r );
    BN_free( bne );

    // 6. return key pair
    return { private_key, public_key };
  }

  ustring RsaOaep::encrypt( const string& public_key, const ustring& plaintext )
  {
    // 1. Read public key
    BIO* bio = BIO_new( BIO_s_mem( ) );
    int len = BIO_write( bio, public_key.data( ), public_key.size( ) );
    RSA* keypair = PEM_read_bio_RSAPublicKey( bio, NULL, NULL, NULL );

    // 2. Encrypt
    ustring encrypt( RSA_size( keypair ), 0 );
    int encrypt_len = RSA_public_encrypt(plaintext.size( ), &plaintext[ 0 ], &encrypt[ 0], keypair, RSA_PKCS1_OAEP_PADDING );
    if( encrypt_len == -1) {
       throw std::runtime_error( "RSA-OAEP encryption error" );
    }

    // 3. Free
    BIO_free_all(bio);
    RSA_free(keypair);

    // 4. Return
    return encrypt;
  }


  ustring RsaOaep::decrypt( const string& private_key, const ustring& encrypt )
  {
    // 1. Read private key
    BIO* bio = BIO_new( BIO_s_mem( ) );
    int len = BIO_write( bio, private_key.data( ), private_key.size( ) );
    RSA* keypair = PEM_read_bio_RSAPrivateKey( bio, NULL, NULL, NULL );

    // 2. Decrypt
    ustring decrypt( RSA_size( keypair ), 0);
    int decrypt_len = RSA_private_decrypt(encrypt.size( ), &encrypt[ 0 ], &decrypt[ 0 ], keypair, RSA_PKCS1_OAEP_PADDING );
    if( decrypt_len == -1 ) {
      throw std::runtime_error( "RSA-OAEP decryption error" );
    }

    // 3. Free
    BIO_free_all( bio );
    RSA_free( keypair );

    // 4. Adjust plaintex size
    decrypt.resize( decrypt_len );

    // 5. Return
    return decrypt;
  }


  ustring RsaEvp::encrypt( const string& public_key, const ustring& plaintext )
  {
    BIO* bio = BIO_new( BIO_s_mem( ) );
    int bio_len = BIO_write(bio, public_key.data( ), public_key.size( ) );
    RSA* pubkey = PEM_read_bio_RSAPublicKey( bio, NULL, NULL, NULL );
    EVP_PKEY* key = EVP_PKEY_new( );
    EVP_PKEY_set1_RSA( key, pubkey );

    ustring ek( EVP_PKEY_size( key ), 0);
    ustring iv( EVP_MAX_IV_LENGTH, 0);
    ustring ciphertext( plaintext.size( ) + EVP_MAX_IV_LENGTH, 0);

    EVP_CIPHER_CTX *ctx;
    int ciphertext_len;
    int len;

    /* Create and initialise the context */
    if(!(ctx = EVP_CIPHER_CTX_new()))
    {
      throw std::runtime_error( "EVP_CIPHER_CTX_new" );
    }

    /* Initialise the envelope seal operation. This operation generates
     * a key for the provided cipher, and then encrypts that key a number
     * of times (one for each public key provided in the pub_key array). In
     * this example the array size is just one. This operation also
     * generates an IV and places it in iv. */
    // auto ek_ptr = (unsigned char*)ek.data();
    uint8_t* ek_ptr = &ek[0];
    auto ek_size = (int)ek.size();
    if(1 != EVP_SealInit(ctx, EVP_aes_256_cbc(), &ek_ptr, &ek_size, &iv[0], &key, 1))
    {
      throw std::runtime_error( "EVP_SealInit" );
    }

    debug("EVP_SealInitEVP_SealInit \n");

    /* Provide the message to be encrypted, and obtain the encrypted output.
     * EVP_SealUpdate can be called multiple times if necessary
     */
    if(1 != EVP_SealUpdate(ctx, &ciphertext[0], &len, plaintext.data(), plaintext.size()))
    {
      throw std::runtime_error( "EVP_SealUpdate" );
    }
    ciphertext_len = len;

    debug("EVP_SealUpdate \n");

    /* Finalise the encryption. Further ciphertext bytes may be written at
     * this stage.
     */
    if(1 != EVP_SealFinal(ctx, &ciphertext[0] + len, &len))
    {
      throw std::runtime_error( "EVP_SealFinal" );
    }
    ciphertext_len += len;

    debug("EVP_SealFinal \n");

    /* Clean up */
    EVP_CIPHER_CTX_free(ctx);

    /* Return */
    ciphertext.resize(ciphertext_len);
    return ek + iv + ciphertext;
  }

  ustring RsaEvp::decrypt( const string& private_key, const ustring& ciphertext )
  {
    BIO* bio = BIO_new( BIO_s_mem( ) );
    int bio_len = BIO_write(bio, private_key.data(), private_key.size());
    RSA* privkey = PEM_read_bio_RSAPrivateKey( bio, NULL, NULL, NULL );
    EVP_PKEY* key = EVP_PKEY_new ();
    EVP_PKEY_set1_RSA(key, privkey);


    EVP_CIPHER_CTX *ctx;
    int len;
    int plaintext_len;

    ustring plaintext(ciphertext.size() + EVP_MAX_IV_LENGTH, 0);
    auto ek = ciphertext.substr(0, EVP_PKEY_size(key));
    auto iv = ciphertext.substr(EVP_PKEY_size(key), EVP_PKEY_size(key) + EVP_MAX_IV_LENGTH );
    auto cipher = ciphertext.substr(EVP_PKEY_size(key) + EVP_MAX_IV_LENGTH);


    /* Create and initialise the context */
    if(!(ctx = EVP_CIPHER_CTX_new()))
    {
      throw std::runtime_error("EVP_CIPHER_CTX_new");
    }

    /* Initialise the decryption operation. The asymmetric private key is
     * provided and priv_key, whilst the encrypted session key is held in
     * encrypted_key */
    if(1 != EVP_OpenInit(ctx, EVP_aes_256_cbc(), &ek[0], ek.size(), &iv[0], key))
    {
      throw std::runtime_error("EVP_OpenInit");
    }

    /* Provide the message to be decrypted, and obtain the plaintext output.
     * EVP_OpenUpdate can be called multiple times if necessary
     */
    if(1 != EVP_OpenUpdate(ctx, &plaintext[0], &len, &cipher[0], cipher.size()))
    {
      throw std::runtime_error("EVP_OpenUpdate");
    }
    plaintext_len = len;

    /* Finalise the decryption. Further plaintext bytes may be written at
     * this stage.
     */
    if(1 != EVP_OpenFinal(ctx, &plaintext[0] + len, &len))
    {
      throw std::runtime_error("EVP_OpenFinal");
    }
    plaintext_len += len;

    /* Clean up */
    EVP_CIPHER_CTX_free(ctx);

    /* Return */
    plaintext.resize(plaintext_len);
    return plaintext;
  }

  ustring RsaSig::sign( const string& private_key, const ustring& message )
  {
    BIO* bio = BIO_new( BIO_s_mem( ) );
    int bio_len = BIO_write(bio, private_key.data(), private_key.size());
    RSA* privkey = PEM_read_bio_RSAPrivateKey( bio, NULL, NULL, NULL );
    // EVP_PKEY* key = EVP_PKEY_new ();
    // EVP_PKEY_set1_RSA(key, privkey);

    EVP_MD_CTX* ctx = EVP_MD_CTX_create();
    size_t sign_len;
    int len;


    EVP_PKEY* priKey  = EVP_PKEY_new();
    EVP_PKEY_assign_RSA(priKey, privkey);

    if (EVP_DigestSignInit(ctx,NULL, EVP_sha256(), NULL,priKey)<=0) {
        throw std::runtime_error("EVP_DigestSignInit");
    }

    if (EVP_DigestSignUpdate(ctx, &message[0], message.size()) <= 0) {
        throw std::runtime_error("EVP_DigestSignUpdate");
    }
    if (EVP_DigestSignFinal(ctx, NULL, &sign_len) <=0) {
        throw std::runtime_error("EVP_DigestSignFinal");
    }
    // *EncMsg = (unsigned char*)malloc(*MsgLenEnc);



    ustring enc_msg(sign_len, 0);
    if (EVP_DigestSignFinal(ctx, &enc_msg[0], &sign_len) <= 0) {
        throw std::runtime_error("EVP_DigestSignFinal");
    }
    EVP_MD_CTX_destroy(ctx);

    return enc_msg;
  }

  bool RsaSig::verify( const string& public_key, const ustring& msg, const ustring& signature )
  {
    BIO* bio = BIO_new( BIO_s_mem( ) );
    int bio_len = BIO_write(bio, public_key.data(), public_key.size( ));
    RSA* privkey = PEM_read_bio_RSAPublicKey( bio, NULL, NULL, NULL );


    EVP_PKEY* pubKey  = EVP_PKEY_new();
    EVP_PKEY_assign_RSA(pubKey, privkey);
    EVP_MD_CTX* m_RSAVerifyCtx = EVP_MD_CTX_create();
    if (EVP_DigestVerifyInit(m_RSAVerifyCtx,NULL, EVP_sha256(),NULL,pubKey)<=0) {
      throw std::runtime_error("EVP_DigestVerifyInit");
    }
    if (EVP_DigestVerifyUpdate(m_RSAVerifyCtx, &msg[0], msg.size()) <= 0) {
      throw std::runtime_error("EVP_DigestVerifyUpdate");
    }

    int AuthStatus = EVP_DigestVerifyFinal(m_RSAVerifyCtx, &signature[0], signature.size());

    if (AuthStatus==1) {
      EVP_MD_CTX_destroy(m_RSAVerifyCtx);
      return true;
    } else if(AuthStatus==0){
      EVP_MD_CTX_destroy(m_RSAVerifyCtx);

      //throw std::runtime_error("Signature does not match the message");

      return false;
    } else{
      EVP_MD_CTX_destroy(m_RSAVerifyCtx);
      throw std::runtime_error("Verify Error");
      return false;
    }

  }


}
