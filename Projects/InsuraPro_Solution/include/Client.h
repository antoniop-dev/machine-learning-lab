#ifndef CLIENT_H
#define CLIENT_H
#pragma once

#include <string>
#include <ctime>

using namespace std;

/**
 * @brief Distinguish between individual and corporate customers.
 */
enum class CustomerType {
    Individual,
    Company
};

/**
 * @brief Internal scoring used to capture client exposure level.
 */
enum class RiskCategory{ 
    Low, 
    Medium, 
    High 
};

/**
 * @brief Core entity representing an insured client.
 */
class Client {
    private:
        static int next_id;   // shared variable for auto-incremented ids
        int id;
        std::string name, surname;
        tm date_of_birth;
        std::string fiscal_code;
        std::string phone_number, email, address;
        int accidents;
        RiskCategory risk_category;
        CustomerType customer_type;

    public:
        // Builder
        /**
         * @brief Instantiate a client with mandatory personal details.
         */
        Client(std::string _name, std::string _surname, tm _date_of_birth,
                std::string _fiscal_code, std::string _phone_number,
                std::string _email, std::string _address,
                CustomerType _customer_type);

        // Getters
        /**
         * @brief Retrieve the client's identifier (mutable overload).
         */
        int get_id() noexcept;
        /**
         * @brief Retrieve the client's identifier (const overload).
         */
        const int& get_id() const noexcept;

        /**
         * @brief Access the client's first name (mutable overload).
         */
        std::string get_name() noexcept;
        /**
         * @brief Access the client's first name (const overload).
         */
        const std::string& get_name() const noexcept;

        /**
         * @brief Access the client's surname (mutable overload).
         */
        std::string get_surname() noexcept;
        /**
         * @brief Access the client's surname (const overload).
         */
        const std::string& get_surname() const noexcept;

        /**
         * @brief Compose the client's full name (mutable overload).
         */
        std::string get_full_name() noexcept;
        /**
         * @brief Compose the client's full name (const overload).
         */
        std::string get_full_name() const noexcept;

        /**
         * @brief Retrieve the date of birth (mutable overload).
         */
        tm get_birth() noexcept;
        /**
         * @brief Retrieve the date of birth (const overload).
         */
        const tm& get_birth() const noexcept;

        /**
         * @brief Access the fiscal code (mutable overload).
         */
        std::string get_fiscal_code() noexcept;
        /**
         * @brief Access the fiscal code (const overload).
         */
        const std::string& get_fiscal_code() const noexcept;

        /**
         * @brief Access the phone number (mutable overload).
         */
        std::string get_phone_number() noexcept;
        /**
         * @brief Access the phone number (const overload).
         */
        const std::string& get_phone_number() const noexcept;

        /**
         * @brief Access the email address (mutable overload).
         */
        std::string get_email() noexcept;
        /**
         * @brief Access the email address (const overload).
         */
        const std::string& get_email() const noexcept;

        /**
         * @brief Access the postal address (mutable overload).
         */
        std::string get_address() noexcept;
        /**
         * @brief Access the postal address (const overload).
         */
        const std::string& get_address() const noexcept;

        /**
         * @brief Inspect the current risk category (mutable overload).
         */
        RiskCategory get_risk_category() noexcept;
        /**
         * @brief Inspect the current risk category (const overload).
         */
        const RiskCategory& get_risk_category() const noexcept;

        /**
         * @brief Get the customer's type (mutable overload).
         */
        CustomerType get_customer_type() noexcept;
        /**
         * @brief Get the customer's type (const overload).
         */
        const CustomerType& get_customer_type() const noexcept;

        // Setters
        /**
         * @brief Update the client's first name.
         */
        void set_name(std::string new_name);
        /**
         * @brief Update the client's surname.
         */
        void set_surname(std::string new_surname);
        /**
         * @brief Update the client's phone number.
         */
        void set_phone_number(std::string new_phone);
        /**
         * @brief Update the client's email address.
         */
        void set_email(std::string new_email);
        /**
         * @brief Update the client's mailing address.
         */
        void set_address(std::string new_address);

        // Logic
        /**
         * @brief Register one or more recent accidents against the client.
         *
         * @param _accidents Number of events to add.
         */
        void add_accidents(int _accidents = 1);
        /**
         * @brief Recalculate the risk category according to current data.
         */
        void update_risk_category();

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
         * @brief Output a formatted client summary to stdout.
         */
        void print_client() const;
};

#endif // CLIENT_H
