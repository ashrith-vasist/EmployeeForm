<template>

  <h1>Employee Form</h1>
  <br>
  <form @submit.prevent="submitForm">
    <!-- <v-text-field
      v-model="empID"
      :error-messages="empIDError"
      label="Employee ID"
    ></v-text-field> -->
    <v-text-field
      v-model="name"
      :counter="10"
      :error-messages="nameError"
      label="Name"
    ></v-text-field>
    <v-text-field
      v-model="phone"
      :counter="7"
      :error-messages="phoneError"
      label="Phone Number"
    ></v-text-field>
    <v-text-field
      v-model="email"
      :error-messages="emailError"
      label="E-mail"
    ></v-text-field>
    <v-text-field
      v-model="date"
      label="Date of Birth"
      readonly
      append-icon="mdi-calendar"
      :error-messages="dateError"
      @click:append="showDatePicker = !showDatePicker"
     
    ></v-text-field>
    <v-dialog
      v-model="showDatePicker"
      persistent
      max-width="290px"
      @click:outside="closeDatePicker"
    >
      <v-date-picker
        v-model="date"
        @input="handleDateSelection"
      ></v-date-picker>
    </v-dialog>
    <v-textarea
      v-model="desc"
      :error-messages="descError"
      label="Address"
    ></v-textarea>

    <v-text-field
            v-model="password"
            :append-icon="show1 ? 'mdi-eye' : 'mdi-eye-off'"
            :rules="[rules.required, rules.min]"
            :type="show1 ? 'text' : 'password'"
            hint="At least 8 characters"
            label="Password"
            name="input-10-1"
            counter
            @click:append="show1 = !show1"
      ></v-text-field>
      <v-text-field
            v-model="confirmPassword"
            :append-icon="show1 ? 'mdi-eye' : 'mdi-eye-off'"
            :rules="[rules.required, rules.min]"
            :type="show1 ? 'text' : 'password'"
            hint="At least 8 characters"
            label="Confirm Password"
            name="input-10-1"
            counter
            @click:append="show1 = !show1"
      ></v-text-field>

    <v-btn class="me-4" type="submit">Register</v-btn>
    <v-btn @click="resetForm">Clear</v-btn>
    <p>If already have an account ? <v-btn @click="this.$router.push('/Emplogin')">Login</v-btn> </p>
  </form>
</template>

<script>
export default {
  data() {
    return {
      name: '',
      phone: '',
      email: '',
      date: null,
      desc: '',
      nameError: '',
      phoneError: '',
      emailError: '',
      descError: '',
      dateError: '',
      showDatePicker: false,
      show1: false,
        show2: true,
        password: '',
        confirmPassword: '',
        rules: {
          required: value => !!value || 'Required.',
          min: v => v.length >= 8 || 'Min 8 characters',
          emailMatch: () => (`The email and password you entered don't match`),
        },
    };
  },

  methods: {
  async submitForm() {
  this.validateAll();
  const hasErrors = Object.values(this.$data)
    .filter(key => key.toString().includes('Error'))
    .some(value => value.length > 0);

  if (!hasErrors) {
    try {
      // Log the data being sent to the backend
      console.log({
        name: this.name,
        phno: this.phone,
        email: this.email,
        dob: this.date,  // Ensure this is a string in the format 'YYYY-MM-DD'
        addr: this.desc
      });

      const response = await fetch('http://localhost:8000/EmpForm', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          
          name: this.name,
          phno: this.phone,
          email: this.email,
          dob: this.date,  // Ensure it's in the 'YYYY-MM-DD' format
          addr: this.desc,
          password: this.password,
          confirm_password: this.confirmPassword
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit form');
      }

      const data = await response.json();
      console.log(data);
      console.log('Form submitted successfully!', data);
      alert('Employee data saved successfully!');
      this.$router.push('/Emplogin')

      
    } catch (error) {
      console.error('Error submitting form:', error);
      alert(`Error: ${error.message}`);
    }
  } else {
    alert('Please fix the errors in the form.');
  }
},
    validateAll() {
      this.nameError = this.name.length >= 2 ? '' : 'Name needs to be at least 2 characters.';
      this.phoneError = /^[0-9-]{10,}$/.test(this.phone) ? '' : 'Phone number needs to be at least 10 digits.';
      this.emailError = /^[a-z.-]+@[a-z.-]+\.[a-z]+$/i.test(this.email) ? '' : 'Must be a valid e-mail.';
      this.descError = this.desc.length > 0 ? '' : 'Enter a valid Address';
      this.dateError = this.date ? '' : 'Date of Birth is required';
    },
    handleDateSelection(selectedDate) {
      // Format the selected date to yyyy-mm-dd
      this.date = this.formatDate(selectedDate);
      this.showDatePicker = false;
    },
    closeDatePicker() {
      this.showDatePicker = false;
    },
    formatDate(date) {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0'); // Months are 0-based
    const day = String(d.getDate()).padStart(2, '0');

    return `${year}-${month}-${day}`;
  },
    resetForm() {
      Object.keys(this.$data).forEach(key => {
        if (key === 'date') {
          this[key] = null;
        } else if (typeof this[key] === 'string') {
          this[key] = '';
        } else if (typeof this[key] === 'boolean') {
          this[key] = false;
        }
      });
    },
  },


};
</script>
