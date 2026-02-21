#ifndef AGENT_H
#define AGENT_H
#pragma once

#include <string>
#include <vector>
#include <memory>
#include "Client.h"

class Client; // forward declaration

/**
 * @brief Represents an insurance agent and their assigned clients.
 */
class Agent {
    private:
        static int next_id; // shared variable for auto-incremented ids
        int id;
        std::string name, surname;
        tm date_of_birth;
        std::string email, phone_number;
        tm hire_date;
        std::vector<std::shared_ptr<Client>> clients;
    
    public:
        // Builder
        /**
         * @brief Construct a new agent with the provided profile details.
         */
        Agent(std::string _name, std::string _surname, tm d_o_b,
            std::string _email, std::string _phone_number, tm _hire_date);
        
        // Getters
        /**
         * @brief Retrieve the assigned identifier (mutable overload).
         */
        int get_id() noexcept;
        /**
         * @brief Retrieve the assigned identifier (const overload).
         */
        const int& get_id() const noexcept;

        /**
         * @brief Get the agent's first name (mutable overload).
         */
        std::string get_name() noexcept;
        /**
         * @brief Get the agent's first name (const overload).
         */
        const std::string& get_name() const noexcept;

        /**
         * @brief Get the agent's surname (mutable overload).
         */
        std::string get_surname() noexcept;
        /**
         * @brief Get the agent's surname (const overload).
         */
        const std::string& get_surname() const noexcept;

        /**
         * @brief Compose the agent's full name (mutable overload).
         */
        std::string get_full_name() noexcept;
        /**
         * @brief Compose the agent's full name (const overload).
         */
        std::string get_full_name() const noexcept;

        /**
         * @brief Retrieve the agent's email address (mutable overload).
         */
        std::string get_email() noexcept;
        /**
         * @brief Retrieve the agent's email address (const overload).
         */
        const std::string& get_email() const noexcept;

        /**
         * @brief Retrieve the agent's phone number (mutable overload).
         */
        std::string get_phone_number() noexcept;
        /**
         * @brief Retrieve the agent's phone number (const overload).
         */
        const std::string& get_phone_number() const noexcept;

        /**
         * @brief Retrieve the hire date (mutable overload).
         */
        tm get_hire_date() noexcept;
        /**
         * @brief Retrieve the hire date (const overload).
         */
        const tm& get_hire_date() const noexcept;

        /**
         * @brief Retrieve the date of birth (mutable overload).
         */
        tm get_birth_date() noexcept;
        /**
         * @brief Retrieve the date of birth (const overload).
         */
        const tm& get_birth_date() const noexcept;

        /**
         * @brief Access the list of clients assigned to the agent.
         */
        const std::vector<std::shared_ptr<Client>>& get_clients() const;

        // Setters
        /**
         * @brief Update the agent's email address.
         */
        void set_email(std::string new_email);
        /**
         * @brief Update the agent's phone number.
         */
        void set_phone_number(std::string new_phone);

        // Logic
        /**
         * @brief Associate a new client with the agent.
         */
        void add_client(std::shared_ptr<Client> c);

        /**
         * @brief Inspect the current id seed used for auto-increment.
         */
        static int current_id_seed() noexcept;
        /**
         * @brief Override the next id seed (used during data loading).
         */
        static void set_next_id_seed(int value) noexcept;

        // Print
        /**
         * @brief Write a formatted summary of the agent to stdout.
         */
        void print_agent() const;
};

#endif //AGENT_H
