import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  en: {
    translation: {
      welcome: 'Welcome to AFCON 2025 Assistant! I can help you with:',
      features: {
        matches: '🏆 Match schedules and results',
        hotels: '🏨 Hotel and accommodation information',
        restaurants: '🍽️ Restaurant recommendations',
        health: '🏥 Hospitals and pharmacies',
        transport: '🚗 Transportation and directions'
      },
      errors: {
        connection: 'Unable to connect to the server. Please check your internet connection.',
        server: 'Server error: {{message}}',
        unknown: 'An unexpected error occurred. Please try again.',
        timeout: 'The request timed out. Please try again.',
        title: 'An error occurred',
        message: 'We apologize for the inconvenience. Please try again.',
        reset: 'Reset'
      },
      loading: {
        thinking: 'Thinking...',
        searching: 'Searching for information...',
        processing: 'Processing your request...',
        default: 'Loading...'
      },
      confidence: 'Confidence level',
      sources: 'Sources',
      suggested: {
        title: 'You might want to ask:',
        matches: 'What matches are scheduled for tomorrow?',
        hotels: 'Which hotels are near the main stadium?',
        transport: 'How can I get from the airport to the stadium?'
      },
      ask: 'How can I assist you today?',
      error: 'Sorry, an error occurred. Please try again.',
      login: 'Login',
      logout: 'Logout',
      input: {
        placeholder: 'Type your message...',
        waiting: 'Please wait for the response...',
        send: 'Send message'
      }
    }
  },
  fr: {
    translation: {
      welcome: 'Bienvenue sur l\'Assistant CAN 2025 ! Je peux vous aider avec :',
      features: {
        matches: '🏆 Calendrier et résultats des matches',
        hotels: '🏨 Informations sur les hôtels et hébergements',
        restaurants: '🍽️ Recommandations de restaurants',
        health: '🏥 Hôpitaux et pharmacies',
        transport: '🚗 Transport et itinéraires'
      },
      errors: {
        connection: 'Impossible de se connecter au serveur. Veuillez vérifier votre connexion internet.',
        server: 'Erreur serveur : {{message}}',
        unknown: 'Une erreur inattendue s\'est produite. Veuillez réessayer.',
        timeout: 'La requête a expiré. Veuillez réessayer.',
        title: 'Une erreur s\'est produite',
        message: 'Nous nous excusons pour la gêne occasionnée. Veuillez réessayer.',
        reset: 'Réinitialiser'
      },
      loading: {
        thinking: 'Je réfléchis...',
        searching: 'Recherche d\'informations...',
        processing: 'Traitement de votre demande...',
        default: 'Chargement...'
      },
      confidence: 'Niveau de confiance',
      sources: 'Sources',
      suggested: {
        title: 'Vous pourriez demander :',
        matches: 'Quels sont les matches prévus demain ?',
        hotels: 'Quels hôtels sont près du stade principal ?',
        transport: 'Comment aller de l\'aéroport au stade ?'
      },
      ask: 'Comment puis-je vous aider aujourd\'hui ?',
      error: 'Désolé, une erreur s\'est produite. Veuillez réessayer.',
      login: 'Connexion',
      logout: 'Déconnexion',
      input: {
        placeholder: 'Tapez votre message...',
        waiting: 'Veuillez attendre la réponse...',
        send: 'Envoyer le message'
      }
    }
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'en', // default language
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;