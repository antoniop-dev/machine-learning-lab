#ifndef PARSE_UTILS_H
#define PARSE_UTILS_H
#pragma once

#include <string>


/**
 * @brief Parse a textual date in the expected DD-MM-YYYY format.
 *
 * @param text Source string containing the date.
 * @return std::tm structure populated with the parsed date.
 * @throws std::runtime_error If the format or values are invalid.
 */
std::tm parse_date(const std::string& text);

/**
 * @brief Parse a textual timestamp with date and time information.
 *
 * @param text Source string containing the timestamp.
 * @return std::time_t representing the parsed local time.
 * @throws std::runtime_error If parsing fails.
 */
std::time_t parse_datetime(const std::string& text);

/**
 * @brief Convert a string field to an integer enforcing a non-empty input.
 *
 * @param text Token to convert.
 * @param field_name Human-readable field label used in error messages.
 * @return Parsed integer value.
 * @throws std::runtime_error If @p text is empty or cannot be converted.
 */
int parse_int_field(const std::string& text, const char* field_name);

/**
 * @brief Parse text into the requested numeric type with validation.
 *
 * @tparam T Supported numeric type (int, std::time_t, double, long long).
 * @param text Token to convert.
 * @param field_name Label used to enrich error messages.
 * @return Parsed value of type @p T.
 * @throws std::runtime_error On empty input, unsupported type, or conversion errors.
 */
template <typename T>
T parse_numeric(const std::string& text, const char* field_name) {
    if (text.empty()) {
        throw std::runtime_error(std::string("Missing numeric value for ") + field_name);
    }
    std::size_t consumed = 0;
    T value{};
    try {
        if constexpr (std::is_same_v<T, int>) {
            value = static_cast<int>(std::stoi(text, &consumed));
        } else if constexpr (std::is_same_v<T, std::time_t>) {
            value = static_cast<std::time_t>(std::stoll(text, &consumed));
        } else if constexpr (std::is_same_v<T, double>) {
            value = std::stod(text, &consumed);
        } else if constexpr (std::is_same_v<T, long long>) {
            value = std::stoll(text, &consumed);
        } else {
            static_assert(!sizeof(T), "Unsupported numeric parse type");
        }
    } catch (const std::exception& ex) {
        throw std::runtime_error(std::string("Cannot parse value '") + text + "' for " + field_name +
                                 ": " + ex.what());
    }
    if (consumed != text.size()) {
        throw std::runtime_error(std::string("Unexpected characters in numeric field ") + field_name);
    }
    return value;
}


#endif //PARSE_UTILS_H
