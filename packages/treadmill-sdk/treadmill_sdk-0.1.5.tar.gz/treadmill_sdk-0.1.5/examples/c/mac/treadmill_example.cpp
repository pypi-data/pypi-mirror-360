#include <stdio.h>
#include <string.h> // 包含 memcmp
#include "treadmill-sdk.h"

int main(int argc, char const *argv[])
{
    // initialize_logging(LogLevel::DEBUG);
    initialize_logging(LogLevel::LEVEL_INFO);

    const char *plaintext = "Hello, Device!";
    const char *user_id = "550e8400-e29b-41d4-a716-446655440000";
    const char *sn_code = "SN123456";
    printf("plaintext: len: %lu, data: %s\n", strlen(plaintext), plaintext);
    for (size_t i = 0; i < strlen(plaintext); i++)
    {
        printf("%02x", plaintext[i]);
    }
    printf("\n");

    size_t enc_out_len;
    uint8_t *encrypted = tml_encrypt((const uint8_t *)plaintext, strlen(plaintext), user_id, sn_code, &enc_out_len);
    printf("Encrypted: len: %lu, data: ", enc_out_len);
    for (size_t i = 0; i < enc_out_len; i++)
    {
        printf("%02x", encrypted[i]);
    }
    printf("\n");

    size_t dec_out_len;
    uint8_t *decrypted = tml_decrypt(encrypted, enc_out_len, user_id, sn_code, &dec_out_len);
    printf("Decrypted: len: %lu, data: ", dec_out_len);
    for (size_t i = 0; i < dec_out_len; i++)
    {
        printf("%02x", decrypted[i]);
    }
    printf("\n");

    // 比较 uint8_t 内容
    if (dec_out_len == strlen(plaintext) &&
        memcmp(decrypted, plaintext, dec_out_len) == 0)
    {
        printf("Decryption successful: plaintext restored correctly\n");
    }
    else
    {
        printf("Decryption failed: plaintext not restored\n");
        printf("Expected len: %lu, got: %lu\n", strlen(plaintext), dec_out_len);
    }

    free_encrypted_or_decrypted(encrypted, enc_out_len);
    free_encrypted_or_decrypted(decrypted, dec_out_len);

    return 0;
}
