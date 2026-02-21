#include "InteractionManager.h"

#include <algorithm>
#include <stdexcept>
#include <utility>

#include "Agent.h"
#include "Appointment.h"
#include "Client.h"
#include "Contract.h"


void InteractionManager::register_client(Client& client) {
    clients.insert_or_assign(client.get_id(), std::ref(client));
}

void InteractionManager::unregister_client(int client_id) noexcept { clients.erase(client_id); }

void InteractionManager::register_agent(Agent& agent) {
    agents.insert_or_assign(agent.get_id(), std::ref(agent));
}

void InteractionManager::unregister_agent(int agent_id) noexcept { agents.erase(agent_id); }

bool InteractionManager::has_client(int client_id) const noexcept {
    return clients.find(client_id) != clients.end();
}

bool InteractionManager::has_agent(int agent_id) const noexcept {
    return agents.find(agent_id) != agents.end();
}

Contract& InteractionManager::create_contract(Client& client,
                                              Agent& agent,
                                              std::string policy_number,
                                              std::string product_name,
                                              double premium,
                                              std::time_t start_date,
                                              std::time_t end_date,
                                              std::time_t created_at) {
    register_client(client);
    register_agent(agent);

    auto contract = std::unique_ptr<Contract>(new Contract(client,
                                                           agent,
                                                           std::move(policy_number),
                                                           std::move(product_name),
                                                           premium,
                                                           start_date,
                                                           end_date,
                                                           created_at));
    return static_cast<Contract&>(add_interaction(std::move(contract)));
}

Appointment& InteractionManager::create_appointment(Client& client,
                                                    Agent& agent,
                                                    std::string topic,
                                                    std::time_t scheduled_for,
                                                    std::string location,
                                                    std::time_t created_at) {
    register_client(client);
    register_agent(agent);

    auto appointment = std::unique_ptr<Appointment>(new Appointment(client,
                                                                    agent,
                                                                    std::move(topic),
                                                                    scheduled_for,
                                                                    std::move(location),
                                                                    created_at));
    return static_cast<Appointment&>(add_interaction(std::move(appointment)));
}

const InteractionManager::InteractionList& InteractionManager::get_interactions() const noexcept {
    return interactions;
}

std::vector<Interaction*> InteractionManager::find_by_client(int client_id) const {
    std::vector<Interaction*> result;
    for (const auto& interaction : interactions) {
        if (interaction && interaction->get_client().get_id() == client_id) {
            result.push_back(interaction.get());
        }
    }
    return result;
}

std::vector<Interaction*> InteractionManager::find_by_agent(int agent_id) const {
    std::vector<Interaction*> result;
    for (const auto& interaction : interactions) {
        if (interaction && interaction->get_agent().get_id() == agent_id) {
            result.push_back(interaction.get());
        }
    }
    return result;
}

void InteractionManager::clear() noexcept { interactions.clear(); }

Interaction& InteractionManager::add_interaction(InteractionPtr interaction) {
    interactions.emplace_back(std::move(interaction));
    return *interactions.back();
}

void InteractionManager::remove_interactions_for_client(int client_id) {
    interactions.erase(std::remove_if(interactions.begin(),
                                      interactions.end(),
                                      [client_id](const InteractionPtr& interaction) {
                                          return interaction &&
                                                 interaction->get_client().get_id() == client_id;
                                      }),
                       interactions.end());
}

void InteractionManager::remove_interactions_for_agent(int agent_id) {
    interactions.erase(std::remove_if(interactions.begin(),
                                      interactions.end(),
                                      [agent_id](const InteractionPtr& interaction) {
                                          return interaction &&
                                                 interaction->get_agent().get_id() == agent_id;
                                      }),
                       interactions.end());
}

Client& InteractionManager::require_client(int client_id) {
    const auto it = clients.find(client_id);
    if (it == clients.end()) {
        throw std::runtime_error("Unknown client id: " + std::to_string(client_id));
    }
    return it->second.get();
}

Agent& InteractionManager::require_agent(int agent_id) {
    const auto it = agents.find(agent_id);
    if (it == agents.end()) {
        throw std::runtime_error("Unknown agent id: " + std::to_string(agent_id));
    }
    return it->second.get();
}
