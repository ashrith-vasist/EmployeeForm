import { createRouter, createWebHistory } from "vue-router";

import EmployeeForm from "@/components/EmployeeForm.vue";
import { components } from "vuetify/dist/vuetify-labs.js";
import EmployeeTable from "@/components/EmployeeTable.vue";

import Login from "@/components/Login.vue";
import EditEmployee from "@/components/EditEmployee.vue";

const routes = [
    {
        path: '/EmpForm',
        name: 'EmployeeForm',
        component: EmployeeForm
    },
    {
        path:'/EmpTable',
        name: 'EmployeeTable',
        component: EmployeeTable
    },
    {
        path: '/edit-employee/:empid',
        name: 'EditEmployee',
        component: EditEmployee
    },
    {
        path: '/Emplogin',
        name: 'Emplogin',
        component: Login
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach((to, from, next) => {
    if (to.matched.some(record => record.meta.requiresAuth)) {
      if (!localStorage.getItem('access_token')) {
        next('/login')
      } else {
        next()
      }
    } else {
      next()
    }
  })
export default router;