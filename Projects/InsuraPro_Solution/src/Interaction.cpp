#include "Interaction.h"

#include <ctime>

int Interaction::next_id = 0;

Interaction::Interaction(Client& _client, Agent& _agent, std::time_t _timestamp)
    : id(++next_id), client(_client), agent(_agent),
      timestamp(_timestamp != std::time_t{} ? _timestamp : std::time(nullptr)) {}

int Interaction::get_id() const noexcept { return id; }

Client& Interaction::get_client() noexcept { return client; }
const Client& Interaction::get_client() const noexcept { return client; }

Agent& Interaction::get_agent() noexcept { return agent; }
const Agent& Interaction::get_agent() const noexcept { return agent; }

std::time_t Interaction::get_timestamp() const noexcept { return timestamp; }

void Interaction::set_timestamp(std::time_t timestamp_value) noexcept { timestamp = timestamp_value; }

int Interaction::current_id_seed() noexcept { return next_id; }

void Interaction::set_next_id_seed(int value) noexcept { next_id = value; }
