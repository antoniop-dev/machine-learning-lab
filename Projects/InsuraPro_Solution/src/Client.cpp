#include "Client.h"

#include <string>
#include <iostream>
#include <sstream>

#include "utilities/utils.h"

using namespace std;

int Client::next_id = 0;

// Builder
Client::Client(string _name, string _surname, tm _date_of_birth,
               string _fiscal_code, string _phone_number,
               string _email, string _address,
               CustomerType _customer_type){
    id = ++next_id;
    name = _name;
    surname = _surname;
    date_of_birth = _date_of_birth;
    fiscal_code = _fiscal_code;
    phone_number = _phone_number;
    email = _email;
    address = _address;
    accidents = 0;
    update_risk_category();
    customer_type = _customer_type;
}


// Getters
int Client::get_id() noexcept { return id; }
const int& Client::get_id() const noexcept { return id; }

string Client::get_name() noexcept { return name; }
const std::string& Client::get_name() const noexcept { return name; }

string Client::get_surname() noexcept { return surname; }
const std::string& Client::get_surname() const noexcept { return surname; }

string Client::get_full_name() noexcept {
  string fullname = name;
  fullname.push_back(' ');
  fullname += surname;
  return fullname;
}
std::string Client::get_full_name() const noexcept {
  string fullname = name;
  fullname.push_back(' ');
  fullname += surname;
  return fullname;
}

tm Client::get_birth() noexcept { return date_of_birth; }
const tm& Client::get_birth() const noexcept { return date_of_birth; }

string Client::get_fiscal_code() noexcept { return fiscal_code; }
const string& Client::get_fiscal_code() const noexcept { return fiscal_code; }

string Client::get_phone_number() noexcept { return phone_number; }
const string & Client::get_phone_number() const noexcept { return phone_number; }

string Client::get_email() noexcept { return email; }
const string& Client::get_email() const noexcept { return email; }

string Client::get_address() noexcept { return address; }
const string& Client::get_address() const noexcept { return address; }

RiskCategory Client::get_risk_category() noexcept { return risk_category; }
const RiskCategory& Client::get_risk_category() const noexcept { return risk_category; }

CustomerType Client::get_customer_type() noexcept { return customer_type; }
const CustomerType& Client::get_customer_type() const noexcept { return customer_type; }

// Setters
void Client::set_name(string new_name) { name = new_name; }

void Client::set_surname(string new_surname) { surname = new_surname; }

void Client::set_phone_number(string new_phone) { phone_number = new_phone; }

void Client::set_email(string new_email) { email = new_email; }

void Client::set_address(string new_address) { address = new_address; }

// Logic
void Client::add_accidents(int _accidents) {
    accidents += _accidents;
    update_risk_category();
}

void Client::update_risk_category() {
    if (accidents == 0) risk_category = RiskCategory::Low;
    else if (accidents < 3) risk_category = RiskCategory::Medium;
    else risk_category = RiskCategory::High;
}

int Client::current_id_seed() noexcept { return next_id; }

void Client::set_next_id_seed(int value) noexcept { next_id = value; }

void Client::print_client() const {
  std::ostringstream oss;
  oss << "\n| ID " << get_id() 
      << "\n| Name: " << get_full_name()
      << "\n| Birth: " << format_date(get_birth())
      << "\n| Tax ID: " << get_fiscal_code()
      << "\n| Phone: " << get_phone_number()
      << "\n| Email: " << get_email()
      << "\n| Type: " << customer_type_to_string(get_customer_type())
      << '\n';
  std::cout << oss.str();
}
