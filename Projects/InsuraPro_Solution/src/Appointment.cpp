#include "Appointment.h"

#include <ctime>
#include <sstream>
#include <utility>

#include "utilities/utils.h"

namespace {
std::time_t normalize_timestamp(std::time_t value, std::time_t fallback) noexcept {
    return value != std::time_t{} ? value : fallback;
}
} // namespace

Appointment::Appointment(Client& _client,
                         Agent& _agent,
                         std::string _topic,
                         std::time_t _scheduled_for,
                         std::string _location,
                         std::time_t _created_at)
    : Interaction(_client, _agent, normalize_timestamp(_created_at, std::time(nullptr))),
      topic(std::move(_topic)),
      location(std::move(_location)),
      scheduled_for(normalize_timestamp(_scheduled_for, std::time(nullptr))),
      completed(false),
      completed_at(std::time_t{}) {}

const std::string& Appointment::get_topic() const noexcept { return topic; }

const std::string& Appointment::get_location() const noexcept { return location; }

std::time_t Appointment::get_scheduled_for() const noexcept { return scheduled_for; }

bool Appointment::is_completed() const noexcept { return completed; }

std::time_t Appointment::get_completed_at() const noexcept { return completed_at; }

void Appointment::set_topic(std::string new_topic) { topic = std::move(new_topic); }

void Appointment::set_location(std::string new_location) { location = std::move(new_location); }

void Appointment::reschedule(std::time_t new_scheduled_for) noexcept {
    scheduled_for = normalize_timestamp(new_scheduled_for, std::time(nullptr));
    completed = false;
    completed_at = std::time_t{};
}

void Appointment::mark_completed(std::time_t completed_timestamp) noexcept {
    completed = true;
    completed_at = normalize_timestamp(completed_timestamp, std::time(nullptr));
}

std::string Appointment::type_name() const { return "Appointment"; }

std::string Appointment::summary() const {
    std::ostringstream oss;
    const Client& meeting_client = get_client();
    const Agent& meeting_agent = get_agent();
    oss << "Appointment on " << scheduled_for << " about " << topic << " with "
        << meeting_client.get_name() << ' ' << meeting_client.get_surname() << " handled by "
        << meeting_agent.get_name() << ' ' << meeting_agent.get_surname();
    if (!location.empty()) {
        oss << " at " << location;
    }
    if (completed) {
        oss << " [completed]";
    } else {
        oss << " [scheduled]";
    }
    return oss.str();
}

void Appointment::print_interaction() const {
    std::ostringstream oss;
    oss << "\n[Appointment] ID " << get_id()
        << "\n | Client: " << get_client().get_full_name()
        << "\n | Agent: " << get_agent().get_full_name()
        << "\n | Topic: " << get_topic()
        << "\n | When: " << format_timestamp(get_scheduled_for());
    if (!get_location().empty()) {
        oss << "\n | Location: " << get_location();
    }
    oss << "\n | State: " << (is_completed() ? "Completed" : "Scheduled");
    if (is_completed()) {
        oss << "\n | Ended: " << format_timestamp(get_completed_at());
    }
    oss << "\n | Created: " << format_timestamp(get_timestamp());
    std::cout << oss.str() << '\n';
}
