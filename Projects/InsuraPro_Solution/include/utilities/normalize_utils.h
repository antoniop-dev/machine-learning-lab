#ifndef NORMALIZE_UTILS_H
#define NORMALIZE_UTILS_H
#pragma once

#include <string>

/**
 * @brief Return a trimmed copy of the provided string.
 *
 * @param value Text to copy and trim.
 * @return Trimmed copy of @p value.
 */
std::string trim_copy(const std::string& value);

/**
 * @brief Trim leading and trailing whitespace characters in place.
 *
 * @param value Text to modify.
 */
void trim_in_place(std::string& value);

/**
 * @brief Normalize whitespace by collapsing consecutive spaces.
 *
 * @param value Text to update.
 */
void normalize_whitespace(std::string& value);

/**
 * @brief Normalize a person's name (case, spacing).
 *
 * @param value Name to normalize.
 */
void normalize_name(std::string& value);

/**
 * @brief Normalize an address string.
 *
 * @param value Address to normalize.
 */
void normalize_address(std::string& value);

/**
 * @brief Sanitize a phone number by stripping separators.
 *
 * @param value Phone number to normalize.
 */
void normalize_phone(std::string& value);

/**
 * @brief Normalize an email address into canonical form.
 *
 * @param value Email to normalize.
 */
void normalize_email(std::string& value);

/**
 * @brief Normalize an identifier such as a policy or fiscal code.
 *
 * @param value Identifier to normalize.
 */
void normalize_policy_number(std::string& value);

/**
 * @brief Collapse internal whitespace to single spaces.
 *
 * @param value Text to update.
 */
void normalize_text_single_space(std::string& value);

/**
 * @brief Normalize yes/no answers to a canonical token.
 *
 * @param value Text to update.
 */
void normalize_yes_no(std::string& value);

#endif // NORMALIZE_UTILS_H
