<template>
  <header class="app-header">
    <div class="burger-menu">

    </div>
    <div class="logo">
      <img src="@/assets/logo.png" alt="Logo" />
    </div>
  </header>

  <nav v-if="menuOpen" class="nav-menu">
    <router-link to="/">Home</router-link>
    <router-link to="/about">About</router-link>
  </nav>

  <router-view />
</template>


<script setup lang="ts">
import { ref } from 'vue'

const menuOpen = ref(false)

const toggleMenu = () => {
  menuOpen.value = !menuOpen.value
}
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background-color: #f5f5f5;
  border-bottom: 1px solid #ddd;
}

.burger-menu {
  font-size: 24px;
  cursor: pointer;
}

.logo {
  flex-grow: 1;
  text-align: center;
}

.logo img {
  height: 40px;
}

.nav-menu {
  display: flex;
  flex-direction: column;
  background-color: #fff;
  border-bottom: 1px solid #ccc;
  padding: 10px 20px;
}

.nav-menu a {
  padding: 10px 0;
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
}

.nav-menu a.router-link-exact-active {
  color: #42b983;
}
</style>

