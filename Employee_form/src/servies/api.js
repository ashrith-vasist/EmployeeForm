// src/services/api.js

// Base configuration
const API_BASE_URL = 'http://localhost:8000'

// Helper function for handling responses
const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => null)
    throw new Error(error?.detail || `HTTP error! status: ${response.status}`)
  }
  return response.json()
}

// API service object
export const employeeApi = {
  // Create new employee
  async createEmployee(employeeData) {
    try {
      const response = await fetch(`${API_BASE_URL}/emp`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(employeeData)
      })
      return handleResponse(response)
    } catch (error) {
      throw new Error(`Failed to create employee: ${error.message}`)
    }
  },

  // Get all employees (if you need this functionality)
  async getEmployees() {
    try {
      const response = await fetch(`${API_BASE_URL}/emp`)
      return handleResponse(response)
    } catch (error) {
      throw new Error(`Failed to fetch employees: ${error.message}`)
    }
  },

  // Get employee by ID (if you need this functionality)
  async getEmployeeById(empId) {
    try {
      const response = await fetch(`${API_BASE_URL}/emp/${empId}`)
      return handleResponse(response)
    } catch (error) {
      throw new Error(`Failed to fetch employee: ${error.message}`)
    }
  }
}