import { createI18n } from 'vue-i18n'
import en from '@/locales/en'
import tr from '@/locales/tr'

// Get saved language from localStorage or default to 'en'
const savedLanguage = localStorage.getItem('app-language') || 'en'

const i18n = createI18n({
  legacy: false,
  locale: savedLanguage,
  fallbackLocale: 'en',
  messages: {
    en,
    tr
  }
})

export default i18n
