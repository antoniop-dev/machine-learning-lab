#include "Agent.h"

#include <string>
#include <sstream>
#include <iostream>

#include "Client.h"
#include "utilities/utils.h"

int Agent::next_id = 0;

using namespace std;

// Builder
Agent::Agent(string _name, string _surname, tm d_o_b,
    string _email, string _phone_number, tm _hire_date)
    : id(++next_id),
      name(_name),
      surname(_surname),
      date_of_birth(d_o_b),
      email(_email),
      phone_number(_phone_number), hire_date(_hire_date) {}  

// Getters

int Agent::get_id() noexcept { return id; }
const int& Agent::get_id() const noexcept { return id; }

string Agent::get_name() noexcept { return name; }
const string& Agent::get_name() const noexcept { return name; }

string Agent::get_surname() noexcept { return surname; }
const string& Agent::get_surname() const noexcept { return surname; }

string Agent::get_full_name() noexcept {
  string fullname = name;
  fullname.push_back(' ');
  fullname += surname;
  return fullname;
}
string Agent::get_full_name() const noexcept {
  string fullname = name;
  fullname.push_back(' ');
  fullname += surname;
  return fullname;
}

string Agent::get_email() noexcept { return email; }
const string& Agent::get_email() const noexcept { return email; }

string Agent::get_phone_number() noexcept { return phone_number; }
const string& Agent::get_phone_number() const noexcept { return phone_number; }

tm Agent::get_hire_date() noexcept { return hire_date; }
const tm& Agent::get_hire_date() const noexcept { return hire_date; }

tm Agent::get_birth_date() noexcept { return date_of_birth; }
const tm& Agent::get_birth_date() const noexcept { return date_of_birth; }

const vector<shared_ptr<Client>>& Agent::get_clients() const { return clients; }

// Setters

void Agent::set_email(string new_email){ email = new_email; }

void Agent::set_phone_number(string new_phone){ phone_number = new_phone; }

// Logic
void Agent::add_client(shared_ptr<Client> c){ clients.push_back(std::move(c)); }

int Agent::current_id_seed() noexcept { return next_id; }

void Agent::set_next_id_seed(int value) noexcept { next_id = value; }

void Agent::print_agent() const {
  std::ostringstream oss;
    oss << "\n| ID " << get_id() 
        << "\n| Name: " << get_full_name()
        << "\n| Date of Birth: " << format_date(get_birth_date())
        << "\n| Phone: " << get_phone_number()
        << "\n| Email: " << get_email()
        << "\n| Hired Date: " << format_date(get_hire_date())
        << '\n';
    std::cout << oss.str();
}
