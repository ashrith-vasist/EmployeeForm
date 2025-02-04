// EmpTable.vue
<template>
  <div>
    <div class="d-flex justify-space-between align-center mb-4">
      <h1>Employee Table</h1>
      <v-btn @click="logout" color="error">Logout</v-btn>
    </div>
    
    <div>
      <div v-if="loading">Loading...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <v-table v-else>
        <thead>
          <tr>
            <th class="text-left">Employee ID</th>
            <th class="text-left">Name</th>
            <th class="text-left">Phone Number</th>
            <th class="text-left">E-mail</th>
            <th class="text-left">Date of Birth</th>
            <th class="text-left">Address</th>
            <th class="text-left">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(employee, index) in employees" :key="index">
            <td>{{ employee.empid }}</td>
            <td>{{ employee.name }}</td>
            <td>{{ employee.phno }}</td>
            <td>{{ employee.email }}</td>
            <td>{{ employee.dob }}</td>
            <td>{{ employee.addr }}</td>
            <td>
              <div class="d-flex">
                <v-btn
                  icon
                  small
                  class="mr-2"
                  @click="editEmployee(employee)"
                  :disabled="employee.email !== currentUserEmail"
                >
                  <v-icon>mdi-pencil</v-icon>
                </v-btn>
                <v-btn
                  icon
                  small
                  color="error"
                  @click="confirmDelete(employee)"
                  :disabled="employee.email !== currentUserEmail"
                >
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </div>
            </td>
          </tr>
        </tbody>
      </v-table>
    </div>

    <!-- Delete Confirmation Dialog -->
    <!-- Delete Confirmation Dialog -->
<v-dialog v-model="deleteDialog" max-width="400">
  <v-card>
    <v-card-title>Confirm Delete</v-card-title>
    <v-card-text>
      Are you sure you want to delete this employee record?
      <div v-if="selectedEmployee" class="mt-2">
        Employee ID: {{ selectedEmployee.empid }}<br>
        Name: {{ selectedEmployee.name }}
      </div>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="grey" text @click="deleteDialog = false">Cancel</v-btn>
      <v-btn color="error" text @click="deleteEmployee">Delete</v-btn>
    </v-card-actions>
  </v-card>
</v-dialog>
  </div>
</template>

<script>
export default {
  data() {
    return {
      employees: [],
      loading: false,
      error: null,
      token: null,
      currentUserEmail: null,
      deleteDialog: false,
      selectedEmployee: null
    }
  },
  created() {
    this.token = localStorage.getItem("access_token")
    if (this.token) {
      this.loadEmployees()
      this.getCurrentUser()
    } else {
      this.$router.push('/login')
    }
  },
  methods: {
    async getCurrentUser() {
      // Get the current user's email from the JWT token
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          const payload = JSON.parse(atob(token.split('.')[1]))
          this.currentUserEmail = payload.sub
        } catch (error) {
          console.error('Error decoding token:', error)
        }
      }
    },
    async loadEmployees() {
      this.loading = true
      try {
        const response = await fetch('http://localhost:8000/EmpList', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        })
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        this.employees = await response.json()
      } catch (error) {
        console.error('Error fetching employees:', error)
        this.error = 'Failed to load employees'
      } finally {
        this.loading = false
      }
    },
    async logout() {
      try {
        await fetch('http://localhost:8000/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        })
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        localStorage.removeItem('access_token')
        this.$router.push('/Emplogin')
      }
    },
    editEmployee(employee) {
      console.log("Edit button")
      this.$router.push(`/edit-employee/${employee.empid}`)
    },
    confirmDelete(employee) {
  console.log('Confirming delete for:', employee); // Debug log
  this.selectedEmployee = {...employee}; // Make a copy of the employee data
  this.deleteDialog = true;
},
    // In EmpTable.vue
async deleteEmployee() {
  if (!this.selectedEmployee) return;
  
  const token = localStorage.getItem('access_token');
  try {
    console.log('Deleting employee:', this.selectedEmployee.empid); // Debug log
    
    const response = await fetch(`http://localhost:8000/employee/${this.selectedEmployee.empid}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to delete employee');
    }

    // Remove the employee from the local list
    this.employees = this.employees.filter(emp => emp.empid !== this.selectedEmployee.empid);
    this.deleteDialog = false;
    
    // Show success message
    alert('Employee deleted successfully');
    
    // If the user deleted their own record, logout
    if (this.selectedEmployee.email === this.currentUserEmail) {
      await this.logout();
    }
  } catch (error) {
    console.error('Error deleting employee:', error);
    alert('Failed to delete employee: ' + error.message);
  } finally {
    this.selectedEmployee = null;
  }
}
  }
}
</script>