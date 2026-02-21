#include "Agent.h"
#include "Appointment.h"
#include "Client.h"
#include "Contract.h"
#include "Interaction.h"
#include "InteractionManager.h"
#include "Ui.h"
#include "utilities/utils.h"
#include "utilities/file_utils.h"

#include <utility>
#include <iostream>
#include <thread>

int main(){
    std::cout << "\n\nFor an optized experience set terminal size to 80 columns (80xYY)...\n\n";
    std::cout.flush();
    std::this_thread::sleep_for(std::chrono::seconds(5));
    AgentStore agents;
    ClientStore clients;
    InteractionManager manager;

    load_data(manager, clients, agents);
    UI ui = UI(std::move(agents), std::move(clients), std::move(manager));
    ui.run();
    
    return 0;
}
