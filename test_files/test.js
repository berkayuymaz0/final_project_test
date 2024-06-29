const assert = require('assert');
const login = require('../src/login');

// Import the necessary modules for testing

// Test case 1: Valid credentials
it('should return true for valid credentials', () => {
    const result = login('username', 'password');
    assert.strictEqual(result, true);
});

// Test case 2: Invalid username
it('should return false for invalid username', () => {
    const result = login('invalid_username', 'password');
    assert.strictEqual(result, false);
});

// Test case 3: Invalid password
it('should return false for invalid password', () => {
    const result = login('username', 'invalid_password');
    assert.strictEqual(result, false);
});

// Test case 4: Empty username and password
it('should return false for empty username and password', () => {
    const result = login('', '');
    assert.strictEqual(result, false);
});