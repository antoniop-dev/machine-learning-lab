#ifndef VALIDATE_UTILS_H
#define VALIDATE_UTILS_H
#pragma once

#include <cstddef>
#include <ctime>
#include <string>

/**
 * @brief Check that a name contains only alphabetic characters and is long enough.
 */
bool validate_name(const std::string& value);

/**
 * @brief Validate a date of birth string.
 */
bool validate_d_o_b(const std::string& value);

/**
 * @brief Validate a generic date string.
 */
bool validate_date(const std::string& value);

/**
 * @brief Validate an Italian fiscal code (Codice Fiscale).
 */
bool validate_fiscal_code(const std::string& value);

/**
 * @brief Ensure a phone number meets minimum digit requirements.
 */
bool validate_phone_number(const std::string& value);

/**
 * @brief Check email address syntax.
 */
bool validate_email(const std::string& value);

/**
 * @brief Validate that a time value is not the platform sentinel for errors.
 */
bool validate_time_t(std::time_t value);

/**
 * @brief Validate policy numbers or similar alphanumeric identifiers.
 */
bool validate_policy_number(const std::string& value);

/**
 * @brief Verify that an address length falls within the allowed bounds.
 */
bool validate_address(const std::string& value,
                      std::size_t min_length = 5,
                      std::size_t max_length = 160);

/**
 * @brief Check that an identifier contains numeric characters only.
 */
bool validate_numeric_identifier(const std::string& value);

/**
 * @brief Validate the size of generic text fields.
 */
bool validate_text_field(const std::string& value,
                         std::size_t min_length = 3,
                         std::size_t max_length = 100);

/**
 * @brief Ensure positive monetary amounts fall in the allowed range.
 */
bool validate_positive_amount(double value,
                              double min_value = 0.0,
                              double max_value = 1'000'000'000.0);

/**
 * @brief Validate datetime strings meant to represent future events.
 */
bool validate_future_datetime(const std::string& value);

/**
 * @brief Validate optional free-text content with only an upper bound.
 */
bool validate_optional_text(const std::string& value,
                            std::size_t max_length = 160);

/**
 * @brief Validate yes/no answers to ensure they match the expected tokens.
 */
bool validate_yes_no_response(const std::string& value);

/**
 * @brief Check that a time range is chronologically consistent.
 */
bool validate_time_range(std::time_t start,
                         std::time_t end,
                         bool allow_open_end = true);

#endif //VALIDATE_UTILS_H
