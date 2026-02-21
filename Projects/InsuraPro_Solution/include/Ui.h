#ifndef UI_H
#define UI_H
#pragma once

#include <functional>

#include "InteractionManager.h"
#include "Client.h"
#include "Agent.h"

using ClientStore = std::unordered_map<int, std::unique_ptr<Client>>;
using AgentStore = std::unordered_map<int, std::unique_ptr<Agent>>;

/**
 * @brief Text-based user interface orchestrating user interactions.
 */
class UI {
public:
    /**
     * @brief Construct the UI with preloaded repositories and manager.
     */
    UI(AgentStore _agents, ClientStore _clients, InteractionManager _manager);
    /**
     * @brief Enter the interactive main loop.
     */
    void run();

    ClientStore clients;
    AgentStore agents;
    InteractionManager manager;

private:
    /**
     * @brief Load persisted data from storage via helper utilities.
     */
    void call_load_data();
    /**
     * @brief Persist the current in-memory data to disk.
     */
    void save_data();

    /**
     * @brief Present the main navigation menu.
     */
    void show_main_menu();
    /**
     * @brief Gather details for a new client and insert it.
     */
    void add_client();
    /**
     * @brief Display the list of clients.
     */
    void list_clients();
    /**
     * @brief Edit an existing client record.
     */
    void edit_client();
    /**
     * @brief Delete a client from the repository.
     */
    void delete_client();
    /**
     * @brief Search clients filtering by user-defined criteria.
     */
    void search_clients();

    /**
     * @brief Entry point for interaction management submenu.
     */
    void manage_interactions();
    /**
     * @brief Collect inputs and create a contract interaction.
     */
    void add_contract();
    /**
     * @brief Collect inputs and create an appointment interaction.
     */
    void add_appointment();
    /**
     * @brief Show interactions associated with a chosen client.
     */
    void view_interactions_for_client();
    /**
     * @brief Show interactions associated with a chosen agent.
     */
    void search_interactions_by_agent();
    /**
     * @brief List every stored interaction.
     */
    void list_all_interactions();

    /**
     * @brief Prompt the user to choose a client.
     *
     * @return Pointer to the selected client or nullptr on cancellation.
     */
    Client* select_client();
    /**
     * @brief Prompt the user to choose an agent.
     *
     * @return Pointer to the selected agent or nullptr on cancellation.
     */
    Agent* select_agent();
    /**
     * @brief Display all registered agents.
     */
    void list_agents();

    /**
     * @brief Read a raw line of user input after showing a message.
     */
    std::string prompt_line(const std::string& message);
    /**
     * @brief Prompt until a non-empty line is provided.
     */
    std::string prompt_non_empty(const std::string& message);
    /**
     * @brief Prompt, normalize and validate textual input.
     */
    std::string prompt_and_validate(const std::string& message,
                                    const std::string& error_message,
                                    const std::function<void(std::string&)>& normalize,
                                    const std::function<bool(const std::string&)>& validate);
    /**
     * @brief Prompt for an integer within inclusive bounds.
     */
    int prompt_int(const std::string& message, int min_value, int max_value);
    /**
     * @brief Prompt for a floating-point value above a minimum.
     */
    double prompt_double(const std::string& message, double min_value);
    /**
     * @brief Prompt the user to enter a calendar date.
     */
    std::tm prompt_date_input(const std::string& message);
    /**
     * @brief Prompt the user to enter a date and time.
     */
    std::time_t prompt_datetime_input(const std::string& message);
    /**
     * @brief Prompt for the customer type selection.
     */
    CustomerType prompt_customer_type();
    /**
     * @brief Prompt for a yes/no answer.
     */
    bool prompt_yes_no(const std::string& message);
    /**
     * @brief Print a formatted header within the terminal width.
     */
    void print_header(std::string header);
    /**
     * @brief Clear the terminal screen.
     */
    void clear_terminal();
    /**
     * @brief Sleep the current thread for the given number of seconds.
     */
    void sleep_seconds(int seconds);
    /**
     * @brief Display a message and wait for the user to press a key.
     */
    void wait_for_input();
};

#endif //UI_H
