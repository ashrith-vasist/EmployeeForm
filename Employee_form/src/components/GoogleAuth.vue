<template>
    <div class="login-container">
      <div class="left-section">
        <img src="./Employee.jpeg" alt="Employee Portal" class="employee-image">
        <h1>Employee Portal</h1>
      </div>
      
      <div class="right-section">
        <div class="login-box">
          <h2>Welcome Back!</h2>
          <button @click="loginWithGoogle" class="google-btn">
            <img src="data:image/png;base64,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" alt="Google Logo" class="google-icon">
            Sign in with Google
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'LoginComponent',
    methods: {
      loginWithGoogle() {
        window.location.href = 'http://localhost:8000/auth/google'
      }
    }
  }
  </script>
  
  <style scoped>
  .login-container {
    display: flex;
    min-height: 100vh;
  }
  
  .left-section {
    width: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background-color: #f5f5f5;
    padding: 20px;
  }
  
  .employee-image {
    width: 300px;
    height: auto;
    margin-bottom: 20px;
  }
  
  .right-section {
    width: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }
  
  .login-box {
    text-align: center;
  }
  
  h1 {
    color: #333;
    margin: 10px 0;
  }
  
  h2 {
    color: white;
    margin-bottom: 20px;
  }
  
  .google-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 10px 20px;
    background-color: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    transition: all 0.3s ease;
    color: black;
  }
  
  .google-btn:hover {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }
  
  .google-icon {
    width: 18px;
    height: 18px;
    margin-right: 10px;
  }
  
  /* Responsive design for smaller screens */
  @media (max-width: 768px) {
    .login-container {
      flex-direction: column;
    }
    
    .left-section,
    .right-section {
      width: 100%;
    }
    
    .left-section {
      padding: 40px 20px;
    }
    
    .employee-image {
      width: 200px;
    }
  }
  </style>