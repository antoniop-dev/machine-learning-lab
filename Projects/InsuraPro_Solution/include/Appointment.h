#ifndef APPOINTMENT_H
#define APPOINTMENT_H
#pragma once

#include <ctime>
#include <string>

#include "Interaction.h"

class InteractionManager; // forward declaration

/**
 * @brief Interaction recording a scheduled appointment between client and agent.
 */
class Appointment : public Interaction {
    friend class InteractionManager;
    public:
        /**
         * @brief Create a new appointment occurrence.
         */
        Appointment(Client& _client,
                    Agent& _agent,
                    std::string _topic,
                    std::time_t _scheduled_for,
                    std::string _location = {},
                    std::time_t _created_at = std::time(nullptr));

        /**
         * @brief Access the appointment topic.
         */
        const std::string& get_topic() const noexcept;
        /**
         * @brief Access the appointment location.
         */
        const std::string& get_location() const noexcept;
        /**
         * @brief Retrieve the scheduled datetime.
         */
        std::time_t get_scheduled_for() const noexcept;
        /**
         * @brief Determine whether the appointment has been completed.
         */
        bool is_completed() const noexcept;
        /**
         * @brief Retrieve the completion timestamp if applicable.
         */
        std::time_t get_completed_at() const noexcept;

        /**
         * @brief Change the appointment topic.
         */
        void set_topic(std::string new_topic);
        /**
         * @brief Change the appointment location.
         */
        void set_location(std::string new_location);
        /**
         * @brief Move the appointment to a different time.
         */
        void reschedule(std::time_t new_scheduled_for) noexcept;
        /**
         * @brief Mark the appointment as completed.
         */
        void mark_completed(std::time_t completed_timestamp = std::time(nullptr)) noexcept;

        /**
         * @brief Provide a human-readable interaction type label.
         */
        std::string type_name() const override;
        /**
         * @brief Generate a short description of the appointment.
         */
        std::string summary() const override;
        /**
         * @brief Print the appointment details to stdout.
         */
        void print_interaction() const override;

    private:
        std::string topic;
        std::string location;
        std::time_t scheduled_for;
        bool completed;
        std::time_t completed_at;
};

#endif // APPOINTMENT_H
