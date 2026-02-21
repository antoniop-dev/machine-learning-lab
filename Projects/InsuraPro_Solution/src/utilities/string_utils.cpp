#include "utilities/string_utils.h"

std::string trim(const std::string& text) {
    auto begin = std::find_if_not(text.begin(), text.end(), [](unsigned char ch) { return std::isspace(ch); });
    auto end = std::find_if_not(text.rbegin(), text.rend(), [](unsigned char ch) { return std::isspace(ch); }).base();
    if (begin >= end) {
        return {};
    }
    return std::string(begin, end);
}

std::string to_lower(std::string text) {
    std::transform(text.begin(), text.end(), text.begin(), [](unsigned char ch) {
        return static_cast<char>(std::tolower(ch));
    });
    return text;
}