/* eslint react/no-unescaped-entities: 0 */
import React, { useState, useEffect } from "react";
import {
  Container,
  Button,
  Form,
  OverlayTrigger,
  Popover,
} from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faInfoCircle } from "@fortawesome/fontawesome-free-solid";

import { firebase } from "./Firebase";
import { Footer } from "./Footer";
import myFetch from "./myFetch";

export const EmailLogin = (props) => {
  const [successMessage, setSuccessMessage] = useState("");
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [didTryToSignIn, setDidTryToSignIn] = useState(false);

  useEffect(() => {
    const loggedInUser = localStorage.getItem("user");
    if (loggedInUser) {
      return;
    }
    // Confirm the link is a sign-in with email link.
    if (
      !didTryToSignIn &&
      firebase.auth().isSignInWithEmailLink(window.location.href)
    ) {
      setDidTryToSignIn(true);
      // Additional state parameters can also be passed via URL.
      // This can be used to continue the user's intended action before triggering
      // the sign-in operation.
      // Get the email if available. This should be available if the user completes
      // the flow on the same device where they started it.
      let localEmail = localStorage.getItem("loginEmail");
      if (!localEmail) {
        // User opened the link on a different device. To prevent session fixation
        // attacks, ask the user to provide the associated email again. For example:
        localEmail = window.prompt(
          "Please provide your email for confirmation"
        );
      }
      if (localEmail) {
        // The client SDK will parse the code from the link for you.
        firebase
          .auth()
          .signInWithEmailLink(localEmail, window.location.href)
          .then((result) => {
            window.localStorage.removeItem("loginEmail");
            const userForStorage = {
              uid: result.user.uid,
              isLoggedInWithEmail: true,
              providerId: "email",
            };
            window.localStorage.setItem("user", JSON.stringify(userForStorage));
            myFetch
              .post("/user/upsert", {
                user: { ...userForStorage, email: localEmail },
              })
              .then((response) => response.json())
              .then((data) => {
                if (!data.success) {
                  alert(
                    "Error saving the user to the databse: " + data.message
                  );
                }

                if (data.isNewUser) {
                  window.dataLayer = window.dataLayer || [];
                  window.dataLayer.push({
                    eventCategory: "Account",
                    eventAction: "Sign Up",
                    eventLabel: "Email",
                    event: "SignUp",
                  });
                }

                props.history.push("/");
              })
              .catch((errorSavingUser) => {
                console.error("Error saving user: " + errorSavingUser);
                alert("Error saving user: " + errorSavingUser);
              });
          })
          .catch((errorLoggingIn) => {
            setMessage("There was a problem logging in: " + errorLoggingIn);
          });
      }
    }
  });

  const submitEmail = (event) => {
    setIsLoading(true);
    event.preventDefault();

    const actionCodeSettings = {
      // URL you want to redirect back to. The domain (www.example.com) for this
      // URL must be in the authorized domains list in the Firebase Console.
      url: `${window.location.origin}/join`,
      handleCodeInApp: true,
    };

    firebase
      .auth()
      .sendSignInLinkToEmail(email, actionCodeSettings)
      .then(() => {
        setIsLoading(false);
        setSuccessMessage("Please check your email for a link to log in!");
        // Should set some local storage for the user's email
        localStorage.setItem("loginEmail", email);
      })
      .catch((error) => {
        setIsLoading(false);
        const errorCode = error.code;
        const errorMessage = error.message;
        console.error(
          "There was an error sending the magic link: " +
            errorCode +
            ", " +
            errorMessage
        );
        setMessage("There was an error: " + errorMessage);
      });
  };
  return (
    <>
      <div
        className="text-center d-flex flex-column align-items-center mb-5"
        style={{ flex: 1, backgroundColor: "white" }}
      >
        <div
          style={{ backgroundImage: "url(/images/signuppage-diamond.svg)" }}
          className="loginBox d-flex flex-column align-items-center justify-content-center text-center"
        >
          <a
            href="/"
            onClick={(e) => {
              e.preventDefault();
              props.history.push("/");
            }}
          >
            <div className="loginLogo">
              <img
                src="/images/Logo.png"
                style={{ maxHeight: 60 }}
                alt="Logo"
              ></img>
            </div>
          </a>
          <Container
            className="mt-5 mb-5 d-flex flex-column"
            style={{ flex: 1 }}
          >
            <h1>Join with Email</h1>
            <div style={{ fontWeight: "normal", height: 200 }}>
              <p>
                Login via email to see similar company benchmarks without
                needing to connect an account.
                <OverlayTrigger
                  trigger={["hover", "focus"]}
                  transition={false}
                  placement="bottom"
                  overlay={(overlayProps) => {
                    return (
                      <Popover id="popover-basic" {...overlayProps}>
                        <Popover.Title as="h3">Joining via Email</Popover.Title>
                        <Popover.Content>
                          Normally you would need to connect a Facebook account
                          to show aggregate benchmarks (anonymously). However if
                          you do not have an account, but still want to see
                          benchmarks, you can join via email. You can always
                          connect your account later to compare your performance
                          vs benchmarks, and unlock other useful features.
                        </Popover.Content>
                      </Popover>
                    );
                  }}
                >
                  {({ ref, ...triggerHandler }) => (
                    <span {...triggerHandler} ref={ref}>
                      <FontAwesomeIcon
                        className="m-1 dataUse"
                        icon={faInfoCircle}
                      />
                    </span>
                  )}
                </OverlayTrigger>
              </p>

              {successMessage ? (
                <span className="success-message">{successMessage}</span>
              ) : (
                <Form
                  onSubmit={submitEmail}
                  className="d-flex align-items-end justify-content-center text-center"
                >
                  <Form.Group className="d-flex flex-column align-items-start justify-content-left">
                    <Form.Label>Email</Form.Label>
                    <Form.Control
                      type="email"
                      name="email"
                      value={email}
                      disabled={isLoading}
                      onChange={(event) => setEmail(event.target.value)}
                    ></Form.Control>
                  </Form.Group>
                  <Form.Group>
                    <Button type="submit" disabled={isLoading}>
                      Log in
                    </Button>
                  </Form.Group>
                  <span className="error">{message}</span>
                </Form>
              )}
            </div>
          </Container>
        </div>
      </div>
      <Footer />
    </>
  );
};
