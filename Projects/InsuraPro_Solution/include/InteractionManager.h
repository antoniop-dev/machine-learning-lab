#ifndef INTERACTION_MANAGER_H
#define INTERACTION_MANAGER_H
#pragma once

#include <ctime>
#include <functional>
#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

#include "Agent.h"
#include "Client.h"
#include "Interaction.h"

class Contract;
class Appointment;

/**
 * @brief Coordinates registration of entities and persistence of interactions.
 */
class InteractionManager {
public:
    using InteractionPtr = std::unique_ptr<Interaction>;
    using InteractionList = std::vector<InteractionPtr>;

    /**
     * @brief Register a client so interactions can reference it.
     */
    void register_client(Client& client);
    /**
     * @brief Remove a client from the registry by id.
     */
    void unregister_client(int client_id) noexcept;
    /**
     * @brief Register an agent so interactions can reference it.
     */
    void register_agent(Agent& agent);
    /**
     * @brief Remove an agent from the registry by id.
     */
    void unregister_agent(int agent_id) noexcept;

    /**
     * @brief Check whether a client exists in the registry.
     */
    bool has_client(int client_id) const noexcept;
    /**
     * @brief Check whether an agent exists in the registry.
     */
    bool has_agent(int agent_id) const noexcept;

    /**
     * @brief Create and store a new contract interaction.
     */
    Contract& create_contract(Client& client,
                              Agent& agent,
                              std::string policy_number,
                              std::string product_name,
                              double premium,
                              std::time_t start_date,
                              std::time_t end_date = std::time_t{},
                              std::time_t created_at = std::time(nullptr));

    /**
     * @brief Create and store a new appointment interaction.
     */
    Appointment& create_appointment(Client& client,
                                    Agent& agent,
                                    std::string topic,
                                    std::time_t scheduled_for,
                                    std::string location = {},
                                    std::time_t created_at = std::time(nullptr));

    /**
     * @brief Access the full collection of interactions.
     */
    const InteractionList& get_interactions() const noexcept;
    /**
     * @brief Collect interactions involving a specific client.
     */
    std::vector<Interaction*> find_by_client(int client_id) const;
    /**
     * @brief Collect interactions involving a specific agent.
     */
    std::vector<Interaction*> find_by_agent(int agent_id) const;

    /**
     * @brief Remove all tracked interactions and deregister references.
     */
    void clear() noexcept;

    /**
     * @brief Delete any interactions associated with the provided client id.
     */
    void remove_interactions_for_client(int client_id);
    /**
     * @brief Delete any interactions associated with the provided agent id.
     */
    void remove_interactions_for_agent(int agent_id);

private:
    using ClientRef = std::reference_wrapper<Client>;
    using AgentRef = std::reference_wrapper<Agent>;

    /**
     * @brief Transfer ownership into the internal storage.
     */
    Interaction& add_interaction(InteractionPtr interaction);

    /**
     * @brief Retrieve a client by id or throw if missing.
     */
    Client& require_client(int client_id);
    /**
     * @brief Retrieve an agent by id or throw if missing.
     */
    Agent& require_agent(int agent_id);

    InteractionList interactions;
    std::unordered_map<int, ClientRef> clients;
    std::unordered_map<int, AgentRef> agents;
};

#endif // INTERACTION_MANAGER_H
