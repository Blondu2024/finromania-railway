// Firebase Configuration for FinRomania
import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut } from 'firebase/auth';

const firebaseConfig = {
  apiKey: "AIzaSyAd-6BrYhjACidqiE6fEx_HjzgB3RT-cNc",
  authDomain: "finromania.ro",
  projectId: "fin-romania",
  storageBucket: "fin-romania.firebasestorage.app",
  messagingSenderId: "767909387138",
  appId: "1:767909387138:web:af4c23d33fef99d7a3cd9b",
  measurementId: "G-Y0MBNC1ZJB"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

// Configure Google Provider
googleProvider.setCustomParameters({
  prompt: 'select_account' // Always show account selector
});

// Sign in with Google
export const signInWithGoogle = async () => {
  try {
    const result = await signInWithPopup(auth, googleProvider);
    const user = result.user;
    
    // Get the ID token to send to backend
    const idToken = await user.getIdToken();
    
    return {
      success: true,
      user: {
        uid: user.uid,
        email: user.email,
        name: user.displayName,
        picture: user.photoURL
      },
      idToken
    };
  } catch (error) {
    console.error('Google sign-in error:', error);
    return {
      success: false,
      error: error.message
    };
  }
};

// Sign out
export const firebaseSignOut = async () => {
  try {
    await signOut(auth);
    return { success: true };
  } catch (error) {
    console.error('Sign out error:', error);
    return { success: false, error: error.message };
  }
};

// Get current user
export const getCurrentUser = () => {
  return auth.currentUser;
};

// Listen to auth state changes
export const onAuthStateChange = (callback) => {
  return auth.onAuthStateChanged(callback);
};

export { auth };
