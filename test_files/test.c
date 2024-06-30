#include <stdio.h>
#include <string.h>

int login(char username[], char password[]) {
    // Check if the username and password match
    if (strcmp(username, "admin") == 0 && strcmp(password, "password") == 0) {
        return 1; // Login successful
    } else {
        return 0; // Login failed
    }
}

int main() {
    char username[20];
    char password[20];

    printf("Enter username: ");
    scanf("%s", username);

    printf("Enter password: ");
    scanf("%s", password);

    if (login(username, password)) {
        printf("Login successful!\n");
    } else {
        printf("Login failed!\n");
    }

    return 0;
}