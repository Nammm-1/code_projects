#include <iostream>
#include <fstream>
#include <unistd.h> // For sleep and usleep functions
#ifdef _WIN32
#include <windows.h>
#else
#include <ApplicationServices/ApplicationServices.h>
#endif

// Function to log details to a file and display them in the console
void logDetails(const std::string& message) {
    // Log to console
    std::cout << message << std::endl;
    
    // Log to file
    std::ofstream logFile("keystrokes.log", std::ios::app); // Open in append mode
    if (logFile.is_open()) {
        logFile << message << std::endl;
        logFile.close();
    } else {
        std::cerr << "Error: Unable to open log file." << std::endl;
    }
}

void sendKeystroke(const std::string& text) {
    for (char c : text) {
        // Log the character being sent
        logDetails("Sending character: " + std::string(1, c));
        
#ifdef _WIN32
        // Windows-specific code
        INPUT ip;
        ip.type = INPUT_KEYBOARD;
        ip.ki.wScan = 0;
        ip.ki.time = 0;
        ip.ki.dwExtraInfo = 0;
        
        // Create a key down event
        ip.ki.wVk = VkKeyScanA(c); // Get the virtual key code for the character
        ip.ki.dwFlags = 0; // Key down
        SendInput(1, &ip, sizeof(INPUT));
        
        // Create a key up event
        ip.ki.dwFlags = KEYEVENTF_KEYUP; // Key up
        SendInput(1, &ip, sizeof(INPUT));
        
        // Small delay between keystrokes
        usleep(10000); // 10ms delay
#else
        // macOS-specific code
        // Create a key down event
        CGEventRef keyDown = CGEventCreateKeyboardEvent(nullptr, 0, true);
        UniChar character = c;
        CGEventKeyboardSetUnicodeString(keyDown, 1, &character);
        CGEventPost(kCGSessionEventTap, keyDown);
        CFRelease(keyDown);
        
        // Create a key up event
        CGEventRef keyUp = CGEventCreateKeyboardEvent(nullptr, 0, false);
        CGEventKeyboardSetUnicodeString(keyUp, 1, &character);
        CGEventPost(kCGSessionEventTap, keyUp);
        CFRelease(keyUp);
        
        // Small delay between keystrokes
        usleep(10000); // 10ms delay
#endif
    }
}

int main() {
    std::string textToSend;
    int delaySeconds;
    
    // Get user input for the text to send
    std::cout << "Enter the text to simulate as keystrokes: ";
    std::getline(std::cin, textToSend);
    
    // Get user input for the delay before sending keystrokes
    std::cout << "Enter the delay (in seconds) before sending keystrokes: ";
    std::cin >> delaySeconds;
    
    // Log the user inputs
    logDetails("User input - Text to send: " + textToSend);
    logDetails("User input - Delay: " + std::to_string(delaySeconds) + " seconds");
    
    std::cout << "Starting keystroke simulation in " << delaySeconds << " seconds..." << std::endl;
    
    // Wait for the specified delay
    sleep(delaySeconds);
    
    // Send the keystrokes
    sendKeystroke(textToSend);
    
    std::cout << "Keystrokes sent. Check 'keystrokes.log' for details." << std::endl;
    return 0;
}
