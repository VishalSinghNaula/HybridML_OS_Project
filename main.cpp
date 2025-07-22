#include <iostream>
#include <thread>
#include <mutex>
#include <fstream>
#include <unistd.h>
#include <arpa/inet.h>
#include <cstring>
#include <chrono>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

std::mutex mtx;
int counter = 0;
const std::string INPUT_FILE = "/mnt/c/Users/hp/Desktop/HybridML_OS_Project/thread_input.txt";

void sendToGUI(const std::string& message) {
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    sockaddr_in gui_addr{};
    gui_addr.sin_family = AF_INET;
    gui_addr.sin_port = htons(65433);
    inet_pton(AF_INET, "127.0.0.1", &gui_addr.sin_addr);
    
    sendto(sock, message.c_str(), message.size(), 0, 
          (struct sockaddr*)&gui_addr, sizeof(gui_addr));
    close(sock);
}

int getPredictionFromPython(int cpu, int wait, int conflict, int priority, int deadline) {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        std::cerr << "Socket creation error" << std::endl;
        return -1;
    }

    struct timeval tv;
    tv.tv_sec = 3;
    tv.tv_usec = 0;
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
    setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));

    sockaddr_in serv_addr{};
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(65432);
    inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr);

    if (connect(sock, (sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
        std::cerr << "Connection to ML server failed" << std::endl;
        close(sock);
        return -1;
    }

    char sendBuf[1024];
    snprintf(sendBuf, sizeof(sendBuf), "%d,%d,%d,%d,%d", cpu, wait, conflict, priority, deadline);
    
    if (send(sock, sendBuf, strlen(sendBuf), 0) < 0) {
        std::cerr << "Send failed" << std::endl;
        close(sock);
        return -1;
    }

    char recvBuf[1024] = {0};
    int valread = read(sock, recvBuf, sizeof(recvBuf));
    if (valread <= 0) {
        std::cerr << "Read failed or timeout" << std::endl;
        close(sock);
        return -1;
    }

    close(sock);
    return atoi(recvBuf);
}

void processThreadRequest() {
    std::ifstream fin(INPUT_FILE);
    if (!fin.is_open()) {
        std::cerr << "Cannot open input file" << std::endl;
        return;
    }

    int cpu, wait, conflicts, priority, deadline;
    fin >> cpu >> wait >> conflicts >> priority >> deadline;
    fin.close();

    std::cout << "Processing thread: CPU=" << cpu 
              << " Wait=" << wait 
              << " Conflicts=" << conflicts
              << " Priority=" << priority
              << " Deadline=" << deadline << std::endl;

    int decision = getPredictionFromPython(cpu, wait, conflicts, priority, deadline);
    
    json message;
    if (decision < 0) {
        std::cerr << "Prediction error occurred" << std::endl;
        message = {{"type", "error"}, {"cpu", cpu}};
    } else if (decision == 1) {
        std::unique_lock<std::mutex> lock(mtx);
        counter++;
        message = {
            {"type", "execution"},
            {"cpu", cpu},
            {"counter", counter}
        };
        std::cout << "Thread executed. Total threads: " << counter << std::endl;
    } else {
        message = {
            {"type", "denied"},
            {"cpu", cpu},
            {"reason", "re-check failed"}
        };
        std::cout << "Thread denied after re-check" << std::endl;
    }
    
    sendToGUI(message.dump());
    remove(INPUT_FILE.c_str());
}

int main() {
    std::cout << "C++ Thread Scheduler started" << std::endl;
    std::cout << "Monitoring: " << INPUT_FILE << std::endl;

    while (true) {
        if (access(INPUT_FILE.c_str(), F_OK) == 0) {
            processThreadRequest();
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    return 0;
}