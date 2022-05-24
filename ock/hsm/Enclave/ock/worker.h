
#ifndef __OCK_WORKER__
#define __OCK_WORKER__

#include <stdarg.h>
#include <string>
#include <memory>
#include <map>
#include <tuple>
#include <vector>

#include "types.h"
#include "kdf.h"
#include "policies.h"
#include "aes.h"




namespace ock
{
  class Worker
  {
  private:
    std::unique_ptr< KDF > kdf;
    std::unique_ptr< PoliciesManager > policies;

    // TODO Permissions
    // TODO Encryptors / Decryptors

    std::map< string, string > aliases;
    std::map< string, string > rsa_private;
    std::map< string, string > rsa_public;


  public:
    Worker();

    //TODO: this method MUST be changed -- what should be passed is JWE token with data
    string import_secrets(
            const     secret_t secret_1,
            const     secret_t secret_2
      );

    std::tuple< ock::Key, ock::Token > create_key(
      const string& access_token,
      const KeyFamily& key_family,
      const char* ip
    );

      std::tuple< ock::Key, ock::Token > import_key(
              const string& access_token,
              const KeyFamily& key_family,
              const string& private_key,
              const string& public_key,
              const char* ip
      );

    std::tuple< Key, Token, AliasPolicy > create_alias(
      const Key& key_id,
      const Token& Keyoken,
      const string& alias,
      const AliasPolicy& policy,
      const char* ip
    );

    bool verify_action_access(
      const Key& key,
      const Token& token,
      const AliasAction& action
    );

    ustring encrypt(
      const Key& key,
      const Token& alias_token,
      const ustring& plaintext,
      const EncryptionMode& mode,
      const char* ip
    );

    ustring decrypt(
      const Key& key,
      const Token& alias_token,
      const ustring& ciphertext_blob,
      const EncryptionMode& mode,
      const char* ip
    );

    ustring sign(
      const Key& key,
      const Token& alias_token,
      const ustring& msg,
      const EncryptionMode& mode,
      const char* ip
    );


    bool verify(
      const Key& key,
      const Token& alias_token,
      const ustring& msg,
      const ustring& signature,
      const EncryptionMode& mode,
      const char* ip
    );


    string digest(
      const Key& key,
      const Token& alias_token,
      const string& msg,
      const EncryptionMode& mode,
      const char* ip
    );

    string shared_secret(
      const Key& key,
      const Token& alias_token,
      const string& public_key,
      const char* ip
    );

    string get_public_key(
      const Key& key,
      const Token& alias_token,
      const char* ip
    );

    ustring random(
      const Key& key,
      const Token& alias_token,
      const int length,
      const char* ip
    );

    string get_epid(
            const char* ip
            );

  };
}

#endif
