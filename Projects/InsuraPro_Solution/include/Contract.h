#ifndef CONTRACT_H
#define CONTRACT_H
#pragma once

#include <ctime>
#include <string>

#include "Interaction.h"

class InteractionManager; // forward declaration

/**
 * @brief Interaction describing an insurance contract lifecycle.
 */
class Contract : public Interaction {
    friend class InteractionManager;

protected:
    /**
     * @brief Base constructor used by factories to instantiate contracts.
     */
    Contract(Client& _client,
             Agent& _agent,
             std::string _policy_number,
             std::string _product_name,
             double _premium,
             std::time_t _start_date,
             std::time_t _end_date = std::time_t{},
             std::time_t _created_at = std::time(nullptr));

public:
    /**
     * @brief Access the unique policy number.
     */
    const std::string& get_policy_number() const noexcept;
    /**
     * @brief Access the name of the insured product.
     */
    const std::string& get_product_name() const noexcept;
    /**
     * @brief Retrieve the premium amount.
     */
   double get_premium() const noexcept;
    /**
     * @brief Retrieve the contract start date.
     */
    std::time_t get_start_date() const noexcept;
    /**
     * @brief Retrieve the contract end date.
     */
    std::time_t get_end_date() const noexcept;
    /**
     * @brief Check if the contract is currently active.
     */
    bool is_active() const noexcept;

    /**
     * @brief Update the human-readable product name.
     */
    void set_product_name(std::string new_product_name);
    /**
     * @brief Update the premium value.
     */
    void set_premium(double new_premium) noexcept;
    /**
     * @brief Adjust the contract end date.
     */
    void set_end_date(std::time_t _end_date) noexcept;

    /**
     * @brief Activate the contract from the provided start date.
     */
    void activate(std::time_t start_date) noexcept;
    /**
     * @brief Terminate the contract, setting the end date.
     */
    void terminate(std::time_t end_date) noexcept;

    /**
     * @brief Provide a human-readable interaction type label.
     */
    std::string type_name() const override;
    /**
     * @brief Generate a short textual summary of the contract.
     */
    std::string summary() const override;
    /**
     * @brief Print the contract details to stdout.
     */
    void print_interaction() const override;

private:
    std::string policy_number;
    std::string product_name;
    double premium;
    std::time_t start_date;
    std::time_t end_date;
    bool active;
};

#endif // CONTRACT_H
