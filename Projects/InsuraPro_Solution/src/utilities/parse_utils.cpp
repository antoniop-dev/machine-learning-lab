#include "utilities/parse_utils.h"
#include "utilities/utils.h"

#include <sstream>
#include <iomanip>

std::tm parse_date(const std::string& text) {
    std::tm value{};
    std::istringstream iss(text);
    iss >> std::get_time(&value, "%d-%m-%Y");
    if (iss.fail()) {
        throw std::runtime_error("Invalid date format. Use DD-MM-YYYY.");
    }
    value.tm_hour = 0;
    value.tm_min = 0;
    value.tm_sec = 0;
    value.tm_isdst = -1;
    return value;
}

std::time_t parse_datetime(const std::string& text) {
    std::tm value{};
    std::istringstream iss(text);
    iss >> std::get_time(&value, "%d-%m-%Y %H:%M");
    if (iss.fail()) {
        throw std::runtime_error("Invalid date and time format. Use DD-MM-YYYY HH:MM.");
    }
    return tm_to_time_t(value);
}

int parse_int_field(const std::string& text, const char* field_name) {
    try {
        std::size_t consumed = 0;
        int value = std::stoi(text, &consumed);
        if (consumed != text.size()) {
            throw std::runtime_error("");
        }
        return value;
    } catch (const std::exception&) {
        throw std::runtime_error(std::string("Invalid value for ") + field_name + " field: " + text);
    }
}
