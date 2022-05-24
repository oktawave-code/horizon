
#include "worker_wrapper.h"

#include "rsa.h"
#include "aes.h"

#include "debug.h"

namespace ock
{
    /*
    std::tuple< string, int> WorkerWrapper::init_secrets( const JsonReader& json, const char* ip)
    {
        //TODO: decode json inside the enclave! -- for now it is decoded in Flask
        auto k1 = json.get<string>("k1");
        auto k2 = json.get<string>("k2");
        string result = worker.import_secrets(k1, k2);
        auto res = JsonObjectBuilder().add_string("InitResult", result).build();
        return {res, 201};

    }*/

  std::tuple< string, int > WorkerWrapper::create_key( const JsonReader& json, const char* ip )
  {
    auto okta_token = json.get< string >( "OktaToken" );
    auto key_family = json.get< KeyFamily >( "Type", "AES" );

    Key key;
    Token token;
    std::tie( key, token ) = worker.create_key( okta_token, key_family, ip );

    auto res = JsonObjectBuilder().add_string( "KeyId", key ).add_string( "Token",  token ).build( );
    return { res, 201 };
  }

    std::tuple< string, int > WorkerWrapper::import_key( const JsonReader& json, const char* ip )
    {
        auto okta_token = json.get< string >( "OktaToken" );
        auto key_family = json.get< KeyFamily >( "Type", "RSA" );
        auto private_key = json.get< string >("PrivateKey");
        auto public_key = json.get< string >("PublicKey");

        Key key;
        Token token;
        std::tie( key, token ) = worker.import_key( okta_token, key_family, private_key, public_key, ip );

        auto res = JsonObjectBuilder().add_string( "KeyId", key ).add_string( "Token",  token ).build( );
        return { res, 201 };
    }

  std::tuple< string, int > WorkerWrapper::create_alias( const JsonReader& json, const char* ip )
  {
    auto key = json.get< Key >( "KeyId" );
    auto token = json.get< Token >( "Token" );
    auto key_alias = json.get< string >( "KeyAlias" );
    auto policy = AliasPolicy( json, json.at_key( "Policies", json.root ) );

    std::tie( key, token, policy ) = worker.create_alias( key, token, key_alias, policy, ip );

    auto res = JsonObjectBuilder( ).add_string( "KeyId", key ).add_string( "Token", token ).add( "Policies", policy).build( );
    return { res, 200 };
  }

  std::tuple< string, int > WorkerWrapper::encrypt( const JsonReader& json, const char* ip )
  {
    auto key = json.get< Key >( "KeyId" );
    auto token = json.get< Token >( "Token" );
    auto plaintext = b64::decode( json.get< string >( "Plaintext" ) );
    // TODO: work with different modes of encryption
    auto mode = json.get< EncryptionMode >( "Mode", "AES-GCM" );

    auto ciphertext_blob = worker.encrypt( key, token, plaintext, mode, ip );

    auto res = JsonObjectBuilder( ).add_string( "KeyId", key ).add_string( "CiphertextBlob", ciphertext_blob ).build( );
    return { res, 200 };
  }

  std::tuple< string, int > WorkerWrapper::decrypt( const JsonReader& json, const char* ip )
  {
    auto key = json.get< Key >( "KeyId" );
    auto token = json.get< Token >( "Token" );
    auto ciphertext_blob = b64::decode( json.get< string >( "CiphertextBlob" ) );
    //TODO: work with different modes of decryption
    auto mode = json.get< EncryptionMode >( "Mode", "AES-GCM" );

    auto plaintext = worker.decrypt( key, token, ciphertext_blob, mode, ip );

    auto res = JsonObjectBuilder( ).add_string( "KeyId", key ).add_string( "Plaintext", plaintext ).build( );
    return { res, 200 };
  }

  std::tuple< string, int > WorkerWrapper::sign( const JsonReader& json, const char* ip )
  {
    auto key = json.get< Key >( "KeyId" );
    auto token = json.get< Token >( "Token" );
    auto msg = b64::decode( json.get< string >( "Message" ) );
    //auto msg = json.get< string >( "Message" );
    //auto msg = json.get<string>("Message");
    //TODO: work with different modes of signatures
    auto mode = json.get< EncryptionMode >( "Mode", "RSA-SHA256" );

    auto signature = worker.sign( key, token, msg, mode, ip );

    auto res = JsonObjectBuilder( ).add_string( "KeyId", key ).add_string( "Signature", signature ).build( );
    return { res, 200 };
  }

  std::tuple< string, int > WorkerWrapper::verify( const JsonReader& json, const char* ip )
  {
    auto key = json.get< Key >( "KeyId" );
    auto token = json.get< Token >( "Token" );
    auto msg = b64::decode( json.get< string >( "Message" ) );
    auto signature = b64::decode( json.get< string >( "Signature" ) );
    //TODO: work with different types of signatures
    auto mode = json.get< EncryptionMode >( "Mode", "RSA-SHA256" );

    auto result = worker.verify( key, token, msg, signature, mode, ip );
    //auto res = nul;
    //*
    auto res = JsonObjectBuilder().build();
    if (result == true) {
      res = JsonObjectBuilder().add_string("KeyId", key).add_string("Result", "OK").build();
    } else {
      res = JsonObjectBuilder().add_string("KeyId", key).add_string("Result", "False").add_string("x","y").build();
    }
     //*/
    //auto   res = JsonObjectBuilder().add_string("KeyId", key).add_string("Result", "OK").build();
    return { res, 200 };
  }

  std::tuple< string, int > WorkerWrapper::digest( const JsonReader& json, const char* ip )
  {
    auto key = json.get< Key >( "KeyId" );
    auto token = json.get< Token >( "Token" );
    auto msg = json.get< string >( "Message" );
    auto mode = json.get< EncryptionMode >( "Mode", "SHA-256" );
    // TODO salt from  input

    auto md = worker.digest( key, token, msg, mode, ip );

    auto res = JsonObjectBuilder( ).add_string( "KeyId", key ).add_string( "Digest", md ).build( );
    return { res, 200 };
  }

  std::tuple< string, int > WorkerWrapper::shared_secret( const JsonReader& json, const char* ip )
  {
    auto key = json.get< Key >( "KeyId" );
    auto token = json.get< Token >( "Token" );
    auto msg = json.get< string >( "PublicKey" );
    // auto mode = json.get< EncryptionMode >( "Mode", "SHA-256" );
    // TODO salt from  input

    auto md = worker.shared_secret( key, token, msg, ip );

    auto res = JsonObjectBuilder( ).add_string( "KeyId", key ).add_string( "Secret", md ).build( );
    return { res, 200 };
  }

  std::tuple< string, int > WorkerWrapper::get_public_key( const JsonReader& json, const char* ip )
  {
    auto key = json.get< Key >( "KeyId" );
    auto token = json.get< Token >( "Token" );
    // auto mode = json.get< EncryptionMode >( "Mode", "SHA-256" );
    // TODO salt from  input

    auto md = worker.get_public_key( key, token, ip );

    auto res = JsonObjectBuilder( ).add_string( "KeyId", key ).add_string( "PublicKey", md ).build( );
    return { res, 200 };
  }

  std::tuple< string, int > WorkerWrapper::random( const JsonReader& json, const char* ip )
  {
    auto key = json.get< Key >( "KeyId" );
    auto token = json.get< Token >( "Token" );
    auto length = json.get_int( "Length" );

    auto rnd = worker.random( key, token, length, ip );

    auto res = JsonObjectBuilder( ).add_string( "KeyId", key ).add_string( "Random", rnd ).build( );
    return { res, 200 };
  }

  std::tuple< string, int > WorkerWrapper::manage( const JsonReader& json, const char* ip )
  {
    auto key = json.get< Key >( "KeyId" );
    auto token = json.get< Token >( "Token" );
    auto msg = b64::decode( json.get< string >( "Message" ) );

    // TODO

    auto res = JsonObjectBuilder( ).add_string( "KeyId", key ).add_string( "Result", "OK" ).build( );
    return { res, 200 };
  }


  std::tuple< string, int > WorkerWrapper::error( const std::exception& re )
  {
    auto res = JsonObjectBuilder().add_string( "ErrorMessage", re.what( ) ).build( );
    return { res, 400 };
  }

  std::tuple< string, int > WorkerWrapper::get_epid( const JsonReader& json,  const char* ip )
  {
        //auto key = json.get< Key >( "KeyId" );
        //auto token = json.get< Token >( "Token" );
        //auto msg = b64::decode( json.get< string >( "Message" ) );

        // TODO
        string epid  = worker.get_epid(ip);
        auto res = JsonObjectBuilder( ).add_string( "EPID", epid ).add_string( "Result", "OK" ).build( );
        return { res, 200 };
  }
}
