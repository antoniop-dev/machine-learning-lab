#include "utilities/file_utils.h"

#include <algorithm>
#include <iostream>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <utility>
#include <filesystem>

#include "Agent.h"
#include "Appointment.h"
#include "Client.h"
#include "Contract.h"
#include "Interaction.h"
#include "InteractionManager.h"
#include "utilities/parse_utils.h"
#include "utilities/string_utils.h"
#include "utilities/utils.h"

namespace {

constexpr const char* kClientsFile = "clients.csv";
constexpr const char* kInteractionsFile = "interactions.csv";

std::string escape_csv(const std::string& value) {
    const bool needs_quotes = value.find_first_of(",\"\n\r") != std::string::npos;
    if (!needs_quotes) {
        return value;
    }

    std::string escaped;
    escaped.reserve(value.size() + 2);
    escaped.push_back('"');
    for (char ch : value) {
        if (ch == '"') {
            escaped.append("\"\"");
        } else {
            escaped.push_back(ch);
        }
    }
    escaped.push_back('"');
    return escaped;
}

Client& require_client(ClientStore& clients, int client_id) {
    const auto it = clients.find(client_id);
    if (it == clients.end() || it->second == nullptr) {
        throw std::runtime_error("Unknown client id: " + std::to_string(client_id));
    }
    return *it->second;
}

Agent& require_agent(AgentStore& agents, int agent_id) {
    const auto it = agents.find(agent_id);
    if (it == agents.end() || it->second == nullptr) {
        throw std::runtime_error("Unknown agent id: " + std::to_string(agent_id));
    }
    return *it->second;
}

} // namespace

std::vector<std::string> split_csv_line(const std::string& line) {
    std::vector<std::string> tokens;
    std::string current;
    bool in_quotes = false;

    for (std::size_t i = 0; i < line.size(); ++i) {
        char ch = line[i];
        if (in_quotes) {
            if (ch == '"') {
                if (i + 1 < line.size() && line[i + 1] == '"') {
                    current.push_back('"');
                    ++i;
                } else {
                    in_quotes = false;
                }
            } else {
                current.push_back(ch);
            }
        } else if (ch == '"') {
            in_quotes = true;
        } else if (ch == ',') {
            tokens.push_back(trim(current));
            current.clear();
        } else {
            current.push_back(ch);
        }
    }

    tokens.push_back(trim(current));
    return tokens;
}

void load_data(InteractionManager& manager, ClientStore& clients, AgentStore& agents) {
    manager = InteractionManager{};
    load_default_agents(agents);
    register_all_agents(agents, manager);

    try {
        load_clients_from_csv(kClientsFile, clients, manager);
        std::cout << "Loaded " << clients.size() << " clients from " << kClientsFile << ".\n";
    } catch (const std::exception& ex) {
        std::cerr << "Error while loading clients: " << ex.what() << '\n';
    }

    std::ifstream check(kInteractionsFile);
    if (!check.is_open()) {
        std::cout << "No interaction file found.\n";
        return;
    }
    check.close();

    try {
        load_interactions_from_csv(kInteractionsFile, manager, clients, agents);
        std::cout << "Loaded interactions from " << kInteractionsFile << ".\n";
    } catch (const std::exception& ex) {
        std::cerr << "Error while loading interactions: " << ex.what() << '\n';
    }
}

void load_clients_from_csv(const std::string& file_path,
                           ClientStore& clients,
                           InteractionManager& manager) {
    clients.clear();
    std::ifstream in(file_path);
    if (!in.is_open()) {
        return;
    }

    std::string line;
    bool first_line = true;
    int max_id = 0;

    while (std::getline(in, line)) {
        if (line.empty()) {
            continue;
        }
        if (first_line) {
            first_line = false;
            if (line.rfind("id,", 0) == 0) {
                continue; // skip header
            }
        }

        const std::vector<std::string> tokens = split_csv_line(line);
        if (tokens.size() < 9) {
            throw std::runtime_error("Invalid client CSV row: " + line);
        }

        const int id = parse_int_field(tokens[0], "id");
        if (id <= 0) {
            throw std::runtime_error("Invalid client id: " + tokens[0]);
        }

        const std::tm birth = parse_date(tokens[3]);
        const CustomerType customer_type = customer_type_from_string(tokens[8]);

        Client::set_next_id_seed(id - 1);
        auto client = std::make_unique<Client>(tokens[1],
                                               tokens[2],
                                               birth,
                                               tokens[4],
                                               tokens[5],
                                               tokens[6],
                                               tokens[7],
                                               customer_type);
        Client& ref = *client;
        clients.emplace(id, std::move(client));
        manager.register_client(ref);

        if (id > max_id) {
            max_id = id;
        }
    }

    Client::set_next_id_seed(max_id);
}

void load_interactions_from_csv(const std::string& file_path,
                                InteractionManager& manager,
                                ClientStore& clients,
                                AgentStore& agents) {
    std::ifstream in(file_path);
    if (!in.is_open()) {
        throw std::runtime_error("Unable to open file for reading: " + file_path);
    }

    manager.clear();

    std::string line;
    bool first_line = true;
    int max_id = Interaction::current_id_seed();

    while (std::getline(in, line)) {
        if (line.empty()) {
            continue;
        }
        if (first_line) {
            first_line = false;
            if (line.rfind("type,", 0) == 0) {
                continue; // skip header
            }
        }

        const std::vector<std::string> tokens = split_csv_line(line);
        if (tokens.size() < 5) {
            throw std::runtime_error("Invalid interaction CSV row: " + line);
        }

        const std::string& type = tokens[0];
        const int id = parse_numeric<int>(tokens[1], "id");
        const int client_id = parse_numeric<int>(tokens[2], "client_id");
        const int agent_id = parse_numeric<int>(tokens[3], "agent_id");
        const std::time_t timestamp = parse_numeric<std::time_t>(tokens[4], "timestamp");

        Client& client = require_client(clients, client_id);
        Agent& agent = require_agent(agents, agent_id);

        manager.register_client(client);
        manager.register_agent(agent);

        Interaction::set_next_id_seed(id - 1);

        if (type == "Contract") {
            if (tokens.size() < 10) {
                throw std::runtime_error("Invalid Contract CSV row: " + line);
            }
            std::string policy_number = tokens[5];
            std::string product_name = tokens[6];
            double premium = parse_numeric<double>(tokens[7], "premium");
            std::time_t start_date = parse_numeric<std::time_t>(tokens[8], "start_date");
            std::time_t end_date = parse_numeric<std::time_t>(tokens[9], "end_date");

            manager.create_contract(client,
                                    agent,
                                    std::move(policy_number),
                                    std::move(product_name),
                                    premium,
                                    start_date,
                                    end_date,
                                    timestamp);
        } else if (type == "Appointment") {
            if (tokens.size() < 10) {
                throw std::runtime_error("Invalid Appointment CSV row: " + line);
            }
            std::string topic = tokens[5];
            std::time_t scheduled_for = parse_numeric<std::time_t>(tokens[6], "scheduled_for");
            std::string location = tokens[7];
            const bool completed = parse_numeric<int>(tokens[8], "completed") != 0;
            std::time_t completed_at = parse_numeric<std::time_t>(tokens[9], "completed_at");

            auto& appointment = manager.create_appointment(
                client, agent, std::move(topic), scheduled_for, std::move(location), timestamp);
            if (completed) {
                appointment.mark_completed(completed_at);
            }
        } else {
            throw std::runtime_error("Unsupported interaction type in CSV: " + type);
        }

        if (id > max_id) {
            max_id = id;
        }
    }

    Interaction::set_next_id_seed(max_id);
}

void save_clients_to_csv(const std::string& file_path, const ClientStore& clients) {
    std::ofstream out(file_path);
    if (!out.is_open()) {
        throw std::runtime_error("Unable to open file for writing: " + file_path);
    }

    out << "id,name,surname,birth,fiscal_code,phone,email,address,customer_type";

    std::vector<const Client*> ordered;
    ordered.reserve(clients.size());
    for (const auto& [id, client] : clients) {
        if (client) {
            ordered.push_back(client.get());
        }
    }

    std::sort(ordered.begin(), ordered.end(), [](const Client* lhs, const Client* rhs) {
        return lhs->get_id() < rhs->get_id();
    });

    for (const Client* client : ordered) {
        out << '\n'
            << client->get_id() << ','
            << escape_csv(client->get_name()) << ','
            << escape_csv(client->get_surname()) << ','
            << escape_csv(format_date(client->get_birth())) << ','
            << escape_csv(client->get_fiscal_code()) << ','
            << escape_csv(client->get_phone_number()) << ','
            << escape_csv(client->get_email()) << ','
            << escape_csv(client->get_address()) << ','
            << customer_type_token(client->get_customer_type());
    }
}

void save_interactions_to_csv(const std::string& file_path, const InteractionManager& manager) {
    std::ofstream out(file_path);
    if (!out.is_open()) {
        throw std::runtime_error("Unable to open file for writing: " + file_path);
    }

    out << "type,id,client_id,agent_id,timestamp,field1,field2,field3,field4,field5";

    const auto& interactions = manager.get_interactions();
    for (const auto& interaction : interactions) {
        if (!interaction) {
            continue;
        }

        const std::string type = interaction->type_name();
        const Client& client = interaction->get_client();
        const Agent& agent = interaction->get_agent();

        out << '\n' << type << ',' << interaction->get_id() << ',' << client.get_id() << ','
            << agent.get_id() << ',' << static_cast<long long>(interaction->get_timestamp());

        if (const auto* contract = dynamic_cast<const Contract*>(interaction.get())) {
            out << ',' << escape_csv(contract->get_policy_number()) << ','
                << escape_csv(contract->get_product_name()) << ',' << contract->get_premium() << ','
                << static_cast<long long>(contract->get_start_date()) << ','
                << static_cast<long long>(contract->get_end_date());
        } else if (const auto* appointment = dynamic_cast<const Appointment*>(interaction.get())) {
            out << ',' << escape_csv(appointment->get_topic()) << ','
                << static_cast<long long>(appointment->get_scheduled_for()) << ','
                << escape_csv(appointment->get_location()) << ','
                << (appointment->is_completed() ? 1 : 0) << ','
                << static_cast<long long>(appointment->get_completed_at());
        } else {
            out << ",,,,";
        }
    }
}
