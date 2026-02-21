#include "Contract.h"

#include <ctime>
#include <sstream>
#include <utility>
#include <iomanip>

#include "utilities/utils.h"

namespace {
std::time_t normalize_timestamp(std::time_t value, std::time_t fallback) noexcept {
    return value != std::time_t{} ? value : fallback;
}

bool is_active_for_now(std::time_t end) noexcept {
    if (end == std::time_t{}) {
        return true;
    }
    const std::time_t now = std::time(nullptr);
    return end >= now;
}
} // namespace

Contract::Contract(Client& _client,
                   Agent& _agent,
                   std::string _policy_number,
                   std::string _product_name,
                   double _premium,
                   std::time_t _start_date,
                   std::time_t _end_date,
                   std::time_t _created_at)
    : Interaction(_client, _agent, normalize_timestamp(_created_at, std::time(nullptr))),
      policy_number(std::move(_policy_number)),
      product_name(std::move(_product_name)),
      premium(_premium >= 0.0 ? _premium : 0.0),
      start_date(normalize_timestamp(_start_date, std::time(nullptr))),
      end_date(_end_date),
      active(is_active_for_now(_end_date)) {}

const std::string& Contract::get_policy_number() const noexcept { return policy_number; }

const std::string& Contract::get_product_name() const noexcept { return product_name; }

double Contract::get_premium() const noexcept { return premium; }

std::time_t Contract::get_start_date() const noexcept { return start_date; }

std::time_t Contract::get_end_date() const noexcept { return end_date; }

bool Contract::is_active() const noexcept { return active; }

void Contract::set_product_name(std::string new_product_name) { product_name = std::move(new_product_name); }

void Contract::set_premium(double new_premium) noexcept { premium = new_premium >= 0.0 ? new_premium : 0.0; }

void Contract::set_end_date(std::time_t new_end_date) noexcept {
    end_date = new_end_date;
    active = is_active_for_now(end_date);
}

void Contract::activate(std::time_t new_start_date) noexcept {
    start_date = normalize_timestamp(new_start_date, std::time(nullptr));
    end_date = std::time_t{};
    active = true;
}

void Contract::terminate(std::time_t new_end_date) noexcept {
    end_date = normalize_timestamp(new_end_date, std::time(nullptr));
    active = false;
}

std::string Contract::type_name() const { return "Contract"; }

std::string Contract::summary() const {
    std::ostringstream oss;
    const Client& interaction_client = get_client();
    const Agent& interaction_agent = get_agent();
    oss << "Contract " << policy_number << " (" << product_name << ") for "
        << interaction_client.get_full_name() << " handled by "
        << interaction_agent.get_full_name()
        << " premium " << premium;
    if (active) {
        oss << " [active]";
    } else {
        oss << " [terminated]";
    }
    return oss.str();
}

void Contract::print_interaction() const {
    std::ostringstream oss;
    oss << "\n[Contract] ID " << get_id()
        << "\n | Client: " << client.get_full_name()
        << "\n | Agent: " << agent.get_full_name()
        << "\n | Policy Number: " << get_policy_number()
        << "\n | Product: " << get_product_name()
        << "\n | Premium: " << std::fixed << std::setprecision(2) << get_premium()
        << std::defaultfloat
        << "\n | Start: " << format_timestamp(get_start_date())
        << "\n | End: " << format_timestamp(get_end_date())
        << "\n | State: " << (is_active() ? "Active" : "Terminated")
        << "\n | Created: " << format_timestamp(get_timestamp());
    std::cout << oss.str() << '\n';
}
