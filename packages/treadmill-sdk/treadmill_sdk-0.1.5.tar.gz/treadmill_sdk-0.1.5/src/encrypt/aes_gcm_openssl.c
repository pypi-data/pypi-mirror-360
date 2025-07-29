// FreeRTOS使用mbedtls代替openssl
// 本文件用于测试AES-GCM加密解密，使用openssl库
#include <openssl/evp.h>
#include <openssl/kdf.h>
#include <openssl/core_names.h>
#include <stdio.h>
#include <string.h>

#define NONCE_LEN 12
#define KEY_BYTE_SIZE 16
#define ENC_KEY_LENGTH 16
#define TAG_LEN 16

static const char *KEY = "BRNC-Treadmill-1";
static const unsigned char NONCE_BYTES[NONCE_LEN] = {
    157, 63, 130, 104, 60, 1, 102, 18, 185, 25, 180, 65};
const unsigned char ENC_KEY_INFO[] = "BRNROBOTCS.Treadmill.EncKey.v1";

typedef enum
{
  SUCCESS = 0,
  ERR_INVALID_INPUT,
  ERR_HKDF_FAILED,
  ERR_ENCRYPTION_FAILED,
  ERR_DECRYPTION_FAILED
} ErrorCode;

// Encryption function (mostly correct in original)
ErrorCode encrypt_with_key_nonce(
    const char *key,
    const unsigned char *nonce_bytes,
    const unsigned char *plain_bytes,
    size_t plain_len,
    unsigned char **out_bytes,
    size_t *out_len)
{
  // Input validation
  size_t key_len = strlen(key);
  if (key_len != KEY_BYTE_SIZE)
  {
    fprintf(stderr, "Key length must be %d bytes, got %zu\n", KEY_BYTE_SIZE, key_len);
    return ERR_INVALID_INPUT;
  }
  if (!plain_bytes || !out_bytes || !out_len || !nonce_bytes)
  {
    fprintf(stderr, "Invalid input parameters\n");
    return ERR_INVALID_INPUT;
  }

  // HKDF key derivation (unchanged from original)
  EVP_KDF *kdf = EVP_KDF_fetch(NULL, "HKDF", NULL);
  if (!kdf)
  {
    fprintf(stderr, "Failed to fetch HKDF\n");
    return ERR_HKDF_FAILED;
  }

  EVP_KDF_CTX *kctx = EVP_KDF_CTX_new(kdf);
  if (!kctx)
  {
    EVP_KDF_free(kdf);
    fprintf(stderr, "Failed to create KDF context\n");
    return ERR_HKDF_FAILED;
  }

  unsigned char enc_key_bytes[ENC_KEY_LENGTH];
  OSSL_PARAM params[5];
  params[0] = OSSL_PARAM_construct_utf8_string("digest", "sha256", 0);
  params[1] = OSSL_PARAM_construct_octet_string("key", (void *)key, key_len);
  params[2] = OSSL_PARAM_construct_octet_string("salt", NULL, 0);
  params[3] = OSSL_PARAM_construct_octet_string("info", (void *)ENC_KEY_INFO, sizeof(ENC_KEY_INFO) - 1);
  params[4] = OSSL_PARAM_construct_end();

  if (EVP_KDF_derive(kctx, enc_key_bytes, ENC_KEY_LENGTH, params) <= 0)
  {
    EVP_KDF_CTX_free(kctx);
    EVP_KDF_free(kdf);
    return ERR_HKDF_FAILED;
  }
  EVP_KDF_CTX_free(kctx);
  EVP_KDF_free(kdf);

  // AES-GCM encryption
  EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
  if (!ctx)
  {
    fprintf(stderr, "Failed to create cipher context\n");
    return ERR_ENCRYPTION_FAILED;
  }

  if (1 != EVP_EncryptInit_ex(ctx, EVP_aes_128_gcm(), NULL, enc_key_bytes, nonce_bytes))
  {
    EVP_CIPHER_CTX_free(ctx);
    return ERR_ENCRYPTION_FAILED;
  }

  *out_len = NONCE_LEN + plain_len + TAG_LEN;
  *out_bytes = (unsigned char *)malloc(*out_len);
  if (!*out_bytes)
  {
    EVP_CIPHER_CTX_free(ctx);
    return ERR_ENCRYPTION_FAILED;
  }

  memcpy(*out_bytes, nonce_bytes, NONCE_LEN);
  int len;
  if (1 != EVP_EncryptUpdate(ctx, *out_bytes + NONCE_LEN, &len, plain_bytes, plain_len))
  {
    free(*out_bytes);
    EVP_CIPHER_CTX_free(ctx);
    return ERR_ENCRYPTION_FAILED;
  }

  int final_len;
  if (1 != EVP_EncryptFinal_ex(ctx, *out_bytes + NONCE_LEN + len, &final_len))
  {
    free(*out_bytes);
    EVP_CIPHER_CTX_free(ctx);
    return ERR_ENCRYPTION_FAILED;
  }

  unsigned char tag[TAG_LEN];
  if (1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, TAG_LEN, tag))
  {
    free(*out_bytes);
    EVP_CIPHER_CTX_free(ctx);
    return ERR_ENCRYPTION_FAILED;
  }

  memcpy(*out_bytes + NONCE_LEN + plain_len, tag, TAG_LEN);
  EVP_CIPHER_CTX_free(ctx);
  return SUCCESS;
}

// Fixed and completed decryption function
ErrorCode decrypt_key_nonce(
    const char *key,
    const unsigned char *nonce_bytes,
    const unsigned char *cipher_bytes,
    size_t cipher_len,
    unsigned char **out_bytes,
    size_t *out_len)
{
  // Input validation
  size_t key_len = strlen(key);
  if (key_len != KEY_BYTE_SIZE)
  {
    fprintf(stderr, "Key length must be %d bytes, got %zu\n", KEY_BYTE_SIZE, key_len);
    return ERR_INVALID_INPUT;
  }
  if (!cipher_bytes || !out_bytes || !out_len || !nonce_bytes || cipher_len <= (NONCE_LEN + TAG_LEN))
  {
    fprintf(stderr, "Invalid input parameters\n");
    return ERR_INVALID_INPUT;
  }

  // HKDF key derivation (same as encryption)
  EVP_KDF *kdf = EVP_KDF_fetch(NULL, "HKDF", NULL);
  if (!kdf)
  {
    fprintf(stderr, "Failed to fetch HKDF\n");
    return ERR_HKDF_FAILED;
  }

  EVP_KDF_CTX *kctx = EVP_KDF_CTX_new(kdf);
  if (!kctx)
  {
    EVP_KDF_free(kdf);
    fprintf(stderr, "Failed to create KDF context\n");
    return ERR_HKDF_FAILED;
  }

  unsigned char enc_key_bytes[ENC_KEY_LENGTH];
  OSSL_PARAM params[5];
  params[0] = OSSL_PARAM_construct_utf8_string("digest", "sha256", 0);
  params[1] = OSSL_PARAM_construct_octet_string("key", (void *)key, key_len);
  params[2] = OSSL_PARAM_construct_octet_string("salt", NULL, 0);
  params[3] = OSSL_PARAM_construct_octet_string("info", (void *)ENC_KEY_INFO, sizeof(ENC_KEY_INFO) - 1);
  params[4] = OSSL_PARAM_construct_end();

  if (EVP_KDF_derive(kctx, enc_key_bytes, ENC_KEY_LENGTH, params) <= 0)
  {
    EVP_KDF_CTX_free(kctx);
    EVP_KDF_free(kdf);
    return ERR_HKDF_FAILED;
  }
  EVP_KDF_CTX_free(kctx);
  EVP_KDF_free(kdf);

  // AES-GCM decryption
  EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
  if (!ctx)
  {
    fprintf(stderr, "Failed to create cipher context\n");
    return ERR_DECRYPTION_FAILED;
  }

  if (1 != EVP_DecryptInit_ex(ctx, EVP_aes_128_gcm(), NULL, enc_key_bytes, nonce_bytes))
  {
    EVP_CIPHER_CTX_free(ctx);
    return ERR_DECRYPTION_FAILED;
  }

  // Calculate plaintext length (total length - nonce - tag)
  *out_len = cipher_len - NONCE_LEN - TAG_LEN;
  *out_bytes = (unsigned char *)malloc(*out_len);
  if (!*out_bytes)
  {
    EVP_CIPHER_CTX_free(ctx);
    return ERR_DECRYPTION_FAILED;
  }

  // Set the tag for verification
  unsigned char *tag = (unsigned char *)(cipher_bytes + cipher_len - TAG_LEN);
  if (1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, TAG_LEN, tag))
  {
    free(*out_bytes);
    EVP_CIPHER_CTX_free(ctx);
    return ERR_DECRYPTION_FAILED;
  }

  // Decrypt the actual ciphertext
  int len;
  if (1 != EVP_DecryptUpdate(ctx, *out_bytes, &len, cipher_bytes + NONCE_LEN, *out_len))
  {
    free(*out_bytes);
    EVP_CIPHER_CTX_free(ctx);
    return ERR_DECRYPTION_FAILED;
  }

  int final_len;
  if (1 != EVP_DecryptFinal_ex(ctx, *out_bytes + len, &final_len))
  {
    free(*out_bytes);
    EVP_CIPHER_CTX_free(ctx);
    return ERR_DECRYPTION_FAILED;
  }

  *out_len = len + final_len;
  EVP_CIPHER_CTX_free(ctx);
  return SUCCESS;
}

int main()
{
  uint8_t plain_bytes[] = "Hello, Device!";
  size_t plain_len = strlen((char *)plain_bytes);

  unsigned char *encrypted = NULL;
  size_t encrypted_len = 0;

  // Test encryption
  ErrorCode enc_result = encrypt_with_key_nonce(KEY, NONCE_BYTES, plain_bytes, plain_len, &encrypted, &encrypted_len);
  if (enc_result == SUCCESS)
  {
    printf("Encryption successful, length: %zu\n", encrypted_len);
    for (size_t i = 0; i < encrypted_len; i++)
    {
      printf("%02x", encrypted[i]);
    }
    printf("\n");
  }
  else
  {
    printf("Encryption failed: %d\n", enc_result);
    return 1;
  }

  // Test decryption
  unsigned char *decrypted = NULL;
  size_t decrypted_len = 0;
  ErrorCode dec_result = decrypt_key_nonce(KEY, NONCE_BYTES, encrypted, encrypted_len, &decrypted, &decrypted_len);
  if (dec_result == SUCCESS)
  {
    printf("Decryption successful, length: %zu\n", decrypted_len);
    printf("Decrypted text: %.*s\n", (int)decrypted_len, decrypted);
  }
  else
  {
    printf("Decryption failed: %d\n", dec_result);
  }

  // Cleanup
  if (encrypted)
    free(encrypted);
  if (decrypted)
    free(decrypted);

  return 0;
}
