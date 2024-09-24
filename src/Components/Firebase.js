import firebase from "firebase/app";
import "firebase/auth";
import "firebase/functions";

const config = {
  apiKey: process.env.REACT_APP_API_KEY,
  authDomain: process.env.REACT_APP_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_PROJECT_ID,
  messagingSenderId: process.env.REACT_APP_MESSAGING_SENDER_ID,
};

firebase.initializeApp(config);

const facebookAuthProvider = new firebase.auth.FacebookAuthProvider();
facebookAuthProvider.addScope("ads_read");

export { firebase, facebookAuthProvider };
