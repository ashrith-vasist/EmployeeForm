<template>
  <div>
    <h1>Edit Employee Information</h1>
    <br>
    <form @submit.prevent="submitForm" v-if="employee">
      <v-text-field
        v-model="employee.name"
        label="Name"
        required
      ></v-text-field>

      <v-text-field
        v-model="employee.phno"
        label="Phone Number"
        required
      ></v-text-field>

      <v-text-field
        v-model="employee.email"
        label="E-mail"
        required
        :rules="[rules.email]"
      ></v-text-field>

      <v-text-field
        v-model="employee.dob"
        label="Date of Birth"
        required
      ></v-text-field>

      <v-text-field
        v-model="employee.addr"
        label="Address"
        required
      ></v-text-field>

      <v-btn
        class="me-4"
        type="submit"
        :loading="loading"
      >
        Update
      </v-btn>

      <v-btn @click="$router.push('/EmpTable')">
        Cancel
      </v-btn>
    </form>
  </div>
</template>

<script>
export default {
  name: 'EditEmployee',
  data() {
    return {
      employee: null,
      loading: false,
      error: null,
      rules: {
        email: v => /.+@.+\..+/.test(v) || 'E-mail must be valid'
      }
    };
  },

  created() {
    // Get the token
    const token = localStorage.getItem('access_token');
    if (!token) {
      this.$router.push('/login');
      return;
    }

    // Get the empid from the route parameters
    const empid = this.$route.params.empid;

    if (!empid) {
      this.$router.push('/EmpTable');
      return;
    }

    // Fetch employee data based on the empid
    this.loadEmployeeData(empid);
  },

  methods: {
    async loadEmployeeData(empid) {
      this.loading = true;

      try {
        const response = await fetch(`http://localhost:8000/employee/${empid}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

        if (!response.ok) {
          throw new Error('Failed to fetch employee data');
        }

        this.employee = await response.json();
      } catch (error) {
        console.error('Error fetching employee data:', error);
        this.error = 'Failed to load employee data';
      } finally {
        this.loading = false;
      }
    },

    async submitForm() {
      this.loading = true;
      const token = localStorage.getItem('access_token');

      try {
        const response = await fetch(`http://localhost:8000/employee/${this.employee.empid}`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            name: this.employee.name,
            phno: this.employee.phno,
            email: this.employee.email,
            dob: this.employee.dob,
            addr: this.employee.addr
          })
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to update employee');
        }

        // Navigate back to table
        this.$router.push('/EmpTable');
      } catch (error) {
        console.error('Error updating employee:', error);
        alert(error.message);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
