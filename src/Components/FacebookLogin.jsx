import React from "react";
import { Button } from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faFacebook } from "@fortawesome/free-brands-svg-icons";

import { firebase, facebookAuthProvider } from "./Firebase";

export const FacebookLogin = (props) => {
  const { isLoading, onLogin } = props;
  if (isLoading) {
    return false;
  }
  return (
    <Button
      className="login mt-4"
      variant="primary"
      onClick={() => {
        firebase
          .auth()
          .signInWithPopup(facebookAuthProvider)
          .then((user) => {
            // push login event
            window.dataLayer = window.dataLayer || [];
            window.dataLayer.push({
              eventCategory: "Account",
              eventAction: "Log In",
              eventLabel: "Facebook",
              event: "LogIn",
            });

            onLogin(user);
          });
      }}
    >
      <div style={{ display: "flex" }}>
        <span className="pr-2">
          <FontAwesomeIcon icon={faFacebook} style={{ fontSize: 28 }} />
        </span>
        <span className="m-auto">Connect with Facebook</span>
      </div>
    </Button>
  );
};

export const ExpandIcon = () => {
  return <FontAwesomeIcon icon={faExpand} width="20" height="20" />;
};
