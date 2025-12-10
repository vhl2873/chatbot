// Firebase Configuration
const firebaseConfig = {
  apiKey: "AIzaSyAxRzNMsNMUvH_obCVwUowpNguHlRsF5BU",
  authDomain: "chatbotgents.firebaseapp.com",
  projectId: "chatbotgents",
  storageBucket: "chatbotgents.firebasestorage.app",
  messagingSenderId: "634217778996",
  appId: "1:634217778996:web:cd79c6e63eae20b5c79f61",
  measurementId: "G-R1M1KMV2M0"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// Initialize Firebase Authentication and Firestore
const auth = firebase.auth();
const db = firebase.firestore();

