
<!-- Login.vue -->
<template>
    <h1>Employee Login</h1>
    <br>
    <form @submit.prevent="submitForm">
      <v-text-field
        v-model="email"
        :error-messages="emailError"
        label="E-mail"
      ></v-text-field>
      <v-text-field
        v-model="password"
        :append-icon="show1 ? 'mdi-eye' : 'mdi-eye-off'"
        :rules="[rules.required, rules.min]"
        :type="show1 ? 'text' : 'password'"
        hint="At least 8 characters"
        label="Password"
        counter
        @click:append="show1 = !show1"
      ></v-text-field>
      <v-btn class="me-4" type="submit" :loading="loading">Login</v-btn>
      <v-btn @click="resetForm">Clear</v-btn>
      <p>Don't have an account? <v-btn @click="$router.push('/EmpForm')">Register</v-btn></p>
    </form>
  </template>
  
  <script>
  export default {
    data() {
      return {
        email: '',
        password: '',
        emailError: '',
        show1: false,
        loading: false,
        rules: {
          required: value => !!value || 'Required.',
          min: v => v.length >= 8 || 'Min 8 characters',
        },
      }
    },
  
    methods: {
      validateAll() {
        this.emailError = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/.test(this.email) ? '' : 'Must be a valid e-mail.'
        return !this.emailError && this.password.length >= 8
      },
  
      async submitForm() {
        if (this.validateAll()) {
          this.loading = true
          try {
            const response = await fetch('http://localhost:8000/Emplogin', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                email: this.email,
                password: this.password
              })
            })
  
            if (!response.ok) {
              const errorData = await response.json()
              throw new Error(errorData.detail || 'Login failed')
            }
  
            const data = await response.json()
            // Store the token in localStorage or your preferred storage method
            localStorage.setItem('access_token', data.access_token)
            console.log('Token stored:', data.access_token)
            this.$router.push('/EmpTable')
          } catch (error) {
            alert(`Error: ${error.message}`)
          } finally {
            this.loading = false
          }
        }
      },
  
      resetForm() {
        this.email = ''
        this.password = ''
        this.emailError = ''
        this.show1 = false
      }
    }
  }
  </script>