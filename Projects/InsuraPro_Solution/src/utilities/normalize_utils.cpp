#include "utilities/normalize_utils.h"

#include <algorithm>
#include <cctype>

std::string trim_copy(const std::string& value) {
    std::string result = value;
    trim_in_place(result);
    return result;
}

void trim_in_place(std::string& value) {
    auto not_space = [](unsigned char ch) { return !std::isspace(ch); };
    const auto begin = std::find_if(value.begin(), value.end(), not_space);
    if (begin == value.end()) {
        value.clear();
        return;
    }
    const auto end = std::find_if(value.rbegin(), value.rend(), not_space).base();
    value.assign(begin, end);
}

void normalize_whitespace(std::string& value) {
    trim_in_place(value);
    std::string normalized;
    normalized.reserve(value.size());
    bool previous_space = false;
    for (char ch : value) {
        if (std::isspace(static_cast<unsigned char>(ch))) {
            if (!previous_space) {
                normalized.push_back(' ');
                previous_space = true;
            }
        } else {
            normalized.push_back(ch);
            previous_space = false;
        }
    }
    value.swap(normalized);
}

void normalize_name(std::string& value) {
    normalize_whitespace(value);
    bool new_word = true;
    std::transform(value.begin(), value.end(), value.begin(), [&new_word](unsigned char ch) {
        if (std::isspace(ch) || ch == '\'' || ch == '-') {
            new_word = true;
            return static_cast<char>(ch);
        }
        if (new_word) {
            new_word = false;
            return static_cast<char>(std::toupper(ch));
        }
        return static_cast<char>(std::tolower(ch));
    });
}

void normalize_address(std::string& value) {
    normalize_whitespace(value);
}

void normalize_phone(std::string& value) {
    value.erase(std::remove_if(value.begin(), value.end(), [](unsigned char ch) {
        return std::isspace(ch) || ch == '-' || ch == '(' || ch == ')' || ch == '.';
    }), value.end());
}

void normalize_email(std::string& value) {
    normalize_whitespace(value);
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char ch) {
        return static_cast<char>(std::tolower(ch));
    });
}

void normalize_policy_number(std::string& value) {
    normalize_whitespace(value);
    value.erase(std::remove_if(value.begin(), value.end(), [](unsigned char ch) {
                     return std::isspace(ch);
                 }),
                 value.end());
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char ch) {
        return static_cast<char>(std::toupper(ch));
    });
}

void normalize_text_single_space(std::string& value) {
    normalize_whitespace(value);
}

void normalize_yes_no(std::string& value) {
    normalize_whitespace(value);
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char ch) {
        return static_cast<char>(std::tolower(ch));
    });
}
