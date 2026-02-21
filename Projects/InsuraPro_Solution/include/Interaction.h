#ifndef INTERACTION_H
#define INTERACTION_H
#pragma once

#include <ctime>
#include <string>

#include "Client.h"
#include "Agent.h"

class InteractionManager; // forward declaration

/**
 * @brief Base class for interactions recorded between clients and agents.
 */
class Interaction {
    friend class InteractionManager;

protected:
    static int next_id;        // shared variable for auto-incremented ids
    int id;                    // unique identifier for the interaction
    Client& client;            // reference to the involved client
    Agent& agent;              // reference to the involved agent
    std::time_t timestamp;     // moment when the interaction took place

    /**
     * @brief Construct a new interaction with participants and timestamp.
     */
    Interaction(Client& _client, Agent& _agent, std::time_t _timestamp = std::time(nullptr));

public:
    virtual ~Interaction() = default;

    Interaction(const Interaction&) = default;
    Interaction(Interaction&&) = default;
    Interaction& operator=(const Interaction&) = delete;
    Interaction& operator=(Interaction&&) = delete;

    /**
     * @brief Retrieve the interaction identifier.
     */
    int get_id() const noexcept;
    /**
     * @brief Access the underlying client (mutable overload).
     */
    Client& get_client() noexcept;
    /**
     * @brief Access the underlying client (const overload).
     */
    const Client& get_client() const noexcept;
    /**
     * @brief Access the associated agent (mutable overload).
     */
    Agent& get_agent() noexcept;
    /**
     * @brief Access the associated agent (const overload).
     */
    const Agent& get_agent() const noexcept;
    /**
     * @brief Retrieve the stored timestamp.
     */
    std::time_t get_timestamp() const noexcept;
    /**
     * @brief Update the interaction timestamp.
     */
    void set_timestamp(std::time_t timestamp) noexcept;

    /**
     * @brief Inspect the current id seed used for auto-increment.
     */
    static int current_id_seed() noexcept;
    /**
     * @brief Override the next id seed (used while importing data).
     */
    static void set_next_id_seed(int value) noexcept;

    /**
     * @brief Return the concrete interaction type label.
     */
    virtual std::string type_name() const = 0;
    /**
     * @brief Produce a short summary describing the interaction.
     */
    virtual std::string summary() const = 0;
    /**
     * @brief Print the interaction to stdout.
     */
    virtual void print_interaction() const = 0;
};

#endif // INTERACTION_H
