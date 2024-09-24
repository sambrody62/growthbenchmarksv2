import React from "react";
import { Button, Image } from "react-bootstrap";
import GoogleReactLogin from "react-google-login";

import { firebase } from "./Firebase";
import myFetch from "./myFetch";

export const GoogleLogin = (props) => {
  const { isLoading, onLogin } = props;
  if (isLoading) {
    return false;
  }

  const responseGoogle = async (response) => {
    // Get a code from Google Login
    const { code } = response;
    if (code) {
      // Then send it to our server
      // Then get a refresh token from the server side
      const tokenResponse = await myFetch
        .post("/user/google_authenticate_code", {
          code,
        })
        .then((response) => response.json());

      // Build Firebase credential with the Google ID token.
      const credential = firebase.auth.GoogleAuthProvider.credential(
        tokenResponse.id_token
      );

      // Sign in with credential from the Google user.
      firebase
        .auth()
        .signInWithCredential(credential)
        .then((user) => {
          // push login event
          window.dataLayer = window.dataLayer || [];
          window.dataLayer.push({
            eventCategory: "Account",
            eventAction: "Log In",
            eventLabel: "Google",
            event: "LogIn",
          });
          // Set the user's access and refresh tokens with the tokens we got manually
          user.credential.accessToken = tokenResponse.access_token;
          user.credential.refreshToken = tokenResponse.refresh_token;
          onLogin(user);
        })
        .catch((error) => {
          console.error("Error logging in: " + error);
        });
    }
  };

  return (
    <GoogleReactLogin
      clientId="480005130966-6g0kp8sdf5bajit6ghqf3h8fpjunqsob.apps.googleusercontent.com"
      scope="profile email https://www.googleapis.com/auth/adwords"
      onSuccess={responseGoogle}
      onFailure={responseGoogle}
      cookiePolicy={"single_host_origin"}
      prompt="consent"
      accessType="offline"
      responseType="code"
      render={(renderProps) => {
        return (
          <Button
            className="google-login"
            style={{
              backgroundColor: "white",
              fontFamily: "Roboto",
              background: "#4285F4",
              padding: 0,
              paddingRight: 20,
              border: 0,
              borderRadius: 2,
            }}
            variant="primary"
            onClick={renderProps.onClick}
          >
            <Image style={{ marginRight: 10 }} src="/images/GoogleLogin.svg" />
            Connect with Google
          </Button>
        );
      }}
    />
  );
};
