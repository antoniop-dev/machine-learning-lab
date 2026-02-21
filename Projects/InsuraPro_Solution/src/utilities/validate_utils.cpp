#include "utilities/validate_utils.h"

#include <algorithm>
#include <cctype>
#include <chrono>
#include <cctype>
#include <cmath>
#include <limits>
#include <regex>

#include "utilities/parse_utils.h"
#include "utilities/string_utils.h"
#include "utilities/utils.h"

namespace {

bool is_allowed_name_char(char ch) {
    return std::isalpha(static_cast<unsigned char>(ch)) || ch == ' ' || ch == '\'' || ch == '-';
}

} // namespace

bool validate_name(const std::string& value) {
    const std::string trimmed = trim(value);
    if (trimmed.size() < 2) {
        return false;
    }
    return std::all_of(trimmed.begin(), trimmed.end(), is_allowed_name_char);
}

bool validate_d_o_b(const std::string& value) {
    try {
        const std::tm birth_tm = parse_date(value);
        const std::time_t birth_time = tm_to_time_t(birth_tm);

        const auto now = std::chrono::system_clock::now();
        const std::time_t now_time = std::chrono::system_clock::to_time_t(now);
        if (birth_time > now_time) {
            return false;
        }

        const auto age = std::chrono::duration_cast<std::chrono::hours>(
            std::chrono::system_clock::from_time_t(now_time) -
            std::chrono::system_clock::from_time_t(birth_time)).count() / (24.0 * 365.25);

        return age >= 0.0 && age <= 120.0;
    } catch (const std::exception&) {
        return false;
    }
}

bool validate_date(const std::string& value) {
    try {
        parse_date(value);
        return true;
    } catch (const std::exception&) {
        return false;
    }
}

bool validate_fiscal_code(const std::string& value) {
    static const std::regex pattern(R"(^[A-Z0-9]{16}$)");
    std::string upper = trim(value);
    std::transform(upper.begin(), upper.end(), upper.begin(), [](unsigned char ch) {
        return static_cast<char>(std::toupper(ch));
    });
    return std::regex_match(upper, pattern);
}

bool validate_phone_number(const std::string& value) {
    const std::string trimmed = trim(value);
    if (trimmed.size() < 5) {
        return false;
    }

    std::size_t digit_count = 0;
    for (std::size_t i = 0; i < trimmed.size(); ++i) {
        const char ch = trimmed[i];
        if (std::isdigit(static_cast<unsigned char>(ch))) {
            ++digit_count;
            continue;
        }
        if (i == 0 && ch == '+') {
            continue;
        }
        if (ch == ' ' || ch == '-' || ch == '(' || ch == ')') {
            continue;
        }
        return false;
    }
    return digit_count >= 5;
}

bool validate_email(const std::string& value) {
    static const std::regex pattern(R"(^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$)", std::regex::icase);
    return std::regex_match(trim(value), pattern);
}

bool validate_time_t(std::time_t value) {
    if (value <= 0) {
        return false;
    }
    constexpr std::time_t max_reasonable =
        static_cast<std::time_t>(std::numeric_limits<int>::max());
    return value < max_reasonable;
}

bool validate_policy_number(const std::string& value) {
    const std::string trimmed = trim(value);
    const std::size_t len = trimmed.size();
    if (len < 3 || len > 32) {
        return false;
    }
    return std::all_of(trimmed.begin(), trimmed.end(), [](unsigned char ch) {
        return std::isalnum(ch) || ch == '-' || ch == '_';
    });
}

bool validate_address(const std::string& value,
                      std::size_t min_length,
                      std::size_t max_length) {
    const std::string trimmed = trim(value);
    if (trimmed.size() < min_length || trimmed.size() > max_length) {
        return false;
    }
    return std::all_of(trimmed.begin(), trimmed.end(), [](unsigned char ch) {
        return std::isalnum(ch) || std::isspace(ch) ||
               ch == '-' || ch == '\'' || ch == ',' ||
               ch == '.' || ch == '/' || ch == '#';
    });
}

bool validate_numeric_identifier(const std::string& value) {
    const std::string trimmed = trim(value);
    if (trimmed.empty()) {
        return false;
    }
    if (!std::all_of(trimmed.begin(), trimmed.end(), [](unsigned char ch) { return std::isdigit(ch); })) {
        return false;
    }
    try {
        const long long numeric = std::stoll(trimmed);
        return numeric > 0 && numeric <= std::numeric_limits<int>::max();
    } catch (const std::exception&) {
        return false;
    }
}

bool validate_text_field(const std::string& value,
                         std::size_t min_length,
                         std::size_t max_length) {
    const std::string trimmed = trim(value);
    if (trimmed.size() < min_length || trimmed.size() > max_length) {
        return false;
    }
    return std::all_of(trimmed.begin(), trimmed.end(), [](unsigned char ch) {
        return std::isprint(ch);
    });
}

bool validate_positive_amount(double value,
                              double min_value,
                              double max_value) {
    if (!std::isfinite(value)) {
        return false;
    }
    return value >= min_value && value <= max_value;
}

bool validate_future_datetime(const std::string& value) {
    try {
        const std::time_t timestamp = parse_datetime(value);
        const auto now = std::chrono::system_clock::now();
        const std::time_t now_time = std::chrono::system_clock::to_time_t(now);
        return timestamp >= now_time;
    } catch (const std::exception&) {
        return false;
    }
}

bool validate_optional_text(const std::string& value,
                            std::size_t max_length) {
    const std::string trimmed = trim(value);
    if (trimmed.empty()) {
        return true;
    }
    return validate_text_field(trimmed, 1, max_length);
}

bool validate_yes_no_response(const std::string& value) {
    const std::string lowered = to_lower(trim(value));
    return lowered == "y" || lowered == "yes" || lowered == "n" || lowered == "no";
}

bool validate_time_range(std::time_t start,
                         std::time_t end,
                         bool allow_open_end) {
    if (!validate_time_t(start)) {
        return false;
    }
    if (end == std::time_t{} && allow_open_end) {
        return true;
    }
    if (!validate_time_t(end)) {
        return false;
    }
    return end >= start;
}
