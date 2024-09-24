import React from "react";
import { OverlayTrigger, Popover } from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faInfoCircle } from "@fortawesome/fontawesome-free-solid";
import { useLocation } from "react-router-dom";

import { FacebookLogin } from "./FacebookLogin";
import { GoogleLogin } from "./GoogleLogin";
import { Footer } from "./Footer";

export const Home = (props) => {
  const { onLogin } = props;
  const location = useLocation();

  return (
    <>
      <div
        className="text-center d-flex flex-column align-items-center"
        style={{ flex: 1, backgroundColor: "white" }}
      >
        <div
          style={{ backgroundImage: "url(/images/signuppage-diamond.svg)" }}
          className="loginBox d-flex flex-column align-items-center justify-content-center text-center"
        >
          <div className="loginLogo">
            <img
              src="/images/Logo.png"
              style={{ maxHeight: 60 }}
              alt="Logo"
            ></img>
          </div>
          <h1 id="homeH1">How good is your marketing performance?</h1>
          <div>
            See your paid ads performance compared to (useful) benchmarks.
          </div>
          <FacebookLogin onLogin={onLogin} />
          <GoogleLogin onLogin={onLogin} />
          <div className="pt-3">
            <small>Connecting won't pull data yet.</small>
            <OverlayTrigger
              trigger={["hover", "focus"]}
              transition={false}
              placement="bottom"
              overlay={(overlayProps) => {
                return (
                  <Popover id="popover-basic" {...overlayProps}>
                    <Popover.Title as="h3">
                      Connecting your account
                    </Popover.Title>
                    <Popover.Content>
                      Facebook or Google will provide us your email address,
                      name and a list of your ad accounts. We will not pull or
                      store any performance data until you fill in the
                      onboarding form for a specific account. We will never sell
                      or share your individual account data with partners, we
                      only use it to show aggregate benchmarks (anonymously).
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
          </div>
        </div>
        <iframe
          width="640"
          height="360"
          src="https://www.loom.com/embed/b5cff446e7aa42d4bf7f88919e3bb772"
          frameBorder="0"
          allowFullScreen
          style={{
            maxWidth: "100%",
            filter: "drop-shadow(0px 25px 40px #0000008)",
            marginBottom: 50,
            marginTop: 120,
          }}
        ></iframe>
      </div>
      <Footer />
    </>
  );
};
