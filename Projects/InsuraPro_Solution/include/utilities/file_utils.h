#ifndef FILE_UTILS_H
#define FILE_UTILS_H
#pragma once

#include <string>
#include <vector>

#include "utilities/utils.h"

/**
 * @brief Split a CSV line into tokens while preserving empty fields.
 *
 * @param line Raw CSV line.
 * @return Vector containing each field.
 */
std::vector<std::string> split_csv_line(const std::string& line);

/**
 * @brief Load clients, agents, and interactions data from persistent storage.
 *
 * @param manager Interaction manager to populate.
 * @param clients Client repository receiving loaded entries.
 * @param agents Agent repository receiving loaded entries.
 * @throws std::runtime_error If any underlying file operation fails.
 */
void load_data(InteractionManager& manager, ClientStore& clients, AgentStore& agents);

/**
 * @brief Populate in-memory clients from a CSV file.
 *
 * @param file_path Path to the clients CSV file.
 * @param clients Target store for the loaded clients.
 * @param manager Interaction manager used to register clients.
 * @throws std::runtime_error On parsing or I/O errors.
 */
void load_clients_from_csv(const std::string& file_path,
                           ClientStore& clients,
                           InteractionManager& manager);

/**
 * @brief Load interactions and ensure related entities are resolved.
 *
 * @param file_path Path to the interactions CSV file.
 * @param manager Interaction manager to populate.
 * @param clients Client repository used to resolve relationships.
 * @param agents Agent repository used to resolve relationships.
 * @throws std::runtime_error On parsing or I/O errors.
 */
void load_interactions_from_csv(const std::string& file_path,
                                InteractionManager& manager,
                                ClientStore& clients,
                                AgentStore& agents);

/**
 * @brief Write the current clients store to a CSV file.
 *
 * @param file_path Destination path for the export.
 * @param clients Data source to serialize.
 * @throws std::runtime_error On I/O errors.
 */
void save_clients_to_csv(const std::string& file_path, const ClientStore& clients);

/**
 * @brief Persist interactions managed by @p manager into a CSV file.
 *
 * @param file_path Destination path for the export.
 * @param manager Interaction manager containing data to save.
 * @throws std::runtime_error On I/O errors.
 */
void save_interactions_to_csv(const std::string& file_path, const InteractionManager& manager);

#endif
