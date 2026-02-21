// include/utilities/string_utils.h
#ifndef STRING_UTILS_H
#define STRING_UTILS_H
#pragma once

#include <string>
#include <algorithm>
#include <cctype>

/**
 * @brief Remove leading and trailing whitespace characters.
 *
 * @param text Input text to trim.
 * @return Trimmed copy of @p text.
 */
std::string trim(const std::string& text);

/**
 * @brief Convert all characters in a string to lowercase.
 *
 * @param text String to transform (copied by value).
 * @return Lowercase version of @p text.
 */
std::string to_lower(std::string text);

#endif //STRING_UTILS_H
