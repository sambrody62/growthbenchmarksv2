import React from "react";

import { firebase } from "./Firebase";

export const Logout = (props) => {
  const { onLogout, user } = props;
  if (user) {
    return (
      <a
        className="logout"
        href="/logout"
        onClick={(event) => {
          event.stopPropagation();
          event.preventDefault();
          firebase
            .auth()
            .signOut()
            .then(() => {
              window.dataLayer = window.dataLayer || [];
              window.dataLayer.push({
                eventCategory: "Account",
                eventAction: "LogOut",
                eventLabel: "LogOut",
                event: "LogOut",
              });
              onLogout();
            });
        }}
      >
        Log out
      </a>
    );
  } else {
    return null;
  }
};
