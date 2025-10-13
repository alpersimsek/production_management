<template>
  <v-container>
    <v-toolbar flat>
      <v-text-field v-model="q" label="Ara" density="comfortable" />
      <v-spacer/>
      <v-btn>Yeni Sipariş</v-btn>
    </v-toolbar>
    <v-data-table :items="items" :headers="headers" />
  </v-container>
</template>
<script setup>
import { ref } from 'vue'
const q = ref('')
const headers = [
  { title: 'ID', key: 'id' },
  { title: 'Müşteri', key: 'customer' },
  { title: 'Termin', key: 'due' },
  { title: 'Durum', key: 'status' }
]
const items = []
</script>
