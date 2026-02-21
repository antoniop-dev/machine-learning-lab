#ifndef UTILS_H
#define UTILS_H
#pragma once

#include <iostream>
#include <memory>
#include <string>
#include <unordered_map>
#include "Client.h"
#include "Agent.h"
#include "InteractionManager.h"

using ClientStore = std::unordered_map<int, std::unique_ptr<Client>>;
using AgentStore = std::unordered_map<int, std::unique_ptr<Agent>>;

/**
 * @brief Construct a std::tm structure from discrete date components.
 */
std::tm make_tm(int year, int month, int day);

/**
 * @brief Convert a std::tm value to std::time_t using local time rules.
 */
std::time_t tm_to_time_t(std::tm value);

/**
 * @brief Convert a std::time_t to local std::tm.
 */
std::tm to_local_tm(std::time_t value);

/**
 * @brief Format a std::tm date as DD-MM-YYYY.
 */
std::string format_date(const std::tm& date);

/**
 * @brief Format a timestamp into a human-readable date/time string.
 */
std::string format_timestamp(std::time_t value);

/**
 * @brief Map a token from storage/user input to the matching CustomerType.
 */
CustomerType customer_type_from_string(const std::string& token);

/**
 * @brief Represent a CustomerType with a human-readable label.
 */
std::string customer_type_to_string(CustomerType type);

/**
 * @brief Obtain the canonical persistence token for a CustomerType.
 */
std::string customer_type_token(CustomerType type);

/**
 * @brief Load default agents into the provided store.
 */
void load_default_agents(AgentStore& agents);

/**
 * @brief Register every agent in the interaction manager.
 */
void register_all_agents(AgentStore& agents, InteractionManager& manager);

#endif // UTILS_H
