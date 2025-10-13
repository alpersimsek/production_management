<template>
  <v-app>
    <v-app-bar app flat>
      <v-toolbar-title>Olgahan ERP</v-toolbar-title>
      <v-spacer />
      <v-btn to="/orders" variant="text">Sipariş</v-btn>
    </v-app-bar>
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>
