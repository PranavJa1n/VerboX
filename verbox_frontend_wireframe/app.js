// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/13.3.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/13.3.0/firebase-analytics.js";
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, onAuthStateChanged, sendEmailVerification } from "https://www.gstatic.com/firebasejs/13.3.0/firebase-auth.js";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const auth = getAuth()

const submitBtn = document.querySelector("#submit-btn")

submitBtn.addEventListener("click", () => {
    let email = userField.value;
    let pass = passField.value;

    if (isLoginView == false) {
        console.log("SignUp")
        createUserWithEmailAndPassword(
            auth, email, pass
        ).then((userCredential) => {
            sendEmailVerification(userCredential.user)
                .then(() => {
                    console.log("Verification email sent! Please verify your inbox before logging in.");
                    alert("Verification email sent! Please verify your inbox before logging in.");
                });
        }
        ).catch((error) => {
            const errorCode = error.code;
            const errorMessage = error.message;
            // ..
        })
    } else {
        console.log("LogIn")
        signInWithEmailAndPassword(
            auth, email, pass
        ).then((userCredential) => {
            const user = userCredential.user;
            if (!user.emailVerified) {
                // Log them right back out so the session isn't saved
                alert("Your email is not verified yet. Please check your inbox and click the verification link.");
                signOut(auth); 
            }
            console.log("verified")
            window.location.href = "/docs.html";
        }).catch((error) => {
            const errorCode = error.code;
            const errorMessage = error.message;
            // ..
        })
    }
})







onAuthStateChanged(auth, (user) => {
    if (user) {
        // User is signed in, see docs for a list of available properties
        // https://firebase.google.com/docs/reference/js/auth.user
        const uid = user.uid;
        // ...
    } else {
        // User is signed out
        // ...
    }
});

const userField = document.querySelector("#email")
const passField = document.querySelector("#pass")
const eye = document.querySelector("#eye")

const userCount = document.querySelector("#userCount");
const passCount = document.querySelector("#passCount");


userField.addEventListener("input", () => {
    const currLength = userField.value.length;
    userCount.textContent = currLength;
    if (currLength == 0) {
        userCount.textContent = null;
    }
})


passField.addEventListener("input", () => {
    const currLength = passField.value.length;
    passCount.textContent = currLength;
    if (currLength == 0) {
        passCount.textContent = null;
    }
})

eye.addEventListener("click", () => {

    if (passField.type == 'text') {
        passField.type = 'password';
    } else {
        passField.type = 'text';
    }
})


let isLoginView = false;
const toggleBtn = document.querySelector("#toggle-btn")
const toggleMsg = document.querySelector("#toggle-msg")


const navSignup = document.querySelector("#nav-signup")
const navLogin = document.querySelector("#nav-login")

const btnClassList = ["w-20", "bg-black", "text-orange-100", "w-30", "bg-orange-100", "text-black"];


function toggle() {
    if (isLoginView == false) {
        toggleBtn.textContent = "Create account"
        submitBtn.textContent = "Log in"
        toggleMsg.textContent = "Don't have an account ?"
        isLoginView = true;
        btnClassList.forEach(cls => toggleBtn.classList.toggle(cls));
        btnClassList.forEach(cls => submitBtn.classList.toggle(cls));
    } else {
        toggleBtn.textContent = "Log in"
        submitBtn.textContent = "Create account"
        toggleMsg.textContent = "Already have an account ?"
        isLoginView = false;
        btnClassList.forEach(cls => toggleBtn.classList.toggle(cls));
        btnClassList.forEach(cls => submitBtn.classList.toggle(cls));
    }
}


toggleBtn.addEventListener("click", () => {
    toggle();
})

navSignup.addEventListener("click", () => {
    if (isLoginView == true) {
        toggleBtn.textContent = "Log in"
        submitBtn.textContent = "Create account"
        toggleMsg.textContent = "Already have an account ?"
        isLoginView = false;
        btnClassList.forEach(cls => toggleBtn.classList.toggle(cls));
        btnClassList.forEach(cls => submitBtn.classList.toggle(cls));
    }
})

navLogin.addEventListener("click", () => {
    if (isLoginView == false) {
        toggleBtn.textContent = "Create account"
        submitBtn.textContent = "Log in"
        toggleMsg.textContent = "Don't have an account ?"
        isLoginView = true;
        btnClassList.forEach(cls => toggleBtn.classList.toggle(cls));
        btnClassList.forEach(cls => submitBtn.classList.toggle(cls));
    }
})

const partners = [
    { id: 1, name: 'SARVAM' }
]



