#include "Ui.h"

#include <algorithm>
#include <functional>
#include <iostream>
#include <fstream>
#include <ostream>
#include <optional>
#include <utility>
#include <cstdlib>
#include <chrono>
#include <thread>
#include <limits>

#include "Contract.h"
#include "Appointment.h"
#include "utilities/parse_utils.h"
#include "utilities/string_utils.h"
#include "utilities/file_utils.h"
#include "utilities/validate_utils.h"
#include "utilities/normalize_utils.h"
#include "utilities/utils.h"

using ClientStore = std::unordered_map<int, std::unique_ptr<Client>>;
using AgentStore = std::unordered_map<int, std::unique_ptr<Agent>>;

constexpr const char* kClientsFile = "clients.csv";
constexpr const char* kInteractionsFile = "interactions.csv";

UI::UI(AgentStore _agents, ClientStore _clients, InteractionManager _manager):
    clients(std::move(_clients)), agents(std::move(_agents)), manager(std::move(_manager)){}

void UI::run() {
    bool running = true;
    while (running) {
        clear_terminal();
        show_main_menu();
        const int choice = prompt_int("\nChoose an option (1-9): ", 1, 9);
        switch (choice) {
        case 1:
            add_client();
            break;
        case 2:
            list_clients();
            wait_for_input();
            break;
        case 3:
            edit_client();
            break;
        case 4:
            delete_client();
            break;
        case 5:
            search_clients();
            break;
        case 6:
            manage_interactions();
            break;
        case 7:
            save_data();
            break;
        case 8:
            call_load_data();
            break;
        case 9:
            if (prompt_yes_no("\nWould you like to save before exiting? (y/n): ")) {
                save_data();
            }
            std::cout << "\nBye!\n";
            running = false;
            break;
        default:
            break;
        }
    }
}

void UI::show_main_menu() {
    print_header("InsuraPro CRM");
    std::cout << "1. Add client\n";
    std::cout << "2. Show clients\n";
    std::cout << "3. Edit client\n";
    std::cout << "4. Delete client\n";
    std::cout << "5. Search client\n";
    std::cout << "6. Manage interactions\n";
    std::cout << "7. Save data\n";
    std::cout << "8. Load data\n";
    std::cout << "9. Exit\n";
}

void UI::add_client() {
    clear_terminal();
    print_header("Add Client");
    std::string name = prompt_and_validate("First name: ",
                                           "Name must contain only letters and be at least 2 characters.",
                                           normalize_name,
                                           validate_name);

    std::string surname = prompt_and_validate("Last name: ",
                                               "Surname must contain only letters and be at least 2 characters.",
                                               normalize_name,
                                               validate_name);

    auto trim_only = [](std::string& text) { trim_in_place(text); };
    std::tm birth = parse_date(prompt_and_validate("Birth date (DD-MM-YYYY): ",
                                                   "Invalid birth date. Use DD-MM-YYYY and ensure it is realistic.",
                                                   trim_only,
                                                   validate_d_o_b));

    std::string fiscal_code = prompt_and_validate("Tax ID: ",
                                                  "Tax ID must be exactly 16 alphanumeric characters.",
                                                  normalize_policy_number,
                                                  validate_fiscal_code);

    std::string phone = prompt_and_validate("Phone number: ",
                                            "Phone number must include at least 5 digits.",
                                            normalize_phone,
                                            validate_phone_number);

    std::string email = prompt_and_validate("Email: ",
                                            "Invalid email address.",
                                            normalize_email,
                                            validate_email);

    auto address_validator = [](const std::string& value) { return validate_address(value); };
    std::string address = prompt_and_validate("Address: ",
                                              "Address must be at least 5 characters.",
                                              normalize_address,
                                              address_validator);
    CustomerType type = prompt_customer_type();

    auto client = std::make_unique<Client>(name, surname, birth, fiscal_code, phone, email, address, type);
    Client& ref = *client;
    const int id = client->get_id();
    manager.register_client(ref);
    clients.emplace(id, std::move(client));

    std::cout << "Client added with ID " << id << ".\n";
    sleep_seconds(2);
}

void UI::list_clients() {
    clear_terminal();
    print_header("Clients List");
    if (clients.empty()) {
        std::cout << "No clients available.\n";
        sleep_seconds(2);
        return;
    }
    std::vector<const Client*> ordered;
    ordered.reserve(clients.size());
    for (const auto& [id, client] : clients) {
        ordered.push_back(client.get());
    }
    std::sort(ordered.begin(), ordered.end(), [](const Client* a, const Client* b) {
        return a->get_id() < b->get_id();
    });
    for (const Client* client : ordered) {
        client->print_client();
        sleep_seconds(1);
    }
}

Client* UI::select_client() {
    if (clients.empty()) {
        std::cout << "There are no clients.\n";
        return nullptr;
    }
    list_clients();
    while (true) {
        std::string input = trim(prompt_line("\nEnter client ID (press enter to cancel): "));
        if (input.empty()) {
            std::cout << "Operation cancelled.\n";
            return nullptr;
        }
        if (!validate_numeric_identifier(input)) {
            std::cout << "Invalid client ID, please enter a positive number.\n";
            continue;
        }
        int id = std::stoi(input);
        auto it = clients.find(id);
        if (it != clients.end()) {
            return it->second.get();
        }
        std::cout << "Client not found, please try again.\n";
    }
}

void UI::edit_client() {
    Client* client = select_client();
    if (!client) {
        return;
    }

    std::cout << "Edit client ID " << client->get_id() << " (" << client->get_full_name() << ")\n";

    auto prompt_optional = [this](const std::string& message,
                                  auto&& normalize,
                                  auto&& validate) -> std::optional<std::string> {
        std::string input = trim(prompt_line(message));
        if (input.empty()) {
            return std::nullopt;
        }
        normalize(input);
        if (!validate(input)) {
            std::cout << "Invalid value, change ignored.\n";
            return std::nullopt;
        }
        return input;
    };

    if (auto new_name = prompt_optional("New first name (leave blank to keep current): ",
                                        normalize_name,
                                        validate_name)) {
        client->set_name(*new_name);
    }

    if (auto new_surname = prompt_optional("New last name (leave blank to keep current): ",
                                           normalize_name,
                                           validate_name)) {
        client->set_surname(*new_surname);
    }

    if (auto new_phone = prompt_optional("New phone number (leave blank to keep current): ",
                                         normalize_phone,
                                         validate_phone_number)) {
        client->set_phone_number(*new_phone);
    }

    if (auto new_email = prompt_optional("New email (leave blank to keep current): ",
                                         normalize_email,
                                         validate_email)) {
        client->set_email(*new_email);
    }

    auto address_validator = [](const std::string& value) { return validate_address(value); };
    if (auto new_address = prompt_optional("New address (leave blank to keep current): ",
                                           normalize_address,
                                           address_validator)) {
        client->set_address(*new_address);
    }

    std::cout << "Client updated.\n";
    sleep_seconds(2);
}

void UI::delete_client() {
    Client* client = select_client();
    if (!client) {
        return;
    }
    std::cout << "Selected Client:\n";
    client->print_client();
    if (!prompt_yes_no("\nConfirm client deletion? (y/n): ")) {
        std::cout << "Deletion cancelled.\n";
        sleep_seconds(2);
        return;
    }
    const int id = client->get_id();
    manager.remove_interactions_for_client(id);
    manager.unregister_client(id);
    clients.erase(id);
    std::cout << "Client and related interactions deleted.\n";
    sleep_seconds(2);
}

void UI::search_clients() {
    if (clients.empty()) {
        std::cout << "No clients available for search.\n";
        return;
    }
    auto search_normalize = [](std::string& text) {
        normalize_text_single_space(text);
        std::transform(text.begin(), text.end(), text.begin(), [](unsigned char ch) {
            return static_cast<char>(std::tolower(ch));
        });
    };
    auto search_validate = [](const std::string& value) {
        return validate_text_field(value, 2, 100);
    };
    std::string query = prompt_and_validate("Enter first or last name to search: ",
                                            "Search term must be at least 2 characters.",
                                            search_normalize,
                                            search_validate);
    std::vector<const Client*> matches;
    for (const auto& [id, client] : clients) {
        if (!client) {
            continue;
        }
        std::string name = to_lower(client->get_name());
        std::string surname = to_lower(client->get_surname());
        if (name.find(query) != std::string::npos || surname.find(query) != std::string::npos) {
            matches.push_back(client.get());
        }
    }
    if (matches.empty()) {
        std::cout << "No clients found for that search.\n";
        sleep_seconds(2);
        return;
    }
    clear_terminal();
    print_header("Results for: " + query + " (" + std::to_string(matches.size()) + ") ");
    std::sort(matches.begin(), matches.end(), [](const Client* a, const Client* b) {
        return a->get_id() < b->get_id();
    });
    for (const Client* client : matches) {
        client->print_client();
    }
    wait_for_input();
}

void UI::list_agents() {
    clear_terminal();
    print_header("Available agents");
    if (agents.empty()) {
        std::cout << "No agents available.\n";
        sleep_seconds(2);
        return;
    }
    std::vector<const Agent*> ordered;
    ordered.reserve(agents.size());
    for (const auto& [id, agent] : agents) {
        ordered.push_back(agent.get());
    }
    std::sort(ordered.begin(), ordered.end(), [](const Agent* a, const Agent* b) {
        return a->get_id() < b->get_id();
    });
    for (const Agent* agent : ordered) {
        agent->print_agent();
    }
}

Agent* UI::select_agent() {
    if (agents.empty()) {
        std::cout << "There are no registered agents.\n";
        return nullptr;
    }
    list_agents();
    while (true) {
        std::string input = trim(prompt_line("Enter agent ID (press enter to cancel): "));
        if (input.empty()) {
            std::cout << "Operation cancelled.\n";
            return nullptr;
        }
        if (!validate_numeric_identifier(input)) {
            std::cout << "Invalid agent ID, please enter a positive number.\n";
            continue;
        }
        int id = std::stoi(input);
        auto it = agents.find(id);
        if (it != agents.end()) {
            return it->second.get();
        }
        std::cout << "Agent not found, please try again.\n";
    }
}

void UI::add_contract() {
    if (clients.empty()) {
        std::cout << "You need at least one client before creating a contract.\n";
        sleep_seconds(2);
        return;
    }
    if (agents.empty()) {
        std::cout << "There are no agents available to assign the contract.\n";
        sleep_seconds(2);
        return;
    }
    Client* client = select_client();
    if (!client) {
        return;
    }
    Agent* agent = select_agent();
    if (!agent) {
        return;
    }

    std::string policy_number = prompt_and_validate("Policy number: ",
                                                    "Policy number must be 3-32 characters (letters, digits, '-', '_').",
                                                    normalize_policy_number,
                                                    validate_policy_number);

    auto product_validator = [](const std::string& value) {
        return validate_text_field(value, 3, 100);
    };
    std::string product_name = prompt_and_validate("Product name: ",
                                                   "Product name must be between 3 and 100 characters.",
                                                   normalize_text_single_space,
                                                   product_validator);

    double premium = 0.0;
    while (true) {
        premium = prompt_double("Annual premium: ", 0.0);
        if (validate_positive_amount(premium)) {
            break;
        }
        std::cout << "Premium must be between 0 and 1,000,000,000.\n";
    }

    auto trim_only = [](std::string& text) { trim_in_place(text); };
    std::tm start_tm = parse_date(prompt_and_validate("Start date (DD-MM-YYYY): ",
                                                      "Invalid start date. Use DD-MM-YYYY.",
                                                      trim_only,
                                                      validate_date));
    std::time_t start_date{};
    try {
        start_date = tm_to_time_t(start_tm);
    } catch (const std::exception& ex) {
        std::cout << "Error: " << ex.what() << '\n';
        return;
    }

    std::time_t end_date = std::time_t{};
    while (true) {
        std::string end_input = trim(prompt_line("End date (DD-MM-YYYY, leave blank if open-ended): "));
        if (end_input.empty()) {
            break;
        }
        if (!validate_date(end_input)) {
            std::cout << "Invalid end date. Use DD-MM-YYYY or leave blank to skip.\n";
            continue;
        }
        try {
            end_date = tm_to_time_t(parse_date(end_input));
        } catch (const std::exception& ex) {
            std::cout << ex.what() << " Try again or leave blank to skip.\n";
            continue;
        }
        if (!validate_time_range(start_date, end_date, false)) {
            std::cout << "End date must be on or after the start date.\n";
            continue;
        }
        break;
    }

    const std::time_t created_at = std::time(nullptr);
    const Contract& contract = manager.create_contract(*client,
                                                       *agent,
                                                       std::move(policy_number),
                                                       std::move(product_name),
                                                       premium,
                                                       start_date,
                                                       end_date,
                                                       created_at);
    std::cout << "Contract created (ID " << contract.get_id() << ").\n";
    sleep_seconds(2);
}

void UI::add_appointment() {
    if (clients.empty()) {
        std::cout << "You need at least one client before scheduling an appointment.\n";
        sleep_seconds(2);
        return;
    }
    if (agents.empty()) {
        std::cout << "There are no agents available to schedule an appointment.\n";
        sleep_seconds(2);
        return;
    }
    Client* client = select_client();
    if (!client) {
        return;
    }
    Agent* agent = select_agent();
    if (!agent) {
        return;
    }

    auto topic_validator = [](const std::string& value) {
        return validate_text_field(value, 3, 120);
    };
    std::string topic = prompt_and_validate("Appointment topic: ",
                                            "Topic must be between 3 and 120 characters.",
                                            normalize_text_single_space,
                                            topic_validator);

    auto trim_only = [](std::string& text) { trim_in_place(text); };
    std::time_t scheduled_for = parse_datetime(prompt_and_validate("Date and time (DD-MM-YYYY HH:MM): ",
                                                                  "Invalid date/time or it is in the past.",
                                                                  trim_only,
                                                                  validate_future_datetime));

    auto optional_text = [this](const std::string& message,
                                const std::function<void(std::string&)>& normalize,
                                const std::function<bool(const std::string&)>& validate,
                                const std::string& error_message) -> std::optional<std::string> {
        std::string input = trim(prompt_line(message));
        if (input.empty()) {
            return std::nullopt;
        }
        std::string value = input;
        normalize(value);
        if (!validate(value)) {
            std::cout << error_message << '\n';
            return std::nullopt;
        }
        return value;
    };

    auto location_validator = [](const std::string& value) { return validate_optional_text(value); };
    std::optional<std::string> location_opt = optional_text("Location (optional): ",
                                                            normalize_address,
                                                            location_validator,
                                                            "Invalid location, value ignored.");
    std::string location = location_opt.value_or(std::string{});

    const Appointment& appointment = manager.create_appointment(*client,
                                                                *agent,
                                                                std::move(topic),
                                                                scheduled_for,
                                                                std::move(location),
                                                                std::time(nullptr));

    std::cout << "Appointment created (ID " << appointment.get_id() << ").\n";
    sleep_seconds(2);
}

void UI::view_interactions_for_client() {
    Client* client = select_client();
    if (!client) {
        return;
    }
    const auto interactions = manager.find_by_client(client->get_id());
    if (interactions.empty()) {
        std::cout << "No interactions found for this client.\n";
        sleep_seconds(2);
        return;
    }
    clear_terminal();
    print_header("Interactions for " + client->get_full_name());
    for (const Interaction* interaction : interactions) {
        if (interaction) {
            interaction->print_interaction();
        }
    }
    wait_for_input();
}

void UI::search_interactions_by_agent() {
    Agent* agent = select_agent();
    if (!agent) {
        return;
    }
    const auto interactions = manager.find_by_agent(agent->get_id());
    if (interactions.empty()) {
        std::cout << "No interactions found for the selected agent.\n";
        sleep_seconds(2);
        return;
    }
    clear_terminal();
    print_header("Interactions handled by " + agent->get_full_name());
    for (const Interaction* interaction : interactions) {
        if (interaction) {
            interaction->print_interaction();
        }
    }
    wait_for_input();
}

void UI::list_all_interactions() {
    clear_terminal();
    print_header("All interactions");
    const auto& interactions = manager.get_interactions();
    if (interactions.empty()) {
        std::cout << "No interactions recorded.\n";
        return;
    }
    for (const auto& ptr : interactions) {
        if (ptr) {
            ptr->print_interaction();
        }
    }
}

void UI::manage_interactions() {
    bool back = false;
    while (!back) {
        clear_terminal();
        print_header("Manage Interactions");
        std::cout << "\n1. Add contract\n";
        std::cout << "2. Add appointment\n";
        std::cout << "3. Show interactions for client\n";
        std::cout << "4. Search interactions by agent\n";
        std::cout << "5. Show all interactions\n";
        std::cout << "6. Back to main menu\n";
        const int choice = prompt_int("\nChoose an option (1-6): ", 1, 6);
        switch (choice) {
        case 1:
            add_contract();
            break;
        case 2:
            add_appointment();
            break;
        case 3:
            view_interactions_for_client();
            break;
        case 4:
            search_interactions_by_agent();
            break;
        case 5:
            list_all_interactions();
            wait_for_input();
            break;
        case 6:
            back = true;
            break;
        default:
            break;
        }
    }
}

void UI::call_load_data(){
    load_data(manager, clients, agents);
    std::cout << "Data succefully loaded.\n";
    std::cout.flush();
    sleep_seconds(2);
}

void UI::save_data(){
    save_clients_to_csv(kClientsFile, clients);
    save_interactions_to_csv(kInteractionsFile, manager);
    std::cout << "Data succefully saved.\n";
    std::cout.flush();
    sleep_seconds(2);
}

std::string UI::prompt_line(const std::string& message) {
    std::cout << message;
    std::string line;
    if (!std::getline(std::cin, line)) {
        throw std::runtime_error("Input interrupted.");
    }
    return line;
}

std::string UI::prompt_non_empty(const std::string& message) {
    while (true) {
        std::string value = trim(prompt_line(message));
        if (!value.empty()) {
            return value;
        }
        std::cout << "Field cannot be empty.\n";
    }
}

std::string UI::prompt_and_validate(const std::string& message,
                                    const std::string& error_message,
                                    const std::function<void(std::string&)>& normalize,
                                    const std::function<bool(const std::string&)>& validate) {
    while (true) {
        std::string value = prompt_non_empty(message);
        normalize(value);
        if (validate(value)) {
            return value;
        }
        std::cout << error_message << '\n';
    }
}

int UI::prompt_int(const std::string& message, int min_value, int max_value) {
    while (true) {
        std::string raw = trim(prompt_line(message));
        try {
            int value = std::stoi(raw);
            if (value < min_value || value > max_value) {
                std::cout << "Enter a number between " << min_value << " and " << max_value << ".\n";
                continue;
            }
            return value;
        } catch (const std::exception&) {
            std::cout << "Invalid numeric value, please try again.\n";
        }
    }
}

double UI::prompt_double(const std::string& message, double min_value) {
    while (true) {
        std::string raw = trim(prompt_line(message));
        try {
            double value = std::stod(raw);
            if (value < min_value) {
                std::cout << "Enter a value greater than or equal to " << min_value << ".\n";
                continue;
            }
            return value;
        } catch (const std::exception&) {
            std::cout << "Invalid numeric value, please use '.' as the decimal separator.\n";
        }
    }
}

std::tm UI::prompt_date_input(const std::string& message) {
    while (true) {
        try {
            return parse_date(trim(prompt_line(message)));
        } catch (const std::exception& ex) {
            std::cout << ex.what() << " Try again.\n";
        }
    }
}

std::time_t UI::prompt_datetime_input(const std::string& message) {
    while (true) {
        try {
            return parse_datetime(trim(prompt_line(message)));
        } catch (const std::exception& ex) {
            std::cout << ex.what() << " Try again.\n";
        }
    }
}

CustomerType UI::prompt_customer_type() {
    std::cout << "Client Type:\n";
    std::cout << "1. Individual\n";
    std::cout << "2. Company\n";
    const int choice = prompt_int("Choose (1-2): ", 1, 2);
    return choice == 1 ? CustomerType::Individual : CustomerType::Company;
}

bool UI::prompt_yes_no(const std::string& message) {
    while (true) {
        std::string answer = trim(prompt_line(message));
        normalize_yes_no(answer);
        if (answer == "y" || answer == "yes") {
            return true;
        }
        if (answer == "n" || answer == "no") {
            return false;
        }
        std::cout << "Please answer 'y' or 'n'.\n";
    }
}

void UI::print_header(std::string header){
    constexpr int kTotalWidth = 80;
    constexpr char kEmptyChar = ' ';
    constexpr char kFillChar = '=';

    if (header.empty()) {
        header = "InsuraPro CRM";
    }

    const int header_length = static_cast<int>(header.size());
    const int total_fill = kTotalWidth - header_length; 
    const int left_fill = total_fill / 2;
    const int right_fill = total_fill - left_fill;

    if (header == "InsuraPro CRM"){
        std::cout << std::string(kTotalWidth, kFillChar) << '\n' 
                << '|' << std::string(left_fill-1, kEmptyChar) << header << std::string(right_fill-1, kEmptyChar) << '|'
                << '|' << std::string(kTotalWidth-2, '-') << '|' << '\n'
                << "| Clients: " << clients.size()
                << "         |         Interactions: " << manager.get_interactions().size()
                << "         |           Agents: " << agents.size() << "  |\n"
                << std::string(kTotalWidth, kFillChar) << '\n' << endl;
    }
    else{
        std::cout << std::string(kTotalWidth, kFillChar) << '\n' 
                << '|' << std::string(left_fill-1, kEmptyChar) << header << std::string(right_fill-1, kEmptyChar) << '|'
                << std::string(kTotalWidth, kFillChar) << '\n';
    }
}

void UI::clear_terminal(){
    #ifdef _WIN32
        std::system("cls");   // Windows
    #else
        std::system("clear"); // Linux / macOS
    #endif
}

void UI::sleep_seconds(int seconds){
    std::this_thread::sleep_for(std::chrono::seconds(seconds));
}

void UI::wait_for_input(){
    std::cout << "\nInsert any key to go back...\n";
    std::cout.flush();

    std::cin.clear();

    if (std::cin.rdbuf()->in_avail() > 0) {
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    }

    std::string dummy;
    std::getline(std::cin, dummy);
}
