#include "utilities/utils.h"
#include "Client.h"
#include "Agent.h"
#include "InteractionManager.h"
#include "utilities/string_utils.h"

#include <sstream>
#include <fstream>
#include <iostream>
#include <ctime>
#include <iomanip>


std::tm make_tm(int year, int month, int day) {
    std::tm value{};
    value.tm_year = year - 1900;
    value.tm_mon = month - 1;
    value.tm_mday = day;
    value.tm_hour = 0;
    value.tm_min = 0;
    value.tm_sec = 0;
    value.tm_isdst = -1;
    return value;
}

std::time_t tm_to_time_t(std::tm value) {
    value.tm_isdst = -1;
    std::time_t result = std::mktime(&value);
    if (result == static_cast<std::time_t>(-1)) {
        throw std::runtime_error("Unable to convert the specified date/time.");
    }
    return result;
}

std::tm to_local_tm(std::time_t value) {
    std::tm result{};
    if (value == std::time_t{}) {
        return result;
    }
#ifdef _WIN32
    localtime_s(&result, &value);
#else
    if (const std::tm* tmp = std::localtime(&value)) {
        result = *tmp;
    }
#endif
    return result;
}

std::string format_date(const std::tm& date) {
    std::ostringstream oss;
    oss << std::put_time(&date, "%d-%m-%Y");
    return oss.str();
}

std::string format_timestamp(std::time_t value) {
    if (value == std::time_t{}) {
        return "-";
    }
    std::tm local = to_local_tm(value);
    std::ostringstream oss;
    oss << std::put_time(&local, "%d-%m-%Y %H:%M");
    return oss.str();
}


CustomerType customer_type_from_string(const std::string& token) {
    const std::string lowered = to_lower(trim(token));
    if (lowered == "individual" || lowered == "private" || lowered == "individuale" || lowered == "privato") {
        return CustomerType::Individual;
    }
    if (lowered == "company" || lowered == "azienda" || lowered == "business") {
        return CustomerType::Company;
    }
    throw std::runtime_error("Invalid value for customer_type: " + token);
}

std::string customer_type_to_string(CustomerType type) {
    switch (type) {
    case CustomerType::Individual:
        return "Individual";
    case CustomerType::Company:
        return "Company";
    default:
        return "Unkown";
    }
}

std::string customer_type_token(CustomerType type) {
    switch (type) {
    case CustomerType::Individual:
        return "individual";
    case CustomerType::Company:
        return "company";
    default:
        return "unknown";
    }
}

void load_default_agents(AgentStore& agents) {
    agents.clear();
    Agent::set_next_id_seed(0);

    std::tm birth1 = make_tm(1985, 2, 11);
    std::tm hire1  = make_tm(2012, 5, 3);
    auto agent1 = std::make_unique<Agent>(
        "Emily", "Johnson", birth1, "emily.johnson@insurapro.uk",
        "+44 20 7946 1234", hire1);

    std::tm birth2 = make_tm(1979, 8, 27);
    std::tm hire2  = make_tm(2009, 10, 14);
    auto agent2 = std::make_unique<Agent>(
        "Michael", "Smith", birth2, "michael.smith@insurapro.uk",
        "+44 161 555 7821", hire2);

    std::tm birth3 = make_tm(1990, 6, 9);
    std::tm hire3  = make_tm(2016, 2, 22);
    auto agent3 = std::make_unique<Agent>(
        "Olivia", "Brown", birth3, "olivia.brown@insurapro.uk",
        "+44 121 678 4402", hire3);

    std::tm birth4 = make_tm(1988, 12, 1);
    std::tm hire4  = make_tm(2013, 11, 5);
    auto agent4 = std::make_unique<Agent>(
        "James", "Wilson", birth4, "james.wilson@insurapro.uk",
        "+44 113 404 9977", hire4);

    std::tm birth5 = make_tm(1992, 9, 18);
    std::tm hire5  = make_tm(2018, 7, 30);
    auto agent5 = std::make_unique<Agent>(
        "Sophie", "Taylor", birth5, "sophie.taylor@insurapro.uk",
        "+44 141 309 6650", hire5);

    agents.emplace(agent1->get_id(), std::move(agent1));
    agents.emplace(agent2->get_id(), std::move(agent2));
    agents.emplace(agent3->get_id(), std::move(agent3));
    agents.emplace(agent4->get_id(), std::move(agent4));
    agents.emplace(agent5->get_id(), std::move(agent5));
}

void register_all_agents(AgentStore& agents, InteractionManager& manager) {
    for (auto& [id, agent] : agents) {
        if (agent) {
            manager.register_agent(*agent);
        }
    }
}
